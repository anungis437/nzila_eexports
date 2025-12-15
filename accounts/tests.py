from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.dealer = User.objects.create_user(
            username='dealer1',
            email='dealer@test.com',
            password='testpass123',
            role='dealer',
            company_name='Test Dealer Co.'
        )
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@test.com',
            password='testpass123',
            role='buyer'
        )

    def test_user_creation(self):
        """Test user can be created with role"""
        self.assertEqual(self.dealer.username, 'dealer1')
        self.assertEqual(self.dealer.role, 'dealer')
        self.assertTrue(self.dealer.is_dealer())
        self.assertFalse(self.dealer.is_buyer())

    def test_user_role_methods(self):
        """Test role checking methods"""
        self.assertTrue(self.buyer.is_buyer())
        self.assertFalse(self.buyer.is_dealer())
        self.assertFalse(self.buyer.is_broker())
        self.assertFalse(self.buyer.is_admin())

    def test_user_string_representation(self):
        """Test string representation of user"""
        expected = f"{self.dealer.username} ({self.dealer.get_role_display()})"
        self.assertEqual(str(self.dealer), expected)
