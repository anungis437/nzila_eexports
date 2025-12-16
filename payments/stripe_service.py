import stripe
from django.conf import settings
from decimal import Decimal
from .models import Payment, PaymentMethod, Currency, Transaction
from django.utils import timezone
import uuid

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Service for handling Stripe payment operations"""
    
    @staticmethod
    def get_or_create_customer(user):
        """Get or create a Stripe customer for the user"""
        from accounts.models import User
        
        # Check if user already has a Stripe customer ID
        if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                return customer
            except stripe.error.InvalidRequestError:
                pass
        
        # Create new Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name() or user.username,
            metadata={
                'user_id': user.id,
                'username': user.username,
            }
        )
        
        # Save Stripe customer ID to user
        User.objects.filter(id=user.id).update(stripe_customer_id=customer.id)
        
        return customer
    
    @staticmethod
    def create_payment_method(user, stripe_token, payment_type='card'):
        """Create a payment method from a Stripe token"""
        customer = StripePaymentService.get_or_create_customer(user)
        
        # Attach payment method to customer
        if payment_type == 'card':
            payment_method = stripe.PaymentMethod.attach(
                stripe_token,
                customer=customer.id,
            )
            
            # Get payment method details
            pm_details = stripe.PaymentMethod.retrieve(stripe_token)
            
            # Create PaymentMethod record
            payment_method_obj = PaymentMethod.objects.create(
                user=user,
                type='card',
                stripe_payment_method_id=payment_method.id,
                card_brand=pm_details.card.brand,
                card_last4=pm_details.card.last4,
                card_exp_month=pm_details.card.exp_month,
                card_exp_year=pm_details.card.exp_year,
                is_verified=True,
            )
            
            # Set as default if it's the first payment method
            if not PaymentMethod.objects.filter(user=user, is_default=True).exists():
                payment_method_obj.is_default = True
                payment_method_obj.save()
            
            return payment_method_obj
        
        return None
    
    @staticmethod
    def create_payment_intent(amount, currency_code, user, deal=None, shipment=None, 
                             payment_for='deal_deposit', payment_method_id=None, description=''):
        """Create a Stripe Payment Intent"""
        customer = StripePaymentService.get_or_create_customer(user)
        currency_obj = Currency.objects.get(code=currency_code.upper())
        
        # Calculate amount in cents (Stripe uses smallest currency unit)
        amount_cents = int(amount * 100)
        
        # Generate idempotency key to prevent duplicate charges on network retry
        # Format: payment_type_entityid_timestamp
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        entity_id = deal.id if deal else (shipment.id if shipment else user.id)
        idempotency_key = f"{payment_for}_{entity_id}_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        # Create Payment Intent
        intent_params = {
            'amount': amount_cents,
            'currency': currency_code.lower(),
            'customer': customer.id,
            'description': description or f'Payment for {payment_for}',
            'metadata': {
                'user_id': user.id,
                'payment_for': payment_for,
            }
        }
        
        if deal:
            intent_params['metadata']['deal_id'] = deal.id
        if shipment:
            intent_params['metadata']['shipment_id'] = shipment.id
        if payment_method_id:
            intent_params['payment_method'] = payment_method_id
            intent_params['confirm'] = True
        
        # Create payment intent with idempotency key (critical for financial safety)
        payment_intent = stripe.PaymentIntent.create(
            **intent_params,
            idempotency_key=idempotency_key
        )
        
        # Calculate USD amount for reporting
        amount_in_usd = amount * float(currency_obj.exchange_rate_to_usd)
        
        # Create Payment record
        payment_method_obj = None
        if payment_method_id:
            payment_method_obj = PaymentMethod.objects.filter(
                stripe_payment_method_id=payment_method_id
            ).first()
        
        payment = Payment.objects.create(
            user=user,
            deal=deal,
            shipment=shipment,
            payment_method=payment_method_obj,
            payment_for=payment_for,
            amount=amount,
            currency=currency_obj,
            amount_in_usd=Decimal(str(amount_in_usd)),
            stripe_payment_intent_id=payment_intent.id,
            stripe_customer_id=customer.id,
            status='pending',
            description=description,
        )
        
        return payment, payment_intent
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirm a payment intent"""
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            # Update Payment record
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.status = 'processing'
            payment.save()
            
            return payment, payment_intent
        except stripe.error.CardError as e:
            # Handle card errors
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.status = 'failed'
            payment.failure_reason = str(e)
            payment.save()
            raise
    
    @staticmethod
    def handle_webhook_event(payload, sig_header):
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            StripePaymentService._handle_payment_success(payment_intent)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            StripePaymentService._handle_payment_failed(payment_intent)
        
        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            StripePaymentService._handle_refund(charge)
        
        return event
    
    @staticmethod
    def _handle_payment_success(payment_intent):
        """Handle successful payment"""
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'succeeded'
            payment.succeeded_at = timezone.now()
            payment.stripe_charge_id = payment_intent.get('charges', {}).get('data', [{}])[0].get('id', '')
            payment.receipt_url = payment_intent.get('charges', {}).get('data', [{}])[0].get('receipt_url', '')
            payment.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=payment.user,
                payment=payment,
                transaction_type='payment',
                amount=payment.amount,
                currency=payment.currency,
                description=f"Payment received for {payment.get_payment_for_display()}",
                reference_number=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            )
            
            # Update invoice if linked
            if payment.invoice:
                payment.invoice.amount_paid += payment.amount
                payment.invoice.update_status()
            
            # Update deal payment status if applicable
            if payment.deal:
                from deals.models import Deal
                deal = payment.deal
                if payment.payment_for == 'deal_deposit':
                    deal.deposit_paid = True
                elif payment.payment_for in ['deal_final', 'deal_full']:
                    deal.final_payment_paid = True
                deal.save()
            
        except Payment.DoesNotExist:
            pass
    
    @staticmethod
    def _handle_payment_failed(payment_intent):
        """Handle failed payment"""
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'failed'
            payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    @staticmethod
    def _handle_refund(charge):
        """Handle refund"""
        try:
            payment = Payment.objects.get(stripe_charge_id=charge['id'])
            refund_amount = Decimal(charge['amount_refunded']) / 100
            
            payment.refund_amount = refund_amount
            if refund_amount >= payment.amount:
                payment.status = 'refunded'
            else:
                payment.status = 'partially_refunded'
            payment.refunded_at = timezone.now()
            payment.save()
            
            # Create transaction record for refund
            Transaction.objects.create(
                user=payment.user,
                payment=payment,
                transaction_type='refund',
                amount=refund_amount,
                currency=payment.currency,
                description=f"Refund for payment {payment.id}",
                reference_number=f"REF-{uuid.uuid4().hex[:12].upper()}",
            )
            
        except Payment.DoesNotExist:
            pass
    
    @staticmethod
    def create_refund(payment, amount=None, reason=''):
        """Create a refund for a payment"""
        if not payment.is_refundable:
            raise ValueError("Payment is not refundable")
        
        refund_amount = amount or payment.refundable_amount
        refund_amount_cents = int(refund_amount * 100)
        
        refund = stripe.Refund.create(
            charge=payment.stripe_charge_id,
            amount=refund_amount_cents,
            reason='requested_by_customer',
            metadata={
                'payment_id': payment.id,
                'reason': reason,
            }
        )
        
        # Update payment
        payment.refund_amount += refund_amount
        payment.refund_reason = reason
        payment.refunded_at = timezone.now()
        
        if payment.refund_amount >= payment.amount:
            payment.status = 'refunded'
        else:
            payment.status = 'partially_refunded'
        
        payment.save()
        
        # Create transaction
        Transaction.objects.create(
            user=payment.user,
            payment=payment,
            transaction_type='refund',
            amount=refund_amount,
            currency=payment.currency,
            description=f"Refund: {reason}",
            reference_number=f"REF-{uuid.uuid4().hex[:12].upper()}",
        )
        
        return refund
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """Retrieve a payment intent from Stripe"""
        return stripe.PaymentIntent.retrieve(payment_intent_id)
    
    @staticmethod
    def list_payment_methods(user):
        """List all payment methods for a user"""
        customer = StripePaymentService.get_or_create_customer(user)
        return stripe.PaymentMethod.list(
            customer=customer.id,
            type='card',
        )
    
    @staticmethod
    def delete_payment_method(payment_method_id):
        """Detach a payment method"""
        payment_method = stripe.PaymentMethod.detach(payment_method_id)
        
        # Delete from our database
        PaymentMethod.objects.filter(stripe_payment_method_id=payment_method_id).delete()
        
        return payment_method


class CurrencyService:
    """Service for handling currency operations"""
    
    @staticmethod
    def get_supported_currencies():
        """Get all active supported currencies"""
        return Currency.objects.filter(is_active=True)
    
    @staticmethod
    def get_african_currencies():
        """Get all African currencies"""
        return Currency.objects.filter(is_active=True, is_african=True)
    
    @staticmethod
    def convert_amount(amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        if from_currency.code == to_currency.code:
            return amount
        
        # Convert to USD first, then to target currency
        amount_in_usd = amount * float(from_currency.exchange_rate_to_usd)
        converted_amount = amount_in_usd / float(to_currency.exchange_rate_to_usd)
        
        return Decimal(str(converted_amount))
    
    @staticmethod
    def update_exchange_rates():
        """
        Update exchange rates from an external API
        This should be called periodically (e.g., daily via Celery task)
        Uses exchangerate-api.com free tier API
        """
        import requests
        from decimal import Decimal
        from .models import ExchangeRateLog
        from django.conf import settings
        
        # Use free exchangerate-api.com or fallback to manual rates
        # To use: Set EXCHANGE_RATE_API_KEY in environment or .env file
        # Free key available at: https://www.exchangerate-api.com/
        api_key = getattr(settings, 'EXCHANGE_RATE_API_KEY', None)
        
        if api_key:
            # Use real API
            try:
                url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get('result') == 'success':
                    rates = data.get('conversion_rates', {})
                    currencies = Currency.objects.filter(is_active=True)
                    
                    for currency in currencies:
                        if currency.code in rates:
                            # Store as rate TO USD (inverse of rate FROM USD)
                            rate_from_usd = Decimal(str(rates[currency.code]))
                            currency.exchange_rate_to_usd = Decimal('1.0') / rate_from_usd
                            currency.save()
                            
                            # Log the update
                            ExchangeRateLog.objects.create(
                                currency=currency,
                                rate_to_usd=currency.exchange_rate_to_usd,
                                source='exchangerate-api.com',
                            )
                    
                    return True
            except Exception as e:
                print(f"Failed to update exchange rates from API: {e}")
                # Fall through to manual logging
        
        # Fallback: Just log current rates without updating
        currencies = Currency.objects.filter(is_active=True)
        for currency in currencies:
            ExchangeRateLog.objects.create(
                currency=currency,
                rate_to_usd=currency.exchange_rate_to_usd,
                source='manual',
            )
        
        return True
