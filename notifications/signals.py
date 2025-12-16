"""
Signals for creating notifications when important events occur.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from deals.models import Lead, Deal
from commissions.models import Commission
from shipments.models import Shipment
from vehicles.models import Vehicle

from .models import Notification

User = get_user_model()


@receiver(post_save, sender=Lead)
def create_lead_notification(sender, instance, created, **kwargs):
    """Create notification when a new lead is created"""
    if created:
        # Notify broker if assigned
        if instance.broker:
            Notification.objects.create(
                user=instance.broker,
                type='lead',
                title=f"New Lead Assigned",
                message=f"A new lead has been assigned to you for {instance.vehicle}.",
                link=f'/leads/{instance.id}',
                related_id=instance.id,
                related_model='lead'
            )


@receiver(post_save, sender=Deal)
def create_deal_notification(sender, instance, created, **kwargs):
    """Create notification when a deal status changes"""
    if not created:
        # Deal status changed
        if instance.buyer:
            Notification.objects.create(
                user=instance.buyer,
                type='deal',
                title=f"Deal Updated: {instance.vehicle.make} {instance.vehicle.model}",
                message=f"Deal status changed to {instance.get_status_display()}.",
                link=f'/deals/{instance.id}',
                related_id=instance.id,
                related_model='deal'
            )


@receiver(post_save, sender=Commission)
def create_commission_notification(sender, instance, created, **kwargs):
    """Create notification when a commission is earned"""
    if created and instance.deal and instance.deal.broker:
        Notification.objects.create(
            user=instance.deal.broker,
            type='commission',
            title="Commission Earned!",
            message=f"You earned a commission of ${instance.amount:,.2f} on deal #{instance.deal.id}.",
            link=f'/commissions',
            related_id=instance.id,
            related_model='commission'
        )


@receiver(post_save, sender=Shipment)
def create_shipment_notification(sender, instance, created, **kwargs):
    """Create notification when shipment status changes"""
    if not created:
        # Shipment status changed
        if instance.deal and instance.deal.buyer:
            Notification.objects.create(
                user=instance.deal.buyer,
                type='shipment',
                title=f"Shipment Update: {instance.tracking_number}",
                message=f"Shipment status changed to {instance.get_status_display()}.",
                link=f'/shipments/{instance.id}',
                related_id=instance.id,
                related_model='shipment'
            )


@receiver(post_save, sender=Vehicle)
def create_vehicle_notification(sender, instance, created, **kwargs):
    """Create notification when a vehicle is added"""
    if created:
        # Notify team about new vehicle (could be specific users or managers)
        # For now, we'll skip automatic notifications for vehicles
        # as they may be bulk imported
        pass


# Helper function to manually create notifications
def create_notification(user, notification_type, title, message, link=None, related_id=None, related_model=None):
    """
    Helper function to manually create notifications.
    
    Args:
        user: User object to receive the notification
        notification_type: Type of notification ('lead', 'deal', 'commission', etc.)
        title: Notification title
        message: Notification message
        link: Optional link to related resource
        related_id: Optional ID of related object
        related_model: Optional model name of related object
    """
    return Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        link=link,
        related_id=related_id,
        related_model=related_model
    )
