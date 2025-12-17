from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ShipmentMilestone(models.Model):
    """Major milestones in the shipment journey"""
    
    MILESTONE_TYPES = [
        ('pickup', _('Vehicle Picked Up')),
        ('departed_origin', _('Departed Origin Port')),
        ('in_transit', _('In Transit')),
        ('arrived_port', _('Arrived at Destination Port')),
        ('customs_clearance', _('Customs Clearance')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered to Buyer')),
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name=_('Shipment')
    )
    
    milestone_type = models.CharField(
        max_length=50,
        choices=MILESTONE_TYPES,
        verbose_name=_('Milestone Type')
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Location')
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Latitude')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Longitude')
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_('Is Completed')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Shipment Milestone')
        verbose_name_plural = _('Shipment Milestones')
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['shipment', 'order']),
            models.Index(fields=['shipment', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.get_milestone_type_display()} - {self.shipment.tracking_number}"


class ShipmentPhoto(models.Model):
    """Photos documenting the shipment journey"""
    
    PHOTO_TYPES = [
        ('loading', _('Loading')),
        ('in_transit', _('In Transit')),
        ('arrival', _('Arrival')),
        ('customs', _('Customs')),
        ('delivery', _('Delivery')),
        ('damage', _('Damage Report')),
        ('other', _('Other')),
    ]
    
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_('Shipment')
    )
    
    photo = models.ImageField(
        upload_to='shipments/photos/%Y/%m/%d/',
        verbose_name=_('Photo')
    )
    
    photo_type = models.CharField(
        max_length=50,
        choices=PHOTO_TYPES,
        default='other',
        verbose_name=_('Photo Type')
    )
    
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Caption')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Location')
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Latitude')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Longitude')
    )
    
    taken_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Taken At')
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Uploaded By')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Shipment Photo')
        verbose_name_plural = _('Shipment Photos')
        ordering = ['-taken_at', '-created_at']
        indexes = [
            models.Index(fields=['shipment', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_photo_type_display()} - {self.shipment.tracking_number}"
