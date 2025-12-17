"""
Email template service for rendering and sending emails.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from typing import Dict, List, Optional


class EmailTemplateService:
    """Service for rendering and sending email templates"""
    
    @staticmethod
    def send_email(
        template_name: str,
        context: Dict,
        subject: str,
        to_emails: List[str],
        from_email: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
    ) -> bool:
        """
        Render and send an email using a template.
        
        Args:
            template_name: Name of the template file (without extension)
            context: Dictionary of context variables for the template
            subject: Email subject line
            to_emails: List of recipient email addresses
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
            cc_emails: List of CC email addresses
            bcc_emails: List of BCC email addresses
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Render HTML template
            html_content = render_to_string(
                f'email_templates/{template_name}.html',
                context
            )
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body='',  # Plain text version (optional)
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                to=to_emails,
                cc=cc_emails or [],
                bcc=bcc_emails or [],
            )
            
            # Attach HTML content
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            return True
            
        except Exception as e:
            # Log error (you can integrate with your logging system)
            print(f"Error sending email: {str(e)}")
            return False
    
    @classmethod
    def send_welcome_email(cls, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        context = {
            'user_name': user_name,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        return cls.send_email(
            template_name='welcome',
            context=context,
            subject='Welcome to Nzila Exports!',
            to_emails=[user_email],
        )
    
    @classmethod
    def send_lead_confirmation(
        cls,
        lead_email: str,
        lead_name: str,
        vehicle_info: Dict,
    ) -> bool:
        """Send lead confirmation email"""
        context = {
            'lead_name': lead_name,
            'vehicle_year': vehicle_info.get('year'),
            'vehicle_make': vehicle_info.get('make'),
            'vehicle_model': vehicle_info.get('model'),
            'vehicle_vin': vehicle_info.get('vin'),
            'support_email': settings.DEFAULT_FROM_EMAIL,
            'portal_url': f"{settings.FRONTEND_URL}/buyer-portal",
        }
        
        return cls.send_email(
            template_name='lead_confirmation',
            context=context,
            subject='We Received Your Inquiry - Nzila Exports',
            to_emails=[lead_email],
        )
    
    @classmethod
    def send_deal_status_update(
        cls,
        buyer_email: str,
        buyer_name: str,
        deal_info: Dict,
    ) -> bool:
        """Send deal status update email"""
        context = {
            'buyer_name': buyer_name,
            'vehicle_info': f"{deal_info.get('year')} {deal_info.get('make')} {deal_info.get('model')}",
            'status': deal_info.get('status'),
            'deal_id': deal_info.get('id'),
            'deal_url': f"{settings.FRONTEND_URL}/deals",
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        status_text = deal_info.get('status', '').replace('_', ' ').title()
        
        return cls.send_email(
            template_name='deal_status',
            context=context,
            subject=f'Deal Status Update: {status_text} - Nzila Exports',
            to_emails=[buyer_email],
        )
    
    @classmethod
    def send_payment_receipt(
        cls,
        buyer_email: str,
        buyer_name: str,
        payment_info: Dict,
    ) -> bool:
        """Send payment receipt email"""
        context = {
            'buyer_name': buyer_name,
            'payment_id': payment_info.get('id'),
            'amount': payment_info.get('amount'),
            'currency': payment_info.get('currency', 'USD'),
            'date': payment_info.get('created_at'),
            'payment_method': payment_info.get('payment_method', 'Credit Card'),
            'deal_id': payment_info.get('deal_id'),
            'invoice_url': f"{settings.FRONTEND_URL}/payments/{payment_info.get('id')}",
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        return cls.send_email(
            template_name='payment_receipt',
            context=context,
            subject=f'Payment Receipt #{payment_info.get("id")} - Nzila Exports',
            to_emails=[buyer_email],
        )
