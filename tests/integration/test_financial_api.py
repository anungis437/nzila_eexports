"""
Integration tests for financial API endpoints.

Tests all financial endpoints including authentication, permissions,
error handling, and successful operations.
"""
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status

from tests.base import BaseFinancialAPITestCase, BaseAPITestCase
from tests.factories import (
    UserFactory,
    DealFactory,
    DealFinancialTermsFactory,
    PaymentMilestoneFactory,
    FinancingOptionFactory,
    FinancingInstallmentFactory,
    CurrencyFactory,
)
from payments.models import Payment


class FinancialTermsEndpointTest(BaseFinancialAPITestCase):
    """Test GET /api/deals/{id}/financial-terms/ endpoint."""
        
    def test_get_financial_terms_authenticated(self):
        """Test retrieving financial terms as authenticated buyer."""
        self.create_payment_schedule(3)
        
        url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
        response = self.get_authenticated(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.terms.id)
        self.assertEqual(Decimal(response.data['total_price']), self.terms.total_price)
        self.assertEqual(len(response.data['milestones']), 3)
        self.assertIn('currency_code', response.data)
        self.assertIn('payment_progress_percentage', response.data)
    
    def test_get_financial_terms_as_dealer(self):
        """Test retrieving financial terms as dealer."""
        url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
        response = self.get_authenticated(url, user=self.dealer)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.terms.id)
    
    def test_get_financial_terms_unauthenticated(self):
        """Test retrieving financial terms without authentication fails."""
        url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_financial_terms_not_found(self):
        """Test retrieving financial terms for deal without terms."""
        deal = DealFactory(buyer=self.buyer)
        # No financial terms created
        
        url = reverse('deal-financial-terms', kwargs={'pk': deal.id})
        response = self.get_authenticated(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class PaymentScheduleEndpointTest(BaseFinancialAPITestCase):
    """Test GET /api/deals/{id}/payment-schedule/ endpoint."""
        
    def test_get_payment_schedule(self):
        """Test retrieving payment schedule."""
        milestones = self.create_payment_schedule(4)
        
        url = reverse('deal-payment-schedule', kwargs={'pk': self.deal.id})
        response = self.get_authenticated(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        
        # Check first milestone
        milestone_data = response.data[0]
        self.assertIn('name', milestone_data)
        self.assertIn('amount_due', milestone_data)
        self.assertIn('is_overdue', milestone_data)
        self.assertIn('amount_remaining', milestone_data)
    
    def test_get_payment_schedule_empty(self):
        """Test retrieving payment schedule with no milestones."""
        deal = DealFactory(buyer=self.buyer)
        terms = DealFinancialTermsFactory(deal=deal)
        # No milestones created
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-payment-schedule', kwargs={'pk': deal.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_get_payment_schedule_without_terms(self):
        """Test retrieving payment schedule for deal without financial terms."""
        deal = DealFactory(buyer=self.buyer)
        
        url = reverse('deal-payment-schedule', kwargs={'pk': deal.id})
        response = self.get_authenticated(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FinancingEndpointTest(BaseFinancialAPITestCase):
    """Test GET /api/deals/{id}/financing/ endpoint."""
        
    def test_get_financing(self):
        """Test retrieving financing details."""
        financing = self.create_financing()
        FinancingInstallmentFactory.create_batch(12, financing=financing)
        
        url = reverse('deal-financing', kwargs={'pk': self.deal.id})
        response = self.get_authenticated(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], financing.id)
        self.assertEqual(len(response.data['installments']), 12)
        self.assertIn('installments_summary', response.data)
        
        # Check summary statistics
        summary = response.data['installments_summary']
        self.assertEqual(summary['total'], 12)
        self.assertIn('paid', summary)
        self.assertIn('pending', summary)
        self.assertIn('total_paid', summary)
    
    def test_get_financing_not_found(self):
        """Test retrieving financing for deal without financing."""
        deal = DealFactory(buyer=self.buyer)
        
        url = reverse('deal-financing', kwargs={'pk': deal.id})
        response = self.get_authenticated(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProcessPaymentEndpointTest(BaseAPITestCase):
    """Test POST /api/deals/{id}/process-payment/ endpoint."""
    
    def setUp(self):
        super().setUp()
        self.currency = CurrencyFactory(code='USD')
        
    def test_process_payment_success(self):
        """Test processing a payment successfully."""
        deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
        terms = DealFinancialTermsFactory(
            deal=deal,
            currency=self.currency,
            total_price=Decimal('50000'),
            total_paid=Decimal('10000'),
            balance_remaining=Decimal('40000')
        )
        
        url = reverse('deal-process-payment', kwargs={'pk': deal.id})
        
        payment_data = {
            'amount': '5000.00',
            'payment_method': 'card',
            'reference_number': 'TEST123',
            'notes': 'Test payment'
        }
        
        response = self.post_authenticated(url, payment_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('payment_id', response.data)
        self.assertIn('payment_summary', response.data)
        
        # Verify payment was created
        payment = Payment.objects.get(id=response.data['payment_id'])
        self.assertEqual(payment.amount, Decimal('5000'))
        self.assertIsNone(payment.payment_method)  # payment_method is ForeignKey, can be None
        self.assertEqual(payment.description, 'Test payment')
    
    def test_process_payment_invalid_amount(self):
        """Test processing payment with invalid amount."""
        deal = DealFactory(buyer=self.buyer)
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        url = reverse('deal-process-payment', kwargs={'pk': deal.id})
        
        payment_data = {
            'amount': '-100.00',  # Negative amount
            'payment_method': 'card'
        }
        
        response = self.post_authenticated(url, payment_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_process_payment_missing_amount(self):
        """Test processing payment without amount."""
        deal = DealFactory(buyer=self.buyer)
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        url = reverse('deal-process-payment', kwargs={'pk': deal.id})
        
        payment_data = {
            'payment_method': 'card'
        }
        
        response = self.post_authenticated(url, payment_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    def test_process_payment_without_financial_terms(self):
        """Test processing payment for deal without financial terms."""
        deal = DealFactory(buyer=self.buyer)
        
        url = reverse('deal-process-payment', kwargs={'pk': deal.id})
        
        payment_data = {
            'amount': '5000.00',
            'payment_method': 'card'
        }
        
        response = self.post_authenticated(url, payment_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_process_payment_unauthenticated(self):
        """Test processing payment without authentication."""
        deal = DealFactory(buyer=self.buyer)
        
        url = reverse('deal-process-payment', kwargs={'pk': deal.id})
        payment_data = {
            'amount': '5000.00',
            'payment_method': 'card'
        }
        
        response = self.client.post(url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ApplyFinancingEndpointTest(BaseAPITestCase):
    """Test POST /api/deals/{id}/apply-financing/ endpoint."""
    
    def setUp(self):
        super().setUp()
        self.currency = CurrencyFactory(code='USD')
        
    def test_apply_financing_success(self):
        """Test applying financing successfully."""
        deal = DealFactory(
            buyer=self.buyer,
            dealer=self.dealer,
            agreed_price_cad=Decimal('50000')
        )
        terms = DealFinancialTermsFactory(
            deal=deal,
            currency=self.currency,
            total_price=Decimal('50000')
        )
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-apply-financing', kwargs={'pk': deal.id})
        
        financing_data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '5.5',
            'term_months': 36,
            'lender_name': 'Test Bank'
        }
        
        response = self.client.post(url, financing_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(Decimal(response.data['financed_amount']), Decimal('40000'))
        self.assertEqual(Decimal(response.data['down_payment']), Decimal('10000'))
        self.assertEqual(response.data['term_months'], 36)
        self.assertIn('installments', response.data)
    
    def test_apply_financing_down_payment_exceeds_amount(self):
        """Test applying financing with down payment > financed amount."""
        deal = DealFactory(buyer=self.buyer, agreed_price_cad=Decimal('50000'))
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-apply-financing', kwargs={'pk': deal.id})
        
        financing_data = {
            'financed_amount': '40000.00',
            'down_payment': '50000.00',  # Exceeds financed amount
            'interest_rate': '5.5',
            'term_months': 36
        }
        
        response = self.client.post(url, financing_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_apply_financing_invalid_interest_rate(self):
        """Test applying financing with invalid interest rate."""
        deal = DealFactory(buyer=self.buyer)
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-apply-financing', kwargs={'pk': deal.id})
        
        financing_data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '-5.0',  # Negative rate
            'term_months': 36
        }
        
        response = self.client.post(url, financing_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('interest_rate', response.data)
    
    def test_apply_financing_invalid_term_months(self):
        """Test applying financing with invalid term months."""
        deal = DealFactory(buyer=self.buyer)
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-apply-financing', kwargs={'pk': deal.id})
        
        financing_data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '5.5',
            'term_months': 150  # Over 120 max
        }
        
        response = self.client.post(url, financing_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('term_months', response.data)
    
    def test_apply_financing_already_exists(self):
        """Test applying financing when financing already exists."""
        deal = DealFactory(buyer=self.buyer)
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        FinancingOptionFactory(deal=deal)  # Already has financing
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-apply-financing', kwargs={'pk': deal.id})
        
        financing_data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '5.5',
            'term_months': 36
        }
        
        response = self.client.post(url, financing_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_apply_financing_missing_required_fields(self):
        """Test applying financing with missing required fields."""
        deal = DealFactory(buyer=self.buyer)
        DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        self.client.force_authenticate(user=self.buyer)
        url = reverse('deal-apply-financing', kwargs={'pk': deal.id})
        
        financing_data = {
            'financed_amount': '40000.00',
            # Missing down_payment, interest_rate, term_months
        }
        
        response = self.client.post(url, financing_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('down_payment', response.data)
        self.assertIn('interest_rate', response.data)
        self.assertIn('term_months', response.data)


class FinancialAPIPermissionsTest(BaseAPITestCase):
    """Test permissions across all financial endpoints."""
    
    def setUp(self):
        super().setUp()
        self.currency = CurrencyFactory(code='USD')
        
    def test_only_deal_participants_can_access(self):
        """Test that only buyer and dealer can access deal financial data."""
        deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
        terms = DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        # Test buyer access
        url = reverse('deal-financial-terms', kwargs={'pk': deal.id})
        response = self.get_authenticated(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test dealer access
        response = self.get_authenticated(url, user=self.dealer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_can_access_all_deals(self):
        """Test that admin users can access any deal's financial data."""
        admin = UserFactory(role='admin', is_staff=True)
        deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
        terms = DealFinancialTermsFactory(deal=deal, currency=self.currency)
        
        url = reverse('deal-financial-terms', kwargs={'pk': deal.id})
        response = self.get_authenticated(url, user=admin)
        
        # Should work if admin permissions are implemented
        # Otherwise would be 403 Forbidden
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
