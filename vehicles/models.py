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
    
    # PHASE 2: Geographic coordinates for proximity search
    # Using Decimal fields for simplicity (no GeoDjango/GDAL required)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Latitude'),
        help_text=_('Latitude coordinate for proximity search')
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Longitude'),
        help_text=_('Longitude coordinate for proximity search')
    )
    
    # Images
    main_image = models.ImageField(
        upload_to='vehicles/',
        blank=True,
        null=True,
        verbose_name=_('Main Image')
    )
    
    # PHASE 2 - Feature 5: PPSA Lien Status
    lien_checked = models.BooleanField(
        default=False,
        verbose_name=_('Lien Checked'),
        help_text=_('Whether PPSA lien search has been performed')
    )
    lien_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Lien Status'),
        help_text=_('CLEAR, LIEN_FOUND, or empty if not checked')
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


# PHASE 1: In-Person Inspection Scheduling Models


class VehicleInspectionSlot(models.Model):
    """Available time slots for in-person vehicle inspections"""
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='inspection_slots',
        verbose_name=_('Vehicle')
    )
    date = models.DateField(
        verbose_name=_('Inspection Date')
    )
    start_time = models.TimeField(
        verbose_name=_('Start Time')
    )
    end_time = models.TimeField(
        verbose_name=_('End Time')
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Available')
    )
    max_attendees = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Maximum Attendees'),
        help_text=_('How many buyers can inspect at this time')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Special instructions for this time slot')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Vehicle Inspection Slot')
        verbose_name_plural = _('Vehicle Inspection Slots')
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['vehicle', 'date', 'is_available']),
            models.Index(fields=['date', 'start_time']),
        ]
        unique_together = [['vehicle', 'date', 'start_time']]
    
    def __str__(self):
        return f"{self.vehicle} - {self.date} {self.start_time}-{self.end_time}"
    
    @property
    def is_past(self):
        """Check if this slot is in the past"""
        from django.utils import timezone
        from datetime import datetime
        slot_datetime = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(slot_datetime) < timezone.now()
    
    @property
    def current_bookings(self):
        """Get count of confirmed bookings for this slot"""
        return self.appointments.filter(
            status__in=['pending', 'confirmed']
        ).count()
    
    @property
    def slots_remaining(self):
        """Calculate remaining available slots"""
        return max(0, self.max_attendees - self.current_bookings)


class InspectionAppointment(models.Model):
    """Buyer appointments for in-person vehicle inspections"""
    STATUS_CHOICES = [
        ('pending', _('Pending Confirmation')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ]
    
    slot = models.ForeignKey(
        VehicleInspectionSlot,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Inspection Slot')
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inspection_appointments',
        verbose_name=_('Buyer')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Buyer details
    contact_phone = models.CharField(
        max_length=20,
        verbose_name=_('Contact Phone'),
        help_text=_('Phone number for day-of coordination')
    )
    contact_email = models.EmailField(
        verbose_name=_('Contact Email')
    )
    number_of_people = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Number of People'),
        help_text=_('How many people will attend the inspection')
    )
    
    # Notes and feedback
    buyer_notes = models.TextField(
        blank=True,
        verbose_name=_('Buyer Notes'),
        help_text=_('Special requests or questions from buyer')
    )
    dealer_notes = models.TextField(
        blank=True,
        verbose_name=_('Dealer Notes'),
        help_text=_('Internal notes for dealer staff')
    )
    inspection_feedback = models.TextField(
        blank=True,
        verbose_name=_('Inspection Feedback'),
        help_text=_('Buyer feedback after inspection')
    )
    
    # Ratings
    vehicle_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name=_('Vehicle Rating'),
        help_text=_('1-5 stars: How did vehicle match expectations?')
    )
    dealer_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name=_('Dealer Rating'),
        help_text=_('1-5 stars: How was the inspection experience?')
    )
    
    # Outcome
    interested_in_purchase = models.BooleanField(
        default=False,
        verbose_name=_('Interested in Purchase'),
        help_text=_('Buyer wants to proceed with purchase after inspection')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Confirmed At')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Cancelled At')
    )
    
    class Meta:
        verbose_name = _('Inspection Appointment')
        verbose_name_plural = _('Inspection Appointments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['slot', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.buyer_notes:
            self.buyer_notes = sanitize_html(self.buyer_notes)
        if self.dealer_notes:
            self.dealer_notes = sanitize_html(self.dealer_notes)
        if self.inspection_feedback:
            self.inspection_feedback = sanitize_html(self.inspection_feedback)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Inspection: {self.buyer.email} - {self.slot.vehicle} on {self.slot.date}"
    
    @property
    def vehicle(self):
        """Get the vehicle being inspected"""
        return self.slot.vehicle
    
    @property
    def dealer(self):
        """Get the dealer for this inspection"""
        return self.slot.vehicle.dealer
