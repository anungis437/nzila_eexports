"""
Audit Service - Helper functions for logging audit events
"""

from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, LoginHistory, DataChangeLog, SecurityEvent, APIAccessLog
import json
from datetime import datetime


class AuditService:
    """Service class for creating audit logs"""

    @staticmethod
    def log_action(user, action, description, content_object=None, changes=None, 
                   metadata=None, severity='info', request=None):
        """
        Log a general action
        
        Args:
            user: User performing the action
            action: Action type (from AuditLog.ACTION_TYPES)
            description: Human-readable description
            content_object: The object being acted upon (optional)
            changes: Dictionary of changes (optional)
            metadata: Additional metadata (optional)
            severity: Severity level (default: 'info')
            request: HTTP request object (optional)
        """
        log_data = {
            'user': user,
            'action': action,
            'description': description,
            'severity': severity,
            'changes': changes or {},
            'metadata': metadata or {},
        }

        # Add content object if provided
        if content_object:
            log_data['content_type'] = ContentType.objects.get_for_model(content_object)
            log_data['object_id'] = content_object.pk

        # Add request information if available
        if request:
            log_data['ip_address'] = get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            log_data['request_method'] = request.method
            log_data['request_path'] = request.path

        return AuditLog.objects.create(**log_data)

    @staticmethod
    def log_login(user, status, ip_address, user_agent='', failure_reason='', 
                  session_key='', two_factor_used=False, two_factor_method=''):
        """Log a login attempt"""
        return LoginHistory.objects.create(
            user=user,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
            session_key=session_key,
            two_factor_used=two_factor_used,
            two_factor_method=two_factor_method,
        )

    @staticmethod
    def log_logout(user, session_key):
        """Log a logout and calculate session duration"""
        from django.utils import timezone as django_timezone
        try:
            login_record = LoginHistory.objects.filter(
                user=user,
                session_key=session_key,
                status='success',
                logout_timestamp__isnull=True
            ).latest('login_timestamp')
            
            login_record.logout_timestamp = django_timezone.now()
            login_record.save()
            
            return login_record
        except LoginHistory.DoesNotExist:
            return None

    @staticmethod
    def log_data_change(user, model_name, object_id, object_repr, action, 
                       field_name='', old_value='', new_value='', reason='', 
                       ip_address=None):
        """Log a data change"""
        return DataChangeLog.objects.create(
            user=user,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            action=action,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else '',
            new_value=str(new_value) if new_value is not None else '',
            reason=reason,
            ip_address=ip_address,
        )

    @staticmethod
    def log_model_change(user, instance, action, changes=None, request=None):
        """
        Log changes to a model instance
        
        Args:
            user: User making the change
            instance: Model instance being changed
            action: 'create', 'update', or 'delete'
            changes: Dictionary of field changes
            request: HTTP request object
        """
        model_name = instance._meta.model_name
        object_repr = str(instance)
        ip_address = get_client_ip(request) if request else None

        if action == 'update' and changes:
            # Log each field change separately
            for field_name, (old_value, new_value) in changes.items():
                DataChangeLog.objects.create(
                    user=user,
                    model_name=model_name,
                    object_id=instance.pk,
                    object_repr=object_repr,
                    action=action,
                    field_name=field_name,
                    old_value=str(old_value) if old_value is not None else '',
                    new_value=str(new_value) if new_value is not None else '',
                    ip_address=ip_address,
                )
        else:
            # Log create or delete action
            DataChangeLog.objects.create(
                user=user,
                model_name=model_name,
                object_id=instance.pk,
                object_repr=object_repr,
                action=action,
                ip_address=ip_address,
            )

    @staticmethod
    def log_security_event(event_type, risk_level, description, user=None, 
                          ip_address=None, user_agent='', request_path='', 
                          blocked=False, action_taken='', metadata=None):
        """Log a security event"""
        return SecurityEvent.objects.create(
            user=user,
            event_type=event_type,
            risk_level=risk_level,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            blocked=blocked,
            action_taken=action_taken,
            metadata=metadata or {},
        )

    @staticmethod
    def log_api_access(user, method, path, status_code, response_time_ms, 
                      ip_address, user_agent='', query_params='', 
                      request_body_size=0, response_body_size=0):
        """Log an API access"""
        return APIAccessLog.objects.create(
            user=user,
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            query_params=query_params,
            request_body_size=request_body_size,
            response_body_size=response_body_size,
        )

    @staticmethod
    def get_user_activity(user, days=30):
        """Get recent activity for a user"""
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        
        return {
            'audit_logs': AuditLog.objects.filter(user=user, timestamp__gte=since).count(),
            'logins': LoginHistory.objects.filter(user=user, login_timestamp__gte=since).count(),
            'data_changes': DataChangeLog.objects.filter(user=user, timestamp__gte=since).count(),
            'api_calls': APIAccessLog.objects.filter(user=user, timestamp__gte=since).count(),
        }

    @staticmethod
    def get_system_stats(days=7):
        """Get system-wide audit statistics"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg
        
        since = timezone.now() - timedelta(days=days)
        
        return {
            'total_actions': AuditLog.objects.filter(timestamp__gte=since).count(),
            'total_logins': LoginHistory.objects.filter(login_timestamp__gte=since).count(),
            'failed_logins': LoginHistory.objects.filter(
                login_timestamp__gte=since, 
                status='failed'
            ).count(),
            'security_events': SecurityEvent.objects.filter(timestamp__gte=since).count(),
            'unresolved_security_events': SecurityEvent.objects.filter(
                timestamp__gte=since, 
                resolved=False
            ).count(),
            'api_calls': APIAccessLog.objects.filter(timestamp__gte=since).count(),
            'avg_response_time': APIAccessLog.objects.filter(
                timestamp__gte=since
            ).aggregate(Avg('response_time_ms'))['response_time_ms__avg'] or 0,
        }


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def serialize_changes(old_instance, new_instance, fields=None):
    """
    Compare two instances and return a dictionary of changes
    
    Args:
        old_instance: Previous state of the object
        new_instance: New state of the object
        fields: List of field names to check (optional, checks all if None)
    
    Returns:
        Dictionary of changes {field_name: {'old': old_value, 'new': new_value}}
    """
    if not old_instance or not new_instance:
        return {}
    
    changes = {}
    
    # Get fields to check
    if fields is None:
        fields = [f.name for f in new_instance._meta.fields]
    
    for field_name in fields:
        try:
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(new_instance, field_name, None)
            
            # Skip if values are the same
            if old_value == new_value:
                continue
            
            # Handle JSON fields
            if isinstance(old_value, dict) or isinstance(new_value, dict):
                old_value = json.dumps(old_value) if old_value else '{}'
                new_value = json.dumps(new_value) if new_value else '{}'
            
            changes[field_name] = {
                'old': str(old_value) if old_value is not None else None,
                'new': str(new_value) if new_value is not None else None,
            }
        except AttributeError:
            continue
    
    return changes
