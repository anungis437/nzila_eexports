from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Import dealer verification models
from .dealer_verification_models import DealerLicense, DealerVerification


class User(AbstractUser):
    """Custom user model with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('dealer', _('Dealer')),
        ('broker', _('Broker')),
        ('buyer', _('Buyer')),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='buyer',
        verbose_name=_('Role')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone Number')
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Company Name')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Address')
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Country')
    )
    preferred_language = models.CharField(
        max_length=5,
        choices=[('en', 'English'), ('fr', 'Français')],
        default='en',
        verbose_name=_('Preferred Language')
    )
    
    # Payment integration
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Stripe Customer ID')
    )
    
    # Two-Factor Authentication
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name=_('2FA Enabled')
    )
    two_factor_secret = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name=_('2FA Secret')
    )
    phone_verified = models.BooleanField(
        default=False,
        verbose_name=_('Phone Verified')
    )
    
    # PIPEDA & Law 25 Compliance - Explicit Consent Tracking
    data_processing_consent = models.BooleanField(
        default=False,
        verbose_name=_('Data Processing Consent'),
        help_text=_('User has consented to processing of personal information (PIPEDA Principle 3)')
    )
    marketing_consent = models.BooleanField(
        default=False,
        verbose_name=_('Marketing Communications Consent'),
        help_text=_('User has consented to receive marketing communications (Law 25 Article 8)')
    )
    third_party_sharing_consent = models.BooleanField(
        default=False,
        verbose_name=_('Third Party Sharing Consent'),
        help_text=_('User has consented to sharing data with brokers/partners across borders')
    )
    consent_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Consent Date'),
        help_text=_('Date when user provided explicit consent')
    )
    consent_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Consent IP Address'),
        help_text=_('IP address from which consent was provided (audit trail)')
    )
    consent_version = models.CharField(
        max_length=20,
        blank=True,
        default='1.0',
        verbose_name=_('Consent Version'),
        help_text=_('Version of privacy policy user consented to')
    )
    
    # Data Subject Rights (Law 25 Articles 8-41)
    data_export_requested_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data Export Requested'),
        help_text=_('When user requested data export (Law 25 Article 8.5)')
    )
    data_deletion_requested_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data Deletion Requested'),
        help_text=_('When user requested account deletion (Law 25 Article 28)')
    )
    data_rectification_requested_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data Rectification Requested'),
        help_text=_('When user requested data correction')
    )
    
    # Cross-border Data Transfer (PIPEDA & Law 25)
    data_transfer_consent_africa = models.BooleanField(
        default=False,
        verbose_name=_('Africa Data Transfer Consent'),
        help_text=_('Consent for transferring personal info to African brokers (PIPEDA Principle 4.1.3)')
    )
    
    # PHASE 1: Canadian Diaspora Buyer Fields
    is_diaspora_buyer = models.BooleanField(
        default=False,
        verbose_name=_('Canadian Diaspora Buyer'),
        help_text=_('Buyer resides in Canada, purchasing for export to Africa')
    )
    
    # Canadian Location (for diaspora buyers)
    canadian_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('City'),
        help_text=_('Toronto, Vancouver, Calgary, Montreal, etc.')
    )
    canadian_province = models.CharField(
        max_length=2,
        blank=True,
        choices=[
            ('ON', 'Ontario'), ('QC', 'Quebec'), ('BC', 'British Columbia'),
            ('AB', 'Alberta'), ('MB', 'Manitoba'), ('SK', 'Saskatchewan'),
            ('NS', 'Nova Scotia'), ('NB', 'New Brunswick'), ('NL', 'Newfoundland and Labrador'),
            ('PE', 'Prince Edward Island'), ('NT', 'Northwest Territories'),
            ('NU', 'Nunavut'), ('YT', 'Yukon'),
        ],
        verbose_name=_('Province/Territory')
    )
    canadian_postal_code = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_('Postal Code'),
        help_text=_('A1A 1A1 format')
    )
    
    # Export Destination
    destination_country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Destination Country'),
        help_text=_('Where vehicle will be shipped (Nigeria, Ghana, Kenya, etc.)')
    )
    destination_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Destination City'),
        help_text=_('Lagos, Accra, Nairobi, etc.')
    )
    
    # Purchase Purpose
    buyer_type = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('personal', _('Personal Use')),
            ('family', _('Gift for Family')),
            ('business', _('Business/Resale')),
        ],
        verbose_name=_('Purchase Purpose')
    )
    
    # Canadian Residency
    residency_status = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('citizen', _('Canadian Citizen')),
            ('pr', _('Permanent Resident')),
            ('work_permit', _('Work Permit')),
            ('study_permit', _('Study Permit')),
            ('visitor', _('Visitor/Tourist')),
        ],
        verbose_name=_('Canadian Residency Status')
    )
    
    # Preferences
    prefers_in_person_inspection = models.BooleanField(
        default=False,
        verbose_name=_('Prefers In-Person Inspection'),
        help_text=_('Buyer wants to physically inspect vehicles before purchase')
    )
    
    # PHASE 1: Dealer Showroom Information
    showroom_address = models.TextField(
        blank=True,
        verbose_name=_('Showroom Address'),
        help_text=_('Physical address where buyers can view vehicles')
    )
    showroom_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Showroom City')
    )
    showroom_province = models.CharField(
        max_length=2,
        blank=True,
        choices=[
            ('ON', 'Ontario'), ('QC', 'Quebec'), ('BC', 'British Columbia'),
            ('AB', 'Alberta'), ('MB', 'Manitoba'), ('SK', 'Saskatchewan'),
            ('NS', 'Nova Scotia'), ('NB', 'New Brunswick'), ('NL', 'Newfoundland and Labrador'),
            ('PE', 'Prince Edward Island'), ('NT', 'Northwest Territories'),
            ('NU', 'Nunavut'), ('YT', 'Yukon'),
        ],
        verbose_name=_('Showroom Province')
    )
    showroom_postal_code = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_('Showroom Postal Code')
    )
    showroom_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Showroom Phone'),
        help_text=_('Direct phone for showroom/inspection bookings')
    )
    business_hours = models.TextField(
        blank=True,
        verbose_name=_('Business Hours'),
        help_text=_('Mon-Fri 9am-6pm, Sat 10am-4pm, etc.')
    )
    allows_test_drives = models.BooleanField(
        default=True,
        verbose_name=_('Allows Test Drives')
    )
    requires_appointment = models.BooleanField(
        default=False,
        verbose_name=_('Requires Appointment'),
        help_text=_('Buyers must book appointment before visiting')
    )
    
    # PHASE 1: Canadian Phone Support
    toll_free_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Toll-Free Number'),
        help_text=_('1-800-XXX-XXXX format')
    )
    local_phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Local Phone Number')
    )
    phone_support_hours = models.TextField(
        blank=True,
        verbose_name=_('Phone Support Hours')
    )
    preferred_contact_method = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('phone', _('Phone Call')),
            ('sms', _('Text/SMS')),
            ('whatsapp', _('WhatsApp')),
            ('email', _('Email')),
            ('chat', _('Live Chat')),
        ],
        verbose_name=_('Preferred Contact Method')
    )
    
    # PHASE 2: Notification Preferences
    sms_notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('SMS Notifications'),
        help_text=_('Receive SMS for critical updates (offers, payments, shipments)')
    )
    email_notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Email Notifications'),
        help_text=_('Receive email notifications')
    )
    whatsapp_notifications_enabled = models.BooleanField(
        default=False,
        verbose_name=_('WhatsApp Notifications'),
        help_text=_('Receive WhatsApp messages (requires WhatsApp number)')
    )
    push_notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Push Notifications'),
        help_text=_('Receive browser/app push notifications')
    )
    
    # Notification frequency (for non-critical updates)
    notification_frequency = models.CharField(
        max_length=20,
        default='instant',
        choices=[
            ('instant', _('Instant')),
            ('hourly', _('Hourly Digest')),
            ('daily', _('Daily Digest')),
            ('weekly', _('Weekly Digest')),
            ('never', _('Never')),
        ],
        verbose_name=_('Notification Frequency'),
        help_text=_('How often to receive non-critical notifications')
    )
    
    # PHASE 2: Location for Proximity Search
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('City'),
        help_text=_('City for proximity search (Canadian buyers)')
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
        verbose_name=_('Province'),
        help_text=_('Province for proximity search and timezone display')
    )
    postal_code = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_('Postal Code'),
        help_text=_('Canadian postal code (e.g., M5H 2N2)')
    )
    # Using Decimal fields for simplicity (no GeoDjango/GDAL required)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Latitude'),
        help_text=_('Latitude for proximity search')
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Longitude'),
        help_text=_('Longitude for proximity search')
    )
    travel_radius_km = models.IntegerField(
        null=True,
        blank=True,
        choices=[
            (50, _('50 km')),
            (100, _('100 km')),
            (200, _('200 km')),
            (500, _('Province-wide')),
            (1000, _('All of Canada')),
        ],
        verbose_name=_('Travel Radius'),
        help_text=_('Maximum distance willing to travel to view vehicles')
    )
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_dealer(self):
        return self.role == 'dealer'
    
    def is_broker(self):
        return self.role == 'broker'
    
    def is_buyer(self):
        return self.role == 'buyer'
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_dealer(self):
        return self.role == 'dealer'
    
    def is_broker(self):
        return self.role == 'broker'
    
    def is_buyer(self):
        return self.role == 'buyer'
