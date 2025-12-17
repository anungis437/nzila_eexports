"""
Carfax API Integration Service

This service provides integration with Carfax API for vehicle history reports.
The service is designed with a placeholder implementation that can be easily
connected to the real Carfax API when credentials are available.

API Documentation: https://www.carfax.com/company/developer
"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class CarfaxAPIError(Exception):
    """Custom exception for Carfax API errors."""
    pass


class CarfaxService:
    """
    Service for interacting with Carfax API.
    
    Configuration required in settings.py:
    - CARFAX_API_KEY: Your Carfax API key
    - CARFAX_API_URL: Carfax API base URL
    - CARFAX_CACHE_TTL: Cache duration in seconds (default: 7 days)
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'CARFAX_API_KEY', None)
        self.api_url = getattr(settings, 'CARFAX_API_URL', 'https://api.carfax.com/v1')
        self.cache_ttl = getattr(settings, 'CARFAX_CACHE_TTL', 604800)  # 7 days
        self.enabled = bool(self.api_key)
    
    def fetch_report(self, vin: str) -> Dict:
        """
        Fetch vehicle history report from Carfax API.
        
        Args:
            vin: 17-character Vehicle Identification Number
            
        Returns:
            Dictionary containing vehicle history report
            
        Raises:
            CarfaxAPIError: If API request fails
        """
        if not self.enabled:
            logger.warning("Carfax API not configured. Returning mock data.")
            return self._get_mock_report(vin)
        
        # Check cache first
        cache_key = f'carfax_report_{vin}'
        cached_report = cache.get(cache_key)
        if cached_report:
            logger.info(f"Returning cached Carfax report for VIN: {vin}")
            return cached_report
        
        try:
            # Make API request
            response = requests.post(
                f'{self.api_url}/reports',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={'vin': vin},
                timeout=30
            )
            
            response.raise_for_status()
            report = response.json()
            
            # Cache the report
            cache.set(cache_key, report, self.cache_ttl)
            logger.info(f"Successfully fetched Carfax report for VIN: {vin}")
            
            return report
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Carfax API request failed for VIN {vin}: {str(e)}")
            raise CarfaxAPIError(f"Failed to fetch Carfax report: {str(e)}")
    
    def validate_vin(self, vin: str) -> bool:
        """
        Validate VIN format and checksum.
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            True if VIN is valid, False otherwise
        """
        # Basic VIN validation
        if not vin or len(vin) != 17:
            return False
        
        # VIN should not contain I, O, or Q
        if any(char in vin.upper() for char in ['I', 'O', 'Q']):
            return False
        
        # TODO: Implement full VIN checksum validation
        return True
    
    def parse_report(self, report: Dict) -> Dict:
        """
        Parse Carfax report into standardized format.
        
        Args:
            report: Raw Carfax API response
            
        Returns:
            Standardized report dictionary
        """
        if not self.enabled:
            return report  # Mock data already in correct format
        
        # Parse real Carfax response
        return {
            'vin': report.get('vin'),
            'title_status': self._parse_title_status(report),
            'accident_history': self._parse_accidents(report),
            'ownership_history': self._parse_ownership(report),
            'service_records': self._parse_service_records(report),
            'odometer_readings': self._parse_odometer(report),
            'report_date': report.get('report_date'),
            'confidence_score': report.get('confidence_score', 95)
        }
    
    def _parse_title_status(self, report: Dict) -> str:
        """Parse title status from Carfax report."""
        title_info = report.get('title_info', {})
        return title_info.get('status', 'unknown')
    
    def _parse_accidents(self, report: Dict) -> list:
        """Parse accident history from Carfax report."""
        accidents = report.get('accidents', [])
        return [{
            'date': acc.get('date'),
            'severity': acc.get('severity'),
            'airbag_deployed': acc.get('airbag_deployed', False),
            'damage_description': acc.get('damage_description')
        } for acc in accidents]
    
    def _parse_ownership(self, report: Dict) -> list:
        """Parse ownership history from Carfax report."""
        owners = report.get('ownership_history', [])
        return [{
            'owner_number': idx + 1,
            'ownership_type': owner.get('type'),
            'state': owner.get('state'),
            'duration_days': owner.get('duration_days')
        } for idx, owner in enumerate(owners)]
    
    def _parse_service_records(self, report: Dict) -> list:
        """Parse service records from Carfax report."""
        services = report.get('service_records', [])
        return [{
            'date': svc.get('date'),
            'odometer': svc.get('odometer'),
            'service_type': svc.get('service_type'),
            'facility': svc.get('facility')
        } for svc in services]
    
    def _parse_odometer(self, report: Dict) -> list:
        """Parse odometer readings from Carfax report."""
        readings = report.get('odometer_readings', [])
        return [{
            'date': reading.get('date'),
            'mileage': reading.get('mileage'),
            'source': reading.get('source')
        } for reading in readings]
    
    def _get_mock_report(self, vin: str) -> Dict:
        """
        Return mock data for testing when API is not configured.
        
        This allows development and testing without Carfax API access.
        Remove or disable this method in production.
        """
        return {
            'vin': vin,
            'title_status': 'clean',
            'accident_history': [],
            'ownership_history': [
                {
                    'owner_number': 1,
                    'ownership_type': 'personal',
                    'state': 'Ontario',
                    'duration_days': 730
                }
            ],
            'service_records': [
                {
                    'date': '2024-06-15',
                    'odometer': 45000,
                    'service_type': 'Oil Change',
                    'facility': 'Honda Dealer'
                },
                {
                    'date': '2024-01-10',
                    'odometer': 40000,
                    'service_type': 'Tire Rotation',
                    'facility': 'Honda Dealer'
                }
            ],
            'odometer_readings': [
                {'date': '2024-06-15', 'mileage': 45000, 'source': 'Service Record'},
                {'date': '2024-01-10', 'mileage': 40000, 'source': 'Service Record'},
                {'date': '2023-06-20', 'mileage': 30000, 'source': 'Service Record'}
            ],
            'report_date': timezone.now().isoformat(),
            'confidence_score': 95,
            'mock_data': True
        }
    
    def clear_cache(self, vin: str) -> bool:
        """
        Clear cached report for a specific VIN.
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            True if cache was cleared
        """
        cache_key = f'carfax_report_{vin}'
        cache.delete(cache_key)
        logger.info(f"Cleared Carfax cache for VIN: {vin}")
        return True


# Singleton instance
carfax_service = CarfaxService()
