from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
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
    
    ENGINE_TYPE_CHOICES = [
        ('4-cylinder', _('4 Cylinder')),
        ('6-cylinder', _('6 Cylinder')),
        ('8-cylinder', _('8 Cylinder')),
        ('electric', _('Electric')),
        ('hybrid', _('Hybrid')),
        ('diesel', _('Diesel')),
    ]
    
    DRIVETRAIN_CHOICES = [
        ('fwd', _('Front-Wheel Drive (FWD)')),
        ('rwd', _('Rear-Wheel Drive (RWD)')),
        ('awd', _('All-Wheel Drive (AWD)')),
        ('4wd', _('Four-Wheel Drive (4WD)')),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('gasoline', _('Gasoline')),
        ('diesel', _('Diesel')),
        ('electric', _('Electric')),
        ('hybrid', _('Hybrid')),
        ('plug-in-hybrid', _('Plug-in Hybrid')),
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
        choices=FUEL_TYPE_CHOICES,
        verbose_name=_('Fuel Type')
    )
    transmission = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Transmission')
    )
    engine_type = models.CharField(
        max_length=50,
        blank=True,
        choices=ENGINE_TYPE_CHOICES,
        verbose_name=_('Engine Type')
    )
    drivetrain = models.CharField(
        max_length=50,
        blank=True,
        choices=DRIVETRAIN_CHOICES,
        verbose_name=_('Drivetrain')
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
    """Additional images and videos for vehicles"""
    
    MEDIA_TYPE_CHOICES = [
        ('image', _('Image')),
        ('video', _('Video')),
    ]
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Vehicle')
    )
    image = models.ImageField(
        upload_to='vehicles/images/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Image')
    )
    video = models.FileField(
        upload_to='vehicles/videos/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Video')
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image',
        verbose_name=_('Media Type')
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
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Video Duration (seconds)')
    )
    thumbnail = models.ImageField(
        upload_to='vehicles/thumbnails/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Video Thumbnail')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Vehicle Media')
        verbose_name_plural = _('Vehicle Media')
        ordering = ['order', '-uploaded_at']
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.caption:
            self.caption = sanitize_html(self.caption)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_media_type_display()} for {self.vehicle}"
    
    @property
    def is_video(self):
        """Check if this is a video"""
        return self.media_type == 'video'
    
    @property
    def media_url(self):
        """Get the URL for the media file"""
        if self.media_type == 'video' and self.video:
            return self.video.url
        elif self.image:
            return self.image.url
        return None


class Offer(models.Model):
    """Buyer offers on vehicles"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('countered', _('Countered')),
        ('withdrawn', _('Withdrawn')),
        ('expired', _('Expired')),
    ]
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name=_('Vehicle')
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicle_offers',
        limit_choices_to={'role': 'buyer'},
        verbose_name=_('Buyer')
    )
    
    offer_amount_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Offer Amount (CAD)')
    )
    message = models.TextField(
        blank=True,
        verbose_name=_('Message to Dealer')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    counter_amount_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Counter Offer Amount (CAD)')
    )
    counter_message = models.TextField(
        blank=True,
        verbose_name=_('Counter Offer Message')
    )
    
    dealer_notes = models.TextField(
        blank=True,
        verbose_name=_('Dealer Notes')
    )
    
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Valid Until')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Responded At')
    )
    
    class Meta:
        verbose_name = _('Offer')
        verbose_name_plural = _('Offers')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicle', 'status']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.message:
            self.message = sanitize_html(self.message)
        if self.counter_message:
            self.counter_message = sanitize_html(self.counter_message)
        if self.dealer_notes:
            self.dealer_notes = sanitize_html(self.dealer_notes)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Offer by {self.buyer.email} on {self.vehicle} - ${self.offer_amount_cad}"
    
    @property
    def is_expired(self):
        """Check if offer has expired"""
        if self.valid_until:
            from django.utils import timezone
            return timezone.now() > self.valid_until
        return False
