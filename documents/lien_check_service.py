"""
PHASE 2 - Feature 5: PPSA Lien Check Service

Personal Property Security Act (PPSA) lien search integration.

In production, this would integrate with provincial PPSA registries:
- Ontario: https://www.ontario.ca/page/personal-property-security-registration
- Other provinces have similar registries

For development, this is a mock service that simulates lien checks.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Optional
from django.core.cache import cache
from django.utils import timezone


class PPSALienCheckService:
    """
    PPSA Lien Check Service - Mock implementation for development
    
    In production, this would integrate with provincial PPSA registries.
    Real integration requires:
    - API keys from provincial authorities
    - Fee payment processing ($8-15 per search)
    - Real-time API calls to provincial systems
    """
    
    # Cache lien check results for 24 hours
    CACHE_TTL = 86400  # 24 hours in seconds
    
    @staticmethod
    def check_lien(vin: str, province_code: str, force_refresh: bool = False) -> Dict:
        """
        Check for liens on a vehicle via PPSA registry
        
        Args:
            vin: Vehicle Identification Number (17 characters)
            province_code: Province where vehicle is registered (ON, QC, etc.)
            force_refresh: Force new check, bypass cache
        
        Returns:
            Dict with lien check results
        """
        # Check cache first
        cache_key = f"ppsa_lien_{vin}_{province_code}"
        
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Mock lien check (replace with real API call in production)
        result = PPSALienCheckService._mock_lien_check(vin, province_code)
        
        # Cache result
        cache.set(cache_key, result, PPSALienCheckService.CACHE_TTL)
        
        return result
    
    @staticmethod
    def _mock_lien_check(vin: str, province_code: str) -> Dict:
        """
        Mock lien check - simulates PPSA registry response
        
        In production, replace with actual API calls to:
        - Ontario PPSA Registry
        - Quebec RDPRM (Registre des droits personnels et réels mobiliers)
        - BC Personal Property Registry
        - Alberta Personal Property Registry
        - Etc.
        """
        # Simulate 90% clear, 10% liens (for testing)
        has_lien = random.random() < 0.10
        
        check_date = timezone.now()
        
        if has_lien:
            # Simulate lien details
            lien_types = ['Bank Loan', 'Lease', 'Consumer Loan', 'Line of Credit']
            lien_type = random.choice(lien_types)
            
            secured_parties = [
                'Royal Bank of Canada',
                'TD Bank',
                'Scotiabank',
                'BMO Financial',
                'CIBC',
                'Desjardins',
                'Credit Union',
            ]
            
            secured_party = random.choice(secured_parties)
            
            # Simulate registration date (1-5 years ago)
            days_ago = random.randint(365, 1825)
            registration_date = check_date - timedelta(days=days_ago)
            
            # Simulate lien amount ($5,000 - $50,000)
            lien_amount = random.randint(5000, 50000)
            
            return {
                'vin': vin,
                'province': province_code,
                'has_lien': True,
                'lien_status': 'LIEN_FOUND',
                'check_date': check_date.isoformat(),
                'registry': f'{PPSALienCheckService._get_province_name(province_code)} PPSA Registry',
                'liens': [
                    {
                        'lien_type': lien_type,
                        'secured_party': secured_party,
                        'registration_date': registration_date.isoformat(),
                        'registration_number': f'PPSA{random.randint(100000, 999999)}',
                        'approximate_amount': lien_amount,
                        'status': 'Active',
                    }
                ],
                'certificate_number': f'CERT{random.randint(10000, 99999)}',
                'message': f'LIEN FOUND: This vehicle has an active lien registered with {secured_party}. Contact the secured party to obtain a discharge before completing the sale.',
                'recommendation': 'DO NOT COMPLETE SALE - Obtain lien discharge first',
                'cached': False,
            }
        else:
            # Clear lien check
            return {
                'vin': vin,
                'province': province_code,
                'has_lien': False,
                'lien_status': 'CLEAR',
                'check_date': check_date.isoformat(),
                'registry': f'{PPSALienCheckService._get_province_name(province_code)} PPSA Registry',
                'liens': [],
                'certificate_number': f'CERT{random.randint(10000, 99999)}',
                'message': 'CLEAR: No active liens found on this vehicle.',
                'recommendation': 'Safe to proceed with purchase',
                'cached': False,
            }
    
    @staticmethod
    def _get_province_name(province_code: str) -> str:
        """Get full province name from code"""
        provinces = {
            'ON': 'Ontario',
            'QC': 'Quebec',
            'BC': 'British Columbia',
            'AB': 'Alberta',
            'MB': 'Manitoba',
            'SK': 'Saskatchewan',
            'NS': 'Nova Scotia',
            'NB': 'New Brunswick',
            'NL': 'Newfoundland and Labrador',
            'PE': 'Prince Edward Island',
            'NT': 'Northwest Territories',
            'YT': 'Yukon',
            'NU': 'Nunavut',
        }
        return provinces.get(province_code.upper(), 'Unknown')
    
    @staticmethod
    def get_registry_info(province_code: str) -> Dict:
        """
        Get PPSA registry information for a province
        
        Returns contact info and URLs for provincial registries
        """
        registries = {
            'ON': {
                'name': 'Ontario Personal Property Security Registration',
                'website': 'https://www.ontario.ca/page/personal-property-security-registration',
                'phone': '1-800-267-8097',
                'search_fee': '$8.00',
                'online_search': True,
            },
            'QC': {
                'name': 'Registre des droits personnels et réels mobiliers (RDPRM)',
                'website': 'https://www.registre-enterprise.gouv.qc.ca/',
                'phone': '1-877-644-4545',
                'search_fee': '$10.00',
                'online_search': True,
            },
            'BC': {
                'name': 'BC Personal Property Registry',
                'website': 'https://www.bcregistry.ca/',
                'phone': '1-877-526-1526',
                'search_fee': '$8.50',
                'online_search': True,
            },
            'AB': {
                'name': 'Alberta Personal Property Registry',
                'website': 'https://www.alberta.ca/personal-property-registry',
                'phone': '310-0000',
                'search_fee': '$10.00',
                'online_search': True,
            },
        }
        
        default = {
            'name': f'{PPSALienCheckService._get_province_name(province_code)} PPSA Registry',
            'website': 'Contact provincial registry',
            'phone': 'N/A',
            'search_fee': '$8-15',
            'online_search': False,
        }
        
        return registries.get(province_code.upper(), default)
    
    @staticmethod
    def invalidate_cache(vin: str, province_code: str):
        """
        Invalidate cached lien check result
        
        Use this when lien status may have changed (e.g., lien discharged)
        """
        cache_key = f"ppsa_lien_{vin}_{province_code}"
        cache.delete(cache_key)
        return True
