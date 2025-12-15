"""
Middleware for audit logging and security enhancements
"""
from django.utils.deprecation import MiddlewareMixin
from nzila_export.models import AuditLog


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log user actions for compliance
    Supports Law 25, PIPEDA, and GDPR requirements
    """
    
    def process_request(self, request):
        # Store request data for later use
        request.audit_data = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        return None
    
    def process_response(self, request, response):
        # Log specific actions if needed
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Log authentication events
            if request.path.endswith('/login/') and response.status_code == 200:
                AuditLog.objects.create(
                    user=request.user,
                    action='login',
                    model_name='User',
                    object_id=str(request.user.id),
                    object_repr=str(request.user),
                    ip_address=request.audit_data.get('ip_address'),
                    user_agent=request.audit_data.get('user_agent')
                )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers for production deployment
    Supports OWASP security best practices
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (CSP)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
        
        return response
