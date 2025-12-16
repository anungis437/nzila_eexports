from django.contrib import admin
from .models import (
    AuditLog, LoginHistory, DataChangeLog,
    SecurityEvent, APIAccessLog
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'severity', 'description', 'timestamp']
    list_filter = ['action', 'severity', 'timestamp']
    search_fields = ['user__email', 'description', 'ip_address']
    readonly_fields = [
        'user', 'action', 'severity', 'description', 'content_type',
        'object_id', 'changes', 'metadata', 'ip_address', 'user_agent',
        'request_method', 'request_path', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'ip_address', 'login_timestamp', 'two_factor_used']
    list_filter = ['status', 'two_factor_used', 'login_timestamp']
    search_fields = ['user__email', 'ip_address', 'location']
    readonly_fields = [
        'user', 'status', 'ip_address', 'user_agent', 'location',
        'failure_reason', 'failed_attempts', 'session_key',
        'login_timestamp', 'logout_timestamp', 'session_duration',
        'two_factor_used', 'two_factor_method'
    ]
    date_hierarchy = 'login_timestamp'
    ordering = ['-login_timestamp']


@admin.register(DataChangeLog)
class DataChangeLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'model_name', 'object_repr', 'action', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__email', 'object_repr', 'field_name']
    readonly_fields = [
        'user', 'model_name', 'object_id', 'object_repr', 'action',
        'field_name', 'old_value', 'new_value', 'reason', 'ip_address',
        'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'risk_level', 'user', 'ip_address', 'resolved', 'timestamp']
    list_filter = ['event_type', 'risk_level', 'resolved', 'blocked', 'timestamp']
    search_fields = ['user__email', 'description', 'ip_address']
    readonly_fields = [
        'user', 'event_type', 'risk_level', 'description', 'ip_address',
        'user_agent', 'request_path', 'blocked', 'action_taken', 'metadata',
        'timestamp'
    ]
    fieldsets = (
        ('Event Details', {
            'fields': ('event_type', 'risk_level', 'description', 'timestamp')
        }),
        ('User & Request Info', {
            'fields': ('user', 'ip_address', 'user_agent', 'request_path')
        }),
        ('Response', {
            'fields': ('blocked', 'action_taken', 'metadata')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_by', 'resolved_at')
        }),
    )
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']


@admin.register(APIAccessLog)
class APIAccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'method', 'path', 'status_code', 'response_time_ms', 'timestamp']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['user__email', 'path', 'ip_address']
    readonly_fields = [
        'user', 'method', 'path', 'query_params', 'status_code',
        'response_time_ms', 'ip_address', 'user_agent',
        'request_body_size', 'response_body_size', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
