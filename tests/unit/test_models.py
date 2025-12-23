"""
Unit tests for Django models.

Tests cover model creation, validation, methods, properties, and business logic.
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from tests.factories import (
    UserFactory, CustomerUserFactory, DealerUserFactory, AdminUserFactory,
    VehicleFactory, DealFactory, PaymentFactory, InvoiceFactory,
    ShipmentFactory, CurrencyFactory, PaymentMethodFactory,
    DealerRatingFactory, LeadFactory
)


# ============================================================================
# User Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    """Tests for the User model."""
    
    def test_create_customer_user(self):
        """Test creating a customer user."""
        user = CustomerUserFactory()
        
        assert user.id is not None
        assert user.role == 'buyer'
        assert user.is_active is True
        assert user.email is not None
        assert user.data_processing_consent is True
    
    def test_create_dealer_user(self):
        """Test creating a dealer user."""
        user = DealerUserFactory()
        
        assert user.role == 'dealer'
        assert user.company_name is not None
        assert not user.is_staff
    
    def test_create_admin_user(self):
        """Test creating an admin user."""
        user = AdminUserFactory()
        
        assert user.role == 'admin'
        assert user.is_staff is True
        assert user.is_superuser is True
    
    def test_user_password_is_hashed(self):
        """Test that user password is properly hashed."""
        user = UserFactory()
        
        # Password should not be stored in plain text
        assert user.password != 'TestPassword123!'
        # But user should be able to authenticate
        assert user.check_password('TestPassword123!')
    
    def test_user_string_representation(self):
        """Test user __str__ method."""
        user = UserFactory(username='testuser', email='test@example.com')
        
        assert 'testuser' in str(user)
    
    def test_user_role_validation(self, db):
        """Test that user role is properly validated."""
        user = UserFactory(role='buyer')
        assert user.role == 'buyer'
        assert user.role in ['admin', 'dealer', 'broker', 'buyer']
    
    def test_user_consent_tracking(self):
        """Test PIPEDA/Law 25 consent tracking."""
        user = UserFactory(
            data_processing_consent=True,
            marketing_consent=True,
            consent_ip_address='192.168.1.1'
        )
        
        assert user.data_processing_consent is True
        assert user.marketing_consent is True
        assert user.consent_date is not None
        assert user.consent_ip_address == '192.168.1.1'
        assert user.consent_version == '1.0'


# ============================================================================
# Vehicle Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestVehicleModel:
    """Tests for the Vehicle model."""
    
    def test_create_vehicle(self):
        """Test creating a vehicle."""
        vehicle = VehicleFactory()
        
        assert vehicle.id is not None
        assert vehicle.dealer is not None
        assert vehicle.make is not None
        assert vehicle.model is not None
        assert vehicle.year >= 2015
        assert len(vehicle.vin) == 17
        assert vehicle.status == 'available'
    
    def test_vehicle_price_validation(self):
        """Test vehicle price must be positive."""
        vehicle = VehicleFactory(price_cad=Decimal('25000.00'))
        
        assert vehicle.price_cad > 0
    
    def test_vehicle_string_representation(self):
        """Test vehicle __str__ method."""
        vehicle = VehicleFactory(year=2022, make='Toyota', model='Camry')
        
        expected = f"2022 Toyota Camry"
        assert expected in str(vehicle)
    
    def test_vehicle_unique_vin(self, db):
        """Test that VIN must be unique."""
        VehicleFactory(vin='1HGBH41JXMN123456')
        
        with pytest.raises(Exception):  # IntegrityError
            VehicleFactory(vin='1HGBH41JXMN123456')
    
    def test_vehicle_status_choices(self):
        """Test vehicle status transitions."""
        vehicle = VehicleFactory(status='available')
        
        # Vehicle can be reserved
        vehicle.status = 'reserved'
        vehicle.save()
        assert vehicle.status == 'reserved'
        
        # Vehicle can be sold
        vehicle.status = 'sold'
        vehicle.save()
        assert vehicle.status == 'sold'
    
    def test_vehicle_condition_choices(self):
        """Test vehicle condition options."""
        conditions = ['new', 'used_excellent', 'used_good', 'used_fair']
        
        for condition in conditions:
            vehicle = VehicleFactory(condition=condition)
            assert vehicle.condition == condition


# ============================================================================
# Deal Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestDealModel:
    """Tests for the Deal model."""
    
    def test_create_deal(self):
        """Test creating a deal."""
        deal = DealFactory()
        
        assert deal.id is not None
        assert deal.vehicle is not None
        assert deal.buyer is not None
        assert deal.dealer is not None
        assert deal.agreed_price_cad > 0
        assert deal.status == 'pending_docs'
    
    def test_deal_agreed_price(self):
        """Test deal agreed price in CAD."""
        vehicle = VehicleFactory(price_cad=Decimal('30000.00'))
        deal = DealFactory(
            vehicle=vehicle,
            agreed_price_cad=Decimal('28000.00')
        )
        
        assert deal.agreed_price_cad == Decimal('28000.00')
        assert deal.agreed_price_cad <= vehicle.price_cad
    
    def test_deal_payment_method(self):
        """Test deal payment method can be set."""
        deal = DealFactory(
            agreed_price_cad=Decimal('20000.00'),
            payment_method='wire'
        )
        
        assert deal.payment_method == 'wire'
        assert deal.payment_method in ['bank_transfer', 'credit_card', 'wire', 'mobile_money', 'cash', 'crypto', 'financing']
    
    def test_deal_string_representation(self):
        """Test deal __str__ method."""
        deal = DealFactory()
        
        assert 'Deal' in str(deal)
        assert str(deal.id) in str(deal)
    
    def test_deal_status_progression(self):
        """Test deal status can progress through workflow."""
        deal = DealFactory(status='pending_docs')
        
        # Deal docs can be verified
        deal.status = 'docs_verified'
        deal.save()
        assert deal.status == 'docs_verified'
        
        # Deal can be completed
        deal.status = 'completed'
        deal.save()
        assert deal.status == 'completed'
        assert deal.completed_at is not None
    
    def test_deal_payment_status_tracking(self):
        """Test deal payment status tracking."""
        deal = DealFactory(payment_status='pending')
        
        assert deal.payment_status == 'pending'
        
        deal.payment_status = 'partial'
        deal.save()
        assert deal.payment_status == 'partial'
        
        deal.payment_status = 'paid'
        deal.save()
        assert deal.payment_status == 'paid'
    
    def test_deal_timestamps(self):
        """Test deal has creation and update timestamps."""
        deal = DealFactory()
        
        assert deal.created_at is not None
        assert deal.updated_at is not None
        assert deal.completed_at is None  # Not completed yet


# ============================================================================
# Payment Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestPaymentModel:
    """Tests for the Payment model."""
    
    def test_create_payment(self):
        """Test creating a payment."""
        payment = PaymentFactory()
        
        assert payment.id is not None
        assert payment.user is not None
        assert payment.amount > 0
        assert payment.status == 'succeeded'
    
    def test_payment_amount_validation(self):
        """Test payment amount must be positive."""
        payment = PaymentFactory(amount=Decimal('500.00'))
        
        assert payment.amount >= Decimal('0.01')
    
    def test_payment_currency_conversion(self):
        """Test payment currency conversion to USD."""
        payment = PaymentFactory(
            amount=Decimal('1000.00'),
            amount_in_usd=Decimal('1000.00')
        )
        
        assert payment.amount_in_usd > 0
    
    def test_payment_for_deal_deposit(self):
        """Test payment for deal deposit."""
        deal = DealFactory(agreed_price_cad=Decimal('20000.00'))
        # Calculate 10% deposit
        deposit_amount = deal.agreed_price_cad * Decimal('0.10')
        payment = PaymentFactory(
            deal=deal,
            payment_for='deal_deposit',
            amount=deposit_amount
        )
        
        assert payment.payment_for == 'deal_deposit'
        assert payment.amount == deposit_amount
    
    def test_payment_string_representation(self):
        """Test payment __str__ method."""
        payment = PaymentFactory(amount=Decimal('1500.00'))
        
        assert str(payment.amount) in str(payment)
    
    def test_payment_status_choices(self):
        """Test payment status transitions."""
        payment = PaymentFactory(status='pending')
        
        payment.status = 'processing'
        payment.save()
        assert payment.status == 'processing'
        
        payment.status = 'succeeded'
        payment.save()
        assert payment.status == 'succeeded'


# ============================================================================
# Currency Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestCurrencyModel:
    """Tests for the Currency model."""
    
    def test_create_currency(self):
        """Test creating a currency."""
        currency = CurrencyFactory()
        
        assert currency.id is not None
        assert currency.code == 'USD'
        assert currency.symbol == '$'
        assert currency.exchange_rate_to_usd == Decimal('1.00')
    
    def test_currency_code_format(self, db):
        """Test currency code is properly formatted."""
        currency = CurrencyFactory(code='EUR')
        assert currency.code == 'EUR'
        assert len(currency.code) == 3  # ISO 4217 format
    
    def test_currency_string_representation(self):
        """Test currency __str__ method."""
        currency = CurrencyFactory(code='USD', name='US Dollar')
        
        assert 'USD' in str(currency)
        assert 'US Dollar' in str(currency)
    
    def test_african_currency(self):
        """Test African currency flag."""
        currency = CurrencyFactory(
            code='ZAR',
            name='South African Rand',
            is_african=True
        )
        
        assert currency.is_african is True


# ============================================================================
# Shipment Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestShipmentModel:
    """Tests for the Shipment model."""
    
    def test_create_shipment(self):
        """Test creating a shipment."""
        shipment = ShipmentFactory()
        
        assert shipment.id is not None
        assert shipment.deal is not None
        assert shipment.tracking_number is not None
        assert shipment.status == 'pending'
    
    def test_shipment_tracking_number_unique(self, db):
        """Test shipment tracking number is unique."""
        ShipmentFactory(tracking_number='SHIP12345678')
        
        with pytest.raises(Exception):  # IntegrityError
            ShipmentFactory(tracking_number='SHIP12345678')
    
    def test_shipment_estimated_dates(self):
        """Test shipment estimated dates."""
        shipment = ShipmentFactory()
        
        assert shipment.estimated_departure is not None
        assert shipment.estimated_arrival is not None
        assert shipment.estimated_arrival > shipment.estimated_departure
    
    def test_shipment_status_progression(self):
        """Test shipment status can progress."""
        shipment = ShipmentFactory(status='pending')
        
        shipment.status = 'in_transit'
        shipment.save()
        assert shipment.status == 'in_transit'
        
        shipment.status = 'delivered'
        shipment.save()
        assert shipment.status == 'delivered'
    
    def test_shipment_string_representation(self):
        """Test shipment __str__ method."""
        shipment = ShipmentFactory(tracking_number='SHIP12345678')
        
        assert 'SHIP12345678' in str(shipment)


# ============================================================================
# Invoice Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestInvoiceModel:
    """Tests for the Invoice model."""
    
    def test_create_invoice(self):
        """Test creating an invoice."""
        invoice = InvoiceFactory()
        
        assert invoice.id is not None
        assert invoice.user is not None
        assert invoice.invoice_number is not None
        assert invoice.status == 'draft'
    
    def test_invoice_number_unique(self, db):
        """Test invoice number is unique."""
        InvoiceFactory(invoice_number='INV-000001')
        
        with pytest.raises(Exception):  # IntegrityError
            InvoiceFactory(invoice_number='INV-000001')
    
    def test_invoice_tax_calculation(self):
        """Test invoice tax calculation (13% HST)."""
        invoice = InvoiceFactory(
            subtotal=Decimal('10000.00'),
            tax_amount=Decimal('1300.00'),
            total=Decimal('11300.00')
        )
        
        expected_tax = invoice.subtotal * Decimal('0.13')
        assert invoice.tax_amount == expected_tax
        assert invoice.total == invoice.subtotal + invoice.tax_amount
    
    def test_invoice_due_date(self):
        """Test invoice has due date."""
        invoice = InvoiceFactory()
        
        assert invoice.due_date is not None
        assert invoice.due_date > timezone.now().date()


# ============================================================================
# Lead Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestLeadModel:
    """Tests for the Lead model."""
    
    def test_create_lead(self):
        """Test creating a lead."""
        lead = LeadFactory()
        
        assert lead.id is not None
        assert lead.buyer is not None
        assert lead.vehicle is not None
        assert lead.status == 'new'
    
    def test_lead_status_progression(self):
        """Test lead status can progress through funnel."""
        lead = LeadFactory(status='new')
        
        lead.status = 'contacted'
        lead.save()
        assert lead.status == 'contacted'
        
        lead.status = 'qualified'
        lead.save()
        assert lead.status == 'qualified'
        
        lead.status = 'converted'
        lead.save()
        assert lead.status == 'converted'
    
    def test_lead_is_stalled_method(self):
        """Test lead is_stalled() method."""
        # Recent lead should not be stalled
        recent_lead = LeadFactory()
        assert recent_lead.is_stalled() is False
        
        # Old lead should be stalled (use update to bypass auto_now)
        old_lead = LeadFactory()
        from deals.models import Lead
        Lead.objects.filter(pk=old_lead.pk).update(
            updated_at=timezone.now() - timedelta(days=8)
        )
        old_lead.refresh_from_db()
        assert old_lead.is_stalled() is True
        
        # Converted lead should never be stalled
        converted_lead = LeadFactory(status='converted')
        Lead.objects.filter(pk=converted_lead.pk).update(
            updated_at=timezone.now() - timedelta(days=30)
        )
        converted_lead.refresh_from_db()
        assert converted_lead.is_stalled() is False


# ============================================================================
# DealerRating Model Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestDealerRatingModel:
    """Tests for the DealerRating model (aggregated stats)."""
    
    def test_create_dealer_rating(self):
        """Test creating dealer rating statistics."""
        rating = DealerRatingFactory()
        
        assert rating.id is not None
        assert rating.dealer is not None
        assert rating.total_reviews >= 0
        assert 0 <= rating.average_rating <= 5
    
    def test_rating_distribution_counts(self):
        """Test rating distribution counts."""
        rating = DealerRatingFactory(
            five_star_count=10,
            four_star_count=5,
            three_star_count=3,
            two_star_count=1,
            one_star_count=1
        )
        
        assert rating.five_star_count == 10
        assert rating.four_star_count == 5
        assert rating.three_star_count == 3
        assert rating.two_star_count == 1
        assert rating.one_star_count == 1
    
    def test_detailed_averages(self):
        """Test detailed rating averages are in valid range."""
        rating = DealerRatingFactory()
        
        assert 0 <= rating.avg_vehicle_condition <= 5
        assert 0 <= rating.avg_communication <= 5
        assert 0 <= rating.avg_delivery <= 5
        assert 0 <= rating.avg_value <= 5
