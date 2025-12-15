from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Vehicle

User = get_user_model()


class VehicleModelTest(TestCase):
    """Test cases for Vehicle model"""

    def setUp(self):
        self.dealer = User.objects.create_user(
            username='dealer1',
            email='dealer@test.com',
            password='testpass123',
            role='dealer'
        )
        self.vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Toyota',
            model='Camry',
            year=2020,
            vin='1HGBH41JXMN109186',
            condition='used_good',
            mileage=50000,
            color='Blue',
            price_cad=Decimal('25000.00'),
            location='Toronto, ON'
        )

    def test_vehicle_creation(self):
        """Test vehicle can be created"""
        self.assertEqual(self.vehicle.make, 'Toyota')
        self.assertEqual(self.vehicle.model, 'Camry')
        self.assertEqual(self.vehicle.year, 2020)
        self.assertEqual(self.vehicle.status, 'available')

    def test_vehicle_string_representation(self):
        """Test string representation of vehicle"""
        expected = f"2020 Toyota Camry (1HGBH41JXMN109186)"
        self.assertEqual(str(self.vehicle), expected)

    def test_vehicle_belongs_to_dealer(self):
        """Test vehicle is associated with dealer"""
        self.assertEqual(self.vehicle.dealer, self.dealer)
        self.assertIn(self.vehicle, self.dealer.vehicles.all())
