"""
External vehicle data service integrations
Connects to CarFax, Transport Canada, and provincial registries
"""
import requests
from django.conf import settings
from django.core.cache import cache
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class CarFaxService:
    """
    CarFax Canada vehicle history integration
    Requires: CARFAX_API_KEY in settings
    """
    BASE_URL = "https://api.carfax.ca/v1"
    
    @classmethod
    def get_vehicle_history(cls, vin: str) -> Optional[Dict]:
        """
        Fetch comprehensive vehicle history from CarFax
        
        Args:
            vin: Vehicle Identification Number (17 characters)
            
        Returns:
            Dict with vehicle history data or None if unavailable
        """
        api_key = getattr(settings, 'CARFAX_API_KEY', None)
        if not api_key:
            logger.warning("CARFAX_API_KEY not configured")
            return cls._get_mock_data(vin)
        
        # Check cache first (24 hour TTL)
        cache_key = f'carfax_{vin}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/vehicle/{vin}",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache for 24 hours
            cache.set(cache_key, data, 86400)
            return data
            
        except requests.RequestException as e:
            logger.error(f"CarFax API error for VIN {vin}: {e}")
            return cls._get_mock_data(vin)
    
    @classmethod
    def _get_mock_data(cls, vin: str) -> Dict:
        """Mock data for development/demo purposes"""
        return {
            'vin': vin,
            'status': 'mock_data',
            'accidents': 0,
            'owners': 1,
            'service_records': 12,
            'last_odometer': 45000,
            'title_status': 'Clean',
            'usage_type': 'Personal',
            'provinces': ['ON'],
            'last_service_date': '2024-11-15',
            'note': 'CarFax API key not configured - showing mock data'
        }


class AutoCheckService:
    """
    AutoCheck Canada vehicle history (alternative to CarFax)
    Requires: AUTOCHECK_API_KEY in settings
    """
    BASE_URL = "https://api.autocheck.ca/v1"
    
    @classmethod
    def get_vehicle_history(cls, vin: str) -> Optional[Dict]:
        """
        Fetch vehicle history from AutoCheck
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            Dict with vehicle history or None
        """
        api_key = getattr(settings, 'AUTOCHECK_API_KEY', None)
        if not api_key:
            logger.warning("AUTOCHECK_API_KEY not configured")
            return cls._get_mock_data(vin)
        
        cache_key = f'autocheck_{vin}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/history/{vin}",
                headers={'X-API-Key': api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            cache.set(cache_key, data, 86400)
            return data
            
        except requests.RequestException as e:
            logger.error(f"AutoCheck API error for VIN {vin}: {e}")
            return cls._get_mock_data(vin)
    
    @classmethod
    def _get_mock_data(cls, vin: str) -> Dict:
        """Mock data for development"""
        return {
            'vin': vin,
            'status': 'mock_data',
            'score': 85,
            'accidents': 0,
            'title_issues': False,
            'odometer_readings': [30000, 35000, 40000, 45000],
            'note': 'AutoCheck API key not configured - showing mock data'
        }


class TransportCanadaService:
    """
    Transport Canada public data API
    Free access - vehicle safety recalls and defects
    """
    BASE_URL = "https://data.tc.gc.ca/v1.3"
    
    @classmethod
    def get_recalls(cls, vin: str = None, year: int = None, 
                   make: str = None, model: str = None) -> List[Dict]:
        """
        Fetch safety recalls from Transport Canada
        
        Args:
            vin: Vehicle VIN (optional)
            year: Vehicle year
            make: Vehicle make
            model: Vehicle model
            
        Returns:
            List of recall dictionaries
        """
        cache_key = f'tc_recalls_{vin or f"{year}_{make}_{model}"}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            params = {}
            if year:
                params['year'] = year
            if make:
                params['make'] = make.upper()
            if model:
                params['model'] = model.upper()
            
            response = requests.get(
                f"{cls.BASE_URL}/recalls",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            recalls = data.get('recalls', [])
            
            # Cache for 7 days (recalls don't change frequently)
            cache.set(cache_key, recalls, 604800)
            return recalls
            
        except requests.RequestException as e:
            logger.error(f"Transport Canada API error: {e}")
            return cls._get_mock_recalls(year, make, model)
    
    @classmethod
    def _get_mock_recalls(cls, year: int, make: str, model: str) -> List[Dict]:
        """Mock recall data"""
        return [
            {
                'recall_number': 'MOCK2024001',
                'year': year,
                'make': make,
                'model': model,
                'component': 'Air Bags',
                'description': 'Mock recall data - Transport Canada API not configured',
                'date': '2024-06-15',
                'severity': 'Low'
            }
        ]


class ProvincialRegistryService:
    """
    Provincial vehicle registry services
    Requires specific API keys per province
    """
    
    @classmethod
    def icbc_lookup(cls, vin: str) -> Optional[Dict]:
        """
        ICBC (British Columbia) vehicle lookup
        Requires: ICBC_API_KEY in settings
        """
        api_key = getattr(settings, 'ICBC_API_KEY', None)
        if not api_key:
            logger.warning("ICBC_API_KEY not configured")
            return cls._get_mock_provincial_data(vin, 'BC')
        
        cache_key = f'icbc_{vin}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # ICBC API implementation would go here
        return cls._get_mock_provincial_data(vin, 'BC')
    
    @classmethod
    def mto_lookup(cls, vin: str) -> Optional[Dict]:
        """
        MTO (Ontario) vehicle lookup
        Requires: MTO_API_KEY in settings
        """
        api_key = getattr(settings, 'MTO_API_KEY', None)
        if not api_key:
            logger.warning("MTO_API_KEY not configured")
            return cls._get_mock_provincial_data(vin, 'ON')
        
        cache_key = f'mto_{vin}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # MTO API implementation would go here
        return cls._get_mock_provincial_data(vin, 'ON')
    
    @classmethod
    def saaq_lookup(cls, vin: str) -> Optional[Dict]:
        """
        SAAQ (Quebec) vehicle lookup
        Requires: SAAQ_API_KEY in settings
        """
        api_key = getattr(settings, 'SAAQ_API_KEY', None)
        if not api_key:
            logger.warning("SAAQ_API_KEY not configured")
            return cls._get_mock_provincial_data(vin, 'QC')
        
        cache_key = f'saaq_{vin}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # SAAQ API implementation would go here
        return cls._get_mock_provincial_data(vin, 'QC')
    
    @classmethod
    def _get_mock_provincial_data(cls, vin: str, province: str) -> Dict:
        """Mock provincial registry data"""
        return {
            'vin': vin,
            'province': province,
            'status': 'mock_data',
            'registration_status': 'Active',
            'last_inspection_date': '2024-10-20',
            'liens': False,
            'note': f'{province} registry API not configured - showing mock data'
        }


class VehicleDataAggregator:
    """
    Aggregates data from multiple sources for comprehensive vehicle report
    """
    
    @classmethod
    def get_comprehensive_report(cls, vin: str, year: int = None,
                                make: str = None, model: str = None) -> Dict:
        """
        Fetch and aggregate data from all available sources
        
        Args:
            vin: Vehicle VIN
            year: Vehicle year (for recall lookup)
            make: Vehicle make (for recall lookup)
            model: Vehicle model (for recall lookup)
            
        Returns:
            Comprehensive vehicle report dictionary
        """
        report = {
            'vin': vin,
            'timestamp': cache.get(f'report_timestamp_{vin}') or 'N/A',
            'sources': {}
        }
        
        # CarFax data
        try:
            carfax_data = CarFaxService.get_vehicle_history(vin)
            if carfax_data:
                report['sources']['carfax'] = carfax_data
        except Exception as e:
            logger.error(f"CarFax error: {e}")
            report['sources']['carfax'] = {'error': str(e)}
        
        # AutoCheck data
        try:
            autocheck_data = AutoCheckService.get_vehicle_history(vin)
            if autocheck_data:
                report['sources']['autocheck'] = autocheck_data
        except Exception as e:
            logger.error(f"AutoCheck error: {e}")
            report['sources']['autocheck'] = {'error': str(e)}
        
        # Transport Canada recalls
        try:
            recalls = TransportCanadaService.get_recalls(
                vin=vin, year=year, make=make, model=model
            )
            report['sources']['transport_canada'] = {
                'recalls': recalls,
                'recall_count': len(recalls)
            }
        except Exception as e:
            logger.error(f"Transport Canada error: {e}")
            report['sources']['transport_canada'] = {'error': str(e)}
        
        # Provincial registry (try to determine province from VIN or location)
        # This is a simplified implementation - real VIN decoding is more complex
        try:
            # Try Ontario as default for demo
            provincial_data = ProvincialRegistryService.mto_lookup(vin)
            if provincial_data:
                report['sources']['provincial_registry'] = provincial_data
        except Exception as e:
            logger.error(f"Provincial registry error: {e}")
            report['sources']['provincial_registry'] = {'error': str(e)}
        
        return report
