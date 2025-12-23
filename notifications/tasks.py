"""
Celery tasks for asynchronous notification processing.
Converts synchronous WhatsApp API calls to background tasks.
Also handles SMS notifications via Twilio.
"""

from celery import shared_task
import logging
from .whatsapp_service import WhatsAppService, WhatsAppAPIError
from utils.sms_service import sms_service
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(WhatsAppAPIError, Exception),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def send_whatsapp_message_async(self, to: str, message: str, vehicle_id: int = None):
    """
    Send WhatsApp message asynchronously via Celery.
    
    Args:
        to: Recipient phone number (with country code)
        message: Message text
        vehicle_id: Optional vehicle ID for context
    
    Returns:
        Dictionary with message_id and status
    
    Retries:
        - Max retries: 3
        - Backoff: Exponential with jitter (60s, 120s, 240s)
        - Auto-retry on WhatsAppAPIError and general exceptions
    """
    try:
        service = WhatsAppService()
        result = service.send_message(to, message, vehicle_id)
        
        logger.info(
            f"WhatsApp message sent successfully to {to}. "
            f"Message ID: {result.get('message_id')}, Vehicle ID: {vehicle_id}"
        )
        
        return result
    
    except WhatsAppAPIError as e:
        logger.error(
            f"WhatsApp API error on attempt {self.request.retries + 1}/3: {str(e)}. "
            f"Vehicle ID: {vehicle_id}"
        )
        raise  # Will auto-retry
    
    except Exception as e:
        logger.error(
            f"Unexpected error sending WhatsApp message: {str(e)}. "
            f"Vehicle ID: {vehicle_id}"
        )
        raise  # Will auto-retry


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(WhatsAppAPIError, Exception),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def send_whatsapp_template_async(
    self, 
    to: str, 
    template_name: str, 
    language_code: str = 'en', 
    parameters: list = None
):
    """
    Send WhatsApp template message asynchronously via Celery.
    
    Args:
        to: Recipient phone number
        template_name: Name of approved WhatsApp template
        language_code: Template language code (default: 'en')
        parameters: List of parameters for template
    
    Returns:
        Dictionary with message_id and status
    
    Retries:
        - Max retries: 3
        - Backoff: Exponential with jitter (60s, 120s, 240s)
        - Auto-retry on WhatsAppAPIError and general exceptions
    """
    try:
        service = WhatsAppService()
        result = service.send_template_message(to, template_name, language_code, parameters)
        
        logger.info(
            f"WhatsApp template '{template_name}' sent successfully to {to}. "
            f"Message ID: {result.get('message_id')}"
        )
        
        return result
    
    except WhatsAppAPIError as e:
        logger.error(
            f"WhatsApp API error on attempt {self.request.retries + 1}/3: {str(e)}. "
            f"Template: {template_name}"
        )
        raise  # Will auto-retry
    
    except Exception as e:
        logger.error(
            f"Unexpected error sending WhatsApp template: {str(e)}. "
            f"Template: {template_name}"
        )
        raise  # Will auto-retry


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 300},
    retry_backoff=True
)
def send_bulk_whatsapp_notifications(self, recipients: list, message: str):
    """
    Send WhatsApp messages to multiple recipients asynchronously.
    
    Args:
        recipients: List of phone numbers
        message: Message text to send to all recipients
    
    Returns:
        Dictionary with success/failure counts
    
    Note:
        Individual message sends are queued as separate tasks for better
        error handling and retry isolation.
    """
    try:
        results = {'success': 0, 'failed': 0, 'total': len(recipients)}
        
        for phone_number in recipients:
            # Queue individual message as separate task for isolation
            send_whatsapp_message_async.delay(phone_number, message)
            results['success'] += 1
        
        logger.info(
            f"Bulk WhatsApp notification queued: {results['success']}/{results['total']} recipients"
        )
        
        return results
    
    except Exception as e:
        logger.error(f"Error queueing bulk WhatsApp notifications: {str(e)}")
        raise  # Will auto-retry


# ==================== SMS NOTIFICATION TASKS (Phase 2) ====================

@shared_task(name='notifications.send_offer_accepted_sms')
def send_offer_accepted_sms(buyer_id, vehicle_make, vehicle_model, vehicle_year, offer_amount):
    """Send SMS when buyer's offer is accepted"""
    from accounts.models import User
    
    try:
        buyer = User.objects.get(id=buyer_id)
        
        if not buyer.sms_notifications_enabled or not buyer.phone:
            logger.info(f"SMS notifications disabled or no phone for buyer {buyer_id}")
            return
        
        vehicle = f"{vehicle_year} {vehicle_make} {vehicle_model}"
        sms_service.send_offer_accepted_notification(
            buyer_phone=buyer.phone,
            vehicle=vehicle,
            offer_amount=offer_amount
        )
        logger.info(f"Sent offer accepted SMS to buyer {buyer_id}")
        
    except User.DoesNotExist:
        logger.error(f"Buyer {buyer_id} not found")
    except Exception as e:
        logger.error(f"Failed to send offer accepted SMS: {e}")


@shared_task(name='notifications.send_payment_due_sms')
def send_payment_due_sms(buyer_id, vehicle_make, vehicle_model, vehicle_year, amount, deadline_str):
    """Send SMS for payment reminder"""
    from accounts.models import User
    
    try:
        buyer = User.objects.get(id=buyer_id)
        
        if not buyer.sms_notifications_enabled or not buyer.phone:
            return
        
        vehicle = f"{vehicle_year} {vehicle_make} {vehicle_model}"
        sms_service.send_payment_due_notification(
            buyer_phone=buyer.phone,
            vehicle=vehicle,
            amount=amount,
            deadline=deadline_str
        )
        logger.info(f"Sent payment due SMS to buyer {buyer_id}")
        
    except User.DoesNotExist:
        logger.error(f"Buyer {buyer_id} not found")
    except Exception as e:
        logger.error(f"Failed to send payment due SMS: {e}")


@shared_task(name='notifications.send_shipment_departure_sms')
def send_shipment_departure_sms(buyer_id, vehicle_make, vehicle_model, vehicle_year, port, eta_str, tracking_number):
    """Send SMS when shipment departs"""
    from accounts.models import User
    
    try:
        buyer = User.objects.get(id=buyer_id)
        
        if not buyer.sms_notifications_enabled or not buyer.phone:
            return
        
        vehicle = f"{vehicle_year} {vehicle_make} {vehicle_model}"
        sms_service.send_shipment_departure_notification(
            buyer_phone=buyer.phone,
            vehicle=vehicle,
            port=port,
            eta=eta_str,
            tracking=tracking_number
        )
        logger.info(f"Sent shipment departure SMS to buyer {buyer_id}")
        
    except User.DoesNotExist:
        logger.error(f"Buyer {buyer_id} not found")
    except Exception as e:
        logger.error(f"Failed to send shipment departure SMS: {e}")


@shared_task(name='notifications.send_inspection_reminder_sms')
def send_inspection_reminder_sms(appointment_id):
    """Send inspection appointment reminder 24 hours before"""
    from vehicles.models import InspectionAppointment
    
    try:
        appointment = InspectionAppointment.objects.select_related(
            'buyer', 'slot__vehicle', 'slot__vehicle__dealer'
        ).get(id=appointment_id)
        
        buyer = appointment.buyer
        if not buyer.sms_notifications_enabled or not buyer.phone:
            return
        
        vehicle = appointment.slot.vehicle
        vehicle_str = f"{vehicle.year} {vehicle.make} {vehicle.model}"
        
        # Format appointment time
        slot_datetime = timezone.datetime.combine(
            appointment.slot.date,
            appointment.slot.start_time
        )
        appointment_time = slot_datetime.strftime("%B %d at %I:%M %p")
        
        # Get dealer address
        dealer = vehicle.dealer
        dealer_address = f"{dealer.showroom_city}, {dealer.showroom_province}" if dealer.showroom_city else "Dealer location"
        
        sms_service.send_inspection_appointment_reminder(
            buyer_phone=buyer.phone,
            vehicle=vehicle_str,
            appointment_time=appointment_time,
            dealer_address=dealer_address
        )
        logger.info(f"Sent inspection reminder SMS for appointment {appointment_id}")
        
    except InspectionAppointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
    except Exception as e:
        logger.error(f"Failed to send inspection reminder SMS: {e}")


@shared_task(name='notifications.send_appointment_confirmed_sms')
def send_appointment_confirmed_sms(appointment_id):
    """Send SMS when dealer confirms inspection appointment"""
    from vehicles.models import InspectionAppointment
    
    try:
        appointment = InspectionAppointment.objects.select_related(
            'buyer', 'slot__vehicle', 'slot__vehicle__dealer'
        ).get(id=appointment_id)
        
        buyer = appointment.buyer
        if not buyer.sms_notifications_enabled or not buyer.phone:
            return
        
        vehicle = appointment.slot.vehicle
        vehicle_str = f"{vehicle.year} {vehicle.make} {vehicle.model}"
        
        # Format appointment time
        slot_datetime = timezone.datetime.combine(
            appointment.slot.date,
            appointment.slot.start_time
        )
        appointment_time = slot_datetime.strftime("%B %d at %I:%M %p")
        
        dealer = vehicle.dealer
        dealer_name = dealer.company_name or dealer.get_full_name() or "the dealer"
        
        sms_service.send_appointment_confirmed_notification(
            buyer_phone=buyer.phone,
            vehicle=vehicle_str,
            appointment_time=appointment_time,
            dealer_name=dealer_name
        )
        logger.info(f"Sent appointment confirmed SMS for {appointment_id}")
        
    except InspectionAppointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
    except Exception as e:
        logger.error(f"Failed to send appointment confirmed SMS: {e}")


@shared_task(name='notifications.send_appointment_cancelled_sms')
def send_appointment_cancelled_sms(buyer_id, buyer_phone, vehicle_make, vehicle_model, vehicle_year, reason=None):
    """Send SMS when appointment is cancelled"""
    from accounts.models import User
    
    try:
        buyer = User.objects.get(id=buyer_id)
        
        if not buyer.sms_notifications_enabled or not buyer_phone:
            return
        
        vehicle = f"{vehicle_year} {vehicle_make} {vehicle_model}"
        sms_service.send_appointment_cancelled_notification(
            buyer_phone=buyer_phone,
            vehicle=vehicle,
            reason=reason
        )
        logger.info(f"Sent appointment cancelled SMS to buyer {buyer_id}")
        
    except User.DoesNotExist:
        logger.error(f"Buyer {buyer_id} not found")
    except Exception as e:
        logger.error(f"Failed to send appointment cancelled SMS: {e}")


@shared_task(name='notifications.schedule_inspection_reminders')
def schedule_inspection_reminders():
    """
    Scheduled task to send inspection reminders 24 hours before appointments
    Should be run hourly via Celery beat
    """
    from vehicles.models import InspectionAppointment
    from datetime import timedelta
    
    # Get appointments happening in 24-25 hours (1-hour window for hourly cron)
    now = timezone.now()
    tomorrow = now + timedelta(hours=24)
    tomorrow_plus_hour = now + timedelta(hours=25)
    
    upcoming_appointments = InspectionAppointment.objects.filter(
        status='confirmed',
        slot__date=tomorrow.date(),
        slot__start_time__gte=tomorrow.time(),
        slot__start_time__lt=tomorrow_plus_hour.time()
    ).select_related('buyer')
    
    sent_count = 0
    for appointment in upcoming_appointments:
        if appointment.buyer.sms_notifications_enabled and appointment.buyer.phone:
            send_inspection_reminder_sms.delay(appointment.id)
            sent_count += 1
    
    logger.info(f"Scheduled {sent_count} inspection reminder SMS")
    return sent_count

