"""
Geolocation utilities for broker and dealer location management
"""
from typing import Optional, Dict, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """
    Get real IP address from request (handles proxies and load balancers)
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def detect_location_from_ip(ip_address: str) -> Optional[Dict]:
    """
    Detect geographic location from IP address using GeoIP2
    
    Args:
        ip_address: IP address string
        
    Returns:
        dict: Location data with country_code, country_name, city, timezone
        None: If detection fails
    """
    try:
        from django.contrib.gis.geoip2 import GeoIP2
        
        g = GeoIP2()
        country = g.country(ip_address)
        city = g.city(ip_address)
        
        return {
            'country_code': country['country_code'],
            'country_name': country['country_name'],
            'city': city.get('city', ''),
            'timezone': city.get('time_zone', 'Africa/Abidjan'),
            'latitude': city.get('latitude'),
            'longitude': city.get('longitude'),
        }
    except Exception as e:
        logger.warning(f"GeoIP2 detection failed for {ip_address}: {e}")
        return None


def geocode_location(city: str, country: str) -> Optional[Dict[str, float]]:
    """
    Geocode city/country to latitude/longitude coordinates
    Uses caching to avoid repeated API calls
    
    Args:
        city: City name (e.g., "Abidjan")
        country: Country name (e.g., "Côte d'Ivoire")
        
    Returns:
        dict: {'latitude': float, 'longitude': float}
        None: If geocoding fails
    """
    from django.core.cache import cache
    
    cache_key = f"geocode:{city}:{country}"
    result = cache.get(cache_key)
    
    if result:
        return result
    
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        
        geolocator = Nominatim(user_agent="nzila_export", timeout=10)
        location = geolocator.geocode(f"{city}, {country}")
        
        if location:
            result = {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
            # Cache for 30 days
            cache.set(cache_key, result, timeout=86400 * 30)
            return result
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        logger.warning(f"Geocoding failed for {city}, {country}: {e}")
    
    return None


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float], 
                       unit: str = 'km') -> Optional[float]:
    """
    Calculate distance between two coordinates
    
    Args:
        coord1: (latitude, longitude) tuple for point 1
        coord2: (latitude, longitude) tuple for point 2
        unit: 'km' (kilometers), 'nm' (nautical miles), or 'mi' (miles)
        
    Returns:
        float: Distance in specified unit
        None: If calculation fails
    """
    try:
        from geopy.distance import geodesic
        
        distance_km = geodesic(coord1, coord2).kilometers
        
        if unit == 'nm':
            return distance_km * 0.539957  # km to nautical miles
        elif unit == 'mi':
            return distance_km * 0.621371  # km to miles
        else:
            return distance_km
    except Exception as e:
        logger.warning(f"Distance calculation failed: {e}")
        return None


def get_shipping_distance_to_canada(broker_coords: Tuple[float, float]) -> Dict:
    """
    Calculate shipping distance from broker location to nearest Canadian port
    
    Args:
        broker_coords: (latitude, longitude) tuple for broker location
        
    Returns:
        dict: {
            'nearest_port': str,
            'distance_km': float,
            'distance_nm': float,
            'estimated_days': int
        }
    """
    # Major Canadian ports with coordinates
    CANADIAN_PORTS = {
        'Halifax': (44.6488, -63.5752),
        'Montreal': (45.5017, -73.5673),
        'Vancouver': (49.2827, -123.1207),
        'Toronto': (43.6532, -79.3832),
    }
    
    distances = {}
    for port_name, port_coords in CANADIAN_PORTS.items():
        dist_km = calculate_distance(broker_coords, port_coords, 'km')
        if dist_km:
            distances[port_name] = dist_km
    
    if not distances:
        return None
    
    # Find nearest port
    nearest_port = min(distances, key=distances.get)
    distance_km = distances[nearest_port]
    distance_nm = distance_km * 0.539957
    
    # Estimate shipping time (average 500 nautical miles per day)
    estimated_days = int(distance_nm / 500)
    
    return {
        'nearest_port': nearest_port,
        'distance_km': round(distance_km, 0),
        'distance_nm': round(distance_nm, 0),
        'estimated_days': max(1, estimated_days),
    }


def get_currency_for_country(country_code: str) -> Dict:
    """
    Get currency information for a country
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'CI', 'NG')
        
    Returns:
        dict: {'code': 'XOF', 'name': 'CFA Franc BCEAO', 'symbol': 'CFA'}
    """
    # Currency mapping for African countries where brokers operate
    COUNTRY_CURRENCIES = {
        'CI': ('XOF', 'CFA Franc BCEAO', 'CFA'),
        'SN': ('XOF', 'CFA Franc BCEAO', 'CFA'),
        'BJ': ('XOF', 'CFA Franc BCEAO', 'CFA'),
        'TG': ('XOF', 'CFA Franc BCEAO', 'CFA'),
        'BF': ('XOF', 'CFA Franc BCEAO', 'CFA'),
        'ML': ('XOF', 'CFA Franc BCEAO', 'CFA'),
        'NG': ('NGN', 'Nigerian Naira', '₦'),
        'GH': ('GHS', 'Ghanaian Cedi', '₵'),
        'CM': ('XAF', 'CFA Franc BEAC', 'FCFA'),
        'CD': ('CDF', 'Congolese Franc', 'FC'),
        'KE': ('KES', 'Kenyan Shilling', 'KSh'),
        'ZA': ('ZAR', 'South African Rand', 'R'),
        'MA': ('MAD', 'Moroccan Dirham', 'MAD'),
        'TN': ('TND', 'Tunisian Dinar', 'TND'),
        'EG': ('EGP', 'Egyptian Pound', 'E£'),
    }
    
    currency_data = COUNTRY_CURRENCIES.get(country_code, ('USD', 'US Dollar', '$'))
    
    return {
        'code': currency_data[0],
        'name': currency_data[1],
        'symbol': currency_data[2],
    }


def get_preferred_language_for_country(country_code: str) -> str:
    """
    Get preferred language for a country
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
        
    Returns:
        str: 'en' or 'fr'
    """
    # French-speaking countries
    FRENCH_SPEAKING = ['CI', 'SN', 'BJ', 'TG', 'BF', 'ML', 'CM', 'CD', 'MA', 'TN']
    
    return 'fr' if country_code in FRENCH_SPEAKING else 'en'


def validate_broker_location(claimed_country: str, detected_country: str) -> bool:
    """
    Validate if claimed location matches detected location
    (Allows for VPN/proxy tolerance)
    
    Args:
        claimed_country: Country code broker claimed
        detected_country: Country code detected from IP
        
    Returns:
        bool: True if locations match or are in same region
    """
    # Same country = valid
    if claimed_country == detected_country:
        return True
    
    # Regional groupings (allow movement within region)
    WEST_AFRICA = ['CI', 'SN', 'GH', 'NG', 'BJ', 'TG', 'BF', 'ML']
    CENTRAL_AFRICA = ['CM', 'CD']
    EAST_AFRICA = ['KE', 'TZ', 'UG']
    NORTH_AFRICA = ['MA', 'TN', 'EG', 'DZ']
    SOUTHERN_AFRICA = ['ZA', 'NA', 'BW']
    
    regions = [WEST_AFRICA, CENTRAL_AFRICA, EAST_AFRICA, NORTH_AFRICA, SOUTHERN_AFRICA]
    
    for region in regions:
        if claimed_country in region and detected_country in region:
            return True
    
    return False


def convert_to_local_time(utc_datetime, timezone_str: str):
    """
    Convert UTC datetime to broker's local timezone
    
    Args:
        utc_datetime: datetime object in UTC
        timezone_str: Timezone string (e.g., 'Africa/Abidjan')
        
    Returns:
        datetime: Converted to local timezone
    """
    import pytz
    
    if not utc_datetime:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        return utc_datetime.astimezone(tz)
    except Exception as e:
        logger.warning(f"Timezone conversion failed for {timezone_str}: {e}")
        return utc_datetime
