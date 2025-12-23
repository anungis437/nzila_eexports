from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from deals.models import Deal
from shipments.models import Shipment

User = get_user_model()


class Currency(models.Model):
    """Supported currencies for multi-currency transactions"""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code (e.g., USD, ZAR, NGN)")
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    exchange_rate_to_usd = models.DecimalField(max_digits=12, decimal_places=6, default=1.0, help_text="Exchange rate to USD")
    is_active = models.BooleanField(default=True)
    is_african = models.BooleanField(default=False, help_text="African currency")
    country = models.CharField(max_length=100, blank=True)
    stripe_supported = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class PaymentMethod(models.Model):
    """Customer payment methods (cards, bank accounts, mobile money)"""
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('mobile_money', 'Mobile Money'),
        ('crypto', 'Cryptocurrency'),
        ('cash', 'Cash'),
        ('interac_etransfer', 'Interac e-Transfer'),  # PHASE 1: Canadian payment method
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Payment Method ID")
    
    # Card details (last 4 digits for display)
    card_brand = models.CharField(max_length=50, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # Bank account details
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account_last4 = models.CharField(max_length=4, blank=True)
    bank_routing_number = models.CharField(max_length=50, blank=True)
    
    # Mobile money details (common in Africa)
    mobile_provider = models.CharField(max_length=100, blank=True, help_text="e.g., M-Pesa, MTN Mobile Money")
    mobile_number = models.CharField(max_length=20, blank=True)
    
    # PHASE 1: Interac e-Transfer details (Canadian payment method)
    etransfer_email = models.EmailField(
        blank=True,
        help_text="Email address registered for Interac e-Transfer"
    )
    etransfer_security_question = models.CharField(
        max_length=255,
        blank=True,
        help_text="Security question for e-Transfer"
    )
    etransfer_security_answer = models.CharField(
        max_length=255,
        blank=True,
        help_text="Security answer (stored securely)"
    )
    etransfer_reference_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Interac reference number for completed transfer"
    )
    
    # General
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.type == 'card':
            return f"{self.card_brand} •••• {self.card_last4}"
        elif self.type == 'bank_account':
            return f"{self.bank_name} •••• {self.bank_account_last4}"
        elif self.type == 'mobile_money':
            return f"{self.mobile_provider} {self.mobile_number}"
        elif self.type == 'interac_etransfer':  # PHASE 1: Interac display
            return f"Interac e-Transfer ({self.etransfer_email})"
        return f"{self.get_type_display()}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset other defaults for this user
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment transactions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('canceled', 'Canceled'),
    ]
    
    PAYMENT_FOR_CHOICES = [
        ('deal_deposit', 'Deal Deposit'),
        ('deal_final', 'Deal Final Payment'),
        ('deal_full', 'Deal Full Payment'),
        ('shipment', 'Shipment Fee'),
        ('commission', 'Commission Payment'),
        ('other', 'Other'),
    ]
    
    # References
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment details
    payment_for = models.CharField(max_length=20, choices=PAYMENT_FOR_CHOICES, default='deal_deposit')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_in_usd = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount converted to USD for reporting")
    
    # Stripe details
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(blank=True)
    
    # Refund tracking
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    receipt_url = models.URLField(blank=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['deal', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - {self.currency.code} {self.amount} ({self.status})"
    
    @property
    def is_refundable(self):
        """Check if payment can be refunded"""
        return self.status == 'succeeded' and self.refund_amount < self.amount
    
    @property
    def refundable_amount(self):
        """Amount that can still be refunded"""
        return self.amount - self.refund_amount


class Invoice(models.Model):
    """Invoices for payments"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('canceled', 'Canceled'),
    ]
    
    # References
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices', help_text="Customer")
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Tax rate in percentage")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    
    # PDF
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['invoice_number']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.currency.code} {self.total}"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone
        return self.status not in ['paid', 'canceled'] and self.due_date < timezone.now().date()
    
    @property
    def amount_due(self):
        """Amount still due on the invoice"""
        return self.total - self.amount_paid
    
    def update_status(self):
        """Update invoice status based on payments"""
        if self.amount_paid >= self.total:
            self.status = 'paid'
            if not self.paid_date:
                from django.utils import timezone
                self.paid_date = timezone.now().date()
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        elif self.is_overdue:
            self.status = 'overdue'
        self.save()


class InvoiceItem(models.Model):
    """Line items on an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.description} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate amount
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """All financial transactions for audit trail"""
    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('commission', 'Commission'),
        ('fee', 'Fee'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
    ]
    
    # References
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    description = models.TextField()
    
    # Balance tracking
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    reference_number = models.CharField(max_length=100, unique=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.currency.code} {self.amount}"


class ExchangeRateLog(models.Model):
    """Log of exchange rate updates for compliance"""
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rate_logs')
    rate_to_usd = models.DecimalField(max_digits=12, decimal_places=6)
    source = models.CharField(max_length=100, help_text="Source of the exchange rate (e.g., ECB, OpenExchangeRates)")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.currency.code} = {self.rate_to_usd} USD at {self.timestamp}"
