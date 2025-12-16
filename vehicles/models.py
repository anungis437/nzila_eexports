from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from nzila_export.sanitizers import sanitize_html


class Vehicle(models.Model):
    """Vehicle model for the export platform"""
    
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('reserved', _('Reserved')),
        ('sold', _('Sold')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
    ]
    
    CONDITION_CHOICES = [
        ('new', _('New')),
        ('used_excellent', _('Used - Excellent')),
        ('used_good', _('Used - Good')),
        ('used_fair', _('Used - Fair')),
    ]
    
    dealer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicles',
        limit_choices_to={'role': 'dealer'},
        verbose_name=_('Dealer')
    )
    
    # Basic Information
    make = models.CharField(max_length=100, verbose_name=_('Make'))
    model = models.CharField(max_length=100, verbose_name=_('Model'))
    year = models.IntegerField(verbose_name=_('Year'))
    vin = models.CharField(
        max_length=17,
        unique=True,
        verbose_name=_('VIN')
    )
    
    # Details
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='used_good',
        verbose_name=_('Condition')
    )
    mileage = models.IntegerField(verbose_name=_('Mileage (km)'))
    color = models.CharField(max_length=50, verbose_name=_('Color'))
    fuel_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Fuel Type')
    )
    transmission = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Transmission')
    )
    
    # Pricing
    price_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Price (CAD)')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name=_('Status')
    )
    
    # Additional Info
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    location = models.CharField(
        max_length=255,
        verbose_name=_('Location in Canada')
    )
    
    # Images
    main_image = models.ImageField(
        upload_to='vehicles/',
        blank=True,
        null=True,
        verbose_name=_('Main Image')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.description:
            self.description = sanitize_html(self.description)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.vin})"


class VehicleImage(models.Model):
    """Additional images for vehicles"""
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Vehicle')
    )
    image = models.ImageField(
        upload_to='vehicles/',
        verbose_name=_('Image')
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Caption')
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Is Primary Image')
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_('Display Order')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Vehicle Image')
        verbose_name_plural = _('Vehicle Images')
        ordering = ['order', '-uploaded_at']
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.caption:
            self.caption = sanitize_html(self.caption)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Image for {self.vehicle}"
