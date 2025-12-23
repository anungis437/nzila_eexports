"""
Seed interest rate data for all Canadian provinces and credit tiers.
This unblocks the Financing.tsx page with dynamic rates instead of hardcoded values.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from commissions.models import InterestRate

def seed_interest_rates():
    """Create initial interest rates for all provinces and credit tiers"""
    
    # Base rates by credit tier (these are typical Canadian auto loan rates)
    base_rates = {
        'excellent': Decimal('4.99'),   # 750+ credit score
        'good': Decimal('6.99'),        # 680-749 credit score
        'fair': Decimal('9.99'),        # 620-679 credit score
        'poor': Decimal('14.99'),       # 550-619 credit score
        'very_poor': Decimal('19.99'),  # <550 credit score
    }
    
    # Province-specific adjustments (some provinces have higher/lower rates)
    province_adjustments = {
        'ON': Decimal('0.00'),    # Ontario - baseline
        'QC': Decimal('-0.25'),   # Quebec - slightly lower
        'BC': Decimal('0.25'),    # British Columbia - slightly higher
        'AB': Decimal('0.00'),    # Alberta - baseline
        'SK': Decimal('0.00'),    # Saskatchewan - baseline
        'MB': Decimal('0.00'),    # Manitoba - baseline
        'NB': Decimal('0.50'),    # New Brunswick - higher (smaller market)
        'NS': Decimal('0.50'),    # Nova Scotia - higher
        'PE': Decimal('0.75'),    # PEI - higher (small market)
        'NL': Decimal('0.75'),    # Newfoundland - higher (remote)
        'YT': Decimal('1.00'),    # Yukon - highest (remote)
        'NT': Decimal('1.00'),    # Northwest Territories - highest
        'NU': Decimal('1.00'),    # Nunavut - highest (most remote)
    }
    
    effective_date = timezone.now().date()
    created_count = 0
    updated_count = 0
    
    print("🏦 Seeding interest rate data...")
    print(f"📅 Effective date: {effective_date}\n")
    
    for province_code, province_name in InterestRate.PROVINCE_CHOICES:
        adjustment = province_adjustments.get(province_code, Decimal('0.00'))
        
        print(f"📍 {province_name} ({province_code}) - Adjustment: {adjustment:+.2f}%")
        
        for credit_tier, credit_tier_display in InterestRate.CREDIT_TIER_CHOICES:
            base_rate = base_rates[credit_tier]
            final_rate = base_rate + adjustment
            
            # Check if rate already exists
            existing_rate = InterestRate.objects.filter(
                province=province_code,
                credit_tier=credit_tier,
                effective_date=effective_date
            ).first()
            
            if existing_rate:
                # Update existing rate
                existing_rate.rate_percentage = final_rate
                existing_rate.is_active = True
                existing_rate.save()
                updated_count += 1
                action = "✓ Updated"
            else:
                # Create new rate
                InterestRate.objects.create(
                    province=province_code,
                    credit_tier=credit_tier,
                    rate_percentage=final_rate,
                    effective_date=effective_date,
                    is_active=True,
                    notes=f"Initial seed data for {province_name}"
                )
                created_count += 1
                action = "✓ Created"
            
            print(f"   {action} {credit_tier_display}: {final_rate}%")
        
        print()  # Blank line between provinces
    
    print("=" * 70)
    print(f"✅ Seeding complete!")
    print(f"   Created: {created_count} rates")
    print(f"   Updated: {updated_count} rates")
    print(f"   Total: {created_count + updated_count} interest rates in database")
    print()
    print("🔗 API Endpoints:")
    print("   GET /api/commissions/interest-rates/current/")
    print("   GET /api/commissions/interest-rates/current/?province=ON")
    print("   GET /api/commissions/interest-rates/by_tier/?province=ON&credit_tier=excellent")
    print()
    print("📝 Next steps:")
    print("   1. Run migrations: python manage.py migrate")
    print("   2. Test Financing.tsx with dynamic rates")
    print("   3. Access InterestRateManagement.tsx admin page")
    print("=" * 70)

if __name__ == '__main__':
    seed_interest_rates()
