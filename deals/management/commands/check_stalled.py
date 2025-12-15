from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from deals.models import Lead, Deal


class Command(BaseCommand):
    help = 'Check for stalled leads and deals and send follow-up notifications'

    def handle(self, *args, **options):
        # Check for stalled leads
        stalled_leads = Lead.objects.filter(
            status__in=['new', 'contacted', 'qualified', 'negotiating']
        )
        
        stalled_count = 0
        for lead in stalled_leads:
            if lead.is_stalled():
                stalled_count += 1
                self.follow_up_lead(lead)
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {stalled_count} stalled leads')
        )
        
        # Check for stalled deals
        stalled_deals = Deal.objects.filter(
            status__in=['pending_docs', 'docs_verified', 'payment_pending', 'ready_to_ship']
        )
        
        stalled_deal_count = 0
        for deal in stalled_deals:
            if deal.is_stalled():
                stalled_deal_count += 1
                self.follow_up_deal(deal)
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {stalled_deal_count} stalled deals')
        )
    
    def follow_up_lead(self, lead):
        """Send follow-up notification for stalled lead"""
        subject = f'Follow-up required: Lead #{lead.id}'
        message = f'''
        Lead #{lead.id} has been inactive for more than 7 days.
        
        Lead Details:
        - Buyer: {lead.buyer.username}
        - Vehicle: {lead.vehicle}
        - Status: {lead.get_status_display()}
        - Last Updated: {lead.updated_at}
        
        Please follow up with the buyer.
        '''
        
        # In production, send to dealer/broker
        recipient = lead.vehicle.dealer.email
        if lead.broker:
            recipient = lead.broker.email
        
        self.stdout.write(f'Follow-up notification for Lead #{lead.id}')
        # Uncomment in production:
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
    
    def follow_up_deal(self, deal):
        """Send follow-up notification for stalled deal"""
        subject = f'Follow-up required: Deal #{deal.id}'
        message = f'''
        Deal #{deal.id} has been inactive for more than 14 days.
        
        Deal Details:
        - Buyer: {deal.buyer.username}
        - Vehicle: {deal.vehicle}
        - Status: {deal.get_status_display()}
        - Last Updated: {deal.updated_at}
        
        Please follow up to advance the deal.
        '''
        
        # Send to dealer and admin
        recipients = [deal.dealer.email]
        
        self.stdout.write(f'Follow-up notification for Deal #{deal.id}')
        # Uncomment in production:
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
