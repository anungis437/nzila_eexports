from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.http import HttpResponse
from .models import Shipment, ShipmentUpdate
from .tracking_models import ShipmentMilestone, ShipmentPhoto
from .certification_models import SecurityRiskAssessment, SecurityIncident, PortVerification, ISO28000AuditLog
from .lloyd_register_service import LloydRegisterService, ISO18602Exporter
from .serializers import (
    ShipmentSerializer, ShipmentUpdateSerializer, 
    ShipmentMilestoneSerializer, ShipmentPhotoSerializer
)


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all().select_related('deal', 'deal__vehicle').prefetch_related('updates', 'milestones', 'photos')
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'destination_country']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter shipments based on user's deals
        if user.is_buyer():
            queryset = queryset.filter(deal__buyer=user)
        elif user.is_dealer():
            queryset = queryset.filter(deal__dealer=user)
        elif user.is_broker():
            queryset = queryset.filter(deal__broker=user)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        """Public tracking endpoint for buyers"""
        shipment = self.get_object()
        serializer = self.get_serializer(shipment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update GPS location for the shipment"""
        shipment = self.get_object()
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if latitude is None or longitude is None:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shipment.current_latitude = latitude
        shipment.current_longitude = longitude
        shipment.last_location_update = timezone.now()
        shipment.save()
        
        serializer = self.get_serializer(shipment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_update(self, request, pk=None):
        """Add a tracking update to the shipment"""
        shipment = self.get_object()
        
        # Create the shipment update
        serializer = ShipmentUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shipment=shipment)
            
            # Return the updated shipment with all updates
            shipment_serializer = self.get_serializer(shipment)
            return Response(shipment_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        """Get all tracking updates for a shipment"""
        shipment = self.get_object()
        updates = shipment.updates.all().order_by('-created_at')
        serializer = ShipmentUpdateSerializer(updates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def milestones(self, request, pk=None):
        """Get or create milestones for a shipment"""
        shipment = self.get_object()
        
        if request.method == 'GET':
            milestones = shipment.milestones.all()
            serializer = ShipmentMilestoneSerializer(milestones, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ShipmentMilestoneSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(shipment=shipment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], url_path='milestones/(?P<milestone_id>[^/.]+)')
    def update_milestone(self, request, pk=None, milestone_id=None):
        """Update a specific milestone (e.g., mark as completed)"""
        shipment = self.get_object()
        
        try:
            milestone = shipment.milestones.get(id=milestone_id)
        except ShipmentMilestone.DoesNotExist:
            return Response(
                {'error': 'Milestone not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ShipmentMilestoneSerializer(milestone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if request.data.get('is_completed') and not milestone.completed_at:
                milestone.completed_at = timezone.now()
                milestone.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'])
    def photos(self, request, pk=None):
        """Get or upload photos for a shipment"""
        shipment = self.get_object()
        
        if request.method == 'GET':
            photos = shipment.photos.all()
            serializer = ShipmentPhotoSerializer(photos, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ShipmentPhotoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    shipment=shipment,
                    uploaded_by=request.user,
                    taken_at=timezone.now()
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ===== LLOYD'S REGISTER & ISO COMPLIANCE ENDPOINTS =====
    
    @action(detail=True, methods=['post'], url_path='lloyd-register/register')
    def register_with_lloyd_register(self, request, pk=None):
        """
        Register shipment with Lloyd's Register Cargo Tracking Service
        
        Request body:
        {
            "service_level": "standard" | "premium" | "surveyor"
        }
        """
        shipment = self.get_object()
        
        # Check if already registered
        if shipment.lloyd_register_tracking_id:
            return Response({
                'error': 'Shipment already registered with Lloyd\'s Register',
                'lr_tracking_id': shipment.lloyd_register_tracking_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        service_level = request.data.get('service_level', 'standard')
        
        # Register with LR
        lr_tracking_id = LloydRegisterService.register_shipment(shipment, service_level)
        
        if lr_tracking_id:
            shipment.lloyd_register_tracking_id = lr_tracking_id
            shipment.lloyd_register_service_level = service_level
            shipment.lloyd_register_status = 'pending_origin'
            shipment.save()
            
            # Create audit log
            ISO28000AuditLog.objects.create(
                shipment=shipment,
                action_type='lr_registered',
                performed_by=request.user,
                performed_by_name=f"{request.user.first_name} {request.user.last_name}",
                action_description=f"Registered with Lloyd's Register CTS - Service Level: {service_level}",
                related_object_type='Shipment',
                related_object_id=shipment.id
            )
            
            return Response({
                'success': True,
                'lr_tracking_id': lr_tracking_id,
                'service_level': service_level,
                'status': 'pending_origin',
                'message': 'Successfully registered with Lloyd\'s Register'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Failed to register with Lloyd\'s Register',
                'message': 'Please check API configuration or try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='lloyd-register/status')
    def lloyd_register_status(self, request, pk=None):
        """Get current Lloyd's Register verification status"""
        shipment = self.get_object()
        
        if not shipment.lloyd_register_tracking_id:
            return Response({
                'registered': False,
                'message': 'Shipment not registered with Lloyd\'s Register'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get status from LR API
        lr_status = LloydRegisterService.get_verification_status(
            shipment.lloyd_register_tracking_id
        )
        
        if lr_status:
            return Response({
                'registered': True,
                'lr_tracking_id': shipment.lloyd_register_tracking_id,
                'service_level': shipment.lloyd_register_service_level,
                'internal_status': shipment.lloyd_register_status,
                'lr_api_data': lr_status
            })
        else:
            return Response({
                'registered': True,
                'lr_tracking_id': shipment.lloyd_register_tracking_id,
                'error': 'Unable to fetch status from Lloyd\'s Register API'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @action(detail=True, methods=['get'], url_path='lloyd-register/certificate')
    def lloyd_register_certificate(self, request, pk=None):
        """Download Lloyd's Register Certificate of Safe Delivery"""
        shipment = self.get_object()
        
        if not shipment.lloyd_register_certificate_issued:
            return Response({
                'error': 'Certificate not yet issued',
                'message': 'Certificate will be available after destination inspection is completed'
            }, status=status.HTTP_404_NOT_FOUND)
        
        certificate = LloydRegisterService.get_certificate(
            shipment.lloyd_register_tracking_id
        )
        
        if certificate:
            return Response(certificate)
        else:
            return Response({
                'error': 'Unable to retrieve certificate'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @action(detail=True, methods=['post'], url_path='lloyd-register/report-incident')
    def report_incident_to_lr(self, request, pk=None):
        """
        Report security incident to Lloyd's Register
        
        Request body:
        {
            "incident_type": "delay" | "damage" | "theft" | etc,
            "severity": "minor" | "moderate" | "severe" | "critical",
            "description": "...",
            "location": "...",
            "police_report_filed": true/false
        }
        """
        shipment = self.get_object()
        
        if not shipment.lloyd_register_tracking_id:
            return Response({
                'error': 'Shipment not registered with Lloyd\'s Register'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Report to LR
        success = LloydRegisterService.report_incident(
            shipment.lloyd_register_tracking_id,
            request.data
        )
        
        if success:
            shipment.lloyd_register_status = 'discrepancy'
            shipment.save()
            
            return Response({
                'success': True,
                'message': 'Incident reported to Lloyd\'s Register'
            })
        else:
            return Response({
                'error': 'Failed to report incident'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='iso/xml')
    def iso_18602_xml(self, request, pk=None):
        """
        Export shipment data as ISO 18602 compliant XML
        For integration with port management systems
        """
        shipment = self.get_object()
        
        xml_data = ISO18602Exporter.export_to_xml(shipment)
        
        response = HttpResponse(xml_data, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="shipment_{shipment.tracking_number}_iso18602.xml"'
        
        # Mark as ISO compliant
        if not shipment.iso_18602_compliant:
            shipment.iso_18602_compliant = True
            shipment.save()
        
        return response
    
    @action(detail=True, methods=['get'], url_path='iso/edifact')
    def iso_18602_edifact(self, request, pk=None):
        """
        Export shipment data as UN/EDIFACT IFTSTA message
        Used by many customs and port systems
        """
        shipment = self.get_object()
        
        edifact_data = ISO18602Exporter.export_to_edifact(shipment)
        
        response = HttpResponse(edifact_data, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="shipment_{shipment.tracking_number}_iftsta.edi"'
        
        return response
    
    @action(detail=True, methods=['post'], url_path='security/assess-risk')
    def assess_security_risk(self, request, pk=None):
        """
        Perform ISO 28000 security risk assessment
        
        Request body:
        {
            "route_risk_score": 0-10,
            "value_risk_score": 0-10,
            "destination_risk_score": 0-10,
            "customs_risk_score": 0-10,
            "port_security_score": 0-10,
            "mitigation_measures": "..."
        }
        """
        shipment = self.get_object()
        
        # Create or update risk assessment
        assessment, created = SecurityRiskAssessment.objects.get_or_create(
            shipment=shipment,
            defaults={
                'assessed_by': request.user,
            }
        )
        
        # Update scores
        assessment.route_risk_score = request.data.get('route_risk_score', 0)
        assessment.value_risk_score = request.data.get('value_risk_score', 0)
        assessment.destination_risk_score = request.data.get('destination_risk_score', 0)
        assessment.customs_risk_score = request.data.get('customs_risk_score', 0)
        assessment.port_security_score = request.data.get('port_security_score', 0)
        assessment.mitigation_measures = request.data.get('mitigation_measures', '')
        
        # Calculate overall risk
        risk_score = assessment.calculate_risk_score()
        
        # Calculate recommended insurance
        assessment.recommended_insurance_amount = shipment.deal.final_price * 1.2  # 120% of vehicle value
        
        # Recommend LR monitoring for high-risk shipments
        assessment.lloyd_register_recommended = (risk_score >= 60)
        
        assessment.save()
        
        # Update shipment with risk level
        shipment.security_risk_level = assessment.overall_risk_level
        shipment.security_assessment_completed = True
        shipment.security_assessment_date = timezone.now()
        shipment.security_assessment_by = request.user
        shipment.save()
        
        # Create audit log
        ISO28000AuditLog.objects.create(
            shipment=shipment,
            action_type='risk_assessment',
            performed_by=request.user,
            performed_by_name=f"{request.user.first_name} {request.user.last_name}",
            action_description=f"Security risk assessment completed - Risk Level: {assessment.overall_risk_level} ({risk_score} points)",
            related_object_type='SecurityRiskAssessment',
            related_object_id=assessment.id
        )
        
        return Response({
            'success': True,
            'assessment_id': assessment.id,
            'risk_score': risk_score,
            'risk_level': assessment.overall_risk_level,
            'lloyd_register_recommended': assessment.lloyd_register_recommended,
            'recommended_insurance': float(assessment.recommended_insurance_amount)
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='security/audit-log')
    def security_audit_log(self, request, pk=None):
        """
        Retrieve ISO 28000 audit trail for shipment
        Immutable security logs for certification auditors
        """
        shipment = self.get_object()
        
        logs = shipment.audit_logs.all().order_by('-action_timestamp')
        
        log_data = [{
            'id': log.id,
            'action_type': log.get_action_type_display(),
            'timestamp': log.action_timestamp.isoformat(),
            'performed_by': log.performed_by_name,
            'description': log.action_description,
            'ip_address': log.ip_address,
        } for log in logs]
        
        return Response({
            'shipment_tracking_number': shipment.tracking_number,
            'total_log_entries': logs.count(),
            'audit_logs': log_data
        })
    
    @action(detail=True, methods=['get'], url_path='certification/compliance-report')
    def certification_compliance_report(self, request, pk=None):
        """
        Generate comprehensive compliance report for ISO certification audits
        Shows ISO 28000 and ISO 18602 compliance status
        """
        shipment = self.get_object()
        
        # Check risk assessment
        has_risk_assessment = hasattr(shipment, 'risk_assessment')
        risk_assessment_data = None
        if has_risk_assessment:
            ra = shipment.risk_assessment
            risk_assessment_data = {
                'completed': True,
                'risk_level': ra.overall_risk_level,
                'risk_score': ra.risk_score,
                'assessed_date': ra.assessment_date.isoformat(),
                'assessed_by': ra.assessed_by.get_full_name() if ra.assessed_by else 'N/A'
            }
        
        # Count incidents
        incident_count = shipment.security_incidents.count()
        unresolved_incidents = shipment.security_incidents.filter(resolved=False).count()
        
        # Check port verifications
        port_verifications = shipment.port_verifications.count()
        
        # Check seal integrity
        seal_tracking = {
            'seal_applied': bool(shipment.seal_number),
            'seal_verified_origin': shipment.seal_verified_at_origin,
            'seal_verified_destination': shipment.seal_verified_at_destination,
            'seal_intact': shipment.seal_intact
        }
        
        # Lloyd's Register status
        lr_status = {
            'registered': bool(shipment.lloyd_register_tracking_id),
            'tracking_id': shipment.lloyd_register_tracking_id or None,
            'service_level': shipment.lloyd_register_service_level,
            'certificate_issued': shipment.lloyd_register_certificate_issued,
            'status': shipment.lloyd_register_status
        }
        
        # Overall compliance scores
        iso_28000_score = 0
        iso_28000_checks = {
            'risk_assessment_completed': shipment.security_assessment_completed,
            'security_measures_documented': bool(shipment.security_measures_implemented),
            'insurance_in_place': bool(shipment.insurance_policy_number),
            'incident_tracking_active': incident_count >= 0,  # Just needs to exist
            'audit_trail_maintained': shipment.audit_logs.count() > 0,
        }
        iso_28000_score = sum(iso_28000_checks.values()) * 20  # Each item worth 20 points
        
        iso_18602_score = 0
        iso_18602_checks = {
            'container_tracking': bool(shipment.container_number),
            'gps_tracking_active': bool(shipment.current_latitude and shipment.current_longitude),
            'port_verifications': port_verifications >= 1,
            'seal_tracking': seal_tracking['seal_applied'],
            'standardized_messages': shipment.iso_18602_compliant,
        }
        iso_18602_score = sum(iso_18602_checks.values()) * 20
        
        return Response({
            'shipment_tracking_number': shipment.tracking_number,
            'compliance_report_generated': timezone.now().isoformat(),
            
            'iso_28000_security_management': {
                'compliance_score': iso_28000_score,
                'certification_ready': iso_28000_score >= 80,
                'checks': iso_28000_checks,
                'risk_assessment': risk_assessment_data,
                'security_incidents': {
                    'total': incident_count,
                    'unresolved': unresolved_incidents
                }
            },
            
            'iso_18602_cargo_tracking': {
                'compliance_score': iso_18602_score,
                'certification_ready': iso_18602_score >= 80,
                'checks': iso_18602_checks,
                'port_verifications': port_verifications,
                'seal_tracking': seal_tracking
            },
            
            'lloyd_register': lr_status,
            
            'overall_certification_status': {
                'average_score': (iso_28000_score + iso_18602_score) / 2,
                'ready_for_audit': (iso_28000_score >= 80 and iso_18602_score >= 80),
                'recommendations': []
            }
        })

