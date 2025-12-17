from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


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
