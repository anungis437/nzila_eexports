"""
Dealer Verification & Badge System Models
Phase 3 - Feature 9

Provides dealer license validation, trust scoring, and badge system.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta


class DealerLicense(models.Model):
    """
    Stores dealer licenses and certifications.
    Supports OMVIC (Ontario), AMVIC (Alberta), and other provincial licenses.
    """
    LICENSE_TYPE_CHOICES = [
        ('omvic', _('OMVIC - Ontario Motor Vehicle Industry Council')),
        ('amvic', _('AMVIC - Alberta Motor Vehicle Industry Council')),
        ('saaq', _('SAAQ - Société de l\'assurance automobile du Québec')),
        ('mvdb', _('MVDB - Motor Vehicle Dealers Board (BC)')),
        ('mgi', _('MGI - Manitoba Government Insurance')),
        ('sgi', _('SGI - Saskatchewan Government Insurance')),
        ('snsmr', _('SNS - Service Nova Scotia Motor Registration')),
        ('snb', _('SNB - Service New Brunswick')),
        ('business', _('Business License')),
        ('gst', _('GST/HST Registration')),
        ('pst', _('PST Registration')),
        ('other', _('Other License/Certification')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Verification')),
        ('verified', _('Verified')),
        ('expired', _('Expired')),
        ('rejected', _('Rejected')),
        ('suspended', _('Suspended')),
    ]
    
    dealer = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'dealer'},
        related_name='licenses',
        verbose_name=_('Dealer')
    )
    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPE_CHOICES,
        verbose_name=_('License Type')
    )
    license_number = models.CharField(
        max_length=100,
        verbose_name=_('License Number'),
        help_text=_('Official license/registration number')
    )
    issuing_authority = models.CharField(
        max_length=200,
        verbose_name=_('Issuing Authority'),
        help_text=_('Organization that issued the license')
    )
    province = models.CharField(
        max_length=2,
        blank=True,
        choices=[
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
            ('NT', _('Northwest Territories')),
            ('YT', _('Yukon')),
            ('NU', _('Nunavut')),
        ],
        verbose_name=_('Province/Territory')
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
        default='pending',
        verbose_name=_('Status')
    )
    
    # Document upload
    document = models.FileField(
        upload_to='dealer_licenses/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('License Document'),
        help_text=_('Upload scanned copy of license')
    )
    
    # Verification details
    verified_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'admin'},
        related_name='verified_licenses',
        verbose_name=_('Verified By')
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verified At')
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_('Rejection Reason')
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Admin Notes')
    )
    
    @property
    def is_expired(self):
        """Check if license is expired"""
        return self.expiry_date < timezone.now().date()
    
    @property
    def expires_soon(self):
        """Check if license expires within 30 days"""
        return (self.expiry_date - timezone.now().date()).days <= 30
    
    @property
    def days_until_expiry(self):
        """Days until license expires"""
        return (self.expiry_date - timezone.now().date()).days
    
    def approve(self, admin_user):
        """Approve/verify the license"""
        self.status = 'verified'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.save()
    
    def reject(self, admin_user, reason):
        """Reject the license"""
        self.status = 'rejected'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    class Meta:
        verbose_name = _('Dealer License')
        verbose_name_plural = _('Dealer Licenses')
        ordering = ['-created_at']
        unique_together = ['dealer', 'license_type', 'license_number']
    
    def __str__(self):
        return f"{self.get_license_type_display()} - {self.license_number} ({self.dealer.username})"


class DealerVerification(models.Model):
    """
    Overall dealer verification status and trust score.
    OneToOne with User (dealer role).
    """
    VERIFICATION_STATUS_CHOICES = [
        ('unverified', _('Unverified')),
        ('pending', _('Verification Pending')),
        ('verified', _('Verified')),
        ('suspended', _('Suspended')),
    ]
    
    BADGE_CHOICES = [
        ('none', _('No Badge')),
        ('bronze', _('Bronze Badge')),
        ('silver', _('Silver Badge')),
        ('gold', _('Gold Badge')),
    ]
    
    dealer = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'dealer'},
        related_name='verification',
        verbose_name=_('Dealer')
    )
    status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='unverified',
        verbose_name=_('Verification Status')
    )
    badge = models.CharField(
        max_length=10,
        choices=BADGE_CHOICES,
        default='none',
        verbose_name=_('Badge Level')
    )
    
    # Business Information
    business_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Legal Business Name')
    )
    business_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Business Number'),
        help_text=_('CRA Business Number (BN)')
    )
    years_in_business = models.IntegerField(
        default=0,
        verbose_name=_('Years in Business')
    )
    business_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Business Start Date')
    )
    
    # Insurance
    has_insurance = models.BooleanField(
        default=False,
        verbose_name=_('Has Business Insurance')
    )
    insurance_provider = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Insurance Provider')
    )
    insurance_policy_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Policy Number')
    )
    insurance_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Insurance Expiry Date')
    )
    
    # Sales Metrics
    total_sales = models.IntegerField(
        default=0,
        verbose_name=_('Total Sales'),
        help_text=_('Total vehicles sold on platform')
    )
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Total Revenue (CAD)'),
        help_text=_('Total transaction value')
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Average Rating'),
        help_text=_('Average review rating (0-5)')
    )
    total_reviews = models.IntegerField(
        default=0,
        verbose_name=_('Total Reviews')
    )
    
    # Trust Score Components
    trust_score = models.IntegerField(
        default=0,
        verbose_name=_('Trust Score'),
        help_text=_('Calculated trust score (0-100)')
    )
    license_verified = models.BooleanField(
        default=False,
        verbose_name=_('License Verified')
    )
    insurance_verified = models.BooleanField(
        default=False,
        verbose_name=_('Insurance Verified')
    )
    business_verified = models.BooleanField(
        default=False,
        verbose_name=_('Business Number Verified')
    )
    identity_verified = models.BooleanField(
        default=False,
        verbose_name=_('Identity Verified'),
        help_text=_('Government ID verified')
    )
    address_verified = models.BooleanField(
        default=False,
        verbose_name=_('Address Verified'),
        help_text=_('Business address verified')
    )
    
    # Verification Dates
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verified At')
    )
    verified_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'admin'},
        related_name='verified_dealers',
        verbose_name=_('Verified By')
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Admin Notes')
    )
    
    def calculate_trust_score(self):
        """
        Calculate trust score (0-100) based on multiple factors.
        
        Components:
        - License verification: 20 points
        - Insurance verification: 15 points
        - Business number verification: 10 points
        - Identity verification: 10 points
        - Address verification: 5 points
        - Years in business: 15 points (max: 3+ years = 15)
        - Sales volume: 10 points (max: 50+ sales = 10)
        - Average rating: 10 points (max: 4.5+ = 10)
        - Review count: 5 points (max: 20+ reviews = 5)
        """
        score = 0
        
        # Verification checks (60 points total)
        if self.license_verified:
            score += 20
        if self.insurance_verified:
            score += 15
        if self.business_verified:
            score += 10
        if self.identity_verified:
            score += 10
        if self.address_verified:
            score += 5
        
        # Years in business (15 points max)
        if self.years_in_business >= 10:
            score += 15
        elif self.years_in_business >= 5:
            score += 12
        elif self.years_in_business >= 3:
            score += 10
        elif self.years_in_business >= 1:
            score += 5
        
        # Sales volume (10 points max)
        if self.total_sales >= 100:
            score += 10
        elif self.total_sales >= 50:
            score += 8
        elif self.total_sales >= 20:
            score += 5
        elif self.total_sales >= 10:
            score += 3
        
        # Average rating (10 points max)
        if self.average_rating >= Decimal('4.8'):
            score += 10
        elif self.average_rating >= Decimal('4.5'):
            score += 8
        elif self.average_rating >= Decimal('4.0'):
            score += 5
        elif self.average_rating >= Decimal('3.5'):
            score += 3
        
        # Review count (5 points max)
        if self.total_reviews >= 50:
            score += 5
        elif self.total_reviews >= 20:
            score += 4
        elif self.total_reviews >= 10:
            score += 2
        elif self.total_reviews >= 5:
            score += 1
        
        return min(score, 100)
    
    def calculate_badge(self):
        """
        Calculate badge level based on criteria.
        
        Gold Badge (5/5 criteria):
        - License verified
        - Insurance verified
        - Business number verified
        - Identity verified
        - Address verified
        
        Silver Badge (3/5 criteria):
        - At least 3 verifications
        
        Bronze Badge (2/5 criteria):
        - At least 2 verifications
        
        None: < 2 verifications
        """
        verifications = sum([
            self.license_verified,
            self.insurance_verified,
            self.business_verified,
            self.identity_verified,
            self.address_verified,
        ])
        
        if verifications >= 5:
            return 'gold'
        elif verifications >= 3:
            return 'silver'
        elif verifications >= 2:
            return 'bronze'
        else:
            return 'none'
    
    def update_metrics(self):
        """Update trust score and badge based on current data"""
        self.trust_score = self.calculate_trust_score()
        self.badge = self.calculate_badge()
        self.save()
    
    def verify_dealer(self, admin_user):
        """Mark dealer as verified"""
        self.status = 'verified'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.update_metrics()
    
    def suspend_dealer(self, reason=''):
        """Suspend dealer verification"""
        self.status = 'suspended'
        if reason:
            self.notes += f"\n[{timezone.now()}] Suspended: {reason}"
        self.save()
    
    @property
    def verification_percentage(self):
        """Calculate percentage of verifications completed"""
        verifications = [
            self.license_verified,
            self.insurance_verified,
            self.business_verified,
            self.identity_verified,
            self.address_verified,
        ]
        return (sum(verifications) / len(verifications)) * 100
    
    @property
    def has_active_licenses(self):
        """Check if dealer has any active verified licenses"""
        return self.dealer.licenses.filter(
            status='verified',
            expiry_date__gte=timezone.now().date()
        ).exists()
    
    class Meta:
        verbose_name = _('Dealer Verification')
        verbose_name_plural = _('Dealer Verifications')
    
    def __str__(self):
        return f"{self.dealer.username} - {self.get_status_display()} ({self.get_badge_display()})"
