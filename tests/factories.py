"""
Factory classes for generating test data using factory_boy.

These factories create model instances with realistic test data for unit and integration tests.
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

fake = Faker()


# ============================================================================
# User Factories
# ============================================================================

class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = 'accounts.User'
        django_get_or_create = ('email',)
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'buyer'
    phone = factory.Faker('phone_number')
    country = factory.Faker('country')
    is_active = True
    is_staff = False
    is_superuser = False
    
    # Data consent (required for PIPEDA/Law 25 compliance)
    data_processing_consent = True
    marketing_consent = True
    consent_date = factory.LazyFunction(timezone.now)
    consent_ip_address = factory.Faker('ipv4')
    consent_version = '1.0'
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password for user."""
        if not create:
            return
        
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('TestPassword123!')


class CustomerUserFactory(UserFactory):
    """Factory for customer users."""
    role = 'buyer'


class DealerUserFactory(UserFactory):
    """Factory for dealer users."""
    role = 'dealer'
    company_name = factory.Faker('company')


class BrokerUserFactory(UserFactory):
    """Factory for broker users."""
    role = 'broker'
    company_name = factory.Faker('company')


class AdminUserFactory(UserFactory):
    """Factory for admin users."""
    role = 'admin'
    is_staff = True
    is_superuser = True


# ============================================================================
# Currency Factory
# ============================================================================

class CurrencyFactory(DjangoModelFactory):
    """Factory for creating Currency instances."""
    
    class Meta:
        model = 'payments.Currency'
        django_get_or_create = ('code',)
    
    code = 'USD'
    name = 'US Dollar'
    symbol = '$'
    exchange_rate_to_usd = Decimal('1.00')
    is_active = True
    is_african = False
    country = 'United States'
    stripe_supported = True


class AFNCurrencyFactory(CurrencyFactory):
    """Factory for African currencies."""
    code = 'ZAR'
    name = 'South African Rand'
    symbol = 'R'
    exchange_rate_to_usd = Decimal('18.50')
    is_african = True
    country = 'South Africa'


# ============================================================================
# Vehicle Factories
# ============================================================================

class VehicleFactory(DjangoModelFactory):
    """Factory for creating Vehicle instances."""
    
    class Meta:
        model = 'vehicles.Vehicle'
    
    dealer = factory.SubFactory(DealerUserFactory)
    
    # Basic Information
    make = factory.Faker('random_element', elements=['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes-Benz', 'Nissan', 'Chevrolet'])
    model = factory.Faker('random_element', elements=['Camry', 'Accord', 'F-150', 'X5', 'E-Class', 'Altima', 'Silverado'])
    year = factory.Faker('random_int', min=2015, max=2024)
    vin = factory.Sequence(lambda n: f'1HGBH41JXMN{n:06d}')
    
    # Details
    condition = factory.Faker('random_element', elements=['new', 'used_excellent', 'used_good', 'used_fair'])
    mileage = factory.Faker('random_int', min=0, max=150000)
    color = factory.Faker('random_element', elements=['Black', 'White', 'Silver', 'Red', 'Blue', 'Gray'])
    fuel_type = factory.Faker('random_element', elements=['gasoline', 'diesel', 'electric', 'hybrid'])
    transmission = factory.Faker('random_element', elements=['Automatic', 'Manual', 'CVT'])
    engine_type = factory.Faker('random_element', elements=['4-cylinder', '6-cylinder', '8-cylinder', 'electric'])
    drivetrain = factory.Faker('random_element', elements=['fwd', 'rwd', 'awd', '4wd'])
    
    # Pricing (correct field name from Vehicle model)
    price_cad = factory.LazyFunction(lambda: Decimal(str(random.uniform(15000, 75000))))
    
    # Location (single field in Vehicle model)
    location = factory.Faker('city')
    
    # Status
    status = 'available'
    
    # Description
    description = factory.Faker('text', max_nb_chars=500)


class VehicleImageFactory(DjangoModelFactory):
    """Factory for creating VehicleImage instances."""
    
    class Meta:
        model = 'vehicles.VehicleImage'
    
    vehicle = factory.SubFactory(VehicleFactory)
    image = factory.django.ImageField(color='blue', width=800, height=600)
    caption = factory.Faker('sentence')
    is_primary = False
    order = factory.Sequence(lambda n: n)


# ============================================================================
# Deal Factories
# ============================================================================

class DealFactory(DjangoModelFactory):
    """Factory for creating Deal instances."""
    
    class Meta:
        model = 'deals.Deal'
    
    vehicle = factory.SubFactory(VehicleFactory)
    buyer = factory.SubFactory(CustomerUserFactory)
    dealer = factory.LazyAttribute(lambda obj: obj.vehicle.dealer)
    
    # Pricing - Deal model has agreed_price_cad field
    agreed_price_cad = factory.LazyAttribute(lambda obj: obj.vehicle.price_cad)
    
    # Payment Information
    payment_method = 'bank_transfer'
    payment_status = 'pending'
    
    # Deal Status - Deal model uses 'pending_docs' not 'pending'
    status = 'pending_docs'
    
    # Notes
    notes = factory.Faker('text', max_nb_chars=300)


class LeadFactory(DjangoModelFactory):
    """Factory for creating Lead instances."""
    
    class Meta:
        model = 'deals.Lead'
    
    buyer = factory.SubFactory(CustomerUserFactory)
    vehicle = factory.SubFactory(VehicleFactory)
    broker = factory.SubFactory(BrokerUserFactory)
    
    status = 'new'
    source = 'website'
    notes = factory.Faker('text', max_nb_chars=300)
    last_contacted = factory.LazyFunction(timezone.now)


# ============================================================================
# Payment Factories
# ============================================================================

class PaymentMethodFactory(DjangoModelFactory):
    """Factory for creating PaymentMethod instances."""
    
    class Meta:
        model = 'payments.PaymentMethod'
    
    user = factory.SubFactory(UserFactory)
    type = 'card'
    
    # Card details
    card_brand = 'Visa'
    card_last4 = factory.Sequence(lambda n: f'{n:04d}')
    card_exp_month = factory.Faker('random_int', min=1, max=12)
    card_exp_year = factory.Faker('random_int', min=2024, max=2030)
    
    currency = factory.SubFactory(CurrencyFactory)
    is_default = False
    is_verified = True
    
    stripe_payment_method_id = factory.Sequence(lambda n: f'pm_test_{n}')


class PaymentFactory(DjangoModelFactory):
    """Factory for creating Payment instances."""
    
    class Meta:
        model = 'payments.Payment'
    
    user = factory.SubFactory(CustomerUserFactory)
    deal = factory.SubFactory(DealFactory)
    payment_method = factory.SubFactory(PaymentMethodFactory)
    
    payment_for = 'deal_deposit'
    amount = factory.LazyFunction(lambda: Decimal(str(random.uniform(500, 10000))))
    currency = factory.SubFactory(CurrencyFactory)
    amount_in_usd = factory.LazyAttribute(lambda obj: obj.amount)
    
    status = 'succeeded'
    
    stripe_payment_intent_id = factory.Sequence(lambda n: f'pi_test_{n}')
    stripe_charge_id = factory.Sequence(lambda n: f'ch_test_{n}')
    
    description = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)


class InvoiceFactory(DjangoModelFactory):
    """Factory for creating Invoice instances."""
    
    class Meta:
        model = 'payments.Invoice'
    
    user = factory.SubFactory(CustomerUserFactory)
    deal = factory.SubFactory(DealFactory)
    
    invoice_number = factory.Sequence(lambda n: f'INV-{n:06d}')
    status = 'draft'
    
    subtotal = factory.LazyFunction(lambda: Decimal(str(random.uniform(10000, 50000))))
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal('0.13'))
    total = factory.LazyAttribute(lambda obj: obj.subtotal + obj.tax_amount)
    
    currency = factory.SubFactory(CurrencyFactory)
    
    issue_date = factory.LazyFunction(lambda: timezone.now().date())
    due_date = factory.LazyFunction(lambda: (timezone.now() + timedelta(days=30)).date())
    notes = factory.Faker('text', max_nb_chars=200)


class InvoiceItemFactory(DjangoModelFactory):
    """Factory for creating InvoiceItem instances."""
    
    class Meta:
        model = 'payments.InvoiceItem'
    
    invoice = factory.SubFactory(InvoiceFactory)
    
    description = factory.Faker('sentence')
    quantity = factory.Faker('random_int', min=1, max=5)
    unit_price = factory.LazyFunction(lambda: Decimal(str(random.uniform(100, 10000))))
    total = factory.LazyAttribute(lambda obj: obj.quantity * obj.unit_price)


# ============================================================================
# Shipment Factories
# ============================================================================

class ShipmentFactory(DjangoModelFactory):
    """Factory for creating Shipment instances."""
    
    class Meta:
        model = 'shipments.Shipment'
    
    deal = factory.SubFactory(DealFactory)
    
    tracking_number = factory.Sequence(lambda n: f'SHIP{n:08d}')
    shipping_company = factory.Faker('company')
    
    origin_port = factory.Faker('city')
    destination_port = factory.Faker('city')
    destination_country = factory.Faker('country')
    
    status = 'pending'
    
    estimated_departure = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=7))
    estimated_arrival = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=30))
    
    notes = factory.Faker('text', max_nb_chars=300)


class ShipmentUpdateFactory(DjangoModelFactory):
    """Factory for creating ShipmentUpdate instances."""
    
    class Meta:
        model = 'shipments.ShipmentUpdate'
    
    shipment = factory.SubFactory(ShipmentFactory)
    
    status = factory.Faker('random_element', elements=['pending', 'in_transit', 'customs', 'delivered'])
    location = factory.Faker('city')
    description = factory.Faker('sentence')
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    created_at = factory.LazyFunction(timezone.now)


# ============================================================================
# Review/Rating Factories
# ============================================================================

class DealerRatingFactory(DjangoModelFactory):
    """Factory for creating DealerRating instances (aggregated stats)."""
    
    class Meta:
        model = 'reviews.DealerRating'
    
    dealer = factory.SubFactory(DealerUserFactory)
    
    # Overall stats
    total_reviews = factory.Faker('random_int', min=0, max=100)
    average_rating = factory.Faker('pydecimal', left_digits=1, right_digits=2, min_value=0, max_value=5)
    
    # Rating distribution
    five_star_count = factory.Faker('random_int', min=0, max=20)
    four_star_count = factory.Faker('random_int', min=0, max=20)
    three_star_count = factory.Faker('random_int', min=0, max=20)
    two_star_count = factory.Faker('random_int', min=0, max=20)
    one_star_count = factory.Faker('random_int', min=0, max=20)
    
    # Detailed averages
    avg_vehicle_condition = factory.Faker('pydecimal', left_digits=1, right_digits=2, min_value=0, max_value=5)
    avg_communication = factory.Faker('pydecimal', left_digits=1, right_digits=2, min_value=0, max_value=5)
    avg_delivery = factory.Faker('pydecimal', left_digits=1, right_digits=2, min_value=0, max_value=5)
    avg_value = factory.Faker('pydecimal', left_digits=1, right_digits=2, min_value=0, max_value=5)
    
    # Recommendation stats
    recommend_count = factory.Faker('random_int', min=0, max=50)
    recommend_percentage = factory.Faker('random_int', min=0, max=100)


# ============================================================================
# Commission/Tier Factories
# ============================================================================

class DealerTierFactory(DjangoModelFactory):
    """Factory for creating DealerTier instances."""
    
    class Meta:
        model = 'commissions.DealerTier'
    
    dealer = factory.SubFactory(DealerUserFactory)
    
    current_tier = 'bronze'
    total_sales = Decimal('0.00')
    total_commission_earned = Decimal('0.00')
    sales_count = 0
    average_rating = Decimal('0.00')
    
    tier_start_date = factory.LazyFunction(timezone.now)


# ============================================================================
# Vehicle History Factory
# ============================================================================

class VehicleHistoryReportFactory(DjangoModelFactory):
    """Factory for creating VehicleHistoryReport instances."""
    
    class Meta:
        model = 'vehicle_history.VehicleHistoryReport'
    
    vehicle = factory.SubFactory(VehicleFactory)
    requested_by = factory.SubFactory(UserFactory)
    
    report_provider = factory.Faker('random_element', elements=['CarFax', 'AutoCheck', 'NMVTIS'])
    report_data = factory.Faker('json')
    
    accidents_reported = factory.Faker('random_int', min=0, max=3)
    owners_count = factory.Faker('random_int', min=1, max=5)
    service_records_count = factory.Faker('random_int', min=0, max=20)
    
    has_clean_title = factory.Faker('boolean', chance_of_getting_true=85)
    
    created_at = factory.LazyFunction(timezone.now)


# ============================================================================
# Utility Functions
# ============================================================================

def create_complete_deal_with_payment(buyer=None, dealer=None, **kwargs):
    """
    Utility function to create a complete deal with payment and vehicle.
    
    Args:
        buyer: User instance (optional, creates new customer if None)
        dealer: User instance (optional, creates new dealer if None)
        **kwargs: Additional attributes for Deal
    
    Returns:
        tuple: (deal, payment, vehicle)
    """
    # Create users if not provided
    if buyer is None:
        buyer = CustomerUserFactory()
    if dealer is None:
        dealer = DealerUserFactory()
    
    # Create vehicle
    vehicle = VehicleFactory(dealer=dealer)
    
    # Create deal
    deal = DealFactory(
        vehicle=vehicle,
        buyer=buyer,
        **kwargs
    )
    
    # Create payment
    payment = PaymentFactory(
        user=buyer,
        deal=deal,
        amount=deal.deposit_amount
    )
    
    return deal, payment, vehicle


def create_complete_shipment_flow(buyer=None, dealer=None):
    """
    Utility function to create a complete deal → payment → shipment flow.
    
    Returns:
        tuple: (deal, payment, shipment)
    """
    deal, payment, vehicle = create_complete_deal_with_payment(buyer, dealer)
    
    # Mark deal as paid
    deal.payment_status = 'paid'
    deal.status = 'confirmed'
    deal.save()
    
    # Create shipment
    shipment = ShipmentFactory(deal=deal)
    
    return deal, payment, shipment


# ============================================================================
# Financial Model Factories (NEW - Week 2 Business Logic Implementation)
# ============================================================================

class DealFinancialTermsFactory(DjangoModelFactory):
    """
    Factory for creating DealFinancialTerms instances.
    
    Creates financial terms with realistic deposit and payment structure.
    """
    
    class Meta:
        model = 'deals.DealFinancialTerms'
    
    deal = factory.SubFactory(DealFactory)
    
    # Pricing
    total_price = Decimal('50000.00')
    currency = factory.SubFactory(CurrencyFactory, code='CAD')
    total_price_usd = Decimal('37500.00')
    
    # Deposit (20% standard)
    deposit_percentage = Decimal('20.00')
    deposit_amount = Decimal('10000.00')
    deposit_due_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=3)
    )
    deposit_paid = False
    deposit_paid_at = None
    
    # Balance
    balance_remaining = Decimal('50000.00')  # Full amount initially
    balance_due_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=33)  # 30 days + 3 grace
    )
    
    # Payment terms
    payment_term_days = 30
    grace_period_days = 3
    
    # Tracking
    total_paid = Decimal('0.00')
    
    # Financing
    is_financed = False
    
    # Exchange rate
    locked_exchange_rate = None
    exchange_rate_locked_at = None
    
    # Refund policy
    deposit_refundable = True
    refund_percentage = Decimal('50.00')
    
    # Timestamps
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class PaymentMilestoneFactory(DjangoModelFactory):
    """
    Factory for creating PaymentMilestone instances.
    
    Creates payment milestones with realistic amounts and due dates.
    """
    
    class Meta:
        model = 'deals.PaymentMilestone'
    
    deal_financial_terms = factory.SubFactory(DealFinancialTermsFactory)
    
    # Milestone details
    milestone_type = 'deposit'
    name = factory.LazyAttribute(
        lambda obj: f'{obj.milestone_type.replace("_", " ").title()} Payment'
    )
    description = factory.LazyAttribute(
        lambda obj: f'Payment for {obj.milestone_type.replace("_", " ")}'
    )
    sequence = 1
    
    # Amount
    amount_due = Decimal('10000.00')
    amount_paid = Decimal('0.00')
    currency = factory.SubFactory(CurrencyFactory, code='CAD')
    
    # Dates
    due_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=3)
    )
    paid_at = None
    
    # Status
    status = 'pending'
    
    # Reminders
    reminder_sent = False
    reminder_sent_at = None
    
    # Timestamps
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    
    @factory.post_generation
    def payments(self, create, extracted, **kwargs):
        """Add payments to this milestone if provided."""
        if not create:
            return
        
        if extracted:
            for payment in extracted:
                self.payments.add(payment)


class FinancingOptionFactory(DjangoModelFactory):
    """
    Factory for creating FinancingOption instances.
    
    Creates financing options with realistic loan terms and auto-calculated payments.
    """
    
    class Meta:
        model = 'deals.FinancingOption'
    
    deal = factory.SubFactory(DealFactory)
    
    # Financing details
    financing_type = 'partner_lender'
    lender_name = factory.Faker('company')
    lender_contact = factory.Faker('email')
    
    # Loan terms
    financed_amount = Decimal('40000.00')
    down_payment = Decimal('10000.00')
    interest_rate = Decimal('5.90')  # 5.9% APR
    term_months = 36  # 3 years
    
    # Calculated fields (auto-set on save)
    monthly_payment = Decimal('0.00')  # Will be calculated
    total_interest = Decimal('0.00')   # Will be calculated
    total_amount = Decimal('0.00')     # Will be calculated
    
    # Status
    status = 'pending_approval'
    
    # Approval
    approved_at = None
    approved_by = None
    
    # Dates
    first_payment_date = factory.LazyFunction(
        lambda: (timezone.now() + timedelta(days=30)).date()
    )
    final_payment_date = factory.LazyFunction(
        lambda: (timezone.now() + timedelta(days=(36 * 30))).date()  # ~36 months
    )
    
    # Credit check
    credit_score = factory.LazyFunction(lambda: random.randint(600, 850))
    credit_check_passed = True
    
    # Documents
    loan_agreement_url = factory.Faker('url')
    
    # Timestamps
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class FinancingInstallmentFactory(DjangoModelFactory):
    """
    Factory for creating FinancingInstallment instances.
    
    Creates individual installment records with principal/interest breakdown.
    """
    
    class Meta:
        model = 'deals.FinancingInstallment'
    
    financing = factory.SubFactory(FinancingOptionFactory)
    
    # Installment details
    installment_number = factory.Sequence(lambda n: n + 1)
    due_date = factory.LazyFunction(
        lambda: (timezone.now() + timedelta(days=30)).date()
    )
    
    # Amounts
    amount_due = Decimal('1206.43')  # Example monthly payment
    principal_amount = Decimal('1009.76')  # Principal portion
    interest_amount = Decimal('196.67')    # Interest portion
    late_fee = Decimal('0.00')
    
    # Payment
    amount_paid = Decimal('0.00')
    paid_at = None
    payment = None
    
    # Balance
    remaining_balance = Decimal('38990.24')  # Balance after this payment
    
    # Status
    status = 'pending'
    days_late = 0
    
    # Timestamps
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


# ============================================================================
# Financial Flow Utility Functions
# ============================================================================

def create_deal_with_financial_terms(buyer=None, dealer=None, deposit_percentage=Decimal('20.00')):
    """
    Utility function to create a deal with complete financial terms.
    
    Args:
        buyer: User instance (optional)
        dealer: User instance (optional)
        deposit_percentage: Decimal percentage for deposit (default 20%)
    
    Returns:
        tuple: (deal, financial_terms)
    """
    # Create users if not provided
    if buyer is None:
        buyer = CustomerUserFactory()
    if dealer is None:
        dealer = DealerUserFactory()
    
    # Create vehicle
    vehicle = VehicleFactory(dealer=dealer)
    
    # Create deal
    deal = DealFactory(
        vehicle=vehicle,
        buyer=buyer,
        dealer=dealer
    )
    
    # Create financial terms using the business logic method
    financial_terms = deal.create_financial_terms(deposit_percentage=deposit_percentage)
    
    return deal, financial_terms


def create_deal_with_payment_schedule(buyer=None, dealer=None):
    """
    Utility function to create a deal with financial terms AND standard payment schedule.
    
    Args:
        buyer: User instance (optional)
        dealer: User instance (optional)
    
    Returns:
        tuple: (deal, financial_terms, milestones)
    """
    deal, financial_terms = create_deal_with_financial_terms(buyer, dealer)
    
    # Create standard 5-milestone payment schedule
    milestones = deal.create_standard_payment_schedule()
    
    return deal, financial_terms, milestones


def create_financed_deal(buyer=None, dealer=None, term_months=36, interest_rate=Decimal('5.90')):
    """
    Utility function to create a financed deal with installment schedule.
    
    Args:
        buyer: User instance (optional)
        dealer: User instance (optional)
        term_months: Number of months for financing (default 36)
        interest_rate: Annual interest rate percentage (default 5.90%)
    
    Returns:
        tuple: (deal, financial_terms, financing_option, installments)
    """
    deal, financial_terms = create_deal_with_financial_terms(buyer, dealer)
    
    # Set up financing (assumes 20% down payment)
    financed_amount = financial_terms.total_price * Decimal('0.80')
    down_payment = financial_terms.deposit_amount
    
    financing_option = deal.setup_financing(
        financed_amount=financed_amount,
        down_payment=down_payment,
        interest_rate=interest_rate,
        term_months=term_months,
        lender_name='Global Auto Finance'
    )
    
    # Get generated installments
    installments = financing_option.installments.all()
    
    return deal, financial_terms, financing_option, installments


def create_deal_with_paid_deposit(buyer=None, dealer=None):
    """
    Utility function to create a deal with paid deposit.
    
    Args:
        buyer: User instance (optional)
        dealer: User instance (optional)
    
    Returns:
        tuple: (deal, financial_terms, deposit_payment)
    """
    deal, financial_terms, milestones = create_deal_with_payment_schedule(buyer, dealer)
    
    # Create payment for deposit
    deposit_payment = PaymentFactory(
        user=deal.buyer,
        deal=deal,
        amount=financial_terms.deposit_amount,
        currency=financial_terms.currency,
        payment_for='deal_deposit',
        status='succeeded'
    )
    
    # Process payment through business logic
    deal.process_payment(deposit_payment)
    
    # Refresh from DB
    financial_terms.refresh_from_db()
    
    return deal, financial_terms, deposit_payment
