"""
Rate throttling for external vehicle data APIs
Prevents exceeding provider rate limits
"""
from rest_framework.throttling import UserRateThrottle


class VehicleHistoryRateThrottle(UserRateThrottle):
    """
    Throttle for CarFax/AutoCheck API calls
    Typical limit: 100 requests/hour per API key
    """
    scope = 'vehicle_history'


class TransportCanadaRateThrottle(UserRateThrottle):
    """
    Throttle for Transport Canada public API
    Limit: 1000 requests/hour (public data)
    """
    scope = 'transport_canada'


class ProvincialRegistryRateThrottle(UserRateThrottle):
    """
    Throttle for provincial registry APIs (ICBC, MTO, SAAQ)
    Varies by province - conservative limit applied
    """
    scope = 'provincial_registry'
