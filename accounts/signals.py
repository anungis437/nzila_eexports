from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send welcome email when a new user registers
    """
    if created and instance.email:
        try:
            subject = 'Welcome to Nzila Ventures! 🎉'
            
            # Plain text version
            text_message = f"""
Dear {instance.get_full_name() or instance.email},

Welcome to Nzila Ventures!

We're thrilled to have you join our platform. Nzila Ventures is your trusted partner for seamless global vehicle exports from Canada to anywhere in the world.

What You Can Do Now:
- Browse our extensive inventory of quality vehicles
- Track your purchases and shipments in real-time
- Access all your export documents and invoices
- Pay in your preferred currency with real-time exchange rates

Visit your dashboard: {settings.FRONTEND_URL}/dashboard

Need help getting started? Our support team is here for you:
- Email: info@nzilaventures.com
- Phone: +1 (234) 567-8900

Welcome aboard, and happy exporting!

Best regards,
The Nzila Ventures Team
"""
            
            # HTML version from template
            html_message = render_to_string('emails/welcome_email.html', {
                'user_name': instance.get_full_name() or instance.email,
                'dashboard_url': f'{settings.FRONTEND_URL}/dashboard',
            })
            
            msg = EmailMultiAlternatives(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=True)
            
        except Exception as e:
            # Log error but don't prevent user creation
            print(f"Error sending welcome email to {instance.email}: {e}")
