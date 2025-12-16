"""
Custom JWT authentication backend that reads tokens from httpOnly cookies
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request


class JWTCookieAuthentication(JWTAuthentication):
    """
    JWT authentication using httpOnly cookies instead of Authorization header
    
    This provides better security against XSS attacks by preventing JavaScript
    from accessing the authentication token.
    """
    
    def authenticate(self, request: Request):
        """
        Try to authenticate using JWT from cookie first, fall back to header
        
        This allows gradual migration and supports both cookie and header auth
        """
        # Try to get token from cookie first
        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            # Validate the token from cookie
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        
        # Fall back to standard header-based authentication
        # This allows backward compatibility during migration
        return super().authenticate(request)
