"""
Celery tasks for shipments app
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 600},
    retry_backoff=True
)
def send_shipment_updates(self):
    """
    Check for shipment updates and notify buyers
    
    Retries: 2 attempts with exponential backoff (10min, 20min)
    """
    from shipments.models import Shipment
    from django.utils import timezone
    from datetime import timedelta
    
    # Get shipments in transit
    shipments = Shipment.objects.filter(
        status='in_transit'
    )
    
    notifications_sent = 0
    
    for shipment in shipments:
        # Check if there are recent updates
        recent_updates = shipment.updates.filter(
            created_at__gte=timezone.now() - timedelta(hours=6)
        ).count()
        
        if recent_updates > 0:
            send_shipment_notification.delay(shipment.id)
            notifications_sent += 1
    
    return {
        'shipments_checked': shipments.count(),
        'notifications_sent': notifications_sent
    }


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 300},
    retry_backoff=True
)
def send_shipment_notification(self, shipment_id):
    """
    Send shipment update notification to buyer
    
    Retries: 2 attempts with exponential backoff (5min, 10min)
    """
    from shipments.models import Shipment
    
    try:
        shipment = Shipment.objects.get(id=shipment_id)
        buyer = shipment.deal.buyer
        
        latest_update = shipment.updates.first()
        
        subject = f'Shipment Update: {shipment.tracking_number}'
        message = f'''
        Your shipment has been updated:
        
        Tracking Number: {shipment.tracking_number}
        Status: {shipment.get_status_display()}
        
        Latest Update:
        Location: {latest_update.location if latest_update else 'N/A'}
        Status: {latest_update.status if latest_update else 'N/A'}
        Time: {latest_update.created_at if latest_update else 'N/A'}
        
        Track your shipment: {settings.SITE_URL}/api/shipments/shipments/{shipment.id}/track/
        '''
        
        if buyer.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [buyer.email],
                fail_silently=False
            )
        
        return f'Notification sent for Shipment #{shipment.id}'
    except Shipment.DoesNotExist:
        return f'Shipment #{shipment_id} not found'


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 600},
    retry_backoff=True
)
def check_delayed_shipments(self):
    """
    Check for delayed shipments and alert stakeholders
    
    Retries: 2 attempts with exponential backoff (10min, 20min)
    """
    from shipments.models import Shipment
    from django.utils import timezone
    
    shipments = Shipment.objects.filter(
        status='in_transit',
        estimated_arrival__lt=timezone.now().date()
    )
    
    for shipment in shipments:
        # Update status to delayed
        shipment.status = 'delayed'
        shipment.save()
        
        # Send notifications
        send_delay_notification.delay(shipment.id)
    
    return {
        'delayed_shipments': shipments.count()
    }


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 300},
    retry_backoff=True
)
def send_delay_notification(self, shipment_id):
    """
    Send notification about delayed shipment
    
    Retries: 2 attempts with exponential backoff (5min, 10min)
    """
    from shipments.models import Shipment
    
    try:
        shipment = Shipment.objects.get(id=shipment_id)
        
        subject = f'Shipment Delayed: {shipment.tracking_number}'
        message = f'''
        ALERT: Your shipment is delayed.
        
        Tracking Number: {shipment.tracking_number}
        Expected Arrival: {shipment.estimated_arrival}
        Current Status: Delayed
        
        We are working to resolve this delay. You will be notified of updates.
        '''
        
        # Notify buyer, dealer, and broker
        recipients = [shipment.deal.buyer.email, shipment.deal.dealer.email]
        if shipment.deal.broker:
            recipients.append(shipment.deal.broker.email)
        
        recipients = [email for email in recipients if email]
        
        if recipients:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False
            )
        
        return f'Delay notification sent for Shipment #{shipment.id}'
    except Shipment.DoesNotExist:
        return f'Shipment #{shipment_id} not found'
