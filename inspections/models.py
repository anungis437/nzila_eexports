"""
PHASE 2 - Feature 6: Third-Party Inspection Integration

Models for third-party vehicle inspectors, inspection reports, and reviews.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from decimal import Decimal


class ThirdPartyInspector(models.Model):
    """
    Third-party vehicle inspection providers across Canada
    
    Tracks inspector profiles, certifications, ratings, and locations
    for diaspora buyers to book independent pre-purchase inspections.
    """
    
    CERTIFICATION_CHOICES = [
        ('ase', _('ASE Certified')),
        ('ari', _('ARI Certified')),
        ('red_seal', _('Red Seal Technician')),
        ('provincially_licensed', _('Provincially Licensed')),
        ('caa_approved', _('CAA Approved')),
        ('manufacturer_certified', _('Manufacturer Certified')),
        ('independent', _('Independent Inspector')),
    ]
    
    PROVINCE_CHOICES = [
        ('ON', _('Ontario')),
        ('QC', _('Quebec')),
        ('BC', _('British Columbia')),
        ('AB', _('Alberta')),
        ('MB', _('Manitoba')),
        ('SK', _('Saskatchewan')),
        ('NS', _('Nova Scotia')),
        ('NB', _('New Brunswick')),
        ('NL', _('Newfoundland and Labrador')),
        ('PE', _('Prince Edward Island')),
        ('YT', _('Yukon')),
        ('NT', _('Northwest Territories')),
        ('NU', _('Nunavut')),
    ]
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        verbose_name=_('Inspector Name'),
        help_text=_('Full name of the inspector or primary contact')
    )
    company = models.CharField(
        max_length=200,
        verbose_name=_('Company Name'),
        help_text=_('Business or company name')
    )
    
    # Location
    city = models.CharField(
        max_length=100,
        verbose_name=_('City')
    )
    province = models.CharField(
        max_length=2,
        choices=PROVINCE_CHOICES,
        verbose_name=_('Province')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Street Address')
    )
    postal_code = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_('Postal Code')
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Latitude'),
        help_text=_('Geographic latitude for proximity search')
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Longitude'),
        help_text=_('Geographic longitude for proximity search')
    )
    
    # Contact Information
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Phone Number')
    )
    email = models.EmailField(
        verbose_name=_('Email Address')
    )
    website = models.URLField(
        blank=True,
        verbose_name=_('Website'),
        help_text=_('Inspector or company website')
    )
    
    # Qualifications
    certifications = models.CharField(
        max_length=50,
        choices=CERTIFICATION_CHOICES,
        default='independent',
        verbose_name=_('Primary Certification'),
        help_text=_('Main certification or accreditation')
    )
    additional_certifications = models.TextField(
        blank=True,
        verbose_name=_('Additional Certifications'),
        help_text=_('Other certifications, comma-separated')
    )
    years_experience = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Years of Experience'),
        help_text=_('Years in vehicle inspection business')
    )
    specializations = models.TextField(
        blank=True,
        verbose_name=_('Specializations'),
        help_text=_('e.g., "Luxury vehicles, Electric vehicles, Classic cars"')
    )
    
    # Services
    mobile_service = models.BooleanField(
        default=False,
        verbose_name=_('Mobile Service Available'),
        help_text=_('Inspector will travel to vehicle location')
    )
    service_radius_km = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0)],
        verbose_name=_('Service Radius (km)'),
        help_text=_('Maximum distance for mobile inspections')
    )
    
    # Pricing
    inspection_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Standard Inspection Fee (CAD)'),
        help_text=_('Base fee for standard pre-purchase inspection')
    )
    mobile_fee_extra = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Mobile Service Extra Fee (CAD)'),
        help_text=_('Additional charge for mobile inspections')
    )
    
    # Ratings & Statistics
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
        verbose_name=_('Average Rating'),
        help_text=_('Calculated from reviews (0.00 - 5.00)')
    )
    total_inspections = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Inspections'),
        help_text=_('Number of inspections completed through platform')
    )
    total_reviews = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Reviews'),
        help_text=_('Number of reviews received')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Inspector is currently accepting bookings')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified'),
        help_text=_('Inspector credentials verified by platform')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Third-Party Inspector')
        verbose_name_plural = _('Third-Party Inspectors')
        ordering = ['-rating', '-total_inspections', 'company']
        indexes = [
            models.Index(fields=['province', 'city']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['-rating', '-total_inspections']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.company} - {self.city}, {self.province}"
    
    def update_rating(self):
        """Recalculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = Decimal(str(round(avg_rating, 2)))
            self.total_reviews = reviews.count()
            self.save(update_fields=['rating', 'total_reviews'])
    
    def get_certification_display_list(self):
        """Get all certifications as a list"""
        certs = [self.get_certifications_display()]
        if self.additional_certifications:
            certs.extend([c.strip() for c in self.additional_certifications.split(',')])
        return certs


class InspectionReport(models.Model):
    """
    Vehicle inspection reports from third-party inspectors
    
    Stores inspection findings, uploaded reports, and overall vehicle condition
    assessments for diaspora buyers considering remote vehicle purchases.
    """
    
    REPORT_TYPE_CHOICES = [
        ('pre_purchase', _('Pre-Purchase Inspection')),
        ('comprehensive', _('Comprehensive Inspection')),
        ('mechanical', _('Mechanical Only')),
        ('body_frame', _('Body & Frame Only')),
        ('electrical', _('Electrical Systems')),
        ('safety', _('Safety Inspection')),
        ('emissions', _('Emissions Test')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', _('Excellent - No issues found')),
        ('good', _('Good - Minor cosmetic issues only')),
        ('fair', _('Fair - Some repairs recommended')),
        ('poor', _('Poor - Major repairs required')),
        ('not_recommended', _('Not Recommended - Serious safety concerns')),
    ]
    
    # Relationships
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='inspection_reports',
        verbose_name=_('Vehicle')
    )
    inspector = models.ForeignKey(
        ThirdPartyInspector,
        on_delete=models.CASCADE,
        related_name='inspections',
        verbose_name=_('Inspector')
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_inspections',
        verbose_name=_('Requesting Buyer'),
        help_text=_('Buyer who requested the inspection')
    )
    
    # Inspection Details
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        default='pre_purchase',
        verbose_name=_('Report Type')
    )
    inspection_date = models.DateField(
        verbose_name=_('Inspection Date'),
        help_text=_('Date inspection was performed')
    )
    
    # Report File
    report_file = models.FileField(
        upload_to='inspection_reports/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])],
        verbose_name=_('Report File'),
        help_text=_('Uploaded inspection report (PDF, DOC, or images)')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('Status')
    )
    
    # Findings
    overall_condition = models.CharField(
        max_length=30,
        choices=CONDITION_CHOICES,
        blank=True,
        verbose_name=_('Overall Condition Assessment')
    )
    issues_found = models.TextField(
        blank=True,
        verbose_name=_('Issues Found'),
        help_text=_('List of issues discovered during inspection')
    )
    recommendations = models.TextField(
        blank=True,
        verbose_name=_('Inspector Recommendations'),
        help_text=_('Recommended repairs or actions')
    )
    estimated_repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Estimated Repair Cost (CAD)'),
        help_text=_('Inspector\'s estimate for recommended repairs')
    )
    
    # Inspection Scores (0-10)
    engine_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Engine Score'),
        help_text=_('0-10 rating for engine condition')
    )
    transmission_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Transmission Score')
    )
    suspension_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Suspension Score')
    )
    brakes_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Brakes Score')
    )
    body_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Body Score')
    )
    interior_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Interior Score')
    )
    
    # Payment
    inspection_fee_paid = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Inspection Fee Paid (CAD)'),
        help_text=_('Amount paid for this inspection')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('paid', _('Paid')),
            ('refunded', _('Refunded')),
        ],
        default='pending',
        verbose_name=_('Payment Status')
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        verbose_name=_('Additional Notes'),
        help_text=_('Any additional information or special circumstances')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Inspection Report')
        verbose_name_plural = _('Inspection Reports')
        ordering = ['-inspection_date', '-created_at']
        indexes = [
            models.Index(fields=['vehicle', 'status']),
            models.Index(fields=['inspector', 'status']),
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['-inspection_date']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.vehicle} by {self.inspector.company}"
    
    def get_average_score(self):
        """Calculate average of all component scores"""
        scores = [
            self.engine_score,
            self.transmission_score,
            self.suspension_score,
            self.brakes_score,
            self.body_score,
            self.interior_score,
        ]
        valid_scores = [s for s in scores if s is not None]
        if not valid_scores:
            return None
        return round(sum(valid_scores) / len(valid_scores), 1)
    
    def mark_completed(self):
        """Mark inspection as completed and update inspector stats"""
        if self.status != 'completed':
            self.status = 'completed'
            self.save(update_fields=['status'])
            # Increment inspector's total inspections
            self.inspector.total_inspections += 1
            self.inspector.save(update_fields=['total_inspections'])


class InspectorReview(models.Model):
    """
    Reviews and ratings for third-party inspectors
    
    Allows buyers to rate inspectors and provide feedback after inspections,
    helping other diaspora buyers make informed decisions.
    """
    
    # Relationships
    inspector = models.ForeignKey(
        ThirdPartyInspector,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Inspector')
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inspector_reviews',
        verbose_name=_('Reviewer')
    )
    inspection_report = models.OneToOneField(
        InspectionReport,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_('Related Inspection'),
        help_text=_('Inspection this review is based on')
    )
    
    # Rating & Review
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating'),
        help_text=_('1-5 stars rating')
    )
    review_text = models.TextField(
        verbose_name=_('Review'),
        help_text=_('Detailed review of the inspection experience')
    )
    
    # Detailed Ratings (optional 1-5 stars each)
    professionalism_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Professionalism'),
        help_text=_('Inspector\'s professional conduct')
    )
    thoroughness_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Thoroughness'),
        help_text=_('How thorough was the inspection')
    )
    communication_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Communication'),
        help_text=_('Quality of communication and explanations')
    )
    value_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Value for Money'),
        help_text=_('Was the service worth the cost')
    )
    
    # Helpfulness
    helpful_votes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Helpful Votes'),
        help_text=_('Number of users who found this review helpful')
    )
    
    # Status
    is_verified_purchase = models.BooleanField(
        default=True,
        verbose_name=_('Verified Inspection'),
        help_text=_('Review is from actual inspection through platform')
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('Published'),
        help_text=_('Review is visible to other users')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Inspector Review')
        verbose_name_plural = _('Inspector Reviews')
        ordering = ['-created_at']
        unique_together = [['buyer', 'inspection_report']]  # One review per inspection
        indexes = [
            models.Index(fields=['inspector', '-created_at']),
            models.Index(fields=['-rating', '-helpful_votes']),
        ]
    
    def __str__(self):
        return f"{self.rating}★ review of {self.inspector.company} by {self.buyer.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update inspector's rating after saving review
        self.inspector.update_rating()
