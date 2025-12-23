"""
Unit tests for financial serializers.

Tests validation rules, computed fields, and nested serialization
for all financial-related serializers.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from deals.serializers import (
    FinancingInstallmentSerializer,
    FinancingOptionSerializer,
    PaymentMilestoneSerializer,
    DealFinancialTermsSerializer,
    ProcessPaymentSerializer,
    ApplyFinancingSerializer,
    DealSerializer,
)
from tests.factories import (
    DealFactory,
    DealFinancialTermsFactory,
    PaymentMilestoneFactory,
    FinancingOptionFactory,
    FinancingInstallmentFactory,
)


class TestFinancingInstallmentSerializer(TestCase):
    """Test FinancingInstallmentSerializer."""
    
    def test_serialization_basic_fields(self):
        """Test basic field serialization."""
        installment = FinancingInstallmentFactory()
        serializer = FinancingInstallmentSerializer(installment)
        data = serializer.data
        
        self.assertEqual(data['id'], installment.id)
        self.assertEqual(data['installment_number'], installment.installment_number)
        self.assertEqual(Decimal(data['amount_due']), installment.amount_due)
        self.assertEqual(Decimal(data['amount_paid']), installment.amount_paid)
        self.assertEqual(data['status'], installment.status)
    
    def test_is_late_computed_field(self):
        """Test is_late computed field."""
        # Past due date, not paid
        past_installment = FinancingInstallmentFactory(
            due_date=date.today() - timedelta(days=5),
            status='pending'
        )
        serializer = FinancingInstallmentSerializer(past_installment)
        self.assertTrue(serializer.data['is_late'])
        
        # Past due date, but paid
        paid_installment = FinancingInstallmentFactory(
            due_date=date.today() - timedelta(days=5),
            status='paid'
        )
        serializer = FinancingInstallmentSerializer(paid_installment)
        self.assertFalse(serializer.data['is_late'])
        
        # Future due date
        future_installment = FinancingInstallmentFactory(
            due_date=date.today() + timedelta(days=5),
            status='pending'
        )
        serializer = FinancingInstallmentSerializer(future_installment)
        self.assertFalse(serializer.data['is_late'])
    
    def test_days_late_computed_field(self):
        """Test days_late computed field."""
        installment = FinancingInstallmentFactory(
            due_date=date.today() - timedelta(days=10),
            status='pending'
        )
        serializer = FinancingInstallmentSerializer(installment)
        self.assertEqual(serializer.data['days_late'], 10)


class TestFinancingOptionSerializer(TestCase):
    """Test FinancingOptionSerializer."""
    
    def test_serialization_basic_fields(self):
        """Test basic field serialization."""
        financing = FinancingOptionFactory()
        serializer = FinancingOptionSerializer(financing)
        data = serializer.data
        
        self.assertEqual(Decimal(data['financed_amount']), financing.financed_amount)
        self.assertEqual(Decimal(data['down_payment']), financing.down_payment)
        self.assertEqual(Decimal(data['interest_rate']), financing.interest_rate)
        self.assertEqual(data['term_months'], financing.term_months)
    
    def test_nested_installments(self):
        """Test nested installment serialization."""
        financing = FinancingOptionFactory()
        # Create installments using correct parameter name
        FinancingInstallmentFactory.create_batch(3, financing=financing)
        
        serializer = FinancingOptionSerializer(financing)
        data = serializer.data
        
        self.assertEqual(len(data['installments']), 3)
        self.assertIn('installment_number', data['installments'][0])
        self.assertIn('amount_due', data['installments'][0])
    
    def test_installments_summary(self):
        """Test installments_summary computed field."""
        financing = FinancingOptionFactory()
        FinancingInstallmentFactory(financing=financing, status='paid', amount_paid=Decimal('1000'))
        FinancingInstallmentFactory(financing=financing, status='paid', amount_paid=Decimal('1000'))
        FinancingInstallmentFactory(financing=financing, status='pending', amount_paid=Decimal('0'))
        
        serializer = FinancingOptionSerializer(financing)
        summary = serializer.data['installments_summary']
        
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['paid'], 2)
        self.assertEqual(summary['pending'], 1)
        self.assertEqual(Decimal(summary['total_paid']), Decimal('2000'))
    
    def test_term_months_validation(self):
        """Test term_months must be positive."""
        serializer = FinancingOptionSerializer(data={
            'financed_amount': '50000',
            'down_payment': '10000',
            'interest_rate': '5.0',
            'term_months': 0,
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('term_months', serializer.errors)
    
    def test_interest_rate_validation(self):
        """Test interest_rate must be non-negative."""
        serializer = FinancingOptionSerializer(data={
            'financed_amount': '50000',
            'down_payment': '10000',
            'interest_rate': '-1.0',
            'term_months': 36,
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('interest_rate', serializer.errors)


class TestPaymentMilestoneSerializer(TestCase):
    """Test PaymentMilestoneSerializer."""
    
    def test_serialization_basic_fields(self):
        """Test basic field serialization."""
        milestone = PaymentMilestoneFactory()
        serializer = PaymentMilestoneSerializer(milestone)
        data = serializer.data
        
        self.assertEqual(data['id'], milestone.id)
        self.assertEqual(data['name'], milestone.name)
        self.assertEqual(data['milestone_type'], milestone.milestone_type)
        self.assertEqual(Decimal(data['amount_due']), milestone.amount_due)
    
    def test_is_overdue_computed_field(self):
        """Test is_overdue computed field."""
        # Past due, not fully paid
        overdue_milestone = PaymentMilestoneFactory(
            due_date=timezone.now() - timedelta(days=5),
            amount_due=Decimal('10000'),
            amount_paid=Decimal('5000'),
            status='pending'  # Set pending status
        )
        serializer = PaymentMilestoneSerializer(overdue_milestone)
        self.assertTrue(serializer.data['is_overdue'])
        
        # Past due, fully paid
        paid_milestone = PaymentMilestoneFactory(
            due_date=timezone.now() - timedelta(days=5),
            amount_due=Decimal('10000'),
            amount_paid=Decimal('10000'),
            status='paid'  # Set paid status
        )
        serializer = PaymentMilestoneSerializer(paid_milestone)
        self.assertFalse(serializer.data['is_overdue'])
    
    def test_amount_remaining_computed_field(self):
        """Test amount_remaining computed field."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000'),
            amount_paid=Decimal('7000')
        )
        serializer = PaymentMilestoneSerializer(milestone)
        self.assertEqual(Decimal(serializer.data['amount_remaining']), Decimal('3000'))
    
    def test_payment_percentage_computed_field(self):
        """Test payment_percentage computed field."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000'),
            amount_paid=Decimal('7500')
        )
        serializer = PaymentMilestoneSerializer(milestone)
        self.assertEqual(Decimal(serializer.data['payment_percentage']), Decimal('75.00'))


class TestDealFinancialTermsSerializer(TestCase):
    """Test DealFinancialTermsSerializer."""
    
    def test_serialization_basic_fields(self):
        """Test basic field serialization."""
        terms = DealFinancialTermsFactory()
        serializer = DealFinancialTermsSerializer(terms)
        data = serializer.data
        
        self.assertEqual(Decimal(data['total_price']), terms.total_price)
        self.assertEqual(Decimal(data['deposit_percentage']), terms.deposit_percentage)
        self.assertEqual(Decimal(data['deposit_amount']), terms.deposit_amount)
    
    def test_nested_milestones(self):
        """Test nested milestone serialization."""
        terms = DealFinancialTermsFactory()
        PaymentMilestoneFactory.create_batch(3, deal_financial_terms=terms)
        
        serializer = DealFinancialTermsSerializer(terms)
        data = serializer.data
        
        self.assertEqual(len(data['milestones']), 3)
        self.assertIn('name', data['milestones'][0])
        self.assertIn('amount_due', data['milestones'][0])
    
    def test_currency_code_computed_field(self):
        """Test currency_code computed field."""
        terms = DealFinancialTermsFactory()
        serializer = DealFinancialTermsSerializer(terms)
        self.assertEqual(serializer.data['currency_code'], terms.currency.code)
    
    def test_payment_progress_percentage(self):
        """Test payment_progress_percentage computed field."""
        terms = DealFinancialTermsFactory(
            total_price=Decimal('50000'),
            total_paid=Decimal('25000')
        )
        serializer = DealFinancialTermsSerializer(terms)
        self.assertEqual(Decimal(serializer.data['payment_progress_percentage']), Decimal('50.00'))
    
    def test_fully_paid_computed_field(self):
        """Test fully_paid computed field."""
        # Not fully paid
        terms = DealFinancialTermsFactory(
            total_price=Decimal('50000'),
            total_paid=Decimal('25000'),
            balance_remaining=Decimal('25000')  # Set balance_remaining
        )
        serializer = DealFinancialTermsSerializer(terms)
        self.assertFalse(serializer.data['fully_paid'])
        
        # Fully paid
        terms.total_paid = Decimal('50000')
        terms.balance_remaining = Decimal('0')  # Set balance to 0
        terms.save()
        serializer = DealFinancialTermsSerializer(terms)
        self.assertTrue(serializer.data['fully_paid'])
    
    def test_deposit_percentage_validation(self):
        """Test deposit_percentage must be 0-100."""
        serializer = DealFinancialTermsSerializer(data={
            'deposit_percentage': '150',  # Invalid
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('deposit_percentage', serializer.errors)


class TestProcessPaymentSerializer(TestCase):
    """Test ProcessPaymentSerializer."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'amount': '1000.00',
            'payment_method': 'card',
            'reference_number': 'REF123',
            'notes': 'Test payment'
        }
        serializer = ProcessPaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_amount_required(self):
        """Test amount is required."""
        data = {
            'payment_method': 'card',
        }
        serializer = ProcessPaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
    
    def test_amount_must_be_positive(self):
        """Test amount must be positive."""
        data = {
            'amount': '-100.00',
            'payment_method': 'card',
        }
        serializer = ProcessPaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
    
    def test_payment_method_choices(self):
        """Test payment_method validates choices."""
        data = {
            'amount': '1000.00',
            'payment_method': 'invalid_method',
        }
        serializer = ProcessPaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('payment_method', serializer.errors)


class TestApplyFinancingSerializer(TestCase):
    """Test ApplyFinancingSerializer."""
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '5.5',
            'term_months': 36,
            'lender_name': 'Test Bank'
        }
        serializer = ApplyFinancingSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_required_fields(self):
        """Test all fields except lender_name are required."""
        data = {
            'financed_amount': '40000.00',
            # Missing other required fields
        }
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('down_payment', serializer.errors)
        self.assertIn('interest_rate', serializer.errors)
        self.assertIn('term_months', serializer.errors)
    
    def test_down_payment_validation(self):
        """Test down_payment must not exceed financed_amount."""
        data = {
            'financed_amount': '40000.00',
            'down_payment': '50000.00',  # More than financed amount
            'interest_rate': '5.5',
            'term_months': 36,
        }
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('down_payment', serializer.errors)
    
    def test_down_payment_validation(self):
        """Test down_payment must not exceed financed_amount."""
        data = {
            'financed_amount': '40000.00',
            'down_payment': '50000.00',  # More than financed amount
            'interest_rate': '5.5',
            'term_months': 36,
        }
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_interest_rate_range(self, ):
        """Test interest_rate must be 0-100."""
        # Negative interest rate
        data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '-1.0',
            'term_months': 36,
        }
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('interest_rate', serializer.errors)
        
        # Over 100% interest rate
        data['interest_rate'] = '101.0'
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('interest_rate', serializer.errors)
    
    def test_term_months_range(self):
        """Test term_months must be 1-120."""
        # Zero months
        data = {
            'financed_amount': '40000.00',
            'down_payment': '10000.00',
            'interest_rate': '5.5',
            'term_months': 0,
        }
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('term_months', serializer.errors)
        
        # Over 120 months
        data['term_months'] = 121
        serializer = ApplyFinancingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('term_months', serializer.errors)


class TestDealSerializerFinancialIntegration(TestCase):
    """Test DealSerializer financial field integration."""
    
    def test_payment_summary_included(self):
        """Test payment_summary is always included."""
        deal = DealFactory()
        serializer = DealSerializer(deal)
        self.assertIn('payment_summary', serializer.data)
    
    def test_financial_terms_default(self):
        """Test financial_terms returns ID by default."""
        deal = DealFactory()
        DealFinancialTermsFactory(deal=deal)
        
        serializer = DealSerializer(deal)
        self.assertIn('financial_terms', serializer.data)
        # Without expansion, should only have ID
        self.assertIn('id', serializer.data['financial_terms'])
    
    def test_financial_terms_expansion(self):
        """Test financial_terms expands when requested."""
        deal = DealFactory()
        terms = DealFinancialTermsFactory(deal=deal)
        
        serializer = DealSerializer(deal, context={'expand': ['financial_terms']})
        data = serializer.data['financial_terms']
        
        # Should have full terms data
        self.assertIn('total_price', data)
        self.assertIn('deposit_amount', data)
        self.assertIn('milestones', data)
    
    def test_financial_terms_none(self):
        """Test financial_terms when not configured."""
        deal = DealFactory()
        # No financial terms created
        
        serializer = DealSerializer(deal)
        self.assertIsNone(serializer.data['financial_terms'])
