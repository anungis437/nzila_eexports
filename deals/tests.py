from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Lead, Deal, Document
from vehicles.models import Vehicle

User = get_user_model()


class LeadModelTest(TestCase):
    """Test cases for Lead model"""

    def setUp(self):
        self.dealer = User.objects.create_user(
            username='dealer1',
            email='dealer@test.com',
            password='testpass123',
            role='dealer'
        )
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@test.com',
            password='testpass123',
            role='buyer'
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
        self.lead = Lead.objects.create(
            buyer=self.buyer,
            vehicle=self.vehicle,
            status='new',
            source='website'
        )

    def test_lead_creation(self):
        """Test lead can be created"""
        self.assertEqual(self.lead.buyer, self.buyer)
        self.assertEqual(self.lead.vehicle, self.vehicle)
        self.assertEqual(self.lead.status, 'new')

    def test_lead_is_stalled(self):
        """Test stalled lead detection"""
        # New lead should not be stalled
        self.assertFalse(self.lead.is_stalled())
        
        # Update lead to be old using update() to bypass auto_now
        old_time = timezone.now() - timedelta(days=8)
        Lead.objects.filter(pk=self.lead.pk).update(updated_at=old_time)
        self.lead.refresh_from_db()
        self.assertTrue(self.lead.is_stalled())

    def test_converted_lead_not_stalled(self):
        """Test converted lead is not marked as stalled"""
        self.lead.status = 'converted'
        old_time = timezone.now() - timedelta(days=10)
        Lead.objects.filter(pk=self.lead.pk).update(status='converted', updated_at=old_time)
        self.lead.refresh_from_db()
        self.assertFalse(self.lead.is_stalled())


class DealModelTest(TestCase):
    """Test cases for Deal model"""

    def setUp(self):
        self.dealer = User.objects.create_user(
            username='dealer1',
            email='dealer@test.com',
            password='testpass123',
            role='dealer'
        )
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@test.com',
            password='testpass123',
            role='buyer'
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
        self.deal = Deal.objects.create(
            vehicle=self.vehicle,
            buyer=self.buyer,
            dealer=self.dealer,
            agreed_price_cad=Decimal('24000.00'),
            status='pending_docs'
        )

    def test_deal_creation(self):
        """Test deal can be created"""
        self.assertEqual(self.deal.buyer, self.buyer)
        self.assertEqual(self.deal.dealer, self.dealer)
        self.assertEqual(self.deal.vehicle, self.vehicle)
        self.assertEqual(self.deal.status, 'pending_docs')

    def test_deal_completion_sets_timestamp(self):
        """Test that completing a deal sets completed_at"""
        self.assertIsNone(self.deal.completed_at)
        self.deal.status = 'completed'
        self.deal.save()
        self.assertIsNotNone(self.deal.completed_at)

    def test_deal_is_stalled(self):
        """Test stalled deal detection"""
        # New deal should not be stalled
        self.assertFalse(self.deal.is_stalled())
        
        # Update deal to be old using update() to bypass auto_now
        old_time = timezone.now() - timedelta(days=15)
        Deal.objects.filter(pk=self.deal.pk).update(updated_at=old_time)
        self.deal.refresh_from_db()
        self.assertTrue(self.deal.is_stalled())
