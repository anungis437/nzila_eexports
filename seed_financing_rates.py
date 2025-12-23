"""
Seed default Canadian interest rates for financing calculator

Run: python seed_financing_rates.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from financing.models import InterestRate
from decimal import Decimal
import datetime

def seed_interest_rates():
    """
    Seed Canadian market interest rates (2025 rates)
    
    Based on Canadian prime rate (7.20% as of Dec 2025) plus spread by credit tier
    """
    
    print("🔄 Seeding Canadian interest rates...")
    
    # Clear existing rates
    InterestRate.objects.all().delete()
    print("   Cleared existing rates")
    
    # Rate structure: {credit_tier: base_rate}
    # Excellent: Prime + 0-2%
    # Good: Prime + 2-4%
    # Fair: Prime + 4-7%
    # Poor: Prime + 7-10%
    # Bad: Sub-prime (12-18%)
    
    rates_data = [
        # EXCELLENT (750+) - Best rates
        ('excellent', 12, Decimal('4.99')),
        ('excellent', 24, Decimal('5.49')),
        ('excellent', 36, Decimal('5.99')),
        ('excellent', 48, Decimal('6.49')),
        ('excellent', 60, Decimal('6.99')),
        ('excellent', 72, Decimal('7.49')),
        ('excellent', 84, Decimal('7.99')),
        
        # GOOD (650-749) - Competitive rates
        ('good', 12, Decimal('6.49')),
        ('good', 24, Decimal('6.99')),
        ('good', 36, Decimal('7.49')),
        ('good', 48, Decimal('7.99')),
        ('good', 60, Decimal('8.49')),
        ('good', 72, Decimal('8.99')),
        ('good', 84, Decimal('9.49')),
        
        # FAIR (600-649) - Moderate rates
        ('fair', 12, Decimal('8.49')),
        ('fair', 24, Decimal('8.99')),
        ('fair', 36, Decimal('9.49')),
        ('fair', 48, Decimal('9.99')),
        ('fair', 60, Decimal('10.49')),
        ('fair', 72, Decimal('10.99')),
        ('fair', 84, Decimal('11.49')),
        
        # POOR (550-599) - Higher rates
        ('poor', 12, Decimal('10.99')),
        ('poor', 24, Decimal('11.49')),
        ('poor', 36, Decimal('11.99')),
        ('poor', 48, Decimal('12.49')),
        ('poor', 60, Decimal('12.99')),
        ('poor', 72, Decimal('13.49')),
        ('poor', 84, Decimal('13.99')),
        
        # BAD (<550) - Sub-prime rates
        ('bad', 12, Decimal('14.99')),
        ('bad', 24, Decimal('15.49')),
        ('bad', 36, Decimal('15.99')),
        ('bad', 48, Decimal('16.49')),
        ('bad', 60, Decimal('16.99')),
        ('bad', 72, Decimal('17.49')),
        ('bad', 84, Decimal('17.99')),
    ]
    
    created_count = 0
    for credit_tier, loan_term_months, annual_interest_rate in rates_data:
        InterestRate.objects.create(
            credit_tier=credit_tier,
            loan_term_months=loan_term_months,
            annual_interest_rate=annual_interest_rate,
            effective_date=datetime.date.today(),
            is_active=True
        )
        created_count += 1
    
    print(f"✅ Created {created_count} interest rates")
    
    # Display rate summary
    print("\n📊 Interest Rate Summary (Canadian Market - Dec 2025):")
    print("-" * 70)
    
    for tier_code, tier_display in InterestRate.CREDIT_TIER_CHOICES:
        rates = InterestRate.objects.filter(credit_tier=tier_code).order_by('loan_term_months')
        if rates.exists():
            rate_range = f"{rates.first().annual_interest_rate}% - {rates.last().annual_interest_rate}%"
            print(f"  {tier_display:25s}: {rate_range}")
    
    print("-" * 70)
    print("✅ Interest rate seeding complete!\n")

if __name__ == '__main__':
    seed_interest_rates()
