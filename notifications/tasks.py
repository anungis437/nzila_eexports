"""
Celery tasks for asynchronous notification processing.
Converts synchronous WhatsApp API calls to background tasks.
"""

from celery import shared_task
import logging
from .whatsapp_service import WhatsAppService, WhatsAppAPIError

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
