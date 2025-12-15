from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class Lead(models.Model):
    """Lead model for tracking potential deals"""
    
    STATUS_CHOICES = [
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('qualified', _('Qualified')),
        ('negotiating', _('Negotiating')),
        ('converted', _('Converted to Deal')),
        ('lost', _('Lost')),
    ]
    
    SOURCE_CHOICES = [
        ('website', _('Website')),
        ('referral', _('Referral')),
        ('broker', _('Broker')),
        ('direct', _('Direct Contact')),
    ]
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads',
        limit_choices_to={'role': 'buyer'},
        verbose_name=_('Buyer')
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name=_('Vehicle')
    )
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brokered_leads',
        limit_choices_to={'role': 'broker'},
        verbose_name=_('Broker')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name=_('Status')
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='website',
        verbose_name=_('Source')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Contacted')
    )
    
    class Meta:
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Lead #{self.id} - {self.buyer.username} - {self.vehicle}"
    
    def is_stalled(self):
        """Check if lead is stalled (no update in 7 days)"""
        if self.status in ['converted', 'lost']:
            return False
        threshold = timezone.now() - timedelta(days=7)
        return self.updated_at < threshold


class Deal(models.Model):
    """Deal model for confirmed sales"""
    
    STATUS_CHOICES = [
        ('pending_docs', _('Pending Documentation')),
        ('docs_verified', _('Documents Verified')),
        ('payment_pending', _('Payment Pending')),
        ('payment_received', _('Payment Received')),
        ('ready_to_ship', _('Ready to Ship')),
        ('shipped', _('Shipped')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name='deal',
        null=True,
        blank=True,
        verbose_name=_('Lead')
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name=_('Vehicle')
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deals_as_buyer',
        limit_choices_to={'role': 'buyer'},
        verbose_name=_('Buyer')
    )
    dealer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deals_as_dealer',
        limit_choices_to={'role': 'dealer'},
        verbose_name=_('Dealer')
    )
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_as_broker',
        limit_choices_to={'role': 'broker'},
        verbose_name=_('Broker')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_docs',
        verbose_name=_('Status')
    )
    
    # Pricing
    agreed_price_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Agreed Price (CAD)')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    class Meta:
        verbose_name = _('Deal')
        verbose_name_plural = _('Deals')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Deal #{self.id} - {self.vehicle}"
    
    def save(self, *args, **kwargs):
        # Auto-complete deal when status is completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    def is_stalled(self):
        """Check if deal is stalled (no update in 14 days)"""
        if self.status in ['completed', 'cancelled']:
            return False
        threshold = timezone.now() - timedelta(days=14)
        return self.updated_at < threshold


class Document(models.Model):
    """Document model for deal verification"""
    
    TYPE_CHOICES = [
        ('title', _('Vehicle Title')),
        ('id', _('Buyer ID')),
        ('payment_proof', _('Payment Proof')),
        ('export_permit', _('Export Permit')),
        ('customs', _('Customs Declaration')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
    ]
    
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Deal')
    )
    document_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_('Document Type')
    )
    file = models.FileField(
        upload_to='documents/',
        verbose_name=_('File')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        verbose_name=_('Uploaded By')
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents',
        verbose_name=_('Verified By')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verified At')
    )
    
    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - Deal #{self.deal.id}"
