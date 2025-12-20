"""
Celery tasks for payments app
"""
from celery import shared_task
from .stripe_service import StripePaymentService


@shared_task(
    name='payments.tasks.update_exchange_rates',
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 300},
    retry_backoff=True,
    retry_backoff_max=1800,
    retry_jitter=True
)
def update_exchange_rates(self):
    """
    Update exchange rates from external API
    Runs daily at 12:30 AM (configured in celery.py)
    
    Retries: 3 attempts with exponential backoff (5min, 10min, 15min)
    """
    try:
        result = StripePaymentService.update_exchange_rates()
        if result:
            return {'status': 'success', 'message': 'Exchange rates updated successfully'}
        else:
            return {'status': 'warning', 'message': 'Exchange rates update returned False'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task(
    name='payments.tasks.process_pending_payments',
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 600},
    retry_backoff=True
)
def process_pending_payments(self):
    """
    Process pending payments and update their status
    Can be used to check Stripe payment status for stuck transactions
    
    Retries: 2 attempts with exponential backoff (10min, 20min)
    """
    from .models import Payment
    import stripe
    from django.conf import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    pending_payments = Payment.objects.filter(status='pending')
    processed_count = 0
    
    for payment in pending_payments:
        try:
            # Check payment status from Stripe
            if payment.stripe_payment_intent_id:
                intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                
                if intent.status == 'succeeded':
                    payment.status = 'succeeded'
                    payment.save()
                    processed_count += 1
                elif intent.status in ['canceled', 'requires_payment_method']:
                    payment.status = 'failed'
                    payment.save()
        except Exception as e:
            print(f"Error processing payment {payment.id}: {e}")
            continue
    
    return {
        'status': 'success',
        'processed': processed_count,
        'total_pending': pending_payments.count()
    }


@shared_task(
    name='payments.tasks.send_payment_reminders',
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 1800},
    retry_backoff=True
)
def send_payment_reminders(self):
    """
    Send email reminders for unpaid invoices that are past due
    
    Retries: 2 attempts with exponential backoff (30min, 60min)
    """
    from .models import Invoice
    from django.utils import timezone
    from datetime import timedelta
    from django.core.mail import send_mail
    from django.conf import settings
    
    # Find invoices that are 3+ days overdue
    overdue_date = timezone.now().date() - timedelta(days=3)
    overdue_invoices = Invoice.objects.filter(
        status='sent',
        due_date__lt=overdue_date
    )
    
    sent_count = 0
    for invoice in overdue_invoices:
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            
            days_overdue = (timezone.now().date() - invoice.due_date).days
            subject = f'Payment Reminder: Invoice #{invoice.id} is Overdue'
            
            # Plain text version
            text_message = f"""
Dear {invoice.user.get_full_name() or invoice.user.email},

This is a friendly reminder that invoice #{invoice.id} is now overdue.

Invoice Details:
- Amount Due: {invoice.currency.symbol}{invoice.total}
- Due Date: {invoice.due_date}
- Days Overdue: {days_overdue}

Please log in to your account to make payment at your earliest convenience.

Thank you,
Nzila Ventures Team
"""
            
            # HTML version from template
            html_message = render_to_string('emails/payment_reminder.html', {
                'invoice': invoice,
                'user_name': invoice.user.get_full_name() or invoice.user.email,
                'user_email': invoice.user.email,
                'days_overdue': days_overdue,
                'payment_url': f'{settings.FRONTEND_URL}/invoices/{invoice.id}',
            })
            
            msg = EmailMultiAlternatives(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [invoice.user.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=True)
            
            sent_count += 1
        except Exception as e:
            print(f"Error sending reminder for invoice {invoice.id}: {e}")
            continue
    
    return {
        'status': 'success',
        'reminders_sent': sent_count,
        'total_overdue': overdue_invoices.count()
    }
