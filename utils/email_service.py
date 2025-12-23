"""
Email Service Configuration
Supports SendGrid and AWS SES for transactional emails
"""
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


class EmailService:
    """Service for sending transactional emails"""
    
    @staticmethod
    def send_invoice_reminder(invoice, recipient_email):
        """Send invoice payment reminder"""
        subject = f"Invoice #{invoice.invoice_number} Payment Reminder"
        
        context = {
            'invoice': invoice,
            'invoice_number': invoice.invoice_number,
            'amount_due': invoice.total_amount,
            'due_date': invoice.due_date,
            'customer_name': invoice.deal.buyer.full_name if invoice.deal else 'Valued Customer',
            'company_name': getattr(settings, 'COMPANY_NAME', 'Nzila Export'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@nzilaexport.com'),
        }
        
        html_content = render_to_string('email/invoice_reminder.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nzilaexport.com'),
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    
    @staticmethod
    def send_breach_notification(breach, recipient_email):
        """Send data breach notification to affected users"""
        subject = "Important Security Notice - Data Breach Notification"
        
        context = {
            'breach': breach,
            'severity': breach.get_severity_display(),
            'data_types': breach.data_types_compromised,
            'discovery_date': breach.breach_date,
            'steps_taken': breach.mitigation_steps,
            'company_name': getattr(settings, 'COMPANY_NAME', 'Nzila Export'),
            'privacy_email': getattr(settings, 'PRIVACY_EMAIL', 'privacy@nzilaexport.com'),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', '1-800-NZILA-EX'),
        }
        
        html_content = render_to_string('email/breach_notification.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nzilaexport.com'),
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    
    @staticmethod
    def send_consent_confirmation(consent_record, recipient_email):
        """Send consent confirmation email"""
        action_text = "granted" if consent_record.consent_given else "withdrawn"
        subject = f"Consent {action_text.capitalize()} - Confirmation"
        
        context = {
            'consent': consent_record,
            'consent_type': consent_record.get_consent_type_display(),
            'action': action_text,
            'timestamp': consent_record.timestamp,
            'company_name': getattr(settings, 'COMPANY_NAME', 'Nzila Export'),
            'privacy_policy_url': getattr(settings, 'PRIVACY_POLICY_URL', 'https://nzilaexport.com/privacy'),
            'manage_preferences_url': getattr(settings, 'MANAGE_PREFERENCES_URL', 'https://nzilaexport.com/preferences'),
        }
        
        html_content = render_to_string('email/consent_confirmation.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nzilaexport.com'),
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    
    @staticmethod
    def send_deal_notification(deal, recipient_email, notification_type):
        """Send deal-related notifications"""
        subject_map = {
            'approved': f"Deal #{deal.id} Approved",
            'rejected': f"Deal #{deal.id} Rejected",
            'pending': f"Deal #{deal.id} Pending Review",
            'shipped': f"Your Vehicle Has Shipped - Deal #{deal.id}",
        }
        
        subject = subject_map.get(notification_type, f"Deal #{deal.id} Update")
        
        context = {
            'deal': deal,
            'notification_type': notification_type,
            'vehicle': f"{deal.vehicle.year} {deal.vehicle.make} {deal.vehicle.model}" if deal.vehicle else 'Vehicle',
            'buyer_name': deal.buyer.full_name if deal.buyer else 'Customer',
            'company_name': getattr(settings, 'COMPANY_NAME', 'Nzila Export'),
            'dashboard_url': getattr(settings, 'DASHBOARD_URL', 'https://nzilaexport.com/dashboard'),
        }
        
        html_content = render_to_string('email/deal_notification.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nzilaexport.com'),
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    
    @staticmethod
    def send_shipment_update(shipment, recipient_email, update_type):
        """Send shipment tracking updates"""
        subject_map = {
            'in_transit': f"Shipment {shipment.tracking_number} - In Transit",
            'customs': f"Shipment {shipment.tracking_number} - At Customs",
            'delivered': f"Shipment {shipment.tracking_number} - Delivered",
            'delayed': f"Shipment {shipment.tracking_number} - Delay Notice",
        }
        
        subject = subject_map.get(update_type, f"Shipment {shipment.tracking_number} Update")
        
        context = {
            'shipment': shipment,
            'update_type': update_type,
            'tracking_number': shipment.tracking_number,
            'current_status': shipment.get_status_display(),
            'company_name': getattr(settings, 'COMPANY_NAME', 'Nzila Export'),
            'tracking_url': f"{getattr(settings, 'TRACKING_URL', 'https://nzilaexport.com/track')}/{shipment.tracking_number}",
        }
        
        html_content = render_to_string('email/shipment_update.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nzilaexport.com'),
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
