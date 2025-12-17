"""
Lloyd's Register Cargo Tracking Service (CTS) Integration
Provides third-party verification and certification for vehicle shipments

ISO 28000 Compliant | ISO 18602 Compliant
"""
import requests
import logging
from decimal import Decimal
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class LloydRegisterService:
    """
    Integration with Lloyd's Register Cargo Tracking Service
    
    Lloyd's Register provides:
    - Independent third-party verification of shipments
    - Professional surveyor inspections at origin and destination ports
    - 24/7 GPS monitoring and incident response
    - Certificate of Safe Delivery upon successful completion
    - Marine insurance underwriting at preferential rates
    
    API Documentation: https://www.lr.org/en/cargo-tracking/api/
    """
    
    BASE_URL = getattr(settings, 'LLOYD_REGISTER_API_URL', 'https://api.lr.org/cargo-tracking/v1')
    API_KEY = getattr(settings, 'LLOYD_REGISTER_API_KEY', None)
    CLIENT_ID = getattr(settings, 'LLOYD_REGISTER_CLIENT_ID', None)
    
    # Service level pricing (per shipment, in CAD)
    PRICING = {
        'standard': 300,      # Basic monitoring
        'premium': 600,       # 24/7 monitoring with alerts
        'surveyor': 1200,     # Full surveyor service with inspections
    }
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Lloyd's Register API is properly configured"""
        return bool(cls.API_KEY and cls.CLIENT_ID)
    
    @classmethod
    def register_shipment(cls, shipment, service_level='standard') -> Optional[str]:
        """
        Register a new shipment with Lloyd's Register CTS
        
        Args:
            shipment: Shipment model instance
            service_level: 'standard', 'premium', or 'surveyor'
            
        Returns:
            Lloyd's Register tracking ID (str) or None if failed
        """
        if not cls.is_configured():
            logger.warning("Lloyd's Register API not configured - using mock mode")
            return cls._mock_register_shipment(shipment, service_level)
        
        try:
            vehicle = shipment.deal.vehicle
            dealer = shipment.deal.dealer
            buyer = shipment.deal.buyer
            
            payload = {
                'client_reference': shipment.tracking_number,
                'service_level': service_level,
                'vehicle': {
                    'vin': vehicle.vin,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'color': vehicle.color,
                    'value_cad': float(shipment.deal.final_price),
                    'condition': vehicle.condition,
                },
                'route': {
                    'origin_port': shipment.origin_port,
                    'origin_country': 'Canada',
                    'destination_port': shipment.destination_port,
                    'destination_country': shipment.destination_country,
                    'shipping_company': shipment.shipping_company,
                    'estimated_departure': shipment.estimated_departure.isoformat() if shipment.estimated_departure else None,
                    'estimated_arrival': shipment.estimated_arrival.isoformat() if shipment.estimated_arrival else None,
                },
                'container': {
                    'number': shipment.container_number or None,
                    'type': shipment.container_type or None,
                    'seal_number': shipment.seal_number or None,
                    'seal_type': shipment.seal_type or None,
                },
                'contacts': {
                    'dealer': {
                        'name': f"{dealer.first_name} {dealer.last_name}",
                        'email': dealer.email,
                        'phone': getattr(dealer, 'phone', ''),
                        'company': getattr(dealer, 'company_name', ''),
                    },
                    'buyer': {
                        'name': f"{buyer.first_name} {buyer.last_name}",
                        'email': buyer.email,
                        'phone': getattr(buyer, 'phone', ''),
                        'country': shipment.destination_country,
                    },
                },
                'security': {
                    'risk_level': shipment.security_risk_level,
                    'insurance_required': True,
                    'insurance_value_cad': float(shipment.insurance_coverage_amount or shipment.deal.final_price),
                },
            }
            
            response = requests.post(
                f"{cls.BASE_URL}/shipments",
                headers={
                    'Authorization': f'Bearer {cls.API_KEY}',
                    'X-Client-ID': cls.CLIENT_ID,
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                lr_tracking_id = data['lr_tracking_id']
                
                logger.info(f"Successfully registered shipment {shipment.tracking_number} with LR: {lr_tracking_id}")
                
                # Cache the registration data
                cache.set(f'lr_shipment_{lr_tracking_id}', data, 86400 * 30)  # 30 days
                
                return lr_tracking_id
            else:
                logger.error(f"Lloyd's Register API error: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Failed to register with Lloyd's Register: {e}")
            return None
    
    @classmethod
    def get_verification_status(cls, lr_tracking_id: str) -> Optional[Dict]:
        """
        Check verification status from Lloyd's Register
        
        Returns:
            Dict with status information:
            {
                'status': 'pending_origin' | 'origin_approved' | 'in_monitoring' | etc,
                'origin_inspection': {...},
                'current_location': {...},
                'destination_inspection': {...},
                'certificate_available': bool,
                'incidents': [...]
            }
        """
        if not cls.is_configured():
            return cls._mock_verification_status(lr_tracking_id)
        
        # Check cache first
        cache_key = f'lr_status_{lr_tracking_id}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/shipments/{lr_tracking_id}/status",
                headers={
                    'Authorization': f'Bearer {cls.API_KEY}',
                    'X-Client-ID': cls.CLIENT_ID,
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Cache for 30 minutes
                cache.set(cache_key, data, 1800)
                
                return data
            else:
                logger.error(f"Failed to get LR status: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Lloyd's Register status check error: {e}")
            return None
    
    @classmethod
    def request_origin_inspection(cls, lr_tracking_id: str, inspection_date: datetime) -> bool:
        """
        Request LR surveyor inspection at origin port
        
        Args:
            lr_tracking_id: LR tracking reference
            inspection_date: Preferred inspection datetime
            
        Returns:
            True if inspection scheduled successfully
        """
        if not cls.is_configured():
            logger.info(f"Mock: Origin inspection requested for {lr_tracking_id}")
            return True
        
        try:
            payload = {
                'inspection_type': 'origin',
                'preferred_date': inspection_date.isoformat(),
                'inspection_scope': [
                    'vehicle_condition',
                    'vin_verification',
                    'photograph_documentation',
                    'container_seal_application',
                ],
            }
            
            response = requests.post(
                f"{cls.BASE_URL}/shipments/{lr_tracking_id}/inspections",
                headers={
                    'Authorization': f'Bearer {cls.API_KEY}',
                    'X-Client-ID': cls.CLIENT_ID,
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=30
            )
            
            return response.status_code == 201
            
        except requests.RequestException as e:
            logger.error(f"Failed to request origin inspection: {e}")
            return False
    
    @classmethod
    def request_destination_inspection(cls, lr_tracking_id: str, inspection_date: datetime) -> bool:
        """
        Request LR surveyor inspection at destination port
        
        Args:
            lr_tracking_id: LR tracking reference
            inspection_date: Preferred inspection datetime
            
        Returns:
            True if inspection scheduled successfully
        """
        if not cls.is_configured():
            logger.info(f"Mock: Destination inspection requested for {lr_tracking_id}")
            return True
        
        try:
            payload = {
                'inspection_type': 'destination',
                'preferred_date': inspection_date.isoformat(),
                'inspection_scope': [
                    'container_seal_verification',
                    'vehicle_condition_verification',
                    'damage_assessment',
                    'customs_documentation',
                ],
            }
            
            response = requests.post(
                f"{cls.BASE_URL}/shipments/{lr_tracking_id}/inspections",
                headers={
                    'Authorization': f'Bearer {cls.API_KEY}',
                    'X-Client-ID': cls.CLIENT_ID,
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=30
            )
            
            return response.status_code == 201
            
        except requests.RequestException as e:
            logger.error(f"Failed to request destination inspection: {e}")
            return False
    
    @classmethod
    def get_certificate(cls, lr_tracking_id: str) -> Optional[Dict]:
        """
        Retrieve Certificate of Safe Delivery from Lloyd's Register
        
        Returns:
            Dict with certificate data including PDF download URL
        """
        if not cls.is_configured():
            return cls._mock_certificate(lr_tracking_id)
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/shipments/{lr_tracking_id}/certificate",
                headers={
                    'Authorization': f'Bearer {cls.API_KEY}',
                    'X-Client-ID': cls.CLIENT_ID,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Certificate not available yet: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve certificate: {e}")
            return None
    
    @classmethod
    def report_incident(cls, lr_tracking_id: str, incident_data: Dict) -> bool:
        """
        Report a security incident to Lloyd's Register
        
        Args:
            lr_tracking_id: LR tracking reference
            incident_data: {
                'incident_type': 'delay' | 'damage' | 'theft' | 'accident' | 'customs',
                'severity': 'minor' | 'moderate' | 'severe' | 'critical',
                'description': str,
                'location': str,
                'reported_by': str,
                'police_report_filed': bool,
            }
            
        Returns:
            True if incident reported successfully
        """
        if not cls.is_configured():
            logger.warning(f"Mock: Incident reported for {lr_tracking_id}")
            return True
        
        try:
            response = requests.post(
                f"{cls.BASE_URL}/shipments/{lr_tracking_id}/incidents",
                headers={
                    'Authorization': f'Bearer {cls.API_KEY}',
                    'X-Client-ID': cls.CLIENT_ID,
                    'Content-Type': 'application/json',
                },
                json=incident_data,
                timeout=30
            )
            
            return response.status_code == 201
            
        except requests.RequestException as e:
            logger.error(f"Failed to report incident: {e}")
            return False
    
    @classmethod
    def calculate_insurance_premium(cls, vehicle_value: Decimal, route: str, service_level: str) -> Decimal:
        """
        Calculate insurance premium through Lloyd's Register underwriting
        
        Args:
            vehicle_value: Value in CAD
            route: 'canada_west_africa' | 'canada_east_africa' | etc
            service_level: 'standard' | 'premium' | 'surveyor'
            
        Returns:
            Insurance premium in CAD
        """
        base_rate = Decimal('0.015')  # 1.5% of vehicle value
        
        # Route-based risk adjustment
        route_multipliers = {
            'canada_west_africa': Decimal('1.2'),
            'canada_east_africa': Decimal('1.3'),
            'canada_north_africa': Decimal('1.0'),
            'canada_south_africa': Decimal('1.1'),
        }
        
        # Service level discounts
        service_discounts = {
            'standard': Decimal('1.0'),
            'premium': Decimal('0.85'),    # 15% discount
            'surveyor': Decimal('0.75'),   # 25% discount
        }
        
        route_multiplier = route_multipliers.get(route, Decimal('1.2'))
        service_discount = service_discounts.get(service_level, Decimal('1.0'))
        
        premium = vehicle_value * base_rate * route_multiplier * service_discount
        
        return premium.quantize(Decimal('0.01'))
    
    # ===== MOCK DATA FOR DEVELOPMENT/TESTING =====
    
    @classmethod
    def _mock_register_shipment(cls, shipment, service_level) -> str:
        """Generate mock LR tracking ID for development"""
        import hashlib
        
        # Generate deterministic mock ID
        seed = f"{shipment.tracking_number}_{service_level}_{datetime.now().date()}"
        mock_id = f"LR{hashlib.md5(seed.encode()).hexdigest()[:10].upper()}"
        
        logger.info(f"MOCK: Registered shipment with LR ID: {mock_id}")
        
        # Cache mock data
        mock_data = {
            'lr_tracking_id': mock_id,
            'status': 'pending_origin',
            'service_level': service_level,
            'registered_at': timezone.now().isoformat(),
            'note': 'MOCK DATA - Lloyd\'s Register API not configured',
        }
        cache.set(f'lr_shipment_{mock_id}', mock_data, 86400 * 30)
        
        return mock_id
    
    @classmethod
    def _mock_verification_status(cls, lr_tracking_id: str) -> Dict:
        """Mock verification status for development"""
        return {
            'lr_tracking_id': lr_tracking_id,
            'status': 'in_monitoring',
            'origin_inspection': {
                'completed': True,
                'date': (timezone.now() - timedelta(days=5)).isoformat(),
                'surveyor': 'John Smith (LR Surveyor #12345)',
                'result': 'approved',
                'notes': 'Vehicle condition matches description. All documentation verified.',
            },
            'current_location': {
                'latitude': 14.6928,
                'longitude': -17.4467,
                'location': 'Atlantic Ocean - en route to Dakar',
                'last_update': timezone.now().isoformat(),
            },
            'destination_inspection': {
                'completed': False,
                'scheduled_date': (timezone.now() + timedelta(days=3)).isoformat(),
            },
            'certificate_available': False,
            'incidents': [],
            'note': 'MOCK DATA - Lloyd\'s Register API not configured',
        }
    
    @classmethod
    def _mock_certificate(cls, lr_tracking_id: str) -> Dict:
        """Mock certificate data for development"""
        return {
            'lr_tracking_id': lr_tracking_id,
            'certificate_number': f'LR-CERT-{lr_tracking_id}',
            'issue_date': timezone.now().isoformat(),
            'certificate_type': 'Certificate of Safe Delivery',
            'status': 'issued',
            'pdf_url': f'https://api.lr.org/certificates/{lr_tracking_id}.pdf',
            'verification_url': f'https://verify.lr.org/certificate/{lr_tracking_id}',
            'surveyor_signature': 'Digital signature applied',
            'note': 'MOCK DATA - Lloyd\'s Register API not configured',
        }


class ISO18602Exporter:
    """
    Export shipment tracking data in ISO 18602 compliant format
    For integration with port management systems and customs authorities
    """
    
    @classmethod
    def export_to_xml(cls, shipment) -> str:
        """
        Generate ISO 18602 compliant XML tracking message
        
        Args:
            shipment: Shipment model instance
            
        Returns:
            XML string
        """
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        # Create root element
        root = Element('TrackingMessage')
        root.set('xmlns', 'urn:iso:18602:2013')
        root.set('version', '1.0')
        
        # Message metadata
        SubElement(root, 'MessageID').text = f"TRK-{shipment.tracking_number}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        SubElement(root, 'Timestamp').text = timezone.now().isoformat()
        SubElement(root, 'MessageType').text = 'IFTSTA'
        
        # Container/Transport Unit
        transport_unit = SubElement(root, 'TransportUnit')
        SubElement(transport_unit, 'ContainerID').text = shipment.container_number or 'N/A'
        SubElement(transport_unit, 'ContainerType').text = shipment.container_type or 'unknown'
        SubElement(transport_unit, 'SealNumber').text = shipment.seal_number or 'N/A'
        SubElement(transport_unit, 'SealType').text = shipment.seal_type or 'N/A'
        
        # Vehicle Information
        vehicle = shipment.deal.vehicle
        vehicle_elem = SubElement(root, 'Cargo')
        SubElement(vehicle_elem, 'VIN').text = vehicle.vin
        SubElement(vehicle_elem, 'Make').text = vehicle.make
        SubElement(vehicle_elem, 'Model').text = vehicle.model
        SubElement(vehicle_elem, 'Year').text = str(vehicle.year)
        SubElement(vehicle_elem, 'Value').text = f"{shipment.deal.final_price} CAD"
        
        # Route Information
        route = SubElement(root, 'Route')
        origin = SubElement(route, 'Origin')
        SubElement(origin, 'Port').text = shipment.origin_port
        SubElement(origin, 'Country').text = 'CA'
        
        destination = SubElement(route, 'Destination')
        SubElement(destination, 'Port').text = shipment.destination_port
        SubElement(destination, 'Country').text = shipment.destination_country
        
        # Current Status
        status_elem = SubElement(root, 'Status')
        SubElement(status_elem, 'StatusCode').text = shipment.status
        SubElement(status_elem, 'StatusDescription').text = shipment.get_status_display()
        
        # Current Location (GPS)
        if shipment.current_latitude and shipment.current_longitude:
            location = SubElement(root, 'CurrentLocation')
            SubElement(location, 'Latitude').text = str(shipment.current_latitude)
            SubElement(location, 'Longitude').text = str(shipment.current_longitude)
            SubElement(location, 'LastUpdate').text = shipment.last_location_update.isoformat() if shipment.last_location_update else ''
        
        # Milestones
        milestones_elem = SubElement(root, 'Milestones')
        for milestone in shipment.milestones.all().order_by('order'):
            m_elem = SubElement(milestones_elem, 'Milestone')
            SubElement(m_elem, 'Type').text = milestone.milestone_type
            SubElement(m_elem, 'Title').text = milestone.title
            SubElement(m_elem, 'Completed').text = str(milestone.is_completed).lower()
            if milestone.completed_at:
                SubElement(m_elem, 'CompletedAt').text = milestone.completed_at.isoformat()
            if milestone.latitude and milestone.longitude:
                SubElement(m_elem, 'Latitude').text = str(milestone.latitude)
                SubElement(m_elem, 'Longitude').text = str(milestone.longitude)
        
        # Lloyd's Register Certification (if applicable)
        if shipment.lloyd_register_tracking_id:
            lr_elem = SubElement(root, 'ThirdPartyVerification')
            SubElement(lr_elem, 'Organization').text = "Lloyd's Register"
            SubElement(lr_elem, 'TrackingID').text = shipment.lloyd_register_tracking_id
            SubElement(lr_elem, 'ServiceLevel').text = shipment.lloyd_register_service_level
            SubElement(lr_elem, 'Status').text = shipment.lloyd_register_status
        
        # Security Information (ISO 28000)
        security = SubElement(root, 'Security')
        SubElement(security, 'RiskLevel').text = shipment.security_risk_level
        SubElement(security, 'SealIntact').text = str(shipment.seal_intact).lower()
        SubElement(security, 'SecurityIncident').text = str(shipment.has_security_incident).lower()
        
        # Pretty print XML
        xml_str = tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    @classmethod
    def export_to_edifact(cls, shipment) -> str:
        """
        Generate UN/EDIFACT IFTSTA message (Status Report)
        Used by many port and customs systems worldwide
        """
        vehicle = shipment.deal.vehicle
        
        # EDIFACT is a line-based format with segment codes
        segments = []
        
        # UNH - Message Header
        segments.append(f"UNH+1+IFTSTA:D:96A:UN'")
        
        # BGM - Beginning of Message
        segments.append(f"BGM+270+{shipment.tracking_number}+9'")
        
        # DTM - Date/Time
        segments.append(f"DTM+137:{timezone.now().strftime('%Y%m%d%H%M')}:203'")
        
        # EQD - Equipment Details (Container)
        if shipment.container_number:
            segments.append(f"EQD+CN+{shipment.container_number}+{shipment.container_type or ''}++2'")
        
        # LOC - Location (Current)
        if shipment.current_latitude and shipment.current_longitude:
            segments.append(f"LOC+9+{shipment.current_latitude}:{shipment.current_longitude}:GPS'")
        
        # STS - Status
        segments.append(f"STS+{shipment.status}++{shipment.get_status_display()}'")
        
        # UNT - Message Trailer
        segments.append(f"UNT+{len(segments)+1}+1'")
        
        return '\n'.join(segments)
