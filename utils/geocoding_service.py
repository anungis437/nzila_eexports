"""
Geocoding service for converting addresses to geographic coordinates.

This module provides utilities for geocoding Canadian addresses into latitude/longitude
coordinates using geopy's Nominatim geocoder. Includes caching to reduce API calls
and rate limiting compliance.

Phase 2: Proximity Search & Travel Radius
Author: Django Development Team
Date: December 2025
"""

from typing import Optional, Tuple
from decimal import Decimal
import logging
from django.core.cache import cache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Service for geocoding addresses to lat/long coordinates with caching.
    
    Uses Nominatim (OpenStreetMap) geocoder for Canadian addresses.
    Implements rate limiting (1 request per second) and caching to reduce API calls.
    """
    
    def __init__(self):
        """Initialize geocoder with user agent for OpenStreetMap compliance."""
        self.geocoder = Nominatim(
            user_agent="nzila_export_platform/1.0",
            timeout=10
        )
        self._last_request_time = 0
        self._min_delay = 1.0  # 1 second between requests (Nominatim requirement)
    
    def _rate_limit(self):
        """Enforce rate limiting: 1 request per second for Nominatim."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()
    
    def geocode_address(
        self, 
        street: str, 
        city: str, 
        province: str, 
        postal_code: str,
        country: str = 'Canada'
    ) -> Optional[Tuple[Decimal, Decimal]]:
        """
        Geocode a Canadian address to latitude/longitude coordinates.
        
        Args:
            street: Street address (e.g., "123 Main St")
            city: City name (e.g., "Toronto")
            province: Province code (e.g., "ON") or name (e.g., "Ontario")
            postal_code: Canadian postal code (e.g., "M5H 2N2")
            country: Country name (default: "Canada")
        
        Returns:
            Tuple of (latitude, longitude) as Decimal objects, or None if geocoding fails
        
        Example:
            >>> geocoder = GeocodingService()
            >>> coords = geocoder.geocode_address("123 Main St", "Toronto", "ON", "M5H 2N2")
            >>> print(coords)
            (Decimal('43.651070'), Decimal('-79.347015'))
        """
        # Build cache key from address components
        cache_key = f"geocode:{street}:{city}:{province}:{postal_code}:{country}"
        
        # Check cache first
        cached_coords = cache.get(cache_key)
        if cached_coords:
            logger.debug(f"Geocoding cache hit for {city}, {province}")
            return cached_coords
        
        # Build full address string
        full_address = f"{street}, {city}, {province} {postal_code}, {country}"
        
        try:
            # Rate limit requests
            self._rate_limit()
            
            # Geocode address
            logger.info(f"Geocoding address: {full_address}")
            location = self.geocoder.geocode(full_address, country_codes=['ca'])
            
            if location:
                coords = (
                    Decimal(str(location.latitude)),
                    Decimal(str(location.longitude))
                )
                
                # Cache for 30 days (addresses rarely change coordinates)
                cache.set(cache_key, coords, timeout=60*60*24*30)
                
                logger.info(f"Geocoded {city}, {province} to {coords}")
                return coords
            else:
                logger.warning(f"Could not geocode address: {full_address}")
                return None
        
        except GeocoderTimedOut:
            logger.error(f"Geocoding timeout for address: {full_address}")
            return None
        
        except GeocoderServiceError as e:
            logger.error(f"Geocoding service error for {full_address}: {e}")
            return None
        
        except Exception as e:
            logger.exception(f"Unexpected geocoding error for {full_address}: {e}")
            return None
    
    def geocode_city(
        self, 
        city: str, 
        province: str,
        country: str = 'Canada'
    ) -> Optional[Tuple[Decimal, Decimal]]:
        """
        Geocode a Canadian city to its center coordinates (for user locations).
        
        Args:
            city: City name (e.g., "Toronto")
            province: Province code (e.g., "ON") or name
            country: Country name (default: "Canada")
        
        Returns:
            Tuple of (latitude, longitude) as Decimal objects, or None if geocoding fails
        
        Example:
            >>> geocoder = GeocodingService()
            >>> coords = geocoder.geocode_city("Vancouver", "BC")
            >>> print(coords)
            (Decimal('49.282729'), Decimal('-123.120738'))
        """
        # Build cache key
        cache_key = f"geocode_city:{city}:{province}:{country}"
        
        # Check cache first
        cached_coords = cache.get(cache_key)
        if cached_coords:
            logger.debug(f"City geocoding cache hit for {city}, {province}")
            return cached_coords
        
        # Build city string
        city_address = f"{city}, {province}, {country}"
        
        try:
            # Rate limit requests
            self._rate_limit()
            
            # Geocode city
            logger.info(f"Geocoding city: {city_address}")
            location = self.geocoder.geocode(city_address, country_codes=['ca'])
            
            if location:
                coords = (
                    Decimal(str(location.latitude)),
                    Decimal(str(location.longitude))
                )
                
                # Cache for 90 days (city centers don't change)
                cache.set(cache_key, coords, timeout=60*60*24*90)
                
                logger.info(f"Geocoded city {city}, {province} to {coords}")
                return coords
            else:
                logger.warning(f"Could not geocode city: {city_address}")
                return None
        
        except GeocoderTimedOut:
            logger.error(f"Geocoding timeout for city: {city_address}")
            return None
        
        except GeocoderServiceError as e:
            logger.error(f"Geocoding service error for {city_address}: {e}")
            return None
        
        except Exception as e:
            logger.exception(f"Unexpected geocoding error for {city_address}: {e}")
            return None


# Global geocoding service instance
geocoding_service = GeocodingService()
