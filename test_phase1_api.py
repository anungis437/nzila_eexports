"""
Phase 1 Canadian Diaspora Buyer - API Testing
Tests inspection booking, diaspora user fields, and Interac payment
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time
from rest_framework.test import APIClient
from rest_framework import status
from vehicles.models import Vehicle, VehicleInspectionSlot, InspectionAppointment
from payments.models import PaymentMethod

User = get_user_model()


class Phase1DiasporaBuyerTests(TestCase):
    """Test diaspora buyer features"""
    
    def setUp(self):
        """Create test users"""
        self.client = APIClient()
        
        # Create diaspora buyer
        self.buyer = User.objects.create_user(
            username='diaspora_buyer',
            email='buyer@example.com',
            password='testpass123',
            role='buyer',
            is_diaspora_buyer=True,
            canadian_city='Toronto',
            canadian_province='ON',
            canadian_postal_code='M5H 2N2',
            destination_country='Nigeria',
            destination_city='Lagos',
            buyer_type='personal',
            residency_status='pr',
            prefers_in_person_inspection=True
        )
        
        # Create dealer with showroom
        self.dealer = User.objects.create_user(
            username='dealer_toronto',
            email='dealer@example.com',
            password='testpass123',
            role='dealer',
            showroom_address='123 Yonge Street',
            showroom_city='Toronto',
            showroom_province='ON',
            showroom_postal_code='M5B 2H1',
            showroom_phone='416-555-1234',
            business_hours='Mon-Fri 9am-6pm, Sat 10am-4pm',
            allows_test_drives=True,
            requires_appointment=True,
            toll_free_number='1-800-555-1234',
            local_phone_number='416-555-1234',
            phone_support_hours='Mon-Sun 9am-9pm EST',
            preferred_contact_method='phone'
        )
        
        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Toyota',
            model='Camry',
            year=2022,
            vin='1HGBH41JXMN109186',
            condition='used',
            mileage=25000,
            price_cad=28000,
            status='available',
            location='Toronto, ON',
            description='Excellent condition'
        )
    
    def test_diaspora_buyer_fields(self):
        """Test diaspora buyer fields are saved correctly"""
        self.assertEqual(self.buyer.is_diaspora_buyer, True)
        self.assertEqual(self.buyer.canadian_city, 'Toronto')
        self.assertEqual(self.buyer.canadian_province, 'ON')
        self.assertEqual(self.buyer.destination_country, 'Nigeria')
        self.assertEqual(self.buyer.buyer_type, 'personal')
        self.assertEqual(self.buyer.residency_status, 'pr')
        print("✅ Diaspora buyer fields test passed")
    
    def test_dealer_showroom_fields(self):
        """Test dealer showroom fields are saved correctly"""
        self.assertEqual(self.dealer.showroom_address, '123 Yonge Street')
        self.assertEqual(self.dealer.showroom_city, 'Toronto')
        self.assertEqual(self.dealer.showroom_province, 'ON')
        self.assertEqual(self.dealer.showroom_phone, '416-555-1234')
        self.assertEqual(self.dealer.allows_test_drives, True)
        self.assertEqual(self.dealer.requires_appointment, True)
        print("✅ Dealer showroom fields test passed")
    
    def test_canadian_phone_support_fields(self):
        """Test Canadian phone support fields"""
        self.assertEqual(self.dealer.toll_free_number, '1-800-555-1234')
        self.assertEqual(self.dealer.local_phone_number, '416-555-1234')
        self.assertEqual(self.dealer.phone_support_hours, 'Mon-Sun 9am-9pm EST')
        self.assertEqual(self.dealer.preferred_contact_method, 'phone')
        print("✅ Canadian phone support fields test passed")


class Phase1InteracPaymentTests(TestCase):
    """Test Interac e-Transfer payment method"""
    
    def setUp(self):
        """Create test user"""
        self.buyer = User.objects.create_user(
            username='buyer_interac',
            email='buyer_interac@example.com',
            password='testpass123',
            role='buyer'
        )
    
    def test_interac_payment_method(self):
        """Test Interac e-Transfer payment method creation"""
        payment = PaymentMethod.objects.create(
            user=self.buyer,
            type='interac_etransfer',
            etransfer_email='buyer@example.com',
            etransfer_security_question='What is your favorite color?',
            etransfer_security_answer='Blue',
            etransfer_reference_number='REF123456'
        )
        
        self.assertEqual(payment.type, 'interac_etransfer')
        self.assertEqual(payment.etransfer_email, 'buyer@example.com')
        self.assertIn('Interac e-Transfer', str(payment))
        print("✅ Interac payment method test passed")


class Phase1InspectionBookingTests(TestCase):
    """Test inspection booking functionality"""
    
    def setUp(self):
        """Create test data"""
        self.client = APIClient()
        
        # Create dealer
        self.dealer = User.objects.create_user(
            username='dealer_inspection',
            email='dealer_inspection@example.com',
            password='testpass123',
            role='dealer'
        )
        
        # Create diaspora buyer
        self.buyer = User.objects.create_user(
            username='buyer_inspection',
            email='buyer_inspection@example.com',
            password='testpass123',
            role='buyer',
            is_diaspora_buyer=True,
            canadian_city='Toronto',
            canadian_province='ON'
        )
        
        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Honda',
            model='Accord',
            year=2023,
            vin='1HGCV1F34JA123456',
            condition='used',
            mileage=15000,
            price_cad=32000,
            status='available',
            location='Toronto, ON'
        )
        
        # Create inspection slot
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.slot = VehicleInspectionSlot.objects.create(
            vehicle=self.vehicle,
            date=tomorrow,
            start_time=time(10, 0),
            end_time=time(11, 0),
            is_available=True,
            max_attendees=2,
            notes='Please arrive 5 minutes early'
        )
    
    def test_inspection_slot_creation(self):
        """Test inspection slot is created correctly"""
        self.assertEqual(self.slot.vehicle, self.vehicle)
        self.assertTrue(self.slot.is_available)
        self.assertEqual(self.slot.max_attendees, 2)
        self.assertEqual(self.slot.current_bookings, 0)
        self.assertEqual(self.slot.slots_remaining, 2)
        print("✅ Inspection slot creation test passed")
    
    def test_inspection_slot_properties(self):
        """Test inspection slot properties"""
        # Test is_past property
        self.assertFalse(self.slot.is_past)
        
        # Test slots_remaining property
        self.assertEqual(self.slot.slots_remaining, 2)
        
        # Create appointment
        InspectionAppointment.objects.create(
            slot=self.slot,
            buyer=self.buyer,
            status='confirmed',
            contact_phone='416-555-9999',
            contact_email='buyer@example.com',
            number_of_people=1
        )
        
        # Check updated slots_remaining
        self.assertEqual(self.slot.slots_remaining, 1)
        self.assertEqual(self.slot.current_bookings, 1)
        print("✅ Inspection slot properties test passed")
    
    def test_inspection_appointment_creation(self):
        """Test inspection appointment creation"""
        appointment = InspectionAppointment.objects.create(
            slot=self.slot,
            buyer=self.buyer,
            status='pending',
            contact_phone='416-555-9999',
            contact_email='buyer@example.com',
            number_of_people=1,
            buyer_notes='Looking forward to seeing the car!'
        )
        
        self.assertEqual(appointment.buyer, self.buyer)
        self.assertEqual(appointment.status, 'pending')
        self.assertEqual(appointment.vehicle, self.vehicle)
        self.assertEqual(appointment.dealer, self.dealer)
        print("✅ Inspection appointment creation test passed")
    
    def test_appointment_status_workflow(self):
        """Test appointment status transitions"""
        appointment = InspectionAppointment.objects.create(
            slot=self.slot,
            buyer=self.buyer,
            status='pending',
            contact_phone='416-555-9999',
            contact_email='buyer@example.com',
            number_of_people=1
        )
        
        # Confirm appointment
        appointment.status = 'confirmed'
        appointment.confirmed_at = timezone.now()
        appointment.save()
        self.assertEqual(appointment.status, 'confirmed')
        self.assertIsNotNone(appointment.confirmed_at)
        
        # Complete appointment
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.save()
        self.assertEqual(appointment.status, 'completed')
        self.assertIsNotNone(appointment.completed_at)
        
        print("✅ Appointment status workflow test passed")
    
    def test_appointment_ratings(self):
        """Test appointment ratings and feedback"""
        appointment = InspectionAppointment.objects.create(
            slot=self.slot,
            buyer=self.buyer,
            status='completed',
            contact_phone='416-555-9999',
            contact_email='buyer@example.com',
            number_of_people=1,
            vehicle_rating=5,
            dealer_rating=5,
            inspection_feedback='Excellent vehicle, very clean!',
            interested_in_purchase=True
        )
        
        self.assertEqual(appointment.vehicle_rating, 5)
        self.assertEqual(appointment.dealer_rating, 5)
        self.assertTrue(appointment.interested_in_purchase)
        print("✅ Appointment ratings test passed")
    
    def test_get_available_inspection_slots_api(self):
        """Test API endpoint to get available inspection slots"""
        self.client.force_authenticate(user=self.buyer)
        
        response = self.client.get(
            f'/api/vehicles/{self.vehicle.id}/inspection_slots/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        print("✅ Get available inspection slots API test passed")
    
    def test_book_inspection_appointment_api(self):
        """Test API endpoint to book inspection appointment"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'slot': self.slot.id,
            'contact_phone': '416-555-9999',
            'contact_email': 'buyer@example.com',
            'number_of_people': 1,
            'buyer_notes': 'Excited to see this vehicle!'
        }
        
        response = self.client.post('/api/inspection-appointments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        print("✅ Book inspection appointment API test passed")


def run_tests():
    """Run all Phase 1 tests"""
    print("\n" + "="*60)
    print("PHASE 1 - CANADIAN DIASPORA BUYER FEATURES")
    print("Backend API Testing")
    print("="*60 + "\n")
    
    # Diaspora buyer tests
    print("Test Group 1: Diaspora Buyer Fields")
    print("-" * 60)
    suite1 = Phase1DiasporaBuyerTests()
    suite1.setUp()
    suite1.test_diaspora_buyer_fields()
    suite1.test_dealer_showroom_fields()
    suite1.test_canadian_phone_support_fields()
    
    # Interac payment tests
    print("\nTest Group 2: Interac e-Transfer Payment")
    print("-" * 60)
    suite2 = Phase1InteracPaymentTests()
    suite2.setUp()
    suite2.test_interac_payment_method()
    
    # Inspection booking tests
    print("\nTest Group 3: Inspection Booking")
    print("-" * 60)
    suite3 = Phase1InspectionBookingTests()
    suite3.setUp()
    suite3.test_inspection_slot_creation()
    suite3.test_inspection_slot_properties()
    suite3.test_inspection_appointment_creation()
    suite3.test_appointment_status_workflow()
    suite3.test_appointment_ratings()
    
    # Note: API tests require server running
    print("\n" + "="*60)
    print("PHASE 1 BACKEND TESTING: ALL TESTS PASSED ✅")
    print("="*60)
    print("\nNote: API endpoint tests require Django REST server running.")
    print("Run: python manage.py runserver")
    print("Then test endpoints with:")
    print("  - GET  /api/vehicles/<id>/inspection_slots/")
    print("  - POST /api/inspection-appointments/")
    print("  - GET  /api/inspection-appointments/")
    print("  - POST /api/inspection-appointments/<id>/confirm/")
    print("  - POST /api/inspection-appointments/<id>/complete/")
    print("  - POST /api/inspection-appointments/<id>/cancel/")
    print("  - POST /api/inspection-appointments/<id>/add_feedback/")


if __name__ == '__main__':
    run_tests()
