"""
Audit Trail Serializers
"""

from rest_framework import serializers
from .models import (
    AuditLog, LoginHistory, DataChangeLog, 
    SecurityEvent, APIAccessLog
)
from accounts.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    user_display = UserSerializer(source='user', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    changes_summary = serializers.CharField(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_display', 'action', 'action_display',
            'severity', 'severity_display', 'description', 'content_type',
            'object_id', 'changes', 'changes_summary', 'metadata',
            'ip_address', 'user_agent', 'request_method', 'request_path',
            'timestamp'
        ]
        read_only_fields = fields


class LoginHistorySerializer(serializers.ModelSerializer):
    user_display = UserSerializer(source='user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'user', 'user_display', 'status', 'status_display',
            'ip_address', 'user_agent', 'location', 'failure_reason',
            'failed_attempts', 'session_key', 'login_timestamp',
            'logout_timestamp', 'session_duration', 'two_factor_used',
            'two_factor_method'
        ]
        read_only_fields = fields


class DataChangeLogSerializer(serializers.ModelSerializer):
    user_display = UserSerializer(source='user', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = DataChangeLog
        fields = [
            'id', 'user', 'user_display', 'model_name', 'object_id',
            'object_repr', 'action', 'action_display', 'field_name',
            'old_value', 'new_value', 'reason', 'ip_address', 'timestamp'
        ]
        read_only_fields = fields


class SecurityEventSerializer(serializers.ModelSerializer):
    user_display = UserSerializer(source='user', read_only=True)
    resolved_by_display = UserSerializer(source='resolved_by', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = SecurityEvent
        fields = [
            'id', 'user', 'user_display', 'event_type', 'event_type_display',
            'risk_level', 'risk_level_display', 'description', 'ip_address',
            'user_agent', 'request_path', 'blocked', 'action_taken',
            'metadata', 'timestamp', 'resolved', 'resolved_by',
            'resolved_by_display', 'resolved_at'
        ]
        read_only_fields = [f for f in fields if f not in ['resolved', 'resolved_by', 'resolved_at']]


class APIAccessLogSerializer(serializers.ModelSerializer):
    user_display = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = APIAccessLog
        fields = [
            'id', 'user', 'user_display', 'method', 'path', 'query_params',
            'status_code', 'response_time_ms', 'ip_address', 'user_agent',
            'request_body_size', 'response_body_size', 'timestamp'
        ]
        read_only_fields = fields


class AuditStatsSerializer(serializers.Serializer):
    """Serializer for audit statistics"""
    total_actions = serializers.IntegerField()
    total_logins = serializers.IntegerField()
    failed_logins = serializers.IntegerField()
    security_events = serializers.IntegerField()
    unresolved_security_events = serializers.IntegerField()
    api_calls = serializers.IntegerField()
    avg_response_time = serializers.FloatField()


class UserActivitySerializer(serializers.Serializer):
    """Serializer for user activity stats"""
    audit_logs = serializers.IntegerField()
    logins = serializers.IntegerField()
    data_changes = serializers.IntegerField()
    api_calls = serializers.IntegerField()
