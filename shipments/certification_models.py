"""
ISO 28000 Security Management and ISO 18602 Compliance Models
Supporting world-class marine cargo certification
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class SecurityRiskAssessment(models.Model):
    """
    ISO 28000 Requirement: Pre-shipment security risk assessment
    
    Every shipment must undergo risk assessment before departure
    Documents: route analysis, value assessment, destination security, insurance requirements
    """
    
    RISK_FACTORS = [
        ('route', _('Route Risk - Piracy, Political Instability')),
        ('value', _('High Value Target')),
        ('destination', _('Destination Country Security')),
        ('cargo_type', _('Cargo Type Risk')),
        ('customs', _('Customs Complexity')),
        ('port_security', _('Port Security Level')),
    ]
    
    shipment = models.OneToOneField(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='risk_assessment',
        verbose_name=_('Shipment')
    )
    
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='risk_assessments_conducted',
        verbose_name=_('Assessed By')
    )
    
    assessment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Assessment Date')
    )
    
    # Overall Risk Rating
    overall_risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Low Risk (0-30 points)')),
            ('medium', _('Medium Risk (31-60 points)')),
            ('high', _('High Risk (61-85 points)')),
            ('critical', _('Critical Risk (86-100 points)')),
        ],
        verbose_name=_('Overall Risk Level')
    )
    
    risk_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Calculated risk score: 0-100'),
        verbose_name=_('Risk Score')
    )
    
    # Individual Risk Factor Scores (0-10 each)
    route_risk_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_('Piracy zones, political instability, weather patterns'),
        verbose_name=_('Route Risk Score')
    )
    
    value_risk_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_('Vehicle value creates theft/fraud risk'),
        verbose_name=_('Value Risk Score')
    )
    
    destination_risk_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_('Destination country security and corruption levels'),
        verbose_name=_('Destination Risk Score')
    )
    
    customs_risk_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_('Customs complexity and documentation requirements'),
        verbose_name=_('Customs Risk Score')
    )
    
    port_security_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_('Security level at origin and destination ports'),
        verbose_name=_('Port Security Score')
    )
    
    # Risk Mitigation Measures
    mitigation_measures = models.TextField(
        help_text=_('Security measures to be implemented'),
        verbose_name=_('Mitigation Measures')
    )
    
    insurance_required = models.BooleanField(
        default=True,
        verbose_name=_('Insurance Required')
    )
    
    recommended_insurance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_('Recommended insurance coverage in CAD'),
        verbose_name=_('Recommended Insurance (CAD)')
    )
    
    lloyd_register_recommended = models.BooleanField(
        default=False,
        help_text=_('True if LR monitoring is recommended based on risk level'),
        verbose_name=_('LR Monitoring Recommended')
    )
    
    approved = models.BooleanField(
        default=False,
        verbose_name=_('Assessment Approved')
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_assessments_approved',
        verbose_name=_('Approved By')
    )
    
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approval Date')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Assessment Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Security Risk Assessment')
        verbose_name_plural = _('Security Risk Assessments')
        ordering = ['-assessment_date']
    
    def __str__(self):
        return f"Risk Assessment: {self.shipment.tracking_number} - {self.overall_risk_level}"
    
    def calculate_risk_score(self):
        """Calculate overall risk score from individual factors"""
        self.risk_score = (
            self.route_risk_score * 10 +
            self.value_risk_score * 10 +
            self.destination_risk_score * 10 +
            self.customs_risk_score * 10 +
            self.port_security_score * 10
        )
        
        # Determine overall risk level
        if self.risk_score <= 30:
            self.overall_risk_level = 'low'
        elif self.risk_score <= 60:
            self.overall_risk_level = 'medium'
        elif self.risk_score <= 85:
            self.overall_risk_level = 'high'
        else:
            self.overall_risk_level = 'critical'
        
        return self.risk_score


class SecurityIncident(models.Model):
    """
    ISO 28000 Requirement: Incident tracking and response
    
    All security incidents must be documented with corrective actions
    """
    
    INCIDENT_TYPES = [
        ('delay', _('Unexpected Delay')),
        ('damage', _('Vehicle Damage')),
        ('theft', _('Theft or Attempted Theft')),
        ('accident', _('Transportation Accident')),
        ('customs', _('Customs Issue')),
        ('seal_breach', _('Container Seal Breached')),
        ('gps_failure', _('GPS Tracking Failure')),
        ('documentation', _('Documentation Discrepancy')),
        ('weather', _('Weather-Related Incident')),
        ('port_security', _('Port Security Issue')),
        ('other', _('Other Incident')),
    ]
    
    SEVERITY_LEVELS = [
        ('minor', _('Minor - No impact on delivery')),
        ('moderate', _('Moderate - Minor delay or cosmetic damage')),
        ('severe', _('Severe - Significant delay or damage')),
        ('critical', _('Critical - Major security breach or total loss')),
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='security_incidents',
        verbose_name=_('Shipment')
    )
    
    incident_type = models.CharField(
        max_length=30,
        choices=INCIDENT_TYPES,
        verbose_name=_('Incident Type')
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        verbose_name=_('Severity Level')
    )
    
    incident_date = models.DateTimeField(
        verbose_name=_('Incident Date/Time')
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name=_('Incident Location')
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name=_('Latitude')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name=_('Longitude')
    )
    
    description = models.TextField(
        verbose_name=_('Incident Description')
    )
    
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidents_reported',
        verbose_name=_('Reported By')
    )
    
    reported_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Reported Date')
    )
    
    # Authorities Notification
    police_report_filed = models.BooleanField(
        default=False,
        verbose_name=_('Police Report Filed')
    )
    
    police_report_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Police Report Number')
    )
    
    insurance_claim_filed = models.BooleanField(
        default=False,
        verbose_name=_('Insurance Claim Filed')
    )
    
    insurance_claim_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Insurance Claim Number')
    )
    
    lloyd_register_notified = models.BooleanField(
        default=False,
        verbose_name=_('Lloyd\'s Register Notified')
    )
    
    # Response and Resolution
    immediate_action_taken = models.TextField(
        blank=True,
        help_text=_('Immediate actions taken to address the incident'),
        verbose_name=_('Immediate Action Taken')
    )
    
    corrective_measures = models.TextField(
        blank=True,
        help_text=_('Long-term corrective measures to prevent recurrence'),
        verbose_name=_('Corrective Measures')
    )
    
    resolved = models.BooleanField(
        default=False,
        verbose_name=_('Incident Resolved')
    )
    
    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolution Date')
    )
    
    resolution_notes = models.TextField(
        blank=True,
        verbose_name=_('Resolution Notes')
    )
    
    # Financial Impact
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Estimated cost in CAD (delays, repairs, etc)'),
        verbose_name=_('Estimated Cost (CAD)')
    )
    
    # Attachments (photos, documents)
    evidence_photos = models.TextField(
        blank=True,
        help_text=_('Links to ShipmentPhoto objects serving as evidence'),
        verbose_name=_('Evidence Photo IDs')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Security Incident')
        verbose_name_plural = _('Security Incidents')
        ordering = ['-incident_date']
        indexes = [
            models.Index(fields=['shipment', '-incident_date']),
            models.Index(fields=['severity', 'resolved']),
        ]
    
    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.shipment.tracking_number} - {self.severity}"


class PortVerification(models.Model):
    """
    ISO 18602 Requirement: Port-based verification records
    
    Documents vehicle condition and container seal status at ports
    """
    
    VERIFICATION_TYPES = [
        ('origin_departure', _('Origin Port - Pre-Departure')),
        ('transit_port', _('Transit Port')),
        ('destination_arrival', _('Destination Port - Arrival')),
        ('destination_release', _('Destination Port - Released to Buyer')),
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='port_verifications',
        verbose_name=_('Shipment')
    )
    
    verification_type = models.CharField(
        max_length=30,
        choices=VERIFICATION_TYPES,
        verbose_name=_('Verification Type')
    )
    
    verification_date = models.DateTimeField(
        verbose_name=_('Verification Date/Time')
    )
    
    port_name = models.CharField(
        max_length=255,
        verbose_name=_('Port Name')
    )
    
    port_country = models.CharField(
        max_length=100,
        verbose_name=_('Port Country')
    )
    
    # Verifier Information
    verified_by_name = models.CharField(
        max_length=255,
        help_text=_('Name of port official, customs officer, or LR surveyor'),
        verbose_name=_('Verified By Name')
    )
    
    verifier_organization = models.CharField(
        max_length=255,
        help_text=_('Port authority, customs, Lloyd\'s Register, etc'),
        verbose_name=_('Verifier Organization')
    )
    
    verifier_credentials = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('License number, badge number, surveyor certification'),
        verbose_name=_('Verifier Credentials')
    )
    
    # Container Seal Verification
    seal_number_verified = models.CharField(
        max_length=50,
        help_text=_('Seal number as observed'),
        verbose_name=_('Seal Number Verified')
    )
    
    seal_intact = models.BooleanField(
        default=True,
        verbose_name=_('Seal Intact')
    )
    
    seal_condition_notes = models.TextField(
        blank=True,
        verbose_name=_('Seal Condition Notes')
    )
    
    # Vehicle Condition
    vehicle_condition_status = models.CharField(
        max_length=20,
        choices=[
            ('excellent', _('Excellent - As Described')),
            ('good', _('Good - Minor Variations')),
            ('fair', _('Fair - Notable Differences')),
            ('poor', _('Poor - Significant Damage')),
        ],
        verbose_name=_('Vehicle Condition Status')
    )
    
    odometer_reading = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Odometer reading at inspection (km)'),
        verbose_name=_('Odometer Reading (km)')
    )
    
    vehicle_condition_notes = models.TextField(
        blank=True,
        verbose_name=_('Vehicle Condition Notes')
    )
    
    # Documentation Status
    documents_complete = models.BooleanField(
        default=True,
        help_text=_('All required documents present and correct'),
        verbose_name=_('Documents Complete')
    )
    
    missing_documents = models.TextField(
        blank=True,
        verbose_name=_('Missing or Incomplete Documents')
    )
    
    # Photos Taken
    photos_taken_count = models.IntegerField(
        default=0,
        help_text=_('Number of photos taken during inspection'),
        verbose_name=_('Photos Taken')
    )
    
    photo_ids = models.TextField(
        blank=True,
        help_text=_('Comma-separated ShipmentPhoto IDs'),
        verbose_name=_('Photo IDs')
    )
    
    # Customs Clearance (if applicable)
    customs_cleared = models.BooleanField(
        default=False,
        verbose_name=_('Customs Cleared')
    )
    
    customs_clearance_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Customs Clearance Date')
    )
    
    customs_reference_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Customs Reference Number')
    )
    
    # Verification Outcome
    verification_passed = models.BooleanField(
        default=True,
        help_text=_('True if verification passed without issues'),
        verbose_name=_('Verification Passed')
    )
    
    issues_identified = models.TextField(
        blank=True,
        help_text=_('Any discrepancies or issues found'),
        verbose_name=_('Issues Identified')
    )
    
    # Digital Signature
    digital_signature = models.TextField(
        blank=True,
        help_text=_('Digital signature or verification code'),
        verbose_name=_('Digital Signature')
    )
    
    verification_certificate_url = models.URLField(
        blank=True,
        help_text=_('URL to downloadable verification certificate'),
        verbose_name=_('Verification Certificate URL')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Port Verification')
        verbose_name_plural = _('Port Verifications')
        ordering = ['-verification_date']
        indexes = [
            models.Index(fields=['shipment', '-verification_date']),
            models.Index(fields=['port_name', 'verification_type']),
        ]
    
    def __str__(self):
        return f"{self.get_verification_type_display()} - {self.shipment.tracking_number} - {self.port_name}"


class ISO28000AuditLog(models.Model):
    """
    ISO 28000 Requirement: Comprehensive audit trail
    
    All security-related activities must be logged for auditors
    """
    
    ACTION_TYPES = [
        ('risk_assessment', _('Security Risk Assessment')),
        ('incident_report', _('Security Incident Reported')),
        ('seal_applied', _('Container Seal Applied')),
        ('seal_verified', _('Container Seal Verified')),
        ('lr_registered', _('Lloyd\'s Register CTS Registered')),
        ('lr_inspection', _('LR Surveyor Inspection')),
        ('port_verification', _('Port Verification')),
        ('insurance_updated', _('Insurance Information Updated')),
        ('customs_cleared', _('Customs Clearance')),
        ('security_measure', _('Security Measure Implemented')),
        ('document_upload', _('Security Document Uploaded')),
        ('access_granted', _('Security Access Granted')),
        ('system_alert', _('Security System Alert')),
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name=_('Shipment')
    )
    
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        verbose_name=_('Action Type')
    )
    
    action_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Action Timestamp')
    )
    
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Performed By')
    )
    
    performed_by_name = models.CharField(
        max_length=255,
        help_text=_('Name of person or system (if not a user account)'),
        verbose_name=_('Performed By Name')
    )
    
    action_description = models.TextField(
        verbose_name=_('Action Description')
    )
    
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('SecurityIncident, PortVerification, etc'),
        verbose_name=_('Related Object Type')
    )
    
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Related Object ID')
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Address')
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    
    # ISO 28000 requires immutable audit logs
    is_immutable = models.BooleanField(
        default=True,
        help_text=_('Audit logs cannot be modified after creation'),
        verbose_name=_('Immutable')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('ISO 28000 Audit Log')
        verbose_name_plural = _('ISO 28000 Audit Logs')
        ordering = ['-action_timestamp']
        indexes = [
            models.Index(fields=['shipment', '-action_timestamp']),
            models.Index(fields=['action_type', '-action_timestamp']),
            models.Index(fields=['performed_by', '-action_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.shipment.tracking_number} - {self.action_timestamp}"
    
    def save(self, *args, **kwargs):
        # ISO 28000: Audit logs are immutable - prevent updates
        if self.pk and self.is_immutable:
            raise ValueError("Audit logs cannot be modified (ISO 28000 requirement)")
        super().save(*args, **kwargs)
