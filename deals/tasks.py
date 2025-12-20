"""
Celery tasks for deals app
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 600},
    retry_backoff=True
)
def check_stalled_deals(self):
    """
    Asynchronous task to check for stalled leads and deals
    Replaces the management command for production use
    
    Retries: 2 attempts with exponential backoff (10min, 20min)
    """
    from deals.models import Lead, Deal
    
    stalled_leads = []
    stalled_deals = []
    
    # Check for stalled leads
    leads = Lead.objects.filter(
        status__in=['new', 'contacted', 'qualified', 'negotiating']
    )
    
    for lead in leads:
        if lead.is_stalled():
            stalled_leads.append(lead)
            send_lead_follow_up.delay(lead.id)
    
    # Check for stalled deals
    deals = Deal.objects.filter(
        status__in=['pending_docs', 'docs_verified', 'payment_pending', 'ready_to_ship']
    )
    
    for deal in deals:
        if deal.is_stalled():
            stalled_deals.append(deal)
            send_deal_follow_up.delay(deal.id)
    
    return {
        'stalled_leads': len(stalled_leads),
        'stalled_deals': len(stalled_deals),
        'timestamp': timezone.now().isoformat()
    }


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 300},
    retry_backoff=True
)
def send_lead_follow_up(self, lead_id):
    """
    Send follow-up email for stalled lead
    
    Retries: 2 attempts with exponential backoff (5min, 10min)
    """
    from deals.models import Lead
    
    try:
        lead = Lead.objects.get(id=lead_id)
        
        subject = f'Follow-up required: Lead #{lead.id}'
        message = f'''
        Lead #{lead.id} has been inactive for more than 7 days.
        
        Lead Details:
        - Buyer: {lead.buyer.username} ({lead.buyer.email})
        - Vehicle: {lead.vehicle}
        - Status: {lead.get_status_display()}
        - Last Updated: {lead.updated_at}
        
        Please follow up with the buyer to advance this lead.
        '''
        
        # Send to dealer/broker
        recipient = lead.vehicle.dealer.email
        if lead.broker:
            recipient = lead.broker.email
        
        if recipient:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False
            )
        
        return f'Follow-up sent for Lead #{lead.id}'
    except Lead.DoesNotExist:
        return f'Lead #{lead_id} not found'


@shared_task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 300},
    retry_backoff=True
)
def send_deal_follow_up(self, deal_id):
    """
    Send follow-up email for stalled deal
    
    Retries: 2 attempts with exponential backoff (5min, 10min)
    """
    from deals.models import Deal
    
    try:
        deal = Deal.objects.get(id=deal_id)
        
        subject = f'Follow-up required: Deal #{deal.id}'
        message = f'''
        Deal #{deal.id} has been inactive for more than 14 days.
        
        Deal Details:
        - Buyer: {deal.buyer.username} ({deal.buyer.email})
        - Vehicle: {deal.vehicle}
        - Status: {deal.get_status_display()}
        - Agreed Price: ${deal.agreed_price_cad}
        - Last Updated: {deal.updated_at}
        
        Please follow up to advance this deal.
        '''
        
        # Send to dealer and admin
        recipients = [deal.dealer.email]
        
        if recipients[0]:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False
            )
        
        return f'Follow-up sent for Deal #{deal.id}'
    except Deal.DoesNotExist:
        return f'Deal #{deal_id} not found'


@shared_task
def process_document_verification(document_id):
    """
    Asynchronous document verification processing
    Can be extended with AI-based quality checks
    """
    from deals.models import Document
    
    try:
        document = Document.objects.get(id=document_id)
        
        # Future: Add AI-based document quality checks here
        # - Check image quality
        # - Verify document authenticity
        # - Extract text with OCR
        # - Validate information
        
        # For now, just log the processing
        return f'Document #{document.id} processed for verification'
    except Document.DoesNotExist:
        return f'Document #{document_id} not found'
