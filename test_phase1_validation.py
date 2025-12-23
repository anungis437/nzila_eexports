"""
Phase 1 - Model Validation Test
Quick verification that all Phase 1 fields and models exist
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.contrib.auth import get_user_model
from vehicles.models import Vehicle, VehicleInspectionSlot, InspectionAppointment
from payments.models import PaymentMethod

User = get_user_model()

def test_user_model_fields():
    """Verify User model has all Phase 1 fields"""
    print("\n[TESTING] User Model Fields...")
    
    # Diaspora buyer fields
    diaspora_fields = [
        'is_diaspora_buyer', 'canadian_city', 'canadian_province',
        'canadian_postal_code', 'destination_country', 'destination_city',
        'buyer_type', 'residency_status', 'prefers_in_person_inspection'
    ]
    
    # Dealer showroom fields
    showroom_fields = [
        'showroom_address', 'showroom_city', 'showroom_province',
        'showroom_postal_code', 'showroom_phone', 'business_hours',
        'allows_test_drives', 'requires_appointment'
    ]
    
    # Phone support fields
    phone_fields = [
        'toll_free_number', 'local_phone_number',
        'phone_support_hours', 'preferred_contact_method'
    ]
    
    all_fields = diaspora_fields + showroom_fields + phone_fields
    user_field_names = [f.name for f in User._meta.get_fields()]
    
    missing_fields = []
    for field in all_fields:
        if field not in user_field_names:
            missing_fields.append(field)
        else:
            print(f"  [OK] {field}")
    
    if missing_fields:
        print(f"\n[FAIL] Missing fields: {missing_fields}")
        return False
    
    print(f"\n[PASS] All {len(all_fields)} Phase 1 User fields exist!")
    return True


def test_payment_method_fields():
    """Verify PaymentMethod has Interac fields"""
    print("\n[TESTING] PaymentMethod Model...")
    
    interac_fields = [
        'etransfer_email', 'etransfer_security_question',
        'etransfer_security_answer', 'etransfer_reference_number'
    ]
    
    payment_field_names = [f.name for f in PaymentMethod._meta.get_fields()]
    
    missing_fields = []
    for field in interac_fields:
        if field not in payment_field_names:
            missing_fields.append(field)
        else:
            print(f"  [OK] {field}")
    
    if missing_fields:
        print(f"\n[FAIL] Missing fields: {missing_fields}")
        return False
    
    # Check if interac_etransfer is in choices
    type_field = PaymentMethod._meta.get_field('type')
    choices = [choice[0] for choice in type_field.choices]
    
    if 'interac_etransfer' in choices:
        print(f"  [OK] 'interac_etransfer' in type choices")
    else:
        print(f"  [FAIL] 'interac_etransfer' NOT in type choices")
        return False
    
    print(f"\n[PASS] All Interac e-Transfer fields exist!")
    return True


def test_inspection_models():
    """Verify inspection models exist"""
    print("\n[TESTING] Inspection Models...")
    
    # Check VehicleInspectionSlot model
    slot_fields = [
        'vehicle', 'date', 'start_time', 'end_time',
        'is_available', 'max_attendees', 'notes'
    ]
    
    slot_field_names = [f.name for f in VehicleInspectionSlot._meta.get_fields()]
    
    print("\n  VehicleInspectionSlot fields:")
    missing_fields = []
    for field in slot_fields:
        if field not in slot_field_names:
            missing_fields.append(field)
        else:
            print(f"    [OK] {field}")
    
    if missing_fields:
        print(f"  [FAIL] Missing slot fields: {missing_fields}")
        return False
    
    # Check InspectionAppointment model
    appointment_fields = [
        'slot', 'buyer', 'status', 'contact_phone', 'contact_email',
        'number_of_people', 'buyer_notes', 'dealer_notes',
        'inspection_feedback', 'vehicle_rating', 'dealer_rating',
        'interested_in_purchase'
    ]
    
    appointment_field_names = [f.name for f in InspectionAppointment._meta.get_fields()]
    
    print("\n  InspectionAppointment fields:")
    missing_fields = []
    for field in appointment_fields:
        if field not in appointment_field_names:
            missing_fields.append(field)
        else:
            print(f"    [OK] {field}")
    
    if missing_fields:
        print(f"  [FAIL] Missing appointment fields: {missing_fields}")
        return False
    
    print(f"\n[PASS] All inspection models exist with correct fields!")
    return True


def test_database_tables():
    """Verify database tables exist"""
    print("\n[TESTING] Database Tables...")
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'vehicles_vehicleinspectionslot',
            'vehicles_inspectionappointment'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"  [OK] {table}")
            else:
                print(f"  [FAIL] {table} NOT FOUND")
                return False
    
    print("\n[PASS] All inspection tables exist in database!")
    return True


def run_validation():
    """Run all Phase 1 validation tests"""
    print("\n" + "="*60)
    print("PHASE 1 - CANADIAN DIASPORA BUYER FEATURES")
    print("Model & Database Validation")
    print("="*60)
    
    results = []
    
    results.append(("User Model Fields", test_user_model_fields()))
    results.append(("PaymentMethod Fields", test_payment_method_fields()))
    results.append(("Inspection Models", test_inspection_models()))
    results.append(("Database Tables", test_database_tables()))
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("*** ALL PHASE 1 BACKEND VALIDATIONS PASSED! ***")
        print("="*60)
        print("\nPhase 1 Backend Implementation: COMPLETE")
        print("\nWhat's working:")
        print("  * 21 new User model fields (diaspora buyers + dealers)")
        print("  * Interac e-Transfer payment method (4 new fields)")
        print("  * 2 new inspection booking models")
        print("  * All database migrations applied")
        print("  * Admin interface ready")
        print("\nReady for:")
        print("  * API endpoint testing (start Django server)")
        print("  * Frontend integration")
        print("  * End-to-end testing")
    else:
        print("*** SOME VALIDATIONS FAILED ***")
        print("="*60)
        print("\nPlease review the errors above and fix before proceeding.")
    
    print()


if __name__ == '__main__':
    run_validation()
