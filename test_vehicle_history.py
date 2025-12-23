"""
PHASE 3 - Feature 8: Vehicle History Integration Tests

Comprehensive test suite for vehicle history functionality:
- Vehicle history report generation
- Accident record tracking
- Service record management
- Title status verification
- Trust score calculation

Run: python test_vehicle_history.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicle_history.models import VehicleHistoryReport, AccidentRecord, ServiceRecord, OwnershipRecord
from accounts.models import User
from vehicles.models import Vehicle
from decimal import Decimal
from datetime import date, timedelta

def clean_test_data():
    """Remove any existing test data"""
    VehicleHistoryReport.objects.filter(vehicle__vin__startswith='TESTHIST').delete()
    Vehicle.objects.filter(vin__startswith='TESTHIST').delete()
    User.objects.filter(email='vehicle_history_test_dealer@example.com').delete()

def test_1_clean_title_vehicle():
    """Test 1: Create clean title vehicle history report"""
    print("\n1. Testing clean title vehicle history...")
    
    # Create test dealer
    dealer = User.objects.create_user(
        username='vehicle_history_test_dealer',
        email='vehicle_history_test_dealer@example.com',
        password='testpass123',
        role='dealer'
    )
    
    # Create test vehicle
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST001',
        year=2020,
        make='Honda',
        model='Accord',
        price_cad=Decimal('28000.00'),
        mileage=35000,
        color='Silver',
        location='Toronto, ON',
        status='available'
    )
    
    # Create clean history report
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        title_issue_date=date(2020, 3, 15),
        title_state='Ontario',
        accident_severity='none',
        total_accidents=0,
        total_owners=1,
        personal_use=True,
        rental_use=False,
        taxi_use=False,
        police_use=False,
        odometer_rollback=False,
        odometer_verified=True,
        last_odometer_reading=35000,
        last_odometer_date=date.today(),
        total_service_records=8,
        last_service_date=date.today() - timedelta(days=30),
        recalls_outstanding=0,
        structural_damage=False,
        frame_damage=False,
        airbag_deployment=False,
        report_source='carfax',
        report_confidence='high'
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ VIN: {vehicle.vin}")
    print(f"   ✓ Title status: {report.get_title_status_display()}")
    print(f"   ✓ Accident severity: {report.get_accident_severity_display()}")
    print(f"   ✓ Total owners: {report.total_owners}")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    print(f"   ✓ Is clean title: {report.is_clean_title}")
    print(f"   ✓ Has accidents: {report.has_accidents}")
    print(f"   ✓ Is one owner: {report.is_one_owner}")
    
    assert report.is_clean_title, "Should have clean title"
    assert not report.has_accidents, "Should have no accidents"
    assert report.is_one_owner, "Should be one owner"
    assert report.trust_score == 100, f"Clean vehicle should have 100 trust score, got {report.trust_score}"
    
    return report

def test_2_accident_history():
    """Test 2: Vehicle with accident history"""
    print("\n2. Testing vehicle with accident history...")
    
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    # Create vehicle with accident history
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST002',
        year=2019,
        make='Toyota',
        model='Camry',
        price_cad=Decimal('24000.00'),
        mileage=55000,
        color='Blue',
        location='Vancouver, BC',
        status='available'
    )
    
    # Create history report with moderate accident
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        accident_severity='moderate',
        total_accidents=1,
        last_accident_date=date(2021, 6, 15),
        total_owners=2,
        personal_use=True,
        odometer_verified=True,
        last_odometer_reading=55000,
        total_service_records=12,
        structural_damage=False,
        frame_damage=False,
        airbag_deployment=True,
        report_source='autocheck',
        report_confidence='high'
    )
    
    # Add accident record
    accident = AccidentRecord.objects.create(
        history_report=report,
        accident_date=date(2021, 6, 15),
        damage_severity='moderate',
        damage_location='Front end',
        estimated_damage_cost=Decimal('8500.00'),
        airbag_deployed=True,
        towed=True,
        police_report_filed=True,
        insurance_claim_filed=True
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Accident severity: {report.get_accident_severity_display()}")
    print(f"   ✓ Total accidents: {report.total_accidents}")
    print(f"   ✓ Last accident: {report.last_accident_date}")
    print(f"   ✓ Airbag deployment: {report.airbag_deployment}")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    
    assert report.has_accidents, "Should have accident history"
    assert report.trust_score < 100, "Accident should lower trust score"
    assert report.trust_score == 75, f"Expected trust score of 75 (100 - 15 moderate - 10 airbag), got {report.trust_score}"
    
    return report

def test_3_salvage_title():
    """Test 3: Salvage title vehicle"""
    print("\n3. Testing salvage title vehicle...")
    
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    # Create salvage title vehicle
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST003',
        year=2018,
        make='Ford',
        model='F-150',
        price_cad=Decimal('18000.00'),
        mileage=75000,
        color='Red',
        location='Calgary, AB',
        status='available'
    )
    
    # Create salvage title report
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='salvage',
        accident_severity='severe',
        total_accidents=1,
        last_accident_date=date(2020, 9, 10),
        total_owners=3,
        personal_use=True,
        odometer_verified=True,
        last_odometer_reading=75000,
        total_service_records=15,
        structural_damage=True,
        frame_damage=True,
        airbag_deployment=True,
        report_source='manual',
        report_confidence='medium'
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Title status: {report.get_title_status_display()}")
    print(f"   ✓ Accident severity: {report.get_accident_severity_display()}")
    print(f"   ✓ Structural damage: {report.structural_damage}")
    print(f"   ✓ Frame damage: {report.frame_damage}")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    
    assert not report.is_clean_title, "Should not have clean title"
    assert report.has_accidents, "Should have accident history"
    assert report.trust_score < 50, f"Salvage title should have low trust score, got {report.trust_score}"
    
    # Expected: 100 - 40 (salvage) - 25 (severe) - 10 (3 owners) - 20 (structural/frame) - 10 (airbag) = -5 -> 0
    assert report.trust_score == 0, f"Expected trust score of 0, got {report.trust_score}"
    
    return report

def test_4_rental_fleet_vehicle():
    """Test 4: Rental/fleet vehicle"""
    print("\n4. Testing rental/fleet vehicle...")
    
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST004',
        year=2021,
        make='Nissan',
        model='Altima',
        price_cad=Decimal('22000.00'),
        mileage=45000,
        color='White',
        location='Montreal, QC',
        status='available'
    )
    
    # Create rental fleet report
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        accident_severity='none',
        total_accidents=0,
        total_owners=1,
        personal_use=False,
        rental_use=True,
        taxi_use=False,
        police_use=False,
        odometer_verified=True,
        last_odometer_reading=45000,
        total_service_records=20,
        structural_damage=False,
        frame_damage=False,
        airbag_deployment=False,
        report_source='carfax',
        report_confidence='high'
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Rental use: {report.rental_use}")
    print(f"   ✓ Has commercial use: {report.has_commercial_use}")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    
    assert report.has_commercial_use, "Should have commercial use"
    assert report.trust_score == 90, f"Rental vehicle should have trust score of 90 (100 - 10 rental), got {report.trust_score}"
    
    return report

def test_5_taxi_vehicle():
    """Test 5: Taxi/rideshare vehicle"""
    print("\n5. Testing taxi/rideshare vehicle...")
    
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST005',
        year=2017,
        make='Toyota',
        model='Prius',
        price_cad=Decimal('15000.00'),
        mileage=185000,
        color='Black',
        location='Toronto, ON',
        status='available'
    )
    
    # Create taxi report
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        accident_severity='minor',
        total_accidents=2,
        total_owners=2,
        personal_use=False,
        rental_use=False,
        taxi_use=True,
        police_use=False,
        odometer_verified=True,
        last_odometer_reading=185000,
        total_service_records=35,
        structural_damage=False,
        frame_damage=False,
        airbag_deployment=False,
        report_source='manual',
        report_confidence='medium'
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Taxi use: {report.taxi_use}")
    print(f"   ✓ Total accidents: {report.total_accidents}")
    print(f"   ✓ Mileage: {vehicle.mileage:,} km")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    
    assert report.taxi_use, "Should be taxi vehicle"
    # Expected: 100 - 5 (minor) - 10 (2 owners) - 20 (taxi) = 65
    assert report.trust_score == 65, f"Expected trust score of 65, got {report.trust_score}"
    
    return report

def test_6_odometer_rollback():
    """Test 6: Odometer rollback detected"""
    print("\n6. Testing odometer rollback...")
    
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST006',
        year=2019,
        make='Chevrolet',
        model='Equinox',
        price_cad=Decimal('20000.00'),
        mileage=45000,
        color='Gray',
        location='Halifax, NS',
        status='available'
    )
    
    # Create report with odometer rollback
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        accident_severity='none',
        total_accidents=0,
        total_owners=2,
        personal_use=True,
        odometer_rollback=True,
        odometer_verified=False,
        last_odometer_reading=45000,
        total_service_records=10,
        structural_damage=False,
        frame_damage=False,
        airbag_deployment=False,
        report_source='carfax',
        report_confidence='low'
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Odometer rollback: {report.odometer_rollback}")
    print(f"   ✓ Odometer verified: {report.odometer_verified}")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    
    assert report.odometer_rollback, "Should have odometer rollback"
    # Expected: 100 - 10 (2 owners) - 30 (rollback) = 60
    assert report.trust_score == 60, f"Expected trust score of 60, got {report.trust_score}"
    
    return report

def test_7_service_records():
    """Test 7: Service record tracking"""
    print("\n7. Testing service record tracking...")
    
    # Get existing clean title vehicle
    report = VehicleHistoryReport.objects.get(vehicle__vin='TESTHIST001')
    
    # Add service records
    service1 = ServiceRecord.objects.create(
        history_report=report,
        service_date=date.today() - timedelta(days=365),
        service_type='oil_change',
        mileage_at_service=15000,
        service_provider='Honda Dealership',
        cost=Decimal('89.99'),
        description='Oil change and filter replacement'
    )
    
    service2 = ServiceRecord.objects.create(
        history_report=report,
        service_date=date.today() - timedelta(days=180),
        service_type='tire_rotation',
        mileage_at_service=25000,
        service_provider='Honda Dealership',
        cost=Decimal('49.99'),
        description='Tire rotation and balance'
    )
    
    service3 = ServiceRecord.objects.create(
        history_report=report,
        service_date=date.today() - timedelta(days=30),
        service_type='inspection',
        mileage_at_service=35000,
        service_provider='Honda Dealership',
        cost=Decimal('129.99'),
        description='Annual safety inspection'
    )
    
    services = ServiceRecord.objects.filter(history_report=report).order_by('service_date')
    
    print(f"   ✓ Total service records: {services.count()}")
    for service in services:
        print(f"      • {service.service_date}: {service.get_service_type_display()} @ {service.mileage_at_service:,} km")
    
    assert services.count() == 3, "Should have 3 service records"
    
    return services

def test_8_ownership_records():
    """Test 8: Ownership history tracking"""
    print("\n8. Testing ownership history tracking...")
    
    # Get vehicle with 3 owners
    report = VehicleHistoryReport.objects.get(vehicle__vin='TESTHIST003')
    
    # Add ownership records
    owner1 = OwnershipRecord.objects.create(
        history_report=report,
        owner_number=1,
        ownership_start_date=date(2018, 5, 1),
        ownership_end_date=date(2019, 8, 15),
        province='Alberta',
        ownership_type='personal',
        estimated_annual_mileage=20000
    )
    
    owner2 = OwnershipRecord.objects.create(
        history_report=report,
        owner_number=2,
        ownership_start_date=date(2019, 8, 16),
        ownership_end_date=date(2022, 3, 10),
        province='Alberta',
        ownership_type='personal',
        estimated_annual_mileage=18000
    )
    
    owner3 = OwnershipRecord.objects.create(
        history_report=report,
        owner_number=3,
        ownership_start_date=date(2022, 3, 11),
        ownership_end_date=None,
        province='Alberta',
        ownership_type='personal',
        estimated_annual_mileage=15000
    )
    
    owners = OwnershipRecord.objects.filter(history_report=report).order_by('owner_number')
    
    print(f"   ✓ Total owners: {owners.count()}")
    for owner in owners:
        duration = (owner.ownership_end_date - owner.ownership_start_date).days // 365 if owner.ownership_end_date else "Current"
        print(f"      • Owner #{owner.owner_number}: {owner.ownership_start_date} to {owner.ownership_end_date or 'Present'} ({duration} years)")
    
    assert owners.count() == 3, "Should have 3 ownership records"
    
    return owners

def test_9_outstanding_recalls():
    """Test 9: Outstanding recalls impact"""
    print("\n9. Testing outstanding recalls...")
    
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST007',
        year=2016,
        make='Honda',
        model='Civic',
        price_cad=Decimal('16000.00'),
        mileage=95000,
        color='White',
        location='Ottawa, ON',
        status='available'
    )
    
    # Create report with outstanding recalls
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        accident_severity='none',
        total_accidents=0,
        total_owners=2,
        personal_use=True,
        odometer_verified=True,
        last_odometer_reading=95000,
        total_service_records=18,
        recalls_outstanding=3,
        structural_damage=False,
        frame_damage=False,
        airbag_deployment=False,
        report_source='transport_canada',
        report_confidence='high'
    )
    
    print(f"   ✓ Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Outstanding recalls: {report.recalls_outstanding}")
    print(f"   ✓ Trust score: {report.trust_score}/100")
    
    # Expected: 100 - 10 (2 owners) - 15 (3 recalls @ 5 each) = 75
    assert report.trust_score == 75, f"Expected trust score of 75, got {report.trust_score}"
    
    return report

def test_10_trust_score_edge_cases():
    """Test 10: Trust score boundary conditions"""
    print("\n10. Testing trust score edge cases...")
    
    # Test minimum score (cannot go below 0)
    dealer = User.objects.get(email='vehicle_history_test_dealer@example.com')
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='TESTHIST008',
        year=2015,
        make='Dodge',
        model='Charger',
        price_cad=Decimal('12000.00'),
        mileage=150000,
        color='Black',
        location='Regina, SK',
        status='available'
    )
    
    # Create worst-case scenario report
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='lemon',
        accident_severity='total_loss',
        total_accidents=5,
        total_owners=8,
        personal_use=False,
        taxi_use=True,
        odometer_rollback=True,
        odometer_verified=False,
        last_odometer_reading=150000,
        total_service_records=5,
        recalls_outstanding=10,
        structural_damage=True,
        frame_damage=True,
        airbag_deployment=True,
        report_source='manual',
        report_confidence='low'
    )
    
    print(f"   ✓ Worst-case vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
    print(f"   ✓ Title: {report.get_title_status_display()}")
    print(f"   ✓ Accidents: {report.total_accidents} ({report.get_accident_severity_display()})")
    print(f"   ✓ Owners: {report.total_owners}")
    print(f"   ✓ Taxi use: {report.taxi_use}")
    print(f"   ✓ Odometer rollback: {report.odometer_rollback}")
    print(f"   ✓ Trust score: {report.trust_score}/100 (floor at 0)")
    
    assert report.trust_score == 0, f"Trust score should floor at 0, got {report.trust_score}"
    
    return report

def run_all_tests():
    """Run all vehicle history tests"""
    print("=" * 80)
    print("PHASE 3 - Feature 8: Vehicle History Integration Tests")
    print("=" * 80)
    
    # Clean any existing test data
    print("\nCleaning up test data...")
    clean_test_data()
    
    tests = [
        test_1_clean_title_vehicle,
        test_2_accident_history,
        test_3_salvage_title,
        test_4_rental_fleet_vehicle,
        test_5_taxi_vehicle,
        test_6_odometer_rollback,
        test_7_service_records,
        test_8_ownership_records,
        test_9_outstanding_recalls,
        test_10_trust_score_edge_cases,
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
        print("\n✓ All tests passed! Vehicle history system is working correctly.")
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
