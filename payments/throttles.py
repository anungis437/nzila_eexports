"""
Payment Throttle Class
Provides stricter rate limiting for sensitive payment endpoints
"""
from rest_framework.throttling import UserRateThrottle


class PaymentRateThrottle(UserRateThrottle):
    """
    Custom throttle for payment endpoints
    Stricter limits to prevent payment abuse
    """
    scope = 'payment'

