from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Shipment(models.Model):
    """Shipment model for tracking vehicle deliveries"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_transit', _('In Transit')),
        ('customs', _('At Customs')),
        ('delivered', _('Delivered')),
        ('delayed', _('Delayed')),
    ]
    
    deal = models.OneToOneField(
        'deals.Deal',
        on_delete=models.CASCADE,
        related_name='shipment',
        verbose_name=_('Deal')
    )
    
    # Shipment Details
    tracking_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Tracking Number')
    )
    shipping_company = models.CharField(
        max_length=255,
        verbose_name=_('Shipping Company')
    )
    
    # Locations
    origin_port = models.CharField(
        max_length=255,
        verbose_name=_('Origin Port')
    )
    destination_port = models.CharField(
        max_length=255,
        verbose_name=_('Destination Port')
    )
    destination_country = models.CharField(
        max_length=100,
        verbose_name=_('Destination Country')
    )
    
    # Status & Dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    estimated_departure = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Departure')
    )
    actual_departure = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Actual Departure')
    )
    estimated_arrival = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Arrival')
    )
    actual_arrival = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Actual Arrival')
    )
    
    # Additional Info
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Shipment')
        verbose_name_plural = _('Shipments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Shipment {self.tracking_number} - Deal #{self.deal.id}"


class ShipmentUpdate(models.Model):
    """Tracking updates for shipments"""
    
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name=_('Shipment')
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name=_('Location')
    )
    status = models.CharField(
        max_length=255,
        verbose_name=_('Status')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Shipment Update')
        verbose_name_plural = _('Shipment Updates')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.shipment.tracking_number} - {self.created_at}"
