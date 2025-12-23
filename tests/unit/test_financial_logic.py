"""
Unit tests for financial business logic.

Tests deposit tracking, payment schedules, financing calculations,
and Deal model business logic methods.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from deals.models import Deal
from deals.financial_models import (
    DealFinancialTerms,
    PaymentMilestone,
    FinancingOption,
    FinancingInstallment
)
from payments.models import Payment, Currency
from vehicles.models import Vehicle

from tests.factories import (
    DealFinancialTermsFactory,
    PaymentMilestoneFactory,
    FinancingOptionFactory,
    FinancingInstallmentFactory,
    DealFactory,
    VehicleFactory,
    CustomerUserFactory,
    DealerUserFactory,
    CurrencyFactory,
    PaymentFactory,
    create_deal_with_financial_terms,
    create_deal_with_payment_schedule,
    create_financed_deal,
    create_deal_with_paid_deposit
)

User = get_user_model()


# CAD currency fixture required by Deal.create_financial_terms()
@pytest.fixture(autouse=True)
def setup_cad_currency(db):
    """Automatically create CAD currency for all tests."""
    from payments.models import Currency
    Currency.objects.get_or_create(
        code='CAD',
        defaults={
            'name': 'Canadian Dollar',
            'symbol': '$',
            'is_active': True
        }
    )


# ============================================================================
# DealFinancialTerms Tests
# ============================================================================

@pytest.mark.django_db
class TestDealFinancialTerms:
    """Test DealFinancialTerms model and methods."""
    
    def test_create_financial_terms(self):
        """Test creating financial terms."""
        financial_terms = DealFinancialTermsFactory()
        
        assert financial_terms.total_price > 0
        assert financial_terms.deposit_percentage == Decimal('20.00')
        assert financial_terms.deposit_amount > 0
        assert financial_terms.balance_remaining > 0
        assert financial_terms.total_paid == Decimal('0.00')
        assert not financial_terms.deposit_paid
    
    def test_calculate_deposit(self):
        """Test deposit calculation from percentage."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            deposit_percentage=Decimal('20.00')
        )
        
        calculated_deposit = financial_terms.calculate_deposit()
        
        assert calculated_deposit == Decimal('10000.00')
        assert calculated_deposit == financial_terms.deposit_amount
    
    def test_calculate_deposit_custom_percentage(self):
        """Test deposit calculation with custom percentage."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            deposit_percentage=Decimal('25.00')
        )
        
        financial_terms.deposit_amount = financial_terms.calculate_deposit()
        financial_terms.save()
        
        assert financial_terms.deposit_amount == Decimal('12500.00')
    
    def test_calculate_balance(self):
        """Test balance calculation."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('10000.00')
        )
        
        balance = financial_terms.calculate_balance()
        
        assert balance == Decimal('40000.00')
    
    def test_record_payment_updates_total_paid(self):
        """Test recording payment updates total_paid."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            deposit_amount=Decimal('10000.00'),
            total_paid=Decimal('0.00'),
            balance_remaining=Decimal('50000.00')
        )
        
        financial_terms.record_payment(Decimal('10000.00'))
        
        assert financial_terms.total_paid == Decimal('10000.00')
        assert financial_terms.balance_remaining == Decimal('40000.00')
    
    def test_record_payment_marks_deposit_paid(self):
        """Test recording deposit payment marks deposit_paid flag."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            deposit_amount=Decimal('10000.00'),
            total_paid=Decimal('0.00'),
            deposit_paid=False
        )
        
        financial_terms.record_payment(Decimal('10000.00'))
        
        assert financial_terms.deposit_paid
        assert financial_terms.deposit_paid_at is not None
    
    def test_record_partial_deposit_doesnt_mark_paid(self):
        """Test partial deposit doesn't mark deposit_paid."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            deposit_amount=Decimal('10000.00'),
            total_paid=Decimal('0.00'),
            deposit_paid=False
        )
        
        financial_terms.record_payment(Decimal('5000.00'))
        
        assert not financial_terms.deposit_paid
        assert financial_terms.deposit_paid_at is None
    
    def test_is_deposit_overdue_not_overdue(self):
        """Test deposit overdue detection when not overdue."""
        financial_terms = DealFinancialTermsFactory(
            deposit_due_date=timezone.now() + timedelta(days=5),
            deposit_paid=False,
            grace_period_days=3
        )
        
        assert not financial_terms.is_deposit_overdue()
    
    def test_is_deposit_overdue_within_grace_period(self):
        """Test deposit not overdue within grace period."""
        financial_terms = DealFinancialTermsFactory(
            deposit_due_date=timezone.now() - timedelta(days=2),
            deposit_paid=False,
            grace_period_days=3
        )
        
        assert not financial_terms.is_deposit_overdue()
    
    def test_is_deposit_overdue_after_grace_period(self):
        """Test deposit overdue after grace period."""
        financial_terms = DealFinancialTermsFactory(
            deposit_due_date=timezone.now() - timedelta(days=5),
            deposit_paid=False,
            grace_period_days=3
        )
        
        assert financial_terms.is_deposit_overdue()
    
    def test_is_deposit_overdue_already_paid(self):
        """Test deposit not overdue if already paid."""
        financial_terms = DealFinancialTermsFactory(
            deposit_due_date=timezone.now() - timedelta(days=10),
            deposit_paid=True,
            grace_period_days=3
        )
        
        assert not financial_terms.is_deposit_overdue()
    
    def test_is_balance_overdue(self):
        """Test balance overdue detection."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('10000.00'),
            balance_due_date=timezone.now() - timedelta(days=5),
            grace_period_days=3
        )
        
        assert financial_terms.is_balance_overdue()
    
    def test_is_balance_not_overdue_if_fully_paid(self):
        """Test balance not overdue if fully paid."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('50000.00'),
            balance_remaining=Decimal('0.00'),
            balance_due_date=timezone.now() - timedelta(days=5),
            grace_period_days=3
        )
        
        assert not financial_terms.is_balance_overdue()
    
    def test_get_payment_progress_percentage(self):
        """Test payment progress percentage calculation."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('25000.00')
        )
        
        progress = financial_terms.get_payment_progress_percentage()
        
        assert progress == Decimal('50.00')
    
    def test_get_payment_progress_percentage_zero(self):
        """Test payment progress at 0%."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('0.00')
        )
        
        progress = financial_terms.get_payment_progress_percentage()
        
        assert progress == Decimal('0.00')
    
    def test_get_payment_progress_percentage_full(self):
        """Test payment progress at 100%."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('50000.00')
        )
        
        progress = financial_terms.get_payment_progress_percentage()
        
        assert progress == Decimal('100.00')
    
    def test_is_fully_paid_true(self):
        """Test is_fully_paid returns True when balance is zero."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('50000.00'),
            balance_remaining=Decimal('0.00')
        )
        
        assert financial_terms.is_fully_paid()
    
    def test_is_fully_paid_false(self):
        """Test is_fully_paid returns False when balance remains."""
        financial_terms = DealFinancialTermsFactory(
            total_price=Decimal('50000.00'),
            total_paid=Decimal('25000.00'),
            balance_remaining=Decimal('25000.00')
        )
        
        assert not financial_terms.is_fully_paid()


# ============================================================================
# PaymentMilestone Tests
# ============================================================================

@pytest.mark.django_db
class TestPaymentMilestone:
    """Test PaymentMilestone model and methods."""
    
    def test_create_payment_milestone(self):
        """Test creating a payment milestone."""
        milestone = PaymentMilestoneFactory()
        
        assert milestone.milestone_type in ['deposit', 'inspection', 'documentation', 
                                            'pre_shipment', 'delivery', 'custom']
        assert milestone.amount_due > 0
        assert milestone.amount_paid == Decimal('0.00')
        assert milestone.status == 'pending'
    
    def test_is_overdue_not_overdue(self):
        """Test milestone not overdue when due date is future."""
        milestone = PaymentMilestoneFactory(
            due_date=timezone.now() + timedelta(days=5),
            status='pending'
        )
        
        assert not milestone.is_overdue()
    
    def test_is_overdue_true(self):
        """Test milestone overdue when past due date."""
        milestone = PaymentMilestoneFactory(
            due_date=timezone.now() - timedelta(days=2),
            status='pending'
        )
        
        assert milestone.is_overdue()
    
    def test_is_overdue_false_when_paid(self):
        """Test milestone not overdue if already paid."""
        milestone = PaymentMilestoneFactory(
            due_date=timezone.now() - timedelta(days=5),
            status='paid'
        )
        
        assert not milestone.is_overdue()
    
    def test_record_payment_full_payment(self):
        """Test recording full payment updates status to paid."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000.00'),
            amount_paid=Decimal('0.00'),
            status='pending'
        )
        
        payment = PaymentFactory(amount=Decimal('10000.00'))
        milestone.record_payment(payment)
        
        assert milestone.amount_paid == Decimal('10000.00')
        assert milestone.status == 'paid'
        assert milestone.paid_at is not None
        assert payment in milestone.payments.all()
    
    def test_record_payment_partial_payment(self):
        """Test recording partial payment updates status to partial."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000.00'),
            amount_paid=Decimal('0.00'),
            status='pending'
        )
        
        payment = PaymentFactory(amount=Decimal('5000.00'))
        milestone.record_payment(payment)
        
        assert milestone.amount_paid == Decimal('5000.00')
        assert milestone.status == 'partial'
        assert milestone.paid_at is None  # Not fully paid
    
    def test_record_multiple_payments(self):
        """Test recording multiple payments accumulates amount."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000.00'),
            amount_paid=Decimal('0.00'),
            status='pending'
        )
        
        payment1 = PaymentFactory(amount=Decimal('3000.00'))
        milestone.record_payment(payment1)
        
        assert milestone.amount_paid == Decimal('3000.00')
        assert milestone.status == 'partial'
        
        payment2 = PaymentFactory(amount=Decimal('7000.00'))
        milestone.record_payment(payment2)
        
        assert milestone.amount_paid == Decimal('10000.00')
        assert milestone.status == 'paid'
    
    def test_get_amount_remaining(self):
        """Test getting remaining amount on milestone."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000.00'),
            amount_paid=Decimal('4000.00')
        )
        
        remaining = milestone.get_amount_remaining()
        
        assert remaining == Decimal('6000.00')
    
    def test_get_amount_remaining_fully_paid(self):
        """Test remaining amount is zero when fully paid."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000.00'),
            amount_paid=Decimal('10000.00')
        )
        
        remaining = milestone.get_amount_remaining()
        
        assert remaining == Decimal('0.00')
    
    def test_get_payment_percentage(self):
        """Test payment percentage calculation."""
        milestone = PaymentMilestoneFactory(
            amount_due=Decimal('10000.00'),
            amount_paid=Decimal('7500.00')
        )
        
        percentage = milestone.get_payment_percentage()
        
        assert percentage == Decimal('75.00')


# ============================================================================
# FinancingOption Tests
# ============================================================================

@pytest.mark.django_db
class TestFinancingOption:
    """Test FinancingOption model and calculations."""
    
    def test_create_financing_option(self):
        """Test creating financing option."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36
        )
        
        assert financing.financed_amount == Decimal('40000.00')
        assert financing.interest_rate == Decimal('5.90')
        assert financing.term_months == 36
        assert financing.monthly_payment > 0  # Auto-calculated
    
    def test_calculate_monthly_payment_with_interest(self):
        """Test monthly payment calculation with interest."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36
        )
        
        monthly_payment = financing.calculate_monthly_payment()
        
        # Expected: ~$1,215.07 (using standard amortization formula)
        assert Decimal('1210.00') < monthly_payment < Decimal('1220.00')
    
    def test_calculate_monthly_payment_zero_interest(self):
        """Test monthly payment with 0% interest."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('36000.00'),
            interest_rate=Decimal('0.00'),
            term_months=36
        )
        
        monthly_payment = financing.calculate_monthly_payment()
        
        # With 0% interest, it's simple division
        assert monthly_payment == Decimal('1000.00')
    
    def test_calculate_monthly_payment_higher_rate(self):
        """Test monthly payment with higher interest rate."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('10.00'),
            term_months=36
        )
        
        monthly_payment = financing.calculate_monthly_payment()
        
        # Higher interest = higher payment
        assert monthly_payment > Decimal('1290.00')
    
    def test_calculate_total_interest(self):
        """Test total interest calculation."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36
        )
        
        financing.monthly_payment = financing.calculate_monthly_payment()
        total_interest = financing.calculate_total_interest()
        
        # Total interest should be positive
        assert total_interest > 0
        assert total_interest < Decimal('5000.00')  # Reasonable range
    
    def test_calculate_total_interest_zero_interest(self):
        """Test total interest is zero with 0% rate."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('36000.00'),
            interest_rate=Decimal('0.00'),
            term_months=36
        )
        
        financing.monthly_payment = financing.calculate_monthly_payment()
        total_interest = financing.calculate_total_interest()
        
        assert total_interest == Decimal('0.00')
    
    def test_auto_calculation_on_save(self):
        """Test that monthly_payment is auto-calculated on save."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36,
            monthly_payment=Decimal('0.00')  # Set to 0
        )
        
        financing.save()  # Should trigger auto-calculation
        
        assert financing.monthly_payment > 0
        assert financing.total_interest > 0
        assert financing.total_amount > financing.financed_amount
    
    def test_generate_installment_schedule(self):
        """Test generating installment schedule."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36,
            first_payment_date=date.today() + timedelta(days=30)
        )
        
        installments = financing.generate_installment_schedule()
        
        assert len(installments) == 36
        assert all(inst.financing == financing for inst in installments)
        assert installments[0].installment_number == 1
        assert installments[-1].installment_number == 36
    
    def test_installment_schedule_dates_sequential(self):
        """Test installment due dates are sequential months."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=12,
            first_payment_date=date(2025, 1, 15)
        )
        
        installments = financing.generate_installment_schedule()
        
        # Check dates increase by roughly 30 days
        for i in range(len(installments) - 1):
            days_diff = (installments[i+1].due_date - installments[i].due_date).days
            assert 28 <= days_diff <= 31  # Account for month variations
    
    def test_installment_schedule_last_balance_zero(self):
        """Test last installment has zero remaining balance."""
        financing = FinancingOptionFactory(
            financed_amount=Decimal('40000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36
        )
        
        installments = financing.generate_installment_schedule()
        last_installment = installments[-1]
        
        assert last_installment.remaining_balance == Decimal('0.00')


# ============================================================================
# FinancingInstallment Tests
# ============================================================================

@pytest.mark.django_db
class TestFinancingInstallment:
    """Test FinancingInstallment model and methods."""
    
    def test_create_financing_installment(self):
        """Test creating financing installment."""
        installment = FinancingInstallmentFactory()
        
        assert installment.installment_number > 0
        assert installment.amount_due > 0
        assert installment.principal_amount > 0
        assert installment.interest_amount >= 0
        assert installment.status == 'pending'
    
    def test_is_late_not_late(self):
        """Test installment not late when before due date."""
        installment = FinancingInstallmentFactory(
            due_date=date.today() + timedelta(days=5),
            status='pending'
        )
        
        assert not installment.is_late()
    
    def test_is_late_true(self):
        """Test installment is late after due date."""
        installment = FinancingInstallmentFactory(
            due_date=date.today() - timedelta(days=3),
            status='pending'
        )
        
        assert installment.is_late()
    
    def test_is_late_false_when_paid(self):
        """Test installment not late if already paid."""
        installment = FinancingInstallmentFactory(
            due_date=date.today() - timedelta(days=10),
            status='paid'
        )
        
        assert not installment.is_late()
    
    def test_calculate_days_late(self):
        """Test calculating days late."""
        installment = FinancingInstallmentFactory(
            due_date=date.today() - timedelta(days=7),
            status='pending'
        )
        
        days_late = installment.calculate_days_late()
        
        assert days_late == 7
    
    def test_calculate_days_late_not_late(self):
        """Test days late is zero when not overdue."""
        installment = FinancingInstallmentFactory(
            due_date=date.today() + timedelta(days=5),
            status='pending'
        )
        
        days_late = installment.calculate_days_late()
        
        assert days_late == 0
    
    def test_calculate_late_fee_default(self):
        """Test late fee calculation with default 5%."""
        # Create installment with past due date
        past_date = timezone.now().date() - timedelta(days=10)
        installment = FinancingInstallmentFactory(
            amount_due=Decimal('1000.00'),
            due_date=past_date,
            status='pending',
            late_fee=Decimal('0.00')
        )
        
        late_fee = installment.calculate_late_fee()
        
        assert late_fee == Decimal('50.00')  # 5% of 1000
    
    def test_calculate_late_fee_custom_percentage(self):
        """Test late fee with custom percentage."""
        # Create installment with past due date
        past_date = timezone.now().date() - timedelta(days=10)
        installment = FinancingInstallmentFactory(
            amount_due=Decimal('1000.00'),
            due_date=past_date,
            status='pending',
            late_fee=Decimal('0.00')
        )
        
        late_fee = installment.calculate_late_fee(percentage=Decimal('10.00'))
        
        assert late_fee == Decimal('100.00')  # 10% of 1000
    
    def test_record_payment(self):
        """Test recording payment for installment."""
        installment = FinancingInstallmentFactory(
            amount_due=Decimal('1206.43'),
            amount_paid=Decimal('0.00'),
            status='pending'
        )
        
        payment = PaymentFactory(amount=Decimal('1206.43'))
        installment.record_payment(payment)
        
        assert installment.amount_paid == Decimal('1206.43')
        assert installment.status == 'paid'
        assert installment.paid_at is not None
        assert installment.payment == payment
    
    def test_record_late_payment_adds_late_fee(self):
        """Test recording late payment includes late fee."""
        installment = FinancingInstallmentFactory(
            amount_due=Decimal('1000.00'),
            due_date=date.today() - timedelta(days=10),
            late_fee=Decimal('0.00'),
            status='pending'
        )
        
        # Calculate and add late fee
        installment.late_fee = installment.calculate_late_fee()
        installment.save()
        
        assert installment.late_fee == Decimal('50.00')
        
        # Payment includes late fee
        payment = PaymentFactory(amount=Decimal('1050.00'))
        installment.record_payment(payment)
        
        assert installment.status == 'paid'


# ============================================================================
# Deal Business Logic Tests
# ============================================================================

@pytest.mark.django_db
class TestDealBusinessLogic:
    """Test Deal model business logic methods."""
    
    def test_create_financial_terms_default_deposit(self):
        """Test creating financial terms with default 20% deposit."""
        deal = DealFactory(agreed_price_cad=Decimal('50000.00'))
        
        financial_terms = deal.create_financial_terms()
        
        assert financial_terms.total_price == Decimal('50000.00')
        assert financial_terms.deposit_percentage == Decimal('20.00')
        assert financial_terms.deposit_amount == Decimal('10000.00')
        assert financial_terms.balance_remaining == Decimal('50000.00')
        assert financial_terms.deposit_due_date is not None
    
    def test_create_financial_terms_custom_deposit(self):
        """Test creating financial terms with custom deposit percentage."""
        deal = DealFactory(agreed_price_cad=Decimal('50000.00'))
        
        financial_terms = deal.create_financial_terms(
            deposit_percentage=Decimal('25.00')
        )
        
        assert financial_terms.deposit_percentage == Decimal('25.00')
        assert financial_terms.deposit_amount == Decimal('12500.00')
    
    def test_create_standard_payment_schedule(self):
        """Test creating standard 5-milestone payment schedule."""
        deal, financial_terms = create_deal_with_financial_terms()
        
        milestones = deal.create_standard_payment_schedule()
        
        assert len(milestones) == 5
        assert milestones[0].milestone_type == 'deposit'
        assert milestones[1].milestone_type == 'inspection'
        assert milestones[2].milestone_type == 'documentation'
        assert milestones[3].milestone_type == 'pre_shipment'
        assert milestones[4].milestone_type == 'delivery'
    
    def test_payment_schedule_percentages_sum_to_100(self):
        """Test payment schedule percentages add up to 100%."""
        deal, financial_terms = create_deal_with_financial_terms()
        
        milestones = deal.create_standard_payment_schedule()
        
        total_amount = sum(m.amount_due for m in milestones)
        
        # Should equal total price (within rounding)
        assert abs(total_amount - financial_terms.total_price) < Decimal('1.00')
    
    def test_payment_schedule_sequential_due_dates(self):
        """Test payment schedule has sequential due dates."""
        deal, financial_terms = create_deal_with_financial_terms()
        
        milestones = deal.create_standard_payment_schedule()
        
        for i in range(len(milestones) - 1):
            assert milestones[i].due_date < milestones[i+1].due_date
    
    def test_setup_financing(self):
        """Test setting up financing for a deal."""
        deal = DealFactory(agreed_price_cad=Decimal('50000.00'))
        financial_terms = deal.create_financial_terms()
        
        financing = deal.setup_financing(
            financed_amount=Decimal('40000.00'),
            down_payment=Decimal('10000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36,
            lender_name='Test Bank'
        )
        
        assert financing.financed_amount == Decimal('40000.00')
        assert financing.interest_rate == Decimal('5.90')
        assert financing.term_months == 36
        assert financing.monthly_payment > 0
        assert financial_terms.is_financed
    
    def test_setup_financing_generates_installments(self):
        """Test setup_financing generates installment schedule."""
        deal = DealFactory(agreed_price_cad=Decimal('50000.00'))
        financial_terms = deal.create_financial_terms()
        
        financing = deal.setup_financing(
            financed_amount=Decimal('40000.00'),
            down_payment=Decimal('10000.00'),
            interest_rate=Decimal('5.90'),
            term_months=36
        )
        
        installments = financing.installments.all()
        
        assert installments.count() == 36
    
    def test_get_payment_status_summary_no_financial_terms(self):
        """Test payment status summary when no financial terms."""
        deal = DealFactory()
        
        summary = deal.get_payment_status_summary()
        
        assert summary['status'] == 'not_configured'
    
    def test_get_payment_status_summary_with_financial_terms(self):
        """Test payment status summary with financial terms."""
        deal, financial_terms = create_deal_with_financial_terms()
        
        summary = deal.get_payment_status_summary()
        
        assert 'total_price' in summary
        assert 'deposit' in summary
        assert 'balance' in summary
        assert summary['total_price'] == financial_terms.total_price
        assert summary['fully_paid'] is False
    
    def test_get_payment_status_summary_with_milestones(self):
        """Test payment status summary includes milestone info."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        summary = deal.get_payment_status_summary()
        
        assert 'milestones' in summary
        assert summary['milestones']['total'] == 5
        assert summary['milestones']['pending'] == 5
        assert summary['milestones']['paid'] == 0
    
    def test_process_payment_allocates_to_milestone(self):
        """Test process_payment allocates to first pending milestone."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        # Get initial values
        initial_balance = financial_terms.balance_remaining
        first_milestone = milestones[0]
        payment_amount = first_milestone.amount_due
        
        # Create payment matching first milestone
        payment = PaymentFactory(
            deal=deal,
            amount=payment_amount,
            status='succeeded'
        )
        
        # Process payment
        deal.process_payment(payment)
        
        # Refresh financial terms
        financial_terms.refresh_from_db()
        
        assert financial_terms.total_paid == payment_amount
        # Compare with quantized decimal to avoid floating point precision issues
        expected_balance = (initial_balance - payment_amount).quantize(Decimal('0.01'))
        assert financial_terms.balance_remaining == expected_balance
        
        # First milestone should be paid
        first_milestone.refresh_from_db()
        assert first_milestone.status == 'paid'
    
    def test_process_payment_updates_deal_status(self):
        """Test process_payment updates deal payment_status."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        assert deal.payment_status == 'pending'
        
        # Pay deposit
        payment = PaymentFactory(
            deal=deal,
            amount=Decimal('10000.00'),
            status='succeeded'
        )
        deal.process_payment(payment)
        
        deal.refresh_from_db()
        assert deal.payment_status == 'partial'
    
    def test_process_payment_marks_deal_paid_when_full(self):
        """Test process_payment marks deal paid when fully paid."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        # Pay full amount (total price)
        total_amount = financial_terms.total_price
        payment = PaymentFactory(
            deal=deal,
            amount=total_amount,
            status='succeeded'
        )
        deal.process_payment(payment)
        
        deal.refresh_from_db()
        financial_terms.refresh_from_db()
        
        assert deal.payment_status == 'paid'
        assert financial_terms.is_fully_paid()
    
    def test_get_next_payment_due_first_milestone(self):
        """Test get_next_payment_due returns first milestone."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        next_payment = deal.get_next_payment_due()
        
        assert next_payment is not None
        assert next_payment.milestone_type == 'deposit'
        assert next_payment.status == 'pending'
    
    def test_get_next_payment_due_after_partial_payment(self):
        """Test get_next_payment_due after some payments."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        # Pay first milestone
        first_milestone = milestones[0]
        payment = PaymentFactory(amount=first_milestone.amount_due)
        first_milestone.record_payment(payment)
        
        next_payment = deal.get_next_payment_due()
        
        assert next_payment is not None
        assert next_payment.milestone_type == 'inspection'
    
    def test_get_next_payment_due_all_paid(self):
        """Test get_next_payment_due returns None when all paid."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        # Pay all milestones
        for milestone in milestones:
            payment = PaymentFactory(amount=milestone.amount_due)
            milestone.record_payment(payment)
        
        next_payment = deal.get_next_payment_due()
        
        assert next_payment is None


# ============================================================================
# Integration Tests (Factory Utility Functions)
# ============================================================================

@pytest.mark.django_db
class TestFinancialIntegration:
    """Integration tests using factory utility functions."""
    
    def test_create_deal_with_financial_terms(self):
        """Test utility function creates deal with financial terms."""
        deal, financial_terms = create_deal_with_financial_terms()
        
        assert deal.id is not None
        assert financial_terms.id is not None
        assert financial_terms.deal == deal
        assert hasattr(deal, 'financial_terms')
    
    def test_create_deal_with_payment_schedule(self):
        """Test utility function creates deal with schedule."""
        deal, financial_terms, milestones = create_deal_with_payment_schedule()
        
        assert deal.id is not None
        assert financial_terms.id is not None
        assert len(milestones) == 5
        assert all(m.deal_financial_terms == financial_terms for m in milestones)
    
    def test_create_financed_deal(self):
        """Test utility function creates financed deal."""
        deal, financial_terms, financing, installments = create_financed_deal()
        
        assert deal.id is not None
        assert financing.id is not None
        assert financing.deal == deal
        assert len(installments) == 36
        assert financial_terms.is_financed
    
    def test_create_deal_with_paid_deposit(self):
        """Test utility function creates deal with paid deposit."""
        deal, financial_terms, deposit_payment = create_deal_with_paid_deposit()
        
        assert deal.id is not None
        assert deposit_payment.id is not None
        assert financial_terms.deposit_paid
        assert financial_terms.total_paid >= financial_terms.deposit_amount
        
        # First milestone should be paid
        first_milestone = PaymentMilestone.objects.filter(
            deal_financial_terms=financial_terms
        ).order_by('sequence').first()
        assert first_milestone.status == 'paid'
