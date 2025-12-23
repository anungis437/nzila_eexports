from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class SecurityRisk(models.Model):
    """
    Security Risk Assessment for Shipments (ISO 28000 compliance)
    Tracks potential security threats for cross-border vehicle shipments
    """
    
    RISK_LEVEL_CHOICES = [
        ('low', _('Low Risk')),
        ('medium', _('Medium Risk')),
        ('high', _('High Risk')),
        ('critical', _('Critical Risk'))
    ]
    
    RISK_CATEGORY_CHOICES = [
        ('theft', _('Theft/Piracy')),
        ('smuggling', _('Smuggling')),
        ('terrorism', _('Terrorism')),
        ('fraud', _('Fraud/Counterfeiting')),
        ('customs', _('Customs/Regulatory')),
        ('cyber', _('Cyber Security')),
        ('personnel', _('Personnel Security')),
        ('facility', _('Facility Security'))
    ]
    
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('mitigating', _('Mitigating')),
        ('mitigated', _('Mitigated')),
        ('accepted', _('Accepted')),
        ('closed', _('Closed'))
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='security_risks',
        verbose_name=_('Shipment')
    )
    
    risk_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Risk ID'),
        help_text=_('Unique identifier for risk tracking')
    )
    
    category = models.CharField(
        max_length=20,
        choices=RISK_CATEGORY_CHOICES,
        verbose_name=_('Risk Category')
    )
    
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default='medium',
        verbose_name=_('Risk Level')
    )
    
    description = models.TextField(
        verbose_name=_('Risk Description'),
        help_text=_('Detailed description of the identified risk')
    )
    
    likelihood = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Likelihood'),
        help_text=_('Probability of risk occurring (1=rare, 5=certain)')
    )
    
    impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Impact'),
        help_text=_('Severity of impact if risk occurs (1=negligible, 5=catastrophic)')
    )
    
    mitigation_strategy = models.TextField(
        blank=True,
        verbose_name=_('Mitigation Strategy'),
        help_text=_('Actions to reduce or eliminate the risk')
    )
    
    contingency_plan = models.TextField(
        blank=True,
        verbose_name=_('Contingency Plan'),
        help_text=_('Response plan if risk materializes')
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name=_('Status')
    )
    
    identified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='identified_risks',
        verbose_name=_('Identified By')
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_risks',
        verbose_name=_('Assigned To')
    )
    
    identified_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Identified Date')
    )
    
    target_resolution_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Target Resolution Date')
    )
    
    resolution_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Resolution Date')
    )
    
    resolution_notes = models.TextField(
        blank=True,
        verbose_name=_('Resolution Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_risks'
        verbose_name = _('Security Risk')
        verbose_name_plural = _('Security Risks')
        ordering = ['-identified_date', 'risk_level']
        indexes = [
            models.Index(fields=['shipment', 'status']),
            models.Index(fields=['risk_level', 'status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.risk_id} - {self.get_category_display()} ({self.risk_level})"  # type: ignore[attr-defined]
    
    @property
    def risk_score(self):
        """Calculate risk score (likelihood × impact)"""
        return self.likelihood * self.impact
    
    @property
    def is_overdue(self):
        """Check if resolution is overdue"""
        from django.utils import timezone
        if self.target_resolution_date and self.status not in ['mitigated', 'closed']:
            return timezone.now().date() > self.target_resolution_date
        return False


class SecurityIncident(models.Model):
    """
    Security Incident Log (ISO 28000 compliance)
    Records actual security events that occurred during shipment
    """
    
    SEVERITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical'))
    ]
    
    INCIDENT_TYPE_CHOICES = [
        ('theft', _('Theft')),
        ('damage', _('Damage/Vandalism')),
        ('tampering', _('Tampering/Seal Breach')),
        ('unauthorized_access', _('Unauthorized Access')),
        ('hijacking', _('Hijacking')),
        ('fraud', _('Documentation Fraud')),
        ('cyber_attack', _('Cyber Attack')),
        ('personnel', _('Personnel Incident')),
        ('natural_disaster', _('Natural Disaster')),
        ('other', _('Other'))
    ]
    
    STATUS_CHOICES = [
        ('reported', _('Reported')),
        ('investigating', _('Investigating')),
        ('contained', _('Contained')),
        ('resolved', _('Resolved')),
        ('escalated', _('Escalated'))
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='security_incidents',
        verbose_name=_('Shipment')
    )
    
    incident_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Incident ID')
    )
    
    incident_type = models.CharField(
        max_length=25,
        choices=INCIDENT_TYPE_CHOICES,
        verbose_name=_('Incident Type')
    )
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='medium',
        verbose_name=_('Severity')
    )
    
    occurred_at = models.DateTimeField(
        verbose_name=_('Occurred At'),
        help_text=_('When the incident occurred')
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name=_('Location'),
        help_text=_('Where the incident occurred')
    )
    
    description = models.TextField(
        verbose_name=_('Incident Description'),
        help_text=_('Detailed description of what happened')
    )
    
    impact_assessment = models.TextField(
        blank=True,
        verbose_name=_('Impact Assessment'),
        help_text=_('Assessment of damage, loss, or impact')
    )
    
    financial_loss = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Estimated Financial Loss'),
        help_text=_('CAD amount')
    )
    
    response_actions = models.TextField(
        blank=True,
        verbose_name=_('Response Actions'),
        help_text=_('Immediate actions taken in response')
    )
    
    root_cause = models.TextField(
        blank=True,
        verbose_name=_('Root Cause Analysis'),
        help_text=_('Analysis of underlying cause')
    )
    
    corrective_actions = models.TextField(
        blank=True,
        verbose_name=_('Corrective Actions'),
        help_text=_('Actions to prevent recurrence')
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='reported',
        verbose_name=_('Status')
    )
    
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_incidents',
        verbose_name=_('Reported By')
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        verbose_name=_('Assigned To')
    )
    
    reported_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Reported Date')
    )
    
    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolution Date')
    )
    
    authorities_notified = models.BooleanField(
        default=False,
        verbose_name=_('Authorities Notified')
    )
    
    insurance_claimed = models.BooleanField(
        default=False,
        verbose_name=_('Insurance Claimed')
    )
    
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Attachments'),
        help_text=_('List of evidence files (photos, reports, etc.)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_incidents'
        verbose_name = _('Security Incident')
        verbose_name_plural = _('Security Incidents')
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['shipment', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['occurred_at']),
        ]
    
    def __str__(self):
        return f"{self.incident_id} - {self.get_incident_type_display()} ({self.severity})"  # type: ignore[attr-defined]


class PortVerification(models.Model):
    """
    Port Security Verification (ISO 28000 compliance)
    Tracks security certifications and verifications for ports
    """
    
    CERTIFICATION_TYPE_CHOICES = [
        ('isps', _('ISPS Code (International Ship and Port Facility Security)')),
        ('c-tpat', _('C-TPAT (Customs-Trade Partnership Against Terrorism)')),
        ('aeo', _('AEO (Authorized Economic Operator)')),
        ('iso_28000', _('ISO 28000 Certification')),
        ('customs', _('Customs Security Clearance')),
        ('other', _('Other Security Certification'))
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('pending_renewal', _('Pending Renewal')),
        ('revoked', _('Revoked'))
    ]
    
    port_name = models.CharField(
        max_length=255,
        verbose_name=_('Port Name')
    )
    
    port_code = models.CharField(
        max_length=10,
        verbose_name=_('Port Code (UN/LOCODE)'),
        help_text=_('e.g., CAVAN (Vancouver), USNYC (New York)')
    )
    
    country = models.CharField(
        max_length=100,
        verbose_name=_('Country')
    )
    
    certification_type = models.CharField(
        max_length=20,
        choices=CERTIFICATION_TYPE_CHOICES,
        verbose_name=_('Certification Type')
    )
    
    certification_number = models.CharField(
        max_length=100,
        verbose_name=_('Certification Number')
    )
    
    certifying_authority = models.CharField(
        max_length=255,
        verbose_name=_('Certifying Authority')
    )
    
    issue_date = models.DateField(
        verbose_name=_('Issue Date')
    )
    
    expiry_date = models.DateField(
        verbose_name=_('Expiry Date')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    
    security_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name=_('Security Level'),
        help_text=_('ISPS security level: 1=normal, 2=heightened, 3=exceptional')
    )
    
    security_measures = models.TextField(
        verbose_name=_('Security Measures'),
        help_text=_('Description of security protocols in place')
    )
    
    last_inspection_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last Inspection Date')
    )
    
    next_inspection_due = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Next Inspection Due')
    )
    
    compliance_notes = models.TextField(
        blank=True,
        verbose_name=_('Compliance Notes')
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verified_ports',
        verbose_name=_('Verified By')
    )
    
    verification_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Verification Date')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'port_verifications'
        verbose_name = _('Port Verification')
        verbose_name_plural = _('Port Verifications')
        ordering = ['-expiry_date', 'port_name']
        indexes = [
            models.Index(fields=['port_code', 'certification_type']),
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['country']),
        ]
        unique_together = ['port_code', 'certification_type', 'certification_number']
    
    def __str__(self):
        return f"{self.port_name} ({self.port_code}) - {self.get_certification_type_display()}"  # type: ignore[attr-defined]
    
    @property
    def is_expired(self):
        """Check if certification is expired"""
        from django.utils import timezone
        return timezone.now().date() > self.expiry_date
    
    @property
    def days_until_expiry(self):
        """Calculate days remaining until expiry"""
        from django.utils import timezone
        delta = self.expiry_date - timezone.now().date()
        return delta.days
