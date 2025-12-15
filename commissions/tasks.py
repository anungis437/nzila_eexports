"""
Celery tasks for commissions app
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal


@shared_task
def process_pending_commissions():
    """
    Process pending commissions for payment
    Prepares batch for Wise/Stripe Connect integration
    """
    from commissions.models import Commission
    
    pending = Commission.objects.filter(status='pending')
    
    approved_count = 0
    total_amount = Decimal('0.00')
    
    # Group by recipient for batch processing
    recipients = {}
    
    for commission in pending:
        # Auto-approve if deal is completed for more than 7 days
        from datetime import timedelta
        from django.utils import timezone
        
        if commission.deal.completed_at:
            days_since_completion = (timezone.now() - commission.deal.completed_at).days
            
            if days_since_completion >= 7:
                commission.status = 'approved'
                commission.approved_at = timezone.now()
                commission.save()
                
                approved_count += 1
                total_amount += commission.amount_cad
                
                # Group by recipient
                recipient_id = commission.recipient.id
                if recipient_id not in recipients:
                    recipients[recipient_id] = {
                        'user': commission.recipient,
                        'commissions': [],
                        'total': Decimal('0.00')
                    }
                
                recipients[recipient_id]['commissions'].append(commission)
                recipients[recipient_id]['total'] += commission.amount_cad
    
    # Send notifications
    for recipient_data in recipients.values():
        send_commission_approval_notification.delay(
            recipient_data['user'].id,
            [c.id for c in recipient_data['commissions']]
        )
    
    return {
        'approved': approved_count,
        'total_amount': str(total_amount),
        'recipients': len(recipients)
    }


@shared_task
def send_commission_approval_notification(user_id, commission_ids):
    """Send notification about approved commissions"""
    from django.contrib.auth import get_user_model
    from commissions.models import Commission
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        commissions = Commission.objects.filter(id__in=commission_ids)
        
        total = sum(c.amount_cad for c in commissions)
        
        subject = 'Commission Payment Approved'
        message = f'''
        Good news! Your commissions have been approved for payment.
        
        Total Amount: ${total} CAD
        Number of Deals: {len(commission_ids)}
        
        Commission Details:
        '''
        
        for commission in commissions:
            message += f'''
        - Deal #{commission.deal.id}: ${commission.amount_cad} ({commission.get_commission_type_display()})
        '''
        
        message += '''
        
        Payment will be processed within 3-5 business days.
        You will receive another notification when payment is completed.
        '''
        
        if user.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
        
        return f'Notification sent to user #{user_id}'
    except User.DoesNotExist:
        return f'User #{user_id} not found'


@shared_task
def mark_commission_paid(commission_id, transaction_id):
    """
    Mark commission as paid after successful payment
    Will be integrated with Wise/Stripe Connect
    """
    from commissions.models import Commission
    from django.utils import timezone
    
    try:
        commission = Commission.objects.get(id=commission_id)
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.notes = f'{commission.notes}\nTransaction ID: {transaction_id}'.strip()
        commission.save()
        
        # Send payment confirmation
        send_payment_confirmation.delay(commission.id, transaction_id)
        
        return f'Commission #{commission_id} marked as paid'
    except Commission.DoesNotExist:
        return f'Commission #{commission_id} not found'


@shared_task
def send_payment_confirmation(commission_id, transaction_id):
    """Send payment confirmation email"""
    from commissions.models import Commission
    
    try:
        commission = Commission.objects.get(id=commission_id)
        
        subject = 'Commission Payment Completed'
        message = f'''
        Your commission payment has been processed successfully!
        
        Amount: ${commission.amount_cad} CAD
        Deal: #{commission.deal.id}
        Transaction ID: {transaction_id}
        Payment Date: {commission.paid_at}
        
        Thank you for your business!
        '''
        
        if commission.recipient.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [commission.recipient.email],
                fail_silently=False
            )
        
        return f'Payment confirmation sent for Commission #{commission_id}'
    except Commission.DoesNotExist:
        return f'Commission #{commission_id} not found'
