"""
Financial models for Deal management.
Handles deposits, payment schedules, financing, and installments.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal


class DealFinancialTerms(models.Model):
    """
    Complete financial terms for a deal.
    Tracks deposits, balance, payment terms, and overall financial status.
    """
    
    deal = models.OneToOneField(
        'deals.Deal',  # Use string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='financial_terms',
        verbose_name=_('Deal')
    )
    
    # Total pricing
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Total Price')
    )
    currency = models.ForeignKey(
        'payments.Currency',
        on_delete=models.PROTECT,
        verbose_name=_('Currency')
    )
    total_price_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Total Price (USD)'),
        help_text=_('For reporting and analytics')
    )
    
    # Deposit terms
    deposit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        verbose_name=_('Deposit Percentage'),
        help_text=_('Percentage of total price required as deposit')
    )
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Deposit Amount')
    )
    deposit_due_date = models.DateTimeField(
        verbose_name=_('Deposit Due Date')
    )
    deposit_paid = models.BooleanField(
        default=False,
        verbose_name=_('Deposit Paid')
    )
    deposit_paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deposit Paid At')
    )
    
    # Balance tracking
    balance_remaining = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Balance Remaining')
    )
    balance_due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Balance Due Date')
    )
    
    # Total paid tracking
    total_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Total Paid')
    )
    
    # Exchange rate lock (for multi-currency deals)
    locked_exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_('Locked Exchange Rate'),
        help_text=_('Exchange rate locked at deal confirmation')
    )
    exchange_rate_locked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Exchange Rate Locked At')
    )
    
    # Payment terms
    payment_term_days = models.IntegerField(
        default=30,
        verbose_name=_('Payment Term Days'),
        help_text=_('Days to pay full balance after deposit')
    )
    grace_period_days = models.IntegerField(
        default=3,
        verbose_name=_('Grace Period Days'),
        help_text=_('Grace period after due date before marked overdue')
    )
    
    # Financing flag
    is_financed = models.BooleanField(
        default=False,
        verbose_name=_('Is Financed'),
        help_text=_('Whether this deal involves financing')
    )
    
    # Refund policy
    deposit_refundable = models.BooleanField(
        default=False,
        verbose_name=_('Deposit Refundable'),
        help_text=_('Whether deposit can be refunded if deal cancelled')
    )
    refund_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Refund Percentage'),
        help_text=_('Percentage of deposit refundable')
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name=_('Financial Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Deal Financial Terms')
        verbose_name_plural = _('Deal Financial Terms')
        ordering = ['-created_at']
    
    def calculate_deposit(self):
        """Calculate deposit amount from percentage"""
        return (self.total_price * self.deposit_percentage / 100).quantize(Decimal('0.01'))
    
    def calculate_balance(self):
        """Calculate remaining balance"""
        return (self.total_price - self.total_paid).quantize(Decimal('0.01'))
    
    def is_deposit_overdue(self):
        """Check if deposit is overdue"""
        if self.deposit_paid:
            return False
        grace_end = self.deposit_due_date + timedelta(days=self.grace_period_days)
        return timezone.now() > grace_end
    
    def is_balance_overdue(self):
        """Check if balance is overdue"""
        if not self.balance_due_date or self.balance_remaining <= 0:
            return False
        grace_end = self.balance_due_date + timedelta(days=self.grace_period_days)
        return timezone.now() > grace_end
    
    def record_payment(self, amount):
        """
        Record a payment and update balances.
        
        Args:
            amount (Decimal): Payment amount to record
        """
        self.total_paid = (self.total_paid + Decimal(str(amount))).quantize(Decimal('0.01'))
        self.balance_remaining = self.calculate_balance()
        
        # Check if deposit is now paid
        if not self.deposit_paid and self.total_paid >= self.deposit_amount:
            self.deposit_paid = True
            self.deposit_paid_at = timezone.now()
            
            # Set balance due date based on payment terms
            if not self.balance_due_date:
                self.balance_due_date = timezone.now() + timedelta(days=self.payment_term_days)
        
        self.save()
    
    def get_payment_progress_percentage(self):
        """Calculate payment progress as percentage"""
        if self.total_price == 0:
            return Decimal('0.00')
        return ((self.total_paid / self.total_price) * 100).quantize(Decimal('0.01'))
    
    def is_fully_paid(self):
        """Check if deal is fully paid"""
        return self.balance_remaining <= 0
    
    def __str__(self):
        return f"Financial Terms for Deal #{self.deal.id} - {self.currency.code} {self.total_price}"


class PaymentMilestone(models.Model):
    """
    Payment milestones for a deal.
    Tracks scheduled payments at different stages of the deal.
    """
    
    MILESTONE_TYPE_CHOICES = [
        ('deposit', _('Initial Deposit')),
        ('inspection', _('Post-Inspection Payment')),
        ('documentation', _('Documentation Payment')),
        ('pre_shipment', _('Pre-Shipment Payment')),
        ('delivery', _('Final Delivery Payment')),
        ('custom', _('Custom Milestone')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('partial', _('Partially Paid')),
        ('paid', _('Fully Paid')),
        ('overdue', _('Overdue')),
        ('waived', _('Waived')),
    ]
    
    deal_financial_terms = models.ForeignKey(
        DealFinancialTerms,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name=_('Deal Financial Terms')
    )
    
    # Milestone details
    milestone_type = models.CharField(
        max_length=20,
        choices=MILESTONE_TYPE_CHOICES,
        verbose_name=_('Milestone Type')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Milestone Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    sequence = models.IntegerField(
        default=1,
        verbose_name=_('Sequence'),
        help_text=_('Order in payment schedule')
    )
    
    # Amount
    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Amount Due')
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Amount Paid')
    )
    currency = models.ForeignKey(
        'payments.Currency',
        on_delete=models.PROTECT,
        verbose_name=_('Currency')
    )
    
    # Timing
    due_date = models.DateTimeField(
        verbose_name=_('Due Date')
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Paid At')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Linked payments
    payments = models.ManyToManyField(
        'payments.Payment',
        blank=True,
        related_name='milestones',
        verbose_name=_('Payments')
    )
    
    # Reminders
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name=_('Reminder Sent')
    )
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reminder Sent At')
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sequence', 'due_date']
        verbose_name = _('Payment Milestone')
        verbose_name_plural = _('Payment Milestones')
        indexes = [
            models.Index(fields=['deal_financial_terms', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
    
    def is_overdue(self):
        """Check if milestone payment is overdue"""
        if self.status == 'paid':
            return False
        return timezone.now() > self.due_date
    
    def record_payment(self, payment_obj):
        """
        Record a payment against this milestone.
        
        Args:
            payment_obj: Payment model instance
        """
        self.amount_paid = (self.amount_paid + payment_obj.amount).quantize(Decimal('0.01'))
        self.payments.add(payment_obj)
        
        # Update status
        if self.amount_paid >= self.amount_due:
            self.status = 'paid'
            self.paid_at = timezone.now()
        elif self.amount_paid > 0:
            self.status = 'partial'
        
        # Check if overdue
        if self.is_overdue() and self.status not in ['paid', 'waived']:
            self.status = 'overdue'
        
        self.save()
    
    def get_amount_remaining(self):
        """Calculate amount still due for this milestone"""
        return (self.amount_due - self.amount_paid).quantize(Decimal('0.01'))
    
    def get_payment_percentage(self):
        """Calculate payment progress percentage"""
        if self.amount_due == 0:
            return Decimal('0.00')
        return ((self.amount_paid / self.amount_due) * 100).quantize(Decimal('0.01'))
    
    def __str__(self):
        return f"{self.get_milestone_type_display()} - {self.name} ({self.status})"


class FinancingOption(models.Model):
    """
    Financing options for deals.
    Handles loan terms, installments, and financing calculations.
    """
    
    FINANCING_TYPE_CHOICES = [
        ('in_house', _('In-House Financing')),
        ('partner_lender', _('Partner Lender')),
        ('bank_loan', _('Bank Loan')),
        ('lease', _('Lease-to-Own')),
    ]
    
    STATUS_CHOICES = [
        ('pending_approval', _('Pending Approval')),
        ('approved', _('Approved')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('defaulted', _('Defaulted')),
        ('cancelled', _('Cancelled')),
    ]
    
    deal = models.OneToOneField(
        'deals.Deal',  # Use string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='financing',
        verbose_name=_('Deal')
    )
    
    # Financing details
    financing_type = models.CharField(
        max_length=20,
        choices=FINANCING_TYPE_CHOICES,
        verbose_name=_('Financing Type')
    )
    lender_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Lender Name')
    )
    lender_contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Lender Contact')
    )
    
    # Loan terms
    financed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Financed Amount'),
        help_text=_('Amount being financed (balance after down payment)')
    )
    down_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Down Payment')
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_('Interest Rate'),
        help_text=_('Annual interest rate as percentage')
    )
    term_months = models.IntegerField(
        verbose_name=_('Term (Months)'),
        help_text=_('Loan term in months (e.g., 12, 24, 36, 48, 60)')
    )
    
    # Calculated amounts
    monthly_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Monthly Payment')
    )
    total_interest = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Total Interest')
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Total Amount'),
        help_text=_('Financed amount + total interest')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_approval',
        verbose_name=_('Status')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approved At')
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_financing',
        verbose_name=_('Approved By')
    )
    
    # Dates
    first_payment_date = models.DateField(
        verbose_name=_('First Payment Date')
    )
    final_payment_date = models.DateField(
        verbose_name=_('Final Payment Date')
    )
    
    # Credit check
    credit_score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Credit Score')
    )
    credit_check_passed = models.BooleanField(
        default=False,
        verbose_name=_('Credit Check Passed')
    )
    
    # Documents
    loan_agreement_url = models.URLField(
        blank=True,
        verbose_name=_('Loan Agreement URL')
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Financing Option')
        verbose_name_plural = _('Financing Options')
        ordering = ['-created_at']
    
    def calculate_monthly_payment(self):
        """
        Calculate monthly payment using amortization formula.
        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
            M = Monthly payment
            P = Principal (financed amount)
            r = Monthly interest rate (annual rate / 12 / 100)
            n = Number of payments (term in months)
        """
        if self.interest_rate == 0:
            # No interest - simple division
            return (self.financed_amount / self.term_months).quantize(Decimal('0.01'))
        
        # Convert annual rate to monthly decimal
        monthly_rate = self.interest_rate / 100 / 12
        
        # Calculate using amortization formula
        numerator = Decimal(str(monthly_rate)) * ((1 + Decimal(str(monthly_rate))) ** self.term_months)
        denominator = ((1 + Decimal(str(monthly_rate))) ** self.term_months) - 1
        
        monthly = self.financed_amount * (numerator / denominator)
        return monthly.quantize(Decimal('0.01'))
    
    def calculate_total_interest(self):
        """Calculate total interest paid over loan term"""
        total = self.monthly_payment * self.term_months
        return (total - self.financed_amount).quantize(Decimal('0.01'))
    
    def generate_installment_schedule(self):
        """
        Generate installment records for each month.
        
        Returns:
            list: List of created FinancingInstallment instances
        """
        installments = []
        current_date = self.first_payment_date
        remaining_balance = self.financed_amount
        
        for month in range(1, self.term_months + 1):
            # Calculate interest and principal for this month
            monthly_rate = self.interest_rate / 100 / 12
            interest_payment = (remaining_balance * Decimal(str(monthly_rate))).quantize(Decimal('0.01'))
            principal_payment = (self.monthly_payment - interest_payment).quantize(Decimal('0.01'))
            
            # Adjust last payment to account for rounding
            if month == self.term_months:
                principal_payment = remaining_balance
                interest_payment = (self.monthly_payment - principal_payment).quantize(Decimal('0.01'))
            
            remaining_balance = (remaining_balance - principal_payment).quantize(Decimal('0.01'))
            
            installment = FinancingInstallment(
                financing=self,
                installment_number=month,
                due_date=current_date,
                amount_due=self.monthly_payment,
                principal_amount=principal_payment,
                interest_amount=interest_payment,
                remaining_balance=remaining_balance if remaining_balance > 0 else Decimal('0.00')
            )
            installments.append(installment)
            
            # Move to next month (approximately 30 days)
            current_date = current_date + timedelta(days=30)
        
        # Bulk create installments
        created = FinancingInstallment.objects.bulk_create(installments)
        return created
    
    def save(self, *args, **kwargs):
        """Auto-calculate financial values before saving"""
        if not self.monthly_payment or self.monthly_payment == 0:
            self.monthly_payment = self.calculate_monthly_payment()
        
        if not self.total_interest or self.total_interest == 0:
            self.total_interest = self.calculate_total_interest()
        
        if not self.total_amount or self.total_amount == 0:
            self.total_amount = self.financed_amount + self.total_interest
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Financing for Deal #{self.deal.id} - {self.term_months} months @ {self.interest_rate}%"


class FinancingInstallment(models.Model):
    """
    Individual installment for financed deals.
    Tracks each monthly payment with principal, interest, and late fees.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('late', _('Late')),
        ('defaulted', _('Defaulted')),
    ]
    
    financing = models.ForeignKey(
        FinancingOption,
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name=_('Financing Option')
    )
    
    # Installment details
    installment_number = models.IntegerField(
        verbose_name=_('Installment Number')
    )
    due_date = models.DateField(
        verbose_name=_('Due Date')
    )
    
    # Amounts
    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Amount Due')
    )
    principal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Principal Amount')
    )
    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Interest Amount')
    )
    late_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Late Fee')
    )
    
    # Payment tracking
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Amount Paid')
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Paid At')
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='installments',
        verbose_name=_('Payment')
    )
    
    # Balance
    remaining_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Remaining Balance'),
        help_text=_('Remaining principal balance after this payment')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Late tracking
    days_late = models.IntegerField(
        default=0,
        verbose_name=_('Days Late')
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['installment_number']
        verbose_name = _('Financing Installment')
        verbose_name_plural = _('Financing Installments')
        indexes = [
            models.Index(fields=['financing', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
        unique_together = ['financing', 'installment_number']
    
    def is_late(self):
        """Check if installment is late"""
        if self.status == 'paid':
            return False
        return date.today() > self.due_date
    
    def calculate_days_late(self):
        """Calculate number of days late"""
        if not self.is_late():
            return 0
        return (date.today() - self.due_date).days
    
    def calculate_late_fee(self, percentage=Decimal('5.00')):
        """
        Calculate late fee based on percentage of installment amount.
        
        Args:
            percentage (Decimal): Late fee as percentage (default 5%)
        
        Returns:
            Decimal: Calculated late fee amount
        """
        if not self.is_late():
            return Decimal('0.00')
        
        return (self.amount_due * percentage / 100).quantize(Decimal('0.01'))
    
    def record_payment(self, payment_obj):
        """
        Record payment for this installment.
        
        Args:
            payment_obj: Payment model instance
        """
        self.amount_paid = (self.amount_paid + payment_obj.amount).quantize(Decimal('0.01'))
        self.payment = payment_obj
        
        # Update status
        total_due = self.amount_due + self.late_fee
        if self.amount_paid >= total_due:
            self.status = 'paid'
            self.paid_at = timezone.now()
        elif self.is_late():
            self.status = 'late'
            self.days_late = self.calculate_days_late()
        
        self.save()
    
    def __str__(self):
        return f"Installment #{self.installment_number} - {self.financing.deal.id} ({self.status})"
