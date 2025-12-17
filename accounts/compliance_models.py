"""
PIPEDA and Law 25 Compliance Models
Tracks data breaches, consent history, and retention policies
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class DataBreachLog(models.Model):
    """
    Track data breaches as required by Law 25 (Quebec Bill 64)
    Article 3.5: Must notify within 72 hours of discovery
    PIPEDA Breach of Security Safeguards Regulations
    """
    SEVERITY_CHOICES = [
        ('low', _('Low - No significant risk')),
        ('medium', _('Medium - Moderate risk')),
        ('high', _('High - Real risk of serious harm')),
        ('critical', _('Critical - Immediate serious harm')),
    ]
    
    STATUS_CHOICES = [
        ('discovered', _('Discovered')),
        ('investigating', _('Investigating')),
        ('users_notified', _('Users Notified')),
        ('authorities_notified', _('Authorities Notified')),
        ('cai_notified', _('CAI Notified (Quebec)')),
        ('opc_notified', _('OPC Notified (Federal)')),
        ('mitigated', _('Mitigated')),
        ('resolved', _('Resolved')),
    ]
    
    # Breach Details
    breach_date = models.DateTimeField(
        verbose_name=_('Breach Date'),
        help_text=_('When the breach occurred (estimated if unknown)')
    )
    discovery_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Discovery Date'),
        help_text=_('When the breach was discovered')
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        verbose_name=_('Severity Level')
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='discovered',
        verbose_name=_('Status')
    )
    
    # Affected Data
    affected_users_count = models.IntegerField(
        default=0,
        verbose_name=_('Number of Affected Users')
    )
    affected_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='data_breaches',
        verbose_name=_('Affected Users')
    )
    data_types_compromised = models.JSONField(
        default=list,
        verbose_name=_('Data Types Compromised'),
        help_text=_('List of data types: email, phone, address, financial, etc.')
    )
    
    # Breach Description
    description = models.TextField(
        verbose_name=_('Breach Description'),
        help_text=_('Detailed description of what happened')
    )
    attack_vector = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Attack Vector'),
        help_text=_('How the breach occurred: phishing, SQL injection, etc.')
    )
    
    # Notification Tracking (Law 25 72-hour requirement)
    users_notified_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Users Notified Date')
    )
    cai_notified_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('CAI Notified Date'),
        help_text=_('Commission d\'accès à l\'information du Québec')
    )
    opc_notified_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('OPC Notified Date'),
        help_text=_('Office of the Privacy Commissioner of Canada')
    )
    
    # Mitigation
    mitigation_steps = models.TextField(
        blank=True,
        verbose_name=_('Mitigation Steps'),
        help_text=_('Steps taken to address the breach')
    )
    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolution Date')
    )
    
    # Compliance Tracking
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_breaches',
        verbose_name=_('Reported By')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Data Breach Log')
        verbose_name_plural = _('Data Breach Logs')
        ordering = ['-discovery_date']
    
    def __str__(self):
        return f"Breach {self.id} - {self.get_severity_display()} ({self.discovery_date.strftime('%Y-%m-%d')})"  # type: ignore[attr-defined]
    
    def is_within_72_hours(self):
        """Check if notifications are within Law 25 72-hour requirement"""
        if not self.users_notified_date:
            return False
        time_diff = self.users_notified_date - self.discovery_date
        return time_diff.total_seconds() <= (72 * 3600)
    
    def days_since_discovery(self):
        """Calculate days since breach discovery"""
        return (timezone.now() - self.discovery_date).days


class ConsentHistory(models.Model):
    """
    Track all consent changes for PIPEDA accountability principle
    Maintains immutable audit trail of consent modifications
    """
    CONSENT_TYPE_CHOICES = [
        ('data_processing', _('Data Processing')),
        ('marketing', _('Marketing Communications')),
        ('third_party_sharing', _('Third Party Sharing')),
        ('cross_border_africa', _('Cross-Border Transfer to Africa')),
        ('cookies', _('Cookie Consent')),
        ('analytics', _('Analytics Tracking')),
    ]
    
    ACTION_CHOICES = [
        ('granted', _('Consent Granted')),
        ('withdrawn', _('Consent Withdrawn')),
        ('modified', _('Consent Modified')),
        ('renewed', _('Consent Renewed')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consent_history',
        verbose_name=_('User')
    )
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPE_CHOICES,
        verbose_name=_('Consent Type')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('Action')
    )
    
    # Consent Details
    consent_given = models.BooleanField(
        verbose_name=_('Consent Given')
    )
    privacy_policy_version = models.CharField(
        max_length=20,
        verbose_name=_('Privacy Policy Version')
    )
    consent_method = models.CharField(
        max_length=50,
        default='web_form',
        verbose_name=_('Consent Method'),
        help_text=_('How consent was collected: web_form, email, phone, in_person')
    )
    
    # Audit Trail (PIPEDA Principle 8 - Individual Access)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Address')
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    consent_text = models.TextField(
        blank=True,
        verbose_name=_('Consent Text Shown'),
        help_text=_('Exact text user consented to')
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Timestamp')
    )
    
    # Additional Context
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    class Meta:
        verbose_name = _('Consent History')
        verbose_name_plural = _('Consent Histories')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['consent_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_consent_type_display()} - {self.get_action_display()} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"  # type: ignore[attr-defined]


class DataRetentionPolicy(models.Model):
    """
    Track data retention policies for different data types
    Law 25 Article 11: Retention limited to necessary period
    PIPEDA Principle 5: Retention Limits
    """
    DATA_CATEGORY_CHOICES = [
        ('user_profile', _('User Profile Information')),
        ('financial', _('Financial Records (7 years)')),
        ('vehicle_listings', _('Vehicle Listings')),
        ('deals_transactions', _('Deals and Transactions (7 years)')),
        ('commissions', _('Commission Records (7 years)')),
        ('audit_logs', _('Audit Logs (7 years)')),
        ('marketing', _('Marketing Communications')),
        ('support_tickets', _('Customer Support Records')),
        ('shipping_documents', _('Shipping Documents (7 years)')),
        ('customs_certifications', _('Customs/Certification Records (7 years)')),
        ('session_logs', _('Session Logs (90 days)')),
        ('analytics', _('Analytics Data (2 years)')),
    ]
    
    data_category = models.CharField(
        max_length=50,
        choices=DATA_CATEGORY_CHOICES,
        unique=True,
        verbose_name=_('Data Category')
    )
    retention_days = models.IntegerField(
        verbose_name=_('Retention Period (Days)'),
        help_text=_('Number of days to retain data (2555 days = 7 years)')
    )
    legal_basis = models.TextField(
        verbose_name=_('Legal Basis'),
        help_text=_('Legal requirement for retention period (e.g., CRA, Tax Act)')
    )
    
    # Automated Deletion
    auto_delete_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Auto-Delete Enabled'),
        help_text=_('Automatically delete data after retention period')
    )
    last_cleanup_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Cleanup Date')
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Data Retention Policy')
        verbose_name_plural = _('Data Retention Policies')
        ordering = ['data_category']
    
    def __str__(self):
        return f"{self.get_data_category_display()} - {self.retention_days} days"  # type: ignore[attr-defined]
    
    def retention_years(self):
        """Calculate retention period in years"""
        return round(self.retention_days / 365, 1)


class PrivacyImpactAssessment(models.Model):
    """
    Track Privacy Impact Assessments (PIA) as required by Law 25
    Article 3.3: PIA required for new technologies with high privacy risk
    """
    RISK_LEVEL_CHOICES = [
        ('low', _('Low Risk')),
        ('medium', _('Medium Risk')),
        ('high', _('High Risk')),
        ('very_high', _('Very High Risk')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('under_review', _('Under Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('requires_revision', _('Requires Revision')),
    ]
    
    # Assessment Details
    title = models.CharField(
        max_length=255,
        verbose_name=_('Assessment Title')
    )
    description = models.TextField(
        verbose_name=_('Description'),
        help_text=_('Description of system/process being assessed')
    )
    project_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Project Name')
    )
    
    # Risk Assessment
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='medium',
        verbose_name=_('Risk Level')
    )
    data_types_processed = models.JSONField(
        default=list,
        verbose_name=_('Data Types Processed'),
        help_text=_('List of personal information types processed')
    )
    cross_border_transfer = models.BooleanField(
        default=False,
        verbose_name=_('Cross-Border Transfer'),
        help_text=_('Does this involve transferring data outside Canada?')
    )
    
    # Mitigation
    identified_risks = models.TextField(
        verbose_name=_('Identified Risks')
    )
    mitigation_measures = models.TextField(
        verbose_name=_('Mitigation Measures')
    )
    
    # Approval
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('Status')
    )
    assessed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_pias',
        verbose_name=_('Assessed By')
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_pias',
        verbose_name=_('Approved By')
    )
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approval Date')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review_due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Review Due Date'),
        help_text=_('When this PIA should be reviewed (typically annually)')
    )
    
    class Meta:
        verbose_name = _('Privacy Impact Assessment')
        verbose_name_plural = _('Privacy Impact Assessments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PIA: {self.title} ({self.get_status_display()})"  # type: ignore[attr-defined]
