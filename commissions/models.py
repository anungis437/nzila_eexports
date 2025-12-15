from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Commission(models.Model):
    """Commission model for tracking broker/dealer earnings"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    ]
    
    deal = models.ForeignKey(
        'deals.Deal',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Deal')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Recipient')
    )
    
    # Commission Details
    commission_type = models.CharField(
        max_length=20,
        choices=[
            ('broker', _('Broker Commission')),
            ('dealer', _('Dealer Commission')),
        ],
        verbose_name=_('Commission Type')
    )
    
    amount_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Amount (CAD)')
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_('Commission percentage'),
        verbose_name=_('Percentage')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approved At')
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Paid At')
    )
    
    class Meta:
        verbose_name = _('Commission')
        verbose_name_plural = _('Commissions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_commission_type_display()} - Deal #{self.deal.id} - ${self.amount_cad}"


@receiver(post_save, sender='deals.Deal')
def create_commissions_on_deal_completion(sender, instance, created, **kwargs):
    """Auto-create commissions when deal is completed"""
    if instance.status == 'completed' and not instance.commissions.exists():
        # Dealer commission (e.g., 5%)
        dealer_commission = Commission.objects.create(
            deal=instance,
            recipient=instance.dealer,
            commission_type='dealer',
            percentage=5.00,
            amount_cad=instance.agreed_price_cad * 0.05,
            status='pending'
        )
        
        # Broker commission if broker is involved (e.g., 3%)
        if instance.broker:
            broker_commission = Commission.objects.create(
                deal=instance,
                recipient=instance.broker,
                commission_type='broker',
                percentage=3.00,
                amount_cad=instance.agreed_price_cad * 0.03,
                status='pending'
            )
