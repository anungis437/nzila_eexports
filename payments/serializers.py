from rest_framework import serializers
from .models import Currency, PaymentMethod, Payment, Invoice, InvoiceItem, Transaction
from django.contrib.auth import get_user_model

User = get_user_model()


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol', 'exchange_rate_to_usd', 'is_active', 
                  'is_african', 'country', 'stripe_supported']
        read_only_fields = ['id']


class PaymentMethodSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    currency_display = CurrencySerializer(source='currency', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'type', 'display_name', 'card_brand', 'card_last4', 'card_exp_month', 
                  'card_exp_year', 'bank_name', 'bank_account_last4', 'mobile_provider', 
                  'mobile_number', 'is_default', 'is_verified', 'currency', 'currency_display',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'display_name']
    
    def get_display_name(self, obj):
        return str(obj)


class PaymentMethodCreateSerializer(serializers.Serializer):
    """Serializer for creating payment method via Stripe token"""
    stripe_token = serializers.CharField(required=True, help_text="Stripe payment method token")
    type = serializers.ChoiceField(choices=['card'], default='card')
    set_as_default = serializers.BooleanField(default=False)


class PaymentSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source='user.username', read_only=True)
    currency_display = CurrencySerializer(source='currency', read_only=True)
    payment_method_display = PaymentMethodSerializer(source='payment_method', read_only=True)
    deal_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_for_display = serializers.CharField(source='get_payment_for_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_display', 'deal', 'deal_display', 'shipment', 
                  'payment_method', 'payment_method_display', 'payment_for', 'payment_for_display',
                  'amount', 'currency', 'currency_display', 'amount_in_usd', 
                  'stripe_payment_intent_id', 'status', 'status_display', 'failure_reason', 
                  'refund_amount', 'refund_reason', 'description', 'receipt_url', 
                  'created_at', 'updated_at', 'succeeded_at', 'refunded_at']
        read_only_fields = ['id', 'user', 'stripe_payment_intent_id', 'amount_in_usd', 
                           'status', 'failure_reason', 'receipt_url', 'created_at', 'updated_at',
                           'succeeded_at', 'refunded_at']
    
    def get_deal_display(self, obj):
        if obj.deal:
            vehicle = obj.deal.vehicle
            return f"Deal #{obj.deal.id} - {vehicle.year} {vehicle.make} {vehicle.model}"
        return None


class PaymentIntentCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment intent"""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    currency = serializers.CharField(max_length=3)
    deal_id = serializers.IntegerField(required=False, allow_null=True)
    shipment_id = serializers.IntegerField(required=False, allow_null=True)
    payment_for = serializers.ChoiceField(
        choices=['deal_deposit', 'deal_final', 'deal_full', 'shipment', 'commission', 'other'],
        default='deal_deposit'
    )
    payment_method_id = serializers.CharField(required=False, allow_null=True, 
                                             help_text="Stripe payment method ID")
    description = serializers.CharField(required=False, allow_blank=True)
    confirm = serializers.BooleanField(default=False, help_text="Confirm payment immediately")


class PaymentConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a payment"""
    payment_intent_id = serializers.CharField(required=True)
    payment_method_id = serializers.CharField(required=False, allow_null=True)


class RefundSerializer(serializers.Serializer):
    """Serializer for creating a refund"""
    payment_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'amount', 'order']
        read_only_fields = ['id', 'amount']


class InvoiceSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source='user.username', read_only=True)
    currency_display = CurrencySerializer(source='currency', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    amount_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'user', 'user_display', 'deal', 'shipment', 
                  'status', 'status_display', 'subtotal', 'tax_rate', 'tax_amount', 
                  'discount_amount', 'total', 'amount_paid', 'amount_due', 'currency', 
                  'currency_display', 'issue_date', 'due_date', 'paid_date', 'is_overdue',
                  'notes', 'terms', 'pdf_file', 'items', 'created_at', 'updated_at', 'sent_at']
        read_only_fields = ['id', 'invoice_number', 'amount_paid', 'amount_due', 
                           'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.Serializer):
    """Serializer for creating an invoice"""
    user_id = serializers.IntegerField(required=True)
    deal_id = serializers.IntegerField(required=False, allow_null=True)
    shipment_id = serializers.IntegerField(required=False, allow_null=True)
    currency = serializers.CharField(max_length=3)
    issue_date = serializers.DateField()
    due_date = serializers.DateField()
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = serializers.CharField(required=False, allow_blank=True)
    terms = serializers.CharField(required=False, allow_blank=True)
    items = InvoiceItemSerializer(many=True, required=True)


class TransactionSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source='user.username', read_only=True)
    currency_display = CurrencySerializer(source='currency', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'user_display', 'payment', 'invoice', 'transaction_type', 
                  'transaction_type_display', 'amount', 'currency', 'currency_display', 
                  'description', 'balance_before', 'balance_after', 'reference_number', 
                  'metadata', 'created_at']
        read_only_fields = ['id', 'user', 'reference_number', 'balance_before', 'balance_after', 
                           'created_at']
