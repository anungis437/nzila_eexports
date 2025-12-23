"""
Dealer Verification System Tests
Phase 3 - Feature 9

Tests for dealer licensing, verification, badge system, and trust scores.
Run: pytest test_dealer_verification.py -v
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

import pytest
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from accounts.models import User
from accounts.dealer_verification_models import DealerLicense, DealerVerification


@pytest.fixture
def cleanup():
    """Clean up test data before and after tests"""
    # Clean up before
    DealerLicense.objects.filter(dealer__email__contains='testdealer').delete()
    DealerVerification.objects.filter(dealer__email__contains='testdealer').delete()
    User.objects.filter(email__contains='testdealer').delete()
    User.objects.filter(email='admin@testdealer.com').delete()
    
    yield
    
    # Clean up after
    DealerLicense.objects.filter(dealer__email__contains='testdealer').delete()
    DealerVerification.objects.filter(dealer__email__contains='testdealer').delete()
    User.objects.filter(email__contains='testdealer').delete()
    User.objects.filter(email='admin@testdealer.com').delete()


@pytest.mark.django_db
def test_dealer_license_creation(cleanup):
    """Test 1: Create dealer license"""
    print("\n" + "="*60)
    print("TEST 1: Dealer License Creation")
    print("="*60)
    
    # Create dealer
    dealer = User.objects.create_user(
        username='ontariodealer',
        email='ontario@testdealer.com',
        password='test123',
        role='dealer',
        company_name='Ontario Motors'
    )
    
    # Create OMVIC license
    license = DealerLicense.objects.create(
        dealer=dealer,
        license_type='omvic',
        license_number='OMVIC-123456',
        issuing_authority='Ontario Motor Vehicle Industry Council',
        province='ON',
        issue_date=date(2020, 1, 1),
        expiry_date=date(2025, 12, 31),
        status='pending'
    )
    
    assert license.dealer == dealer
    assert license.license_type == 'omvic'
    assert license.status == 'pending'
    assert not license.is_expired
    assert license.days_until_expiry > 0
    
    print(f"✓ License created: {license}")
    print(f"✓ Status: {license.get_status_display()}")
    print(f"✓ Expires in: {license.days_until_expiry} days")
    print(f"✓ Is expired: {license.is_expired}")
    print("="*60)


@pytest.mark.django_db
def test_license_expiration_check(cleanup):
    """Test 2: License expiration detection"""
    print("\n" + "="*60)
    print("TEST 2: License Expiration Detection")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='expireddealer',
        email='expired@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    # Create expired license
    expired_license = DealerLicense.objects.create(
        dealer=dealer,
        license_type='amvic',
        license_number='AMVIC-789',
        issuing_authority='AMVIC',
        province='AB',
        issue_date=date(2020, 1, 1),
        expiry_date=date(2023, 12, 31),  # Already expired
        status='verified'
    )
    
    # Create license expiring soon (25 days)
    expiring_license = DealerLicense.objects.create(
        dealer=dealer,
        license_type='business',
        license_number='BN-456',
        issuing_authority='CRA',
        province='AB',
        issue_date=date(2023, 1, 1),
        expiry_date=date.today() + timedelta(days=25),
        status='verified'
    )
    
    assert expired_license.is_expired
    assert expired_license.days_until_expiry < 0
    assert expiring_license.expires_soon
    assert not expiring_license.is_expired
    
    print(f"✓ Expired license detected: {expired_license.is_expired}")
    print(f"✓ Days past expiry: {abs(expired_license.days_until_expiry)}")
    print(f"✓ Expiring soon detected: {expiring_license.expires_soon}")
    print(f"✓ Days until expiry: {expiring_license.days_until_expiry}")
    print("="*60)


@pytest.mark.django_db
def test_license_approval_workflow(cleanup):
    """Test 3: License approval workflow"""
    print("\n" + "="*60)
    print("TEST 3: License Approval Workflow")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='approvaldealer',
        email='approval@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    admin = User.objects.create_user(
        username='adminuser',
        email='admin@testdealer.com',
        password='test123',
        role='admin'
    )
    
    license = DealerLicense.objects.create(
        dealer=dealer,
        license_type='omvic',
        license_number='OMVIC-999',
        issuing_authority='OMVIC',
        province='ON',
        issue_date=date.today(),
        expiry_date=date.today() + timedelta(days=365),
        status='pending'
    )
    
    # Approve license
    license.approve(admin)
    
    assert license.status == 'verified'
    assert license.verified_by == admin
    assert license.verified_at is not None
    
    print(f"✓ License approved by: {license.verified_by.username}")
    print(f"✓ Approval time: {license.verified_at}")
    print(f"✓ Final status: {license.get_status_display()}")
    print("="*60)


@pytest.mark.django_db
def test_license_rejection_workflow(cleanup):
    """Test 4: License rejection workflow"""
    print("\n" + "="*60)
    print("TEST 4: License Rejection Workflow")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='rejecteddealer',
        email='rejected@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    admin = User.objects.create_user(
        username='adminrej',
        email='adminrej@testdealer.com',
        password='test123',
        role='admin'
    )
    
    license = DealerLicense.objects.create(
        dealer=dealer,
        license_type='omvic',
        license_number='OMVIC-INVALID',
        issuing_authority='OMVIC',
        province='ON',
        issue_date=date.today(),
        expiry_date=date.today() + timedelta(days=365),
        status='pending'
    )
    
    # Reject license
    rejection_reason = 'License number could not be verified with OMVIC database'
    license.reject(admin, rejection_reason)
    
    assert license.status == 'rejected'
    assert license.rejection_reason == rejection_reason
    assert license.verified_by == admin
    
    print(f"✓ License rejected by: {license.verified_by.username}")
    print(f"✓ Rejection reason: {license.rejection_reason}")
    print(f"✓ Final status: {license.get_status_display()}")
    print("="*60)


@pytest.mark.django_db
def test_dealer_verification_creation(cleanup):
    """Test 5: Dealer verification creation"""
    print("\n" + "="*60)
    print("TEST 5: Dealer Verification Creation")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='verifydealer',
        email='verify@testdealer.com',
        password='test123',
        role='dealer',
        company_name='Toronto Auto Sales'
    )
    
    verification = DealerVerification.objects.create(
        dealer=dealer,
        business_name='Toronto Auto Sales Inc.',
        business_number='123456789RC0001',
        years_in_business=5,
        business_start_date=date(2019, 1, 1),
        has_insurance=True,
        insurance_provider='Intact Insurance',
        insurance_policy_number='POL-789456',
        insurance_expiry=date.today() + timedelta(days=180)
    )
    
    assert verification.dealer == dealer
    assert verification.status == 'unverified'
    assert verification.badge == 'none'
    assert verification.trust_score == 0
    
    print(f"✓ Verification created for: {verification.dealer.company_name}")
    print(f"✓ Status: {verification.get_status_display()}")
    print(f"✓ Badge: {verification.get_badge_display()}")
    print(f"✓ Trust score: {verification.trust_score}/100")
    print("="*60)


@pytest.mark.django_db
def test_trust_score_calculation(cleanup):
    """Test 6: Trust score calculation"""
    print("\n" + "="*60)
    print("TEST 6: Trust Score Calculation")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='trustdealer',
        email='trust@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    verification = DealerVerification.objects.create(
        dealer=dealer,
        license_verified=True,  # 20 points
        insurance_verified=True,  # 15 points
        business_verified=True,  # 10 points
        identity_verified=True,  # 10 points
        address_verified=True,  # 5 points
        years_in_business=5,  # 12 points (5+ years)
        total_sales=75,  # 8 points (50+ sales)
        average_rating=Decimal('4.6'),  # 8 points (4.5+ rating)
        total_reviews=25  # 4 points (20+ reviews)
    )
    
    calculated_score = verification.calculate_trust_score()
    expected_score = 20 + 15 + 10 + 10 + 5 + 12 + 8 + 8 + 4  # 92 points
    
    assert calculated_score == expected_score
    assert calculated_score == 92
    
    # Update metrics
    verification.update_metrics()
    
    assert verification.trust_score == 92
    
    print(f"✓ Verification checks: 5/5 (60 points)")
    print(f"✓ Years in business: 5 years (12 points)")
    print(f"✓ Sales volume: 75 sales (8 points)")
    print(f"✓ Average rating: 4.6/5 (8 points)")
    print(f"✓ Total reviews: 25 (4 points)")
    print(f"✓ TOTAL TRUST SCORE: {verification.trust_score}/100")
    print("="*60)


@pytest.mark.django_db
def test_badge_calculation_gold(cleanup):
    """Test 7: Gold badge calculation (5/5 verifications)"""
    print("\n" + "="*60)
    print("TEST 7: Gold Badge Calculation")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='golddealer',
        email='gold@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    verification = DealerVerification.objects.create(
        dealer=dealer,
        license_verified=True,
        insurance_verified=True,
        business_verified=True,
        identity_verified=True,
        address_verified=True
    )
    
    badge = verification.calculate_badge()
    
    assert badge == 'gold'
    
    verification.update_metrics()
    
    assert verification.badge == 'gold'
    
    print(f"✓ License verified: {verification.license_verified}")
    print(f"✓ Insurance verified: {verification.insurance_verified}")
    print(f"✓ Business verified: {verification.business_verified}")
    print(f"✓ Identity verified: {verification.identity_verified}")
    print(f"✓ Address verified: {verification.address_verified}")
    print(f"✓ BADGE: 🥇 {verification.get_badge_display()}")
    print("="*60)


@pytest.mark.django_db
def test_badge_calculation_silver(cleanup):
    """Test 8: Silver badge calculation (3/5 verifications)"""
    print("\n" + "="*60)
    print("TEST 8: Silver Badge Calculation")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='silverdealer',
        email='silver@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    verification = DealerVerification.objects.create(
        dealer=dealer,
        license_verified=True,
        insurance_verified=True,
        business_verified=True,
        identity_verified=False,
        address_verified=False
    )
    
    badge = verification.calculate_badge()
    
    assert badge == 'silver'
    
    verification.update_metrics()
    
    assert verification.badge == 'silver'
    
    print(f"✓ License verified: {verification.license_verified}")
    print(f"✓ Insurance verified: {verification.insurance_verified}")
    print(f"✓ Business verified: {verification.business_verified}")
    print(f"✓ Identity verified: {verification.identity_verified}")
    print(f"✓ Address verified: {verification.address_verified}")
    print(f"✓ BADGE: 🥈 {verification.get_badge_display()}")
    print("="*60)


@pytest.mark.django_db
def test_badge_calculation_bronze(cleanup):
    """Test 9: Bronze badge calculation (2/5 verifications)"""
    print("\n" + "="*60)
    print("TEST 9: Bronze Badge Calculation")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='bronzedealer',
        email='bronze@testdealer.com',
        password='test123',
        role='dealer'
    )
    
    verification = DealerVerification.objects.create(
        dealer=dealer,
        license_verified=True,
        insurance_verified=True,
        business_verified=False,
        identity_verified=False,
        address_verified=False
    )
    
    badge = verification.calculate_badge()
    
    assert badge == 'bronze'
    
    verification.update_metrics()
    
    assert verification.badge == 'bronze'
    
    print(f"✓ License verified: {verification.license_verified}")
    print(f"✓ Insurance verified: {verification.insurance_verified}")
    print(f"✓ Business verified: {verification.business_verified}")
    print(f"✓ Identity verified: {verification.identity_verified}")
    print(f"✓ Address verified: {verification.address_verified}")
    print(f"✓ BADGE: 🥉 {verification.get_badge_display()}")
    print("="*60)


@pytest.mark.django_db
def test_dealer_verification_workflow(cleanup):
    """Test 10: Complete dealer verification workflow"""
    print("\n" + "="*60)
    print("TEST 10: Complete Dealer Verification Workflow")
    print("="*60)
    
    dealer = User.objects.create_user(
        username='completedelearworkflow',
        email='complete@testdealer.com',
        password='test123',
        role='dealer',
        company_name='Complete Auto Group'
    )
    
    admin = User.objects.create_user(
        username='adminverify',
        email='adminverify@testdealer.com',
        password='test123',
        role='admin'
    )
    
    # Step 1: Create verification
    verification = DealerVerification.objects.create(
        dealer=dealer,
        business_name='Complete Auto Group Inc.',
        business_number='987654321RC0001',
        years_in_business=10,
        business_start_date=date(2014, 6, 1),
        has_insurance=True,
        total_sales=150,
        total_revenue=Decimal('5500000.00'),
        average_rating=Decimal('4.8'),
        total_reviews=75
    )
    
    print(f"Step 1: Verification created")
    print(f"  Status: {verification.get_status_display()}")
    print(f"  Badge: {verification.get_badge_display()}")
    print(f"  Trust score: {verification.trust_score}/100")
    
    # Step 2: Submit license
    license = DealerLicense.objects.create(
        dealer=dealer,
        license_type='omvic',
        license_number='OMVIC-COMPLETE',
        issuing_authority='OMVIC',
        province='ON',
        issue_date=date(2014, 6, 1),
        expiry_date=date.today() + timedelta(days=365),
        status='pending'
    )
    
    print(f"\nStep 2: License submitted")
    print(f"  License: {license.license_number}")
    print(f"  Status: {license.get_status_display()}")
    
    # Step 3: Admin approves license
    license.approve(admin)
    verification.license_verified = True
    verification.insurance_verified = True
    verification.business_verified = True
    verification.identity_verified = True
    verification.address_verified = True
    verification.update_metrics()
    
    print(f"\nStep 3: All verifications completed")
    print(f"  License status: {license.get_status_display()}")
    print(f"  Verification percentage: {verification.verification_percentage}%")
    print(f"  Trust score: {verification.trust_score}/100")
    print(f"  Badge: {verification.get_badge_display()}")
    
    # Step 4: Verify dealer
    verification.verify_dealer(admin)
    
    print(f"\nStep 4: Dealer verified")
    print(f"  Status: {verification.get_status_display()}")
    print(f"  Verified by: {verification.verified_by.username}")
    print(f"  Verified at: {verification.verified_at}")
    
    assert verification.status == 'verified'
    assert verification.badge == 'gold'
    assert verification.trust_score == 100  # Perfect score
    assert verification.verification_percentage == 100
    assert license.status == 'verified'
    
    print(f"\n✓ VERIFICATION COMPLETE!")
    print(f"✓ Final badge: 🥇 {verification.get_badge_display()}")
    print(f"✓ Final trust score: {verification.trust_score}/100")
    print("="*60)


if __name__ == '__main__':
    import sys
    
    pytest.main([__file__, '-v', '--tb=short'] + sys.argv[1:])
