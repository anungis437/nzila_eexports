"""
Seed script to create test tier data for brokers and dealers
Run with: python seed_tier_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from decimal import Decimal
from accounts.models import User
from commissions.models import BrokerTier, DealerTier, BonusTransaction
from django.utils import timezone


def create_broker_tiers():
    """Create broker tier test data"""
    print("\n📊 Creating Broker Tier Test Data...")
    
    # Find or create broker users
    brokers = User.objects.filter(role='seller_broker')[:10]
    
    if not brokers.exists():
        print("⚠️  No brokers found. Create some broker users first.")
        return
    
    tier_data = [
        # Diamond tier broker (top performer)
        {'deals': 95, 'volume': Decimal('2850000'), 'streak': 45, 'highest': 102},
        # Platinum tier brokers
        {'deals': 52, 'volume': Decimal('1560000'), 'streak': 28, 'highest': 60},
        {'deals': 48, 'volume': Decimal('1440000'), 'streak': 15, 'highest': 55},
        # Gold tier brokers
        {'deals': 28, 'volume': Decimal('840000'), 'streak': 12, 'highest': 35},
        {'deals': 23, 'volume': Decimal('690000'), 'streak': 8, 'highest': 30},
        # Silver tier brokers
        {'deals': 15, 'volume': Decimal('450000'), 'streak': 5, 'highest': 18},
        {'deals': 12, 'volume': Decimal('360000'), 'streak': 3, 'highest': 15},
        # Bronze tier brokers
        {'deals': 7, 'volume': Decimal('210000'), 'streak': 2, 'highest': 9},
        {'deals': 6, 'volume': Decimal('180000'), 'streak': 1, 'highest': 8},
        # Starter tier broker
        {'deals': 2, 'volume': Decimal('60000'), 'streak': 1, 'highest': 3},
    ]
    
    for broker, data in zip(brokers, tier_data):
        broker_tier, created = BrokerTier.objects.get_or_create(broker=broker)
        
        broker_tier.deals_this_month = data['deals']
        broker_tier.volume_this_month = data['volume']
        broker_tier.total_deals = data['deals'] * 3  # Simulate 3 months of history
        broker_tier.total_commissions_earned = data['volume'] * Decimal('0.04')  # Avg 4%
        broker_tier.average_deal_value = data['volume'] / data['deals'] if data['deals'] > 0 else Decimal('0')
        broker_tier.streak_days = data['streak']
        broker_tier.highest_month = data['highest']
        broker_tier.last_deal_date = timezone.now().date()
        broker_tier.current_tier = broker_tier.calculate_tier()
        
        # Add achievement boost for top performers
        if data['deals'] >= 50:
            broker_tier.achievement_boost = Decimal('0.5')  # +0.5% for epic achievements
        elif data['deals'] >= 20:
            broker_tier.achievement_boost = Decimal('0.25')  # +0.25% for rare achievements
        
        broker_tier.save()
        
        print(f"  ✅ {broker.get_full_name()}: {broker_tier.get_current_tier_display()} "
              f"({data['deals']} deals, {broker_tier.get_commission_rate()}% rate)")


def create_dealer_tiers():
    """Create dealer tier test data"""
    print("\n🚗 Creating Dealer Tier Test Data...")
    
    # Find or create dealer users
    dealers = User.objects.filter(role='seller_dealer')[:10]
    
    if not dealers.exists():
        print("⚠️  No dealers found. Create some dealer users first.")
        return
    
    provinces = ['ON', 'QC', 'BC', 'AB', 'ON', 'BC', 'SK', 'NB', 'NS', 'MB']
    cities = [
        'Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Ottawa',
        'Surrey', 'Regina', 'Moncton', 'Halifax', 'Winnipeg'
    ]
    
    tier_data = [
        # Premier tier dealers
        {'deals_q': 62, 'total': 180, 'rural': False, 'fn': False, 'cert': 'omvic'},
        {'deals_q': 54, 'total': 150, 'rural': False, 'fn': False, 'cert': 'none'},
        # Elite tier dealers
        {'deals_q': 35, 'total': 95, 'rural': True, 'fn': False, 'cert': 'amvic'},
        {'deals_q': 28, 'total': 80, 'rural': False, 'fn': False, 'cert': 'omvic'},
        # Preferred tier dealers
        {'deals_q': 18, 'total': 45, 'rural': False, 'fn': True, 'cert': 'none'},
        {'deals_q': 14, 'total': 38, 'rural': True, 'fn': False, 'cert': 'none'},
        {'deals_q': 11, 'total': 28, 'rural': False, 'fn': False, 'cert': 'none'},
        # Standard tier dealers
        {'deals_q': 7, 'total': 18, 'rural': False, 'fn': False, 'cert': 'none'},
        {'deals_q': 5, 'total': 12, 'rural': True, 'fn': False, 'cert': 'none'},
        {'deals_q': 3, 'total': 7, 'rural': False, 'fn': True, 'cert': 'omvic'},
    ]
    
    for dealer, province, city, data in zip(dealers, provinces, cities, tier_data):
        dealer_tier, created = DealerTier.objects.get_or_create(dealer=dealer)
        
        dealer_tier.province = province
        dealer_tier.city = city
        dealer_tier.is_rural = data['rural']
        dealer_tier.is_first_nations = data['fn']
        dealer_tier.omvic_certified = data['cert'] == 'omvic'
        dealer_tier.amvic_certified = data['cert'] == 'amvic'
        
        dealer_tier.deals_this_quarter = data['deals_q']
        dealer_tier.deals_last_quarter = max(data['deals_q'] - 5, 0)
        dealer_tier.total_deals = data['total']
        dealer_tier.average_deal_value = Decimal('28000')  # Avg vehicle price
        dealer_tier.total_commissions_earned = data['total'] * Decimal('28000') * Decimal('0.055')  # Avg 5.5%
        dealer_tier.current_tier = dealer_tier.calculate_tier()
        
        # Mark bonuses as paid for established dealers
        if data['total'] >= 5:
            dealer_tier.welcome_bonus_paid = True
            dealer_tier.first_deal_bonus_paid = True
            dealer_tier.fast_start_bonus_paid = data['total'] >= 10
        
        dealer_tier.save()
        
        rate = dealer_tier.get_total_commission_rate()
        bonuses = []
        if data['rural']:
            bonuses.append('Rural +1%')
        if data['fn']:
            bonuses.append('First Nations +1.5%')
        if data['cert'] != 'none':
            bonuses.append(data['cert'].upper())
        
        bonus_str = f" ({', '.join(bonuses)})" if bonuses else ""
        
        print(f"  ✅ {dealer.get_full_name()} ({city}, {province}): "
              f"{dealer_tier.get_current_tier_display()} "
              f"({data['deals_q']} deals this Q, {rate}% rate{bonus_str})")


def create_sample_bonuses():
    """Create sample bonus transactions"""
    print("\n💰 Creating Sample Bonus Transactions...")
    
    dealers = User.objects.filter(role='seller_dealer')[:3]
    brokers = User.objects.filter(role='seller_broker')[:3]
    
    bonus_count = 0
    
    for dealer in dealers:
        # Welcome bonus
        BonusTransaction.objects.get_or_create(
            user=dealer,
            bonus_type='welcome',
            defaults={
                'amount_cad': Decimal('500.00'),
                'status': 'paid',
                'description': 'Welcome bonus for verified Canadian dealer',
                'approved_at': timezone.now(),
                'paid_at': timezone.now(),
            }
        )
        bonus_count += 1
        
        # First deal bonus
        BonusTransaction.objects.get_or_create(
            user=dealer,
            bonus_type='first_deal',
            defaults={
                'amount_cad': Decimal('1000.00'),
                'status': 'paid',
                'description': 'First deal completion bonus',
                'approved_at': timezone.now(),
                'paid_at': timezone.now(),
            }
        )
        bonus_count += 1
    
    print(f"  ✅ Created {bonus_count} bonus transactions")


def main():
    print("🚀 Starting Tier Data Seeding...")
    print("=" * 60)
    
    create_broker_tiers()
    create_dealer_tiers()
    create_sample_bonuses()
    
    print("\n" + "=" * 60)
    print("✅ Tier data seeding completed successfully!")
    print("\n📊 Summary:")
    print(f"  - Broker Tiers: {BrokerTier.objects.count()}")
    print(f"  - Dealer Tiers: {DealerTier.objects.count()}")
    print(f"  - Bonus Transactions: {BonusTransaction.objects.count()}")
    print("\n🎯 You can now test the tiered commission system!")


if __name__ == '__main__':
    main()
