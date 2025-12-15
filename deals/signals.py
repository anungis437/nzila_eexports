from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Document, Deal


@receiver(post_save, sender=Document)
def advance_deal_on_document_verification(sender, instance, **kwargs):
    """
    Automatically advance deal status when documents are verified
    """
    if instance.status == 'verified':
        instance.verified_at = timezone.now()
        instance.save(update_fields=['verified_at'])
        
        deal = instance.deal
        
        # Check if all required documents are verified
        required_docs = ['title', 'id', 'payment_proof']
        verified_docs = deal.documents.filter(
            document_type__in=required_docs,
            status='verified'
        ).values_list('document_type', flat=True)
        
        # If all required docs are verified, advance deal status
        if set(required_docs).issubset(set(verified_docs)):
            if deal.status == 'pending_docs':
                deal.status = 'docs_verified'
                deal.save()
            elif deal.status == 'payment_pending':
                deal.status = 'payment_received'
                deal.save()


@receiver(post_save, sender=Deal)
def update_vehicle_status_on_deal_change(sender, instance, created, **kwargs):
    """
    Update vehicle status based on deal status
    """
    vehicle = instance.vehicle
    
    if instance.status in ['pending_docs', 'docs_verified', 'payment_pending']:
        vehicle.status = 'reserved'
    elif instance.status == 'ready_to_ship':
        vehicle.status = 'sold'
    elif instance.status == 'shipped':
        vehicle.status = 'shipped'
    elif instance.status == 'completed':
        vehicle.status = 'delivered'
    elif instance.status == 'cancelled':
        vehicle.status = 'available'
    
    vehicle.save()
