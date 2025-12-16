from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Invoice


@receiver(post_save, sender=Payment)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    """Update invoice when payment is made"""
    if instance.invoice and instance.status == 'succeeded':
        invoice = instance.invoice
        invoice.amount_paid = sum(
            p.amount for p in invoice.payments.filter(status='succeeded')
        )
        invoice.update_status()


@receiver(post_save, sender=Invoice)
def check_invoice_overdue(sender, instance, **kwargs):
    """Check if invoice is overdue"""
    if instance.is_overdue and instance.status not in ['paid', 'canceled']:
        instance.status = 'overdue'
        instance.save(update_fields=['status'])
