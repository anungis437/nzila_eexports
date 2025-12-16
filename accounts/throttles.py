"""
Login Throttle Class
Prevents brute force login attacks
"""
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Custom throttle for login endpoint
    Strict limits to prevent brute force attacks
    """
    scope = 'login'

