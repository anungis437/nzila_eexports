"""
Management command to reset monthly/quarterly tier counters
Run this at the start of each month/quarter via cron or Celery beat
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from commissions.models import BrokerTier, DealerTier
from django.db.models import Count, Sum


class Command(BaseCommand):
    help = 'Reset monthly broker counters and quarterly dealer counters'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--monthly',
            action='store_true',
            help='Reset monthly broker counters',
        )
        parser.add_argument(
            '--quarterly',
            action='store_true',
            help='Reset quarterly dealer counters',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset even if not at period boundary',
        )
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        if options['monthly'] or (not options['quarterly']):
            self.reset_monthly_brokers(options['force'])
        
        if options['quarterly']:
            self.reset_quarterly_dealers(now.month, options['force'])
        
        self.stdout.write(self.style.SUCCESS('Tier reset completed successfully'))
    
    def reset_monthly_brokers(self, force=False):
        """Reset broker monthly counters at start of month"""
        now = timezone.now()
        
        # Only reset on 1st of month unless forced
        if not force and now.day != 1:
            self.stdout.write(
                self.style.WARNING('Not the 1st of month - skipping broker reset (use --force to override)')
            )
            return
        
        broker_tiers = BrokerTier.objects.all()
        
        for broker_tier in broker_tiers:
            # Store last month's performance
            last_month_deals = broker_tier.deals_this_month
            
            # Reset monthly counters
            broker_tier.deals_this_month = 0
            broker_tier.volume_this_month = 0
            
            # Recalculate tier (will go back to starter unless they perform)
            broker_tier.current_tier = broker_tier.calculate_tier()
            broker_tier.save()
            
            self.stdout.write(
                f"Reset {broker_tier.broker.get_full_name()}: "
                f"{last_month_deals} deals last month"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Reset {broker_tiers.count()} broker tier counters')
        )
    
    def reset_quarterly_dealers(self, current_month, force=False):
        """Reset dealer quarterly counters at start of quarter"""
        
        # Quarters start in Jan, Apr, Jul, Oct
        quarter_start_months = [1, 4, 7, 10]
        
        if not force and current_month not in quarter_start_months:
            self.stdout.write(
                self.style.WARNING('Not start of quarter - skipping dealer reset (use --force to override)')
            )
            return
        
        dealer_tiers = DealerTier.objects.all()
        
        for dealer_tier in dealer_tiers:
            # Move current quarter to last quarter
            dealer_tier.deals_last_quarter = dealer_tier.deals_this_quarter
            
            # Reset quarterly counter
            dealer_tier.deals_this_quarter = 0
            
            # Recalculate tier
            dealer_tier.current_tier = dealer_tier.calculate_tier()
            dealer_tier.save()
            
            self.stdout.write(
                f"Reset {dealer_tier.dealer.get_full_name()}: "
                f"{dealer_tier.deals_last_quarter} deals last quarter"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Reset {dealer_tiers.count()} dealer tier counters')
        )
