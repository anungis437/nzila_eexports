from django.db import models
from django.utils.translation import gettext_lazy as _
from vehicles.models import Vehicle


class VehicleHistoryReport(models.Model):
    """
    Comprehensive vehicle history report (Carfax/AutoCheck style)
    Stores accident history, service records, title status, and ownership history
    """
    
    TITLE_STATUS_CHOICES = [
        ('clean', _('Clean Title')),
        ('salvage', _('Salvage')),
        ('rebuilt', _('Rebuilt')),
        ('flood', _('Flood Damage')),
        ('hail', _('Hail Damage')),
        ('lemon', _('Lemon Law Buyback')),
        ('junk', _('Junk')),
    ]
    
    ACCIDENT_SEVERITY_CHOICES = [
        ('none', _('No Accidents')),
        ('minor', _('Minor Damage')),
        ('moderate', _('Moderate Damage')),
        ('severe', _('Severe Damage')),
        ('total_loss', _('Total Loss')),
    ]
    
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='history_report',
        verbose_name=_('Vehicle')
    )
    
    # Title Information
    title_status = models.CharField(
        max_length=20,
        choices=TITLE_STATUS_CHOICES,
        default='clean',
        verbose_name=_('Title Status')
    )
    title_issue_date = models.DateField(null=True, blank=True, verbose_name=_('Title Issue Date'))
    title_state = models.CharField(max_length=50, blank=True, verbose_name=_('Title State/Province'))
    
    # Accident History
    accident_severity = models.CharField(
        max_length=20,
        choices=ACCIDENT_SEVERITY_CHOICES,
        default='none',
        verbose_name=_('Accident Severity')
    )
    total_accidents = models.PositiveIntegerField(default=0, verbose_name=_('Total Accidents'))
    last_accident_date = models.DateField(null=True, blank=True, verbose_name=_('Last Accident Date'))
    
    # Ownership History
    total_owners = models.PositiveIntegerField(default=1, verbose_name=_('Total Owners'))
    personal_use = models.BooleanField(default=True, verbose_name=_('Personal Use'))
    rental_use = models.BooleanField(default=False, verbose_name=_('Rental/Fleet Use'))
    taxi_use = models.BooleanField(default=False, verbose_name=_('Taxi/Rideshare Use'))
    police_use = models.BooleanField(default=False, verbose_name=_('Police/Government Use'))
    
    # Odometer
    odometer_rollback = models.BooleanField(default=False, verbose_name=_('Odometer Rollback Detected'))
    odometer_verified = models.BooleanField(default=True, verbose_name=_('Odometer Verified'))
    last_odometer_reading = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Last Reading'))
    last_odometer_date = models.DateField(null=True, blank=True, verbose_name=_('Last Reading Date'))
    
    # Service History
    total_service_records = models.PositiveIntegerField(default=0, verbose_name=_('Total Service Records'))
    last_service_date = models.DateField(null=True, blank=True, verbose_name=_('Last Service Date'))
    recalls_outstanding = models.PositiveIntegerField(default=0, verbose_name=_('Outstanding Recalls'))
    
    # Damage History
    structural_damage = models.BooleanField(default=False, verbose_name=_('Structural Damage'))
    frame_damage = models.BooleanField(default=False, verbose_name=_('Frame Damage'))
    airbag_deployment = models.BooleanField(default=False, verbose_name=_('Airbag Deployment'))
    
    # Report Metadata
    report_generated_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Report Generated'))
    report_updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Report Updated'))
    report_source = models.CharField(
        max_length=50,
        default='manual',
        verbose_name=_('Report Source'),
        help_text=_('Source of the report: manual, carfax, autocheck, etc.')
    )
    report_confidence = models.CharField(
        max_length=20,
        choices=[
            ('high', _('High Confidence')),
            ('medium', _('Medium Confidence')),
            ('low', _('Low Confidence')),
        ],
        default='high',
        verbose_name=_('Report Confidence')
    )
    
    # Additional Notes
    notes = models.TextField(blank=True, verbose_name=_('Additional Notes'))
    
    class Meta:
        verbose_name = _('Vehicle History Report')
        verbose_name_plural = _('Vehicle History Reports')
        ordering = ['-report_updated_at']
        indexes = [
            models.Index(fields=['vehicle']),
            models.Index(fields=['title_status']),
            models.Index(fields=['accident_severity']),
        ]
    
    def __str__(self):
        return f"History Report - {self.vehicle.vin}"
    
    @property
    def is_clean_title(self):
        """Check if vehicle has clean title"""
        return self.title_status == 'clean'
    
    @property
    def has_accidents(self):
        """Check if vehicle has accident history"""
        return self.total_accidents > 0
    
    @property
    def is_one_owner(self):
        """Check if vehicle has single owner"""
        return self.total_owners == 1
    
    @property
    def has_commercial_use(self):
        """Check if vehicle was used commercially"""
        return self.rental_use or self.taxi_use or self.police_use
    
    @property
    def trust_score(self):
        """Calculate trust score (0-100) based on history"""
        score = 100
        
        # Title status penalties
        if self.title_status == 'salvage':
            score -= 40
        elif self.title_status in ['rebuilt', 'flood', 'hail']:
            score -= 30
        elif self.title_status == 'lemon':
            score -= 50
        
        # Accident penalties
        if self.accident_severity == 'severe':
            score -= 25
        elif self.accident_severity == 'moderate':
            score -= 15
        elif self.accident_severity == 'minor':
            score -= 5
        
        # Odometer issues
        if self.odometer_rollback:
            score -= 30
        elif not self.odometer_verified:
            score -= 10
        
        # Ownership penalties
        if self.total_owners > 5:
            score -= 15
        elif self.total_owners > 3:
            score -= 10
        
        # Commercial use
        if self.taxi_use:
            score -= 20
        elif self.rental_use:
            score -= 10
        
        # Damage penalties
        if self.structural_damage or self.frame_damage:
            score -= 20
        if self.airbag_deployment:
            score -= 10
        
        # Recalls
        if self.recalls_outstanding > 0:
            score -= 5 * self.recalls_outstanding
        
        return max(0, min(100, score))


class AccidentRecord(models.Model):
    """
    Individual accident record with details
    """
    
    DAMAGE_SEVERITY_CHOICES = [
        ('minor', _('Minor')),
        ('moderate', _('Moderate')),
        ('severe', _('Severe')),
    ]
    
    history_report = models.ForeignKey(
        VehicleHistoryReport,
        on_delete=models.CASCADE,
        related_name='accident_records',
        verbose_name=_('History Report')
    )
    
    accident_date = models.DateField(verbose_name=_('Accident Date'))
    damage_severity = models.CharField(
        max_length=20,
        choices=DAMAGE_SEVERITY_CHOICES,
        verbose_name=_('Damage Severity')
    )
    
    # Damage Details
    front_damage = models.BooleanField(default=False, verbose_name=_('Front Damage'))
    rear_damage = models.BooleanField(default=False, verbose_name=_('Rear Damage'))
    left_side_damage = models.BooleanField(default=False, verbose_name=_('Left Side Damage'))
    right_side_damage = models.BooleanField(default=False, verbose_name=_('Right Side Damage'))
    roof_damage = models.BooleanField(default=False, verbose_name=_('Roof Damage'))
    undercarriage_damage = models.BooleanField(default=False, verbose_name=_('Undercarriage Damage'))
    
    # Repair Information
    repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Repair Cost')
    )
    repair_facility = models.CharField(max_length=200, blank=True, verbose_name=_('Repair Facility'))
    repair_completed = models.BooleanField(default=True, verbose_name=_('Repair Completed'))
    
    # Insurance
    insurance_claim = models.BooleanField(default=False, verbose_name=_('Insurance Claim Filed'))
    
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Accident Record')
        verbose_name_plural = _('Accident Records')
        ordering = ['-accident_date']
        indexes = [
            models.Index(fields=['history_report', 'accident_date']),
        ]
    
    def __str__(self):
        return f"{self.damage_severity.title()} - {self.accident_date}"


class ServiceRecord(models.Model):
    """
    Service and maintenance records
    """
    
    SERVICE_TYPE_CHOICES = [
        ('oil_change', _('Oil Change')),
        ('tire_rotation', _('Tire Rotation')),
        ('brake_service', _('Brake Service')),
        ('transmission_service', _('Transmission Service')),
        ('engine_repair', _('Engine Repair')),
        ('inspection', _('Inspection')),
        ('recall', _('Recall Repair')),
        ('other', _('Other')),
    ]
    
    history_report = models.ForeignKey(
        VehicleHistoryReport,
        on_delete=models.CASCADE,
        related_name='service_records',
        verbose_name=_('History Report')
    )
    
    service_date = models.DateField(verbose_name=_('Service Date'))
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES,
        verbose_name=_('Service Type')
    )
    
    odometer_reading = models.PositiveIntegerField(verbose_name=_('Odometer at Service'))
    service_facility = models.CharField(max_length=200, blank=True, verbose_name=_('Service Facility'))
    service_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Service Cost')
    )
    
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Service Record')
        verbose_name_plural = _('Service Records')
        ordering = ['-service_date']
        indexes = [
            models.Index(fields=['history_report', 'service_date']),
        ]
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.service_date}"


class OwnershipRecord(models.Model):
    """
    Ownership history timeline
    """
    
    history_report = models.ForeignKey(
        VehicleHistoryReport,
        on_delete=models.CASCADE,
        related_name='ownership_records',
        verbose_name=_('History Report')
    )
    
    owner_number = models.PositiveIntegerField(verbose_name=_('Owner Number'))
    ownership_start = models.DateField(verbose_name=_('Ownership Start'))
    ownership_end = models.DateField(null=True, blank=True, verbose_name=_('Ownership End'))
    
    state_province = models.CharField(max_length=50, blank=True, verbose_name=_('State/Province'))
    ownership_type = models.CharField(
        max_length=50,
        choices=[
            ('personal', _('Personal')),
            ('lease', _('Lease')),
            ('rental', _('Rental/Fleet')),
            ('commercial', _('Commercial')),
            ('government', _('Government')),
        ],
        default='personal',
        verbose_name=_('Ownership Type')
    )
    
    estimated_annual_miles = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Annual Miles/KM')
    )
    
    class Meta:
        verbose_name = _('Ownership Record')
        verbose_name_plural = _('Ownership Records')
        ordering = ['owner_number']
        indexes = [
            models.Index(fields=['history_report', 'owner_number']),
        ]
    
    def __str__(self):
        return f"Owner #{self.owner_number} - {self.ownership_start}"
