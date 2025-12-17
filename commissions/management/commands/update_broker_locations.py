"""
Management command to update existing broker tiers with default location values
"""
from django.core.management.base import BaseCommand
from commissions.models import BrokerTier


class Command(BaseCommand):
    help = 'Set default location values for existing broker tiers'

    def handle(self, *args, **options):
        # Get all broker tiers with missing location data
        brokers_to_update = BrokerTier.objects.filter(country='')
        
        if not brokers_to_update.exists():
            self.stdout.write(self.style.SUCCESS('✅ All broker tiers already have location data'))
            return
        
        count = brokers_to_update.count()
        self.stdout.write(f'Found {count} broker tier(s) without location data')
        
        # Set default values for Côte d'Ivoire (primary broker hub)
        updated = brokers_to_update.update(
            country='CI',
            timezone='Africa/Abidjan',
            qualified_buyers_network=0,
            buyer_conversion_rate=0.00
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Updated {updated} broker tier(s) with default values:\n'
            f'   - Country: CI (Côte d\'Ivoire)\n'
            f'   - Timezone: Africa/Abidjan (GMT)\n'
            f'   - Qualified Buyers Network: 0\n'
            f'   - Buyer Conversion Rate: 0.00%'
        ))
        
        # Show summary
        self.stdout.write('\n📊 Current broker distribution by country:')
        from django.db.models import Count
        distribution = BrokerTier.objects.values('country').annotate(count=Count('id')).order_by('-count')
        
        for item in distribution:
            country_code = item['country']
            count = item['count']
            try:
                country_display = dict(BrokerTier.COUNTRY_CHOICES).get(country_code, country_code)
                self.stdout.write(f'   {country_display}: {count} broker(s)')
            except:
                self.stdout.write(f'   {country_code}: {count} broker(s)')
