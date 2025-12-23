"""
PHASE 3 - Feature 7: Financing Calculator Enhancement Tests

Comprehensive test suite for financing calculator functionality:
- Interest rate management
- Loan scenario calculations
- Trade-in value estimation
- Quick payment calculator
- Scenario comparison

Run: python test_financing.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from financing.models import InterestRate, LoanScenario, TradeInEstimate
from accounts.models import User
from vehicles.models import Vehicle
from decimal import Decimal
import datetime

def clean_test_data():
    """Remove any existing test data"""
    LoanScenario.objects.filter(buyer__email='financing_test_buyer@example.com').delete()
    TradeInEstimate.objects.filter(buyer__email='financing_test_buyer@example.com').delete()
    User.objects.filter(email='financing_test_buyer@example.com').delete()
    Vehicle.objects.filter(vin='TESTFINANCINGVIN001').delete()

def test_1_interest_rate_retrieval():
    """Test 1: Retrieve interest rates by credit tier and loan term"""
    print("\n1. Testing interest rate retrieval...")
    
    # Get rate for excellent credit, 48-month term
    rate = InterestRate.objects.filter(
        credit_tier='excellent',
        loan_term_months=48,
        is_active=True
    ).first()
    
    assert rate is not None, "Rate not found"
    assert rate.annual_interest_rate == Decimal('6.49'), f"Expected 6.49%, got {rate.annual_interest_rate}%"
    
    print(f"   ✓ Interest rate retrieved: {rate.get_credit_tier_display()} - {rate.loan_term_months}mo @ {rate.annual_interest_rate}%")
    print(f"   ✓ Monthly rate: {rate.monthly_interest_rate:.6f}%")
    return True

def test_2_loan_scenario_creation():
    """Test 2: Create loan scenario and calculate payments"""
    print("\n2. Testing loan scenario creation...")
    
    # Create test buyer
    buyer = User.objects.create_user(
        username='financing_test_buyer',
        email='financing_test_buyer@example.com',
        password='testpass123',
        role='buyer',
        first_name='Test',
        last_name='Buyer'
    )
    
    # Create test vehicle
    dealer = User.objects.filter(role='dealer').first()
    if not dealer:
        dealer = User.objects.create_user(
            username='test_dealer',
            email='test_dealer@example.com',
            password='testpass123',
            role='dealer'
        )
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTFINANCINGVIN001',
        year=2022,
        make='Toyota',
        model='Camry',
        price_cad=Decimal('32000.00'),
        mileage=25000,
        color='Blue',
        location='Toronto, ON',
        status='available'
    )
    
    # Create loan scenario
    scenario = LoanScenario.objects.create(
        buyer=buyer,
        vehicle=vehicle,
        vehicle_price=Decimal('32000.00'),
        down_payment=Decimal('6400.00'),  # 20% down
        trade_in_value=Decimal('0.00'),
        loan_term_months=60,
        credit_tier='good',
        province='ON',
        scenario_name='60-month good credit scenario'
    )
    
    # Calculate
    scenario.calculate()
    
    print(f"   ✓ Scenario created: ${scenario.vehicle_price:,.2f} vehicle")
    print(f"   ✓ Down payment: ${scenario.down_payment:,.2f} ({scenario.down_payment_percentage}%)")
    print(f"   ✓ Loan amount: ${scenario.loan_amount:,.2f}")
    print(f"   ✓ Monthly payment: ${scenario.monthly_payment:,.2f}")
    print(f"   ✓ Interest rate: {scenario.annual_interest_rate}%")
    print(f"   ✓ Total interest: ${scenario.total_interest:,.2f}")
    print(f"   ✓ Total cost: ${scenario.total_cost:,.2f}")
    
    assert scenario.monthly_payment > 0, "Monthly payment should be greater than 0"
    assert scenario.total_interest > 0, "Total interest should be greater than 0"
    assert scenario.loan_amount > 0, "Loan amount should be greater than 0"
    
    return scenario

def test_3_provincial_tax_calculation():
    """Test 3: Verify provincial tax calculations"""
    print("\n3. Testing provincial tax calculations...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    
    # Test Ontario (13% HST)
    scenario_on = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=Decimal('30000.00'),
        down_payment=Decimal('0.00'),
        trade_in_value=Decimal('0.00'),
        loan_term_months=48,
        credit_tier='good',
        province='ON',
        scenario_name='Ontario HST test'
    )
    scenario_on.calculate()
    
    expected_hst = Decimal('3900.00')  # 13% of 30,000
    assert scenario_on.gst_hst_amount == expected_hst, f"Expected ${expected_hst}, got ${scenario_on.gst_hst_amount}"
    print(f"   ✓ Ontario (HST 13%): ${scenario_on.gst_hst_amount:,.2f}")
    
    # Test British Columbia (5% GST + 7% PST)
    scenario_bc = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=Decimal('30000.00'),
        down_payment=Decimal('0.00'),
        trade_in_value=Decimal('0.00'),
        loan_term_months=48,
        credit_tier='good',
        province='BC',
        scenario_name='BC GST+PST test'
    )
    scenario_bc.calculate()
    
    expected_gst = Decimal('1500.00')  # 5% of 30,000
    expected_pst = Decimal('2100.00')  # 7% of 30,000
    assert scenario_bc.gst_hst_amount == expected_gst, f"Expected ${expected_gst}, got ${scenario_bc.gst_hst_amount}"
    assert scenario_bc.pst_amount == expected_pst, f"Expected ${expected_pst}, got ${scenario_bc.pst_amount}"
    print(f"   ✓ British Columbia (GST 5% + PST 7%): GST ${scenario_bc.gst_hst_amount:,.2f} + PST ${scenario_bc.pst_amount:,.2f}")
    
    # Test Alberta (5% GST only)
    scenario_ab = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=Decimal('30000.00'),
        down_payment=Decimal('0.00'),
        trade_in_value=Decimal('0.00'),
        loan_term_months=48,
        credit_tier='good',
        province='AB',
        scenario_name='Alberta GST only test'
    )
    scenario_ab.calculate()
    
    expected_gst_ab = Decimal('1500.00')  # 5% of 30,000
    assert scenario_ab.gst_hst_amount == expected_gst_ab, f"Expected ${expected_gst_ab}, got ${scenario_ab.gst_hst_amount}"
    assert scenario_ab.pst_amount == Decimal('0.00'), f"Alberta should have no PST"
    print(f"   ✓ Alberta (GST 5% only): ${scenario_ab.gst_hst_amount:,.2f} (no PST)")
    
    return True

def test_4_down_payment_scenarios():
    """Test 4: Test different down payment scenarios"""
    print("\n4. Testing down payment scenarios...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    vehicle_price = Decimal('25000.00')
    
    # 0% down
    scenario_0 = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=vehicle_price,
        down_payment=Decimal('0.00'),
        trade_in_value=Decimal('0.00'),
        loan_term_months=48,
        credit_tier='good',
        province='ON',
        scenario_name='0% down'
    )
    scenario_0.calculate()
    
    # 20% down
    scenario_20 = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=vehicle_price,
        down_payment=vehicle_price * Decimal('0.20'),
        trade_in_value=Decimal('0.00'),
        loan_term_months=48,
        credit_tier='good',
        province='ON',
        scenario_name='20% down'
    )
    scenario_20.calculate()
    
    print(f"   ✓ 0% down - Monthly: ${scenario_0.monthly_payment:,.2f}, LTV: {scenario_0.loan_to_value_ratio}%")
    print(f"   ✓ 20% down - Monthly: ${scenario_20.monthly_payment:,.2f}, LTV: {scenario_20.loan_to_value_ratio}%")
    print(f"   ✓ Savings with 20% down: ${scenario_0.monthly_payment - scenario_20.monthly_payment:,.2f}/month")
    
    assert scenario_20.monthly_payment < scenario_0.monthly_payment, "20% down should have lower monthly payment"
    assert scenario_20.loan_to_value_ratio < scenario_0.loan_to_value_ratio, "20% down should have lower LTV"
    
    return True

def test_5_trade_in_estimation():
    """Test 5: Test trade-in value estimation"""
    print("\n5. Testing trade-in value estimation...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    
    # Generate estimate using mock KBB algorithm
    estimates = TradeInEstimate.generate_estimate(
        year=2019,
        make='Honda',
        model='Civic',
        mileage=65000,
        condition='good',
        province='ON'
    )
    
    # Create trade-in estimate with values
    estimate = TradeInEstimate.objects.create(
        buyer=buyer,
        year=2019,
        make='Honda',
        model='Civic',
        trim='LX',
        mileage=65000,
        condition='good',
        province='ON',
        notes='Clean vehicle, regular maintenance',
        trade_in_value=estimates['trade_in_value'],
        private_party_value=estimates['private_party_value'],
        retail_value=estimates['retail_value']
    )
    
    print(f"   ✓ Vehicle: {estimate.year} {estimate.make} {estimate.model}")
    print(f"   ✓ Mileage: {estimate.mileage:,} km")
    print(f"   ✓ Condition: {estimate.get_condition_display()}")
    print(f"   ✓ Trade-in value: ${estimate.trade_in_value:,.2f}")
    print(f"   ✓ Private party value: ${estimate.private_party_value:,.2f}")
    print(f"   ✓ Retail value: ${estimate.retail_value:,.2f}")
    
    assert estimate.trade_in_value > 0, "Trade-in value should be greater than 0"
    assert estimate.private_party_value > estimate.trade_in_value, "Private party value should be higher than trade-in"
    assert estimate.retail_value > estimate.private_party_value, "Retail value should be highest"
    
    return estimate

def test_6_loan_with_trade_in():
    """Test 6: Loan scenario with trade-in"""
    print("\n6. Testing loan scenario with trade-in...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    
    # Create scenario with trade-in
    scenario = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=Decimal('30000.00'),
        down_payment=Decimal('3000.00'),  # $3k cash down
        trade_in_value=Decimal('8000.00'),  # $8k trade-in
        loan_term_months=60,
        credit_tier='good',
        province='ON',
        scenario_name='With trade-in'
    )
    scenario.calculate()
    
    total_upfront = scenario.down_payment + scenario.trade_in_value
    
    print(f"   ✓ Vehicle price: ${scenario.vehicle_price:,.2f}")
    print(f"   ✓ Cash down: ${scenario.down_payment:,.2f}")
    print(f"   ✓ Trade-in: ${scenario.trade_in_value:,.2f}")
    print(f"   ✓ Total upfront: ${total_upfront:,.2f}")
    print(f"   ✓ Loan amount: ${scenario.loan_amount:,.2f}")
    print(f"   ✓ Monthly payment: ${scenario.monthly_payment:,.2f}")
    
    assert scenario.loan_amount < scenario.vehicle_price, "Loan amount should be less than vehicle price with down payment"
    
    return True

def test_7_credit_tier_comparison():
    """Test 7: Compare monthly payments across credit tiers"""
    print("\n7. Testing credit tier comparison...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    vehicle_price = Decimal('28000.00')
    
    scenarios = {}
    for tier_code, tier_display in InterestRate.CREDIT_TIER_CHOICES:
        scenario = LoanScenario.objects.create(
            buyer=buyer,
            vehicle_price=vehicle_price,
            down_payment=Decimal('0.00'),
            trade_in_value=Decimal('0.00'),
            loan_term_months=60,
            credit_tier=tier_code,
            province='ON',
            scenario_name=f'{tier_display} credit'
        )
        scenario.calculate()
        scenarios[tier_code] = scenario
    
    print(f"   ✓ Vehicle price: ${vehicle_price:,.2f}, 60-month term, 0% down, Ontario")
    print(f"   ✓ Credit tier impact on monthly payment:")
    
    for tier_code, tier_display in InterestRate.CREDIT_TIER_CHOICES:
        scenario = scenarios[tier_code]
        print(f"      • {tier_display:25s}: ${scenario.monthly_payment:>8,.2f}/mo @ {scenario.annual_interest_rate}%")
    
    # Verify excellent credit has lowest payment
    assert scenarios['excellent'].monthly_payment < scenarios['bad'].monthly_payment, \
        "Excellent credit should have lower payment than bad credit"
    
    payment_difference = scenarios['bad'].monthly_payment - scenarios['excellent'].monthly_payment
    print(f"   ✓ Difference (excellent vs bad): ${payment_difference:,.2f}/month")
    
    return True

def test_8_loan_term_comparison():
    """Test 8: Compare monthly payments across loan terms"""
    print("\n8. Testing loan term comparison...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    vehicle_price = Decimal('35000.00')
    
    print(f"   ✓ Vehicle price: ${vehicle_price:,.2f}, Good credit, 0% down, Ontario")
    print(f"   ✓ Loan term impact on monthly payment:")
    
    for loan_term in [12, 24, 36, 48, 60, 72, 84]:
        scenario = LoanScenario.objects.create(
            buyer=buyer,
            vehicle_price=vehicle_price,
            down_payment=Decimal('0.00'),
            trade_in_value=Decimal('0.00'),
            loan_term_months=loan_term,
            credit_tier='good',
            province='ON',
            scenario_name=f'{loan_term}-month term'
        )
        scenario.calculate()
        
        print(f"      • {loan_term:2d} months: ${scenario.monthly_payment:>8,.2f}/mo (total interest: ${scenario.total_interest:>10,.2f})")
    
    return True

def test_9_scenario_favorite_toggle():
    """Test 9: Test favorite scenario functionality"""
    print("\n9. Testing favorite scenario toggle...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    
    scenario = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=Decimal('25000.00'),
        down_payment=Decimal('5000.00'),
        trade_in_value=Decimal('0.00'),
        loan_term_months=48,
        credit_tier='good',
        province='ON',
        scenario_name='Favorite test scenario',
        is_favorite=False
    )
    
    print(f"   ✓ Created scenario: {scenario.scenario_name}")
    print(f"   ✓ Initial favorite status: {scenario.is_favorite}")
    
    # Toggle favorite
    scenario.is_favorite = True
    scenario.save()
    
    # Verify
    scenario.refresh_from_db()
    assert scenario.is_favorite == True, "Scenario should be marked as favorite"
    print(f"   ✓ After toggle: {scenario.is_favorite}")
    
    return True

def test_10_quick_calculation_validation():
    """Test 10: Test calculation validation and edge cases"""
    print("\n10. Testing calculation validation...")
    
    buyer = User.objects.get(email='financing_test_buyer@example.com')
    
    # Test: Down payment + trade-in equals vehicle price (no loan needed)
    scenario_full_payment = LoanScenario.objects.create(
        buyer=buyer,
        vehicle_price=Decimal('20000.00'),
        down_payment=Decimal('12000.00'),
        trade_in_value=Decimal('8000.00'),
        loan_term_months=48,
        credit_tier='good',
        province='ON',
        scenario_name='Full payment test'
    )
    scenario_full_payment.calculate()
    
    print(f"   ✓ Full payment scenario (no loan needed):")
    print(f"      • Vehicle price: ${scenario_full_payment.vehicle_price:,.2f}")
    print(f"      • Down + trade-in: ${scenario_full_payment.down_payment + scenario_full_payment.trade_in_value:,.2f}")
    print(f"      • Loan amount: ${scenario_full_payment.loan_amount:,.2f}")
    print(f"      • Monthly payment: ${scenario_full_payment.monthly_payment:,.2f}")
    
    assert scenario_full_payment.loan_amount <= 0 or scenario_full_payment.loan_amount == scenario_full_payment.pst_amount + scenario_full_payment.gst_hst_amount + scenario_full_payment.documentation_fee + scenario_full_payment.license_registration_fee, \
        "No loan should be needed when down payment + trade-in cover vehicle price"
    
    return True

def run_all_tests():
    """Run all financing calculator tests"""
    print("=" * 80)
    print("PHASE 3 - Feature 7: Financing Calculator Enhancement Tests")
    print("=" * 80)
    
    # Clean any existing test data
    print("\nCleaning up test data...")
    clean_test_data()
    
    tests = [
        test_1_interest_rate_retrieval,
        test_2_loan_scenario_creation,
        test_3_provincial_tax_calculation,
        test_4_down_payment_scenarios,
        test_5_trade_in_estimation,
        test_6_loan_with_trade_in,
        test_7_credit_tier_comparison,
        test_8_loan_term_comparison,
        test_9_scenario_favorite_toggle,
        test_10_quick_calculation_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"   ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"   ✗ Test error: {e}")
            failed += 1
    
    # Cleanup
    print("\nCleaning up test data...")
    clean_test_data()
    
    print("\n" + "=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✓ All tests passed! Financing calculator is working correctly.")
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
