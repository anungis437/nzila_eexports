"""
Audit Middleware - Automatically log API requests and responses
"""

import time
import sys
from .services import AuditService, get_client_ip


class AuditMiddleware:
    """
    Middleware to automatically log API requests and track response times
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Record start time
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Only log API requests (not static files)
        if request.path.startswith('/api/'):
            try:
                # Get user (may be None for unauthenticated requests)
                user = request.user if request.user.is_authenticated else None
                
                # Get request body size
                request_body_size = int(request.META.get('CONTENT_LENGTH', 0))
                
                # Get response body size
                response_body_size = len(response.content) if hasattr(response, 'content') else 0
                
                # Log the API access
                AuditService.log_api_access(
                    user=user,
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    query_params=request.META.get('QUERY_STRING', '')[:500],
                    request_body_size=request_body_size,
                    response_body_size=response_body_size,
                )
            except Exception as e:
                # Don't let logging errors break the request
                print(f"Error logging API access: {e}", file=sys.stderr)
        
        return response


class SecurityAuditMiddleware:
    """
    Middleware to detect and log security events
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.failed_login_attempts = {}  # Track failed attempts per IP

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check for suspicious activity
        try:
            ip_address = get_client_ip(request)
            
            # Check for SQL injection patterns in query params
            query_string = request.META.get('QUERY_STRING', '')
            if any(pattern in query_string.lower() for pattern in ['union select', 'drop table', '--', ';--']):
                AuditService.log_security_event(
                    event_type='sql_injection_attempt',
                    risk_level='high',
                    description=f'Potential SQL injection attempt detected in query: {query_string[:200]}',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_path=request.path,
                    blocked=True,
                    action_taken='Request blocked and logged',
                )
            
            # Check for XSS patterns
            if any(pattern in query_string.lower() for pattern in ['<script', 'javascript:', 'onerror=']):
                AuditService.log_security_event(
                    event_type='xss_attempt',
                    risk_level='high',
                    description=f'Potential XSS attempt detected: {query_string[:200]}',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_path=request.path,
                    blocked=True,
                    action_taken='Request blocked and logged',
                )
            
            # Track failed login attempts
            if request.path == '/api/accounts/login/' and response.status_code in [401, 403]:
                self.failed_login_attempts[ip_address] = self.failed_login_attempts.get(ip_address, 0) + 1
                
                if self.failed_login_attempts[ip_address] >= 5:
                    AuditService.log_security_event(
                        event_type='multiple_failed_logins',
                        risk_level='medium',
                        description=f'Multiple failed login attempts from IP: {ip_address}',
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        request_path=request.path,
                        blocked=False,
                        action_taken='Monitoring for account lockout',
                        metadata={'attempts': self.failed_login_attempts[ip_address]},
                    )
            
            # Reset counter on successful login
            if request.path == '/api/accounts/login/' and response.status_code == 200:
                self.failed_login_attempts.pop(ip_address, None)
            
            # Check for rate limit exceeded (429 responses)
            if response.status_code == 429:
                user = request.user if request.user.is_authenticated else None
                AuditService.log_security_event(
                    event_type='api_rate_limit_exceeded',
                    risk_level='medium',
                    description=f'API rate limit exceeded for path: {request.path}',
                    user=user,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_path=request.path,
                    blocked=True,
                    action_taken='Request throttled',
                )
            
        except Exception as e:
            # Don't let security logging errors break the request
            print(f"Error in security audit middleware: {e}", file=sys.stderr)
        
        return response
