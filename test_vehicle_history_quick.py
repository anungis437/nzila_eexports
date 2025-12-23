"""
PHASE 3 - Feature 8: Vehicle History - Quick Validation

Tests that vehicle history system is operational.
Run: python test_vehicle_history_quick.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicle_history.models import VehicleHistoryReport, AccidentRecord, ServiceRecord, OwnershipRecord
from accounts.models import User
from vehicles.models import Vehicle
from decimal import Decimal
from datetime import date

def test_vehicle_history_system():
    """Quick validation that vehicle history system works"""
    print("\nTesting Vehicle History System...")
    
    # Clean up
    VehicleHistoryReport.objects.filter(vehicle__vin='QUICKTEST001').delete()
    Vehicle.objects.filter(vin='QUICKTEST001').delete()
    User.objects.filter(email='quicktest@example.com').delete()
    
    # Create dealer and vehicle
    dealer = User.objects.create_user(
        username='quicktest',
        email='quicktest@example.com',
        password='test123',
        role='dealer'
    )
    
    vehicle = Vehicle.objects.create(
        dealer=dealer,
        vin='QUICKTEST001',
        year=2020,
        make='Honda',
        model='Civic',
        price_cad=Decimal('25000.00'),
        mileage=30000,
        color='Blue',
        location='Toronto, ON',
        status='available'
    )
    
    # Create history report
    report = VehicleHistoryReport.objects.create(
        vehicle=vehicle,
        title_status='clean',
        accident_severity='none',
        total_accidents=0,
        total_owners=1,
        personal_use=True,
        odometer_verified=True,
        last_odometer_reading=30000,
        total_service_records=5
    )
    
    print(f"✓ Vehicle History Report created: {report}")
    print(f"✓ Title status: {report.get_title_status_display()}")
    print(f"✓ Trust score: {report.trust_score}/100")
    print(f"✓ Is clean title: {report.is_clean_title}")
    print(f"✓ One owner: {report.is_one_owner}")
    
    # Add accident record
    accident = AccidentRecord.objects.create(
        history_report=report,
        accident_date=date(2021, 6, 15),
        damage_severity='minor',
        front_damage=True,
        repair_completed=True,
        insurance_claim=True
    )
    print(f"✓ Accident Record created: {accident}")
    
    # Add service record
    service = ServiceRecord.objects.create(
        history_report=report,
        service_date=date.today(),
        service_type='oil_change',
        odometer_reading=30000,
        service_facility='Honda Dealership',
        service_cost=Decimal('89.99')
    )
    print(f"✓ Service Record created: {service}")
    
    # Add ownership record
    ownership = OwnershipRecord.objects.create(
        history_report=report,
        owner_number=1,
        ownership_start=date(2020, 5, 1),
        state_province='Ontario',
        ownership_type='personal'
    )
    print(f"✓ Ownership Record created: {ownership}")
    
    # Verify counts
    assert VehicleHistoryReport.objects.filter(vehicle=vehicle).count() == 1
    assert AccidentRecord.objects.filter(history_report=report).count() == 1
    assert ServiceRecord.objects.filter(history_report=report).count() == 1
    assert OwnershipRecord.objects.filter(history_report=report).count() == 1
    
    print("\n✓ Vehicle History System: OPERATIONAL")
    
    # Clean up
    report.delete()
    vehicle.delete()
    dealer.delete()
    
    return True

if __name__ == '__main__':
    try:
        test_vehicle_history_system()
        print("\n" + "=" * 60)
        print("VEHICLE HISTORY VALIDATION: PASSED")
        print("=" * 60)
        exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n" + "=" * 60)
        print("VEHICLE HISTORY VALIDATION: FAILED")
        print("=" * 60)
        exit(1)
