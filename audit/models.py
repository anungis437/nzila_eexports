"""
Audit Trail Models
Comprehensive logging system for tracking all user actions and system events
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

User = get_user_model()


class AuditLog(models.Model):
    """
    Main audit log model - tracks all actions in the system
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('payment_created', 'Payment Created'),
        ('payment_succeeded', 'Payment Succeeded'),
        ('payment_failed', 'Payment Failed'),
        ('payment_refunded', 'Payment Refunded'),
        ('invoice_created', 'Invoice Created'),
        ('invoice_sent', 'Invoice Sent'),
        ('invoice_paid', 'Invoice Paid'),
        ('deal_created', 'Deal Created'),
        ('deal_updated', 'Deal Updated'),
        ('deal_status_changed', 'Deal Status Changed'),
        ('shipment_created', 'Shipment Created'),
        ('shipment_updated', 'Shipment Updated'),
        ('document_uploaded', 'Document Uploaded'),
        ('document_deleted', 'Document Deleted'),
        ('commission_calculated', 'Commission Calculated'),
        ('commission_paid', 'Commission Paid'),
        ('settings_changed', 'Settings Changed'),
        ('export', 'Data Export'),
        ('import', 'Data Import'),
        ('api_call', 'API Call'),
        ('webhook_received', 'Webhook Received'),
        ('email_sent', 'Email Sent'),
        ('sms_sent', 'SMS Sent'),
        ('other', 'Other'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    # User who performed the action
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    # Action details
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info', db_index=True)
    description = models.TextField()

    # Generic relation to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional data
    changes = models.JSONField(default=dict, blank=True)  # Before/after values
    metadata = models.JSONField(default=dict, blank=True)  # Extra context
    
    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)  # GET, POST, etc.
    request_path = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'action']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        user_str = self.user.email if self.user else 'System'
        return f'{user_str} - {self.get_action_display()} at {self.timestamp}'

    @property
    def changes_summary(self):
        """Return a human-readable summary of changes"""
        if not self.changes:
            return "No changes recorded"
        
        summary = []
        for field, change in self.changes.items():
            old_val = change.get('old', 'N/A')
            new_val = change.get('new', 'N/A')
            summary.append(f"{field}: {old_val} → {new_val}")
        
        return "; ".join(summary)


class LoginHistory(models.Model):
    """
    Dedicated model for tracking login attempts and sessions
    """
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)  # City, Country
    
    # Failure details
    failure_reason = models.CharField(max_length=200, blank=True)
    failed_attempts = models.IntegerField(default=0)
    
    # Session details
    session_key = models.CharField(max_length=100, blank=True)
    login_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    logout_timestamp = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)
    
    # 2FA details
    two_factor_used = models.BooleanField(default=False)
    two_factor_method = models.CharField(max_length=20, blank=True)  # totp, sms
    
    class Meta:
        ordering = ['-login_timestamp']
        indexes = [
            models.Index(fields=['user', '-login_timestamp']),
            models.Index(fields=['status', '-login_timestamp']),
        ]
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'

    def save(self, *args, **kwargs):
        """Calculate session duration if logout_timestamp is set"""
        if self.logout_timestamp and self.login_timestamp:
            self.session_duration = self.logout_timestamp - self.login_timestamp
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email} - {self.status} at {self.login_timestamp}'


class DataChangeLog(models.Model):
    """
    Detailed logging of data changes for compliance and auditing
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_changes'
    )
    
    # Model information
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    object_repr = models.CharField(max_length=200)  # String representation
    
    # Change details
    action = models.CharField(max_length=20, choices=[
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ], db_index=True)
    
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Additional context
    reason = models.TextField(blank=True)  # Why was this changed?
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
        verbose_name = 'Data Change Log'
        verbose_name_plural = 'Data Change Logs'

    def __str__(self):
        return f'{self.model_name} #{self.object_id} - {self.action} by {self.user}'


class SecurityEvent(models.Model):
    """
    Track security-related events
    """
    EVENT_TYPES = [
        ('suspicious_login', 'Suspicious Login'),
        ('multiple_failed_logins', 'Multiple Failed Logins'),
        ('password_reset_request', 'Password Reset Request'),
        ('password_reset_complete', 'Password Reset Complete'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('2fa_bypass_attempt', '2FA Bypass Attempt'),
        ('permission_denied', 'Permission Denied'),
        ('api_rate_limit_exceeded', 'API Rate Limit Exceeded'),
        ('sql_injection_attempt', 'SQL Injection Attempt'),
        ('xss_attempt', 'XSS Attempt'),
        ('csrf_failure', 'CSRF Failure'),
        ('unusual_activity', 'Unusual Activity'),
    ]

    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, db_index=True)
    description = models.TextField()
    
    # Request details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    
    # Response
    blocked = models.BooleanField(default=False)
    action_taken = models.CharField(max_length=200, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_security_events'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'risk_level']),
            models.Index(fields=['resolved', '-timestamp']),
        ]
        verbose_name = 'Security Event'
        verbose_name_plural = 'Security Events'

    def __str__(self):
        return f'{self.event_type} - {self.risk_level} at {self.timestamp}'


class APIAccessLog(models.Model):
    """
    Track all API access for monitoring and analytics
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_access_logs'
    )
    
    # Request details
    method = models.CharField(max_length=10, db_index=True)  # GET, POST, etc.
    path = models.CharField(max_length=500, db_index=True)
    query_params = models.TextField(blank=True)
    
    # Response details
    status_code = models.IntegerField(db_index=True)
    response_time_ms = models.IntegerField()  # Response time in milliseconds
    
    # Request info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Additional data
    request_body_size = models.IntegerField(default=0)
    response_body_size = models.IntegerField(default=0)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'status_code']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['path', '-timestamp']),
        ]
        verbose_name = 'API Access Log'
        verbose_name_plural = 'API Access Logs'

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f'{user_str} - {self.method} {self.path} [{self.status_code}]'
