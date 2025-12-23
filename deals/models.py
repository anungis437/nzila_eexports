from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from nzila_export.sanitizers import sanitize_html


class Lead(models.Model):
    """Lead model for tracking potential deals"""
    
    STATUS_CHOICES = [
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('qualified', _('Qualified')),
        ('negotiating', _('Negotiating')),
        ('converted', _('Converted to Deal')),
        ('lost', _('Lost')),
    ]
    
    SOURCE_CHOICES = [
        ('website', _('Website')),
        ('referral', _('Referral')),
        ('broker', _('Broker')),
        ('direct', _('Direct Contact')),
    ]
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads',
        limit_choices_to={'role': 'buyer'},
        verbose_name=_('Buyer')
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name=_('Vehicle')
    )
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brokered_leads',
        limit_choices_to={'role': 'broker'},
        verbose_name=_('Broker')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name=_('Status')
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='website',
        verbose_name=_('Source')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Contacted')
    )
    
    class Meta:
        verbose_name = _('Lead')
        verbose_name_plural = _('Leads')
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.notes:
            self.notes = sanitize_html(self.notes)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Lead #{self.id} - {self.buyer.username} - {self.vehicle}"
    
    def is_stalled(self):
        """Check if lead is stalled (no update in 7 days)"""
        if self.status in ['converted', 'lost']:
            return False
        threshold = timezone.now() - timedelta(days=7)
        return self.updated_at < threshold


class Deal(models.Model):
    """Deal model for confirmed sales"""
    
    STATUS_CHOICES = [
        ('pending_docs', _('Pending Documentation')),
        ('docs_verified', _('Documents Verified')),
        ('payment_pending', _('Payment Pending')),
        ('payment_received', _('Payment Received')),
        ('ready_to_ship', _('Ready to Ship')),
        ('shipped', _('Shipped')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('wire', _('Wire Transfer')),
        ('mobile_money', _('Mobile Money')),
        ('cash', _('Cash')),
        ('crypto', _('Cryptocurrency')),
        ('financing', _('Financing')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('partial', _('Partial Payment')),
        ('paid', _('Fully Paid')),
        ('refunded', _('Refunded')),
        ('failed', _('Failed')),
    ]
    
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name='deal',
        null=True,
        blank=True,
        verbose_name=_('Lead')
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name=_('Vehicle')
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deals_as_buyer',
        limit_choices_to={'role': 'buyer'},
        verbose_name=_('Buyer')
    )
    dealer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deals_as_dealer',
        limit_choices_to={'role': 'dealer'},
        verbose_name=_('Dealer')
    )
    broker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_as_broker',
        limit_choices_to={'role': 'broker'},
        verbose_name=_('Broker')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_docs',
        verbose_name=_('Status')
    )
    
    # Pricing
    agreed_price_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Agreed Price (CAD)')
    )
    
    # Payment Information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('Payment Method')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name=_('Payment Status')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    class Meta:
        verbose_name = _('Deal')
        verbose_name_plural = _('Deals')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Deal #{self.id} - {self.vehicle}"
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content and auto-complete deal"""
        # Sanitize notes
        if self.notes:
            self.notes = sanitize_html(self.notes)
        # Auto-complete deal when status is completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    def is_stalled(self):
        """Check if deal is stalled (no update in 14 days)"""
        if self.status in ['completed', 'cancelled']:
            return False
        threshold = timezone.now() - timedelta(days=14)
        return self.updated_at < threshold
    
    # ==================== FINANCIAL MANAGEMENT METHODS ====================
    
    def create_financial_terms(self, deposit_percentage=Decimal('20.00'), payment_term_days=30):
        """
        Initialize financial terms for this deal.
        
        Args:
            deposit_percentage (Decimal): Deposit percentage (default 20%)
            payment_term_days (int): Days to pay balance after deposit (default 30)
        
        Returns:
            DealFinancialTerms: Created financial terms instance
        """
        from .financial_models import DealFinancialTerms
        from payments.models import Currency
        
        # Get CAD currency
        cad_currency = Currency.objects.get(code='CAD')
        
        # Convert to USD for reporting
        total_price_usd = self.agreed_price_cad * cad_currency.exchange_rate_to_usd
        
        # Calculate deposit amount
        deposit_amount = (self.agreed_price_cad * deposit_percentage / 100).quantize(Decimal('0.01'))
        
        financial_terms = DealFinancialTerms.objects.create(
            deal=self,
            total_price=self.agreed_price_cad,
            currency=cad_currency,
            total_price_usd=total_price_usd,
            deposit_percentage=deposit_percentage,
            deposit_amount=deposit_amount,
            deposit_due_date=timezone.now() + timedelta(days=3),
            balance_remaining=self.agreed_price_cad,
            balance_due_date=timezone.now() + timedelta(days=payment_term_days + 3),
            payment_term_days=payment_term_days
        )
        
        return financial_terms
    
    def create_standard_payment_schedule(self):
        """
        Create standard 5-milestone payment schedule:
        1. Initial Deposit (20%) - due in 3 days
        2. Post-Inspection (15%) - due in 10 days
        3. Documentation (25%) - due in 20 days
        4. Pre-Shipment (25%) - due in 30 days
        5. Final Delivery (15%) - due in 45 days
        
        Returns:
            list: Created PaymentMilestone instances
        """
        from .financial_models import PaymentMilestone
        
        if not hasattr(self, 'financial_terms'):
            raise ValueError("Financial terms must be created before payment schedule")
        
        terms = self.financial_terms
        
        milestones_config = [
            {
                'type': 'deposit',
                'name': 'Initial Deposit',
                'percentage': Decimal('20.00'),
                'days_offset': 3,
                'sequence': 1,
                'description': 'Initial deposit to secure the vehicle'
            },
            {
                'type': 'inspection',
                'name': 'Post-Inspection Payment',
                'percentage': Decimal('15.00'),
                'days_offset': 10,
                'sequence': 2,
                'description': 'Payment after vehicle inspection is completed'
            },
            {
                'type': 'documentation',
                'name': 'Documentation Payment',
                'percentage': Decimal('25.00'),
                'days_offset': 20,
                'sequence': 3,
                'description': 'Payment after all documents are verified'
            },
            {
                'type': 'pre_shipment',
                'name': 'Pre-Shipment Payment',
                'percentage': Decimal('25.00'),
                'days_offset': 30,
                'sequence': 4,
                'description': 'Payment before vehicle is loaded for shipment'
            },
            {
                'type': 'delivery',
                'name': 'Final Delivery Payment',
                'percentage': Decimal('15.00'),
                'days_offset': 45,
                'sequence': 5,
                'description': 'Final payment upon delivery confirmation'
            },
        ]
        
        milestones = []
        for config in milestones_config:
            amount_due = (terms.total_price * config['percentage'] / 100).quantize(Decimal('0.01'))
            
            milestone = PaymentMilestone.objects.create(
                deal_financial_terms=terms,
                milestone_type=config['type'],
                name=config['name'],
                description=config['description'],
                sequence=config['sequence'],
                amount_due=amount_due,
                currency=terms.currency,
                due_date=timezone.now() + timedelta(days=config['days_offset'])
            )
            milestones.append(milestone)
        
        return milestones
    
    def setup_financing(self, financed_amount, down_payment, interest_rate, term_months, lender_name=''):
        """
        Set up financing for this deal.
        
        Args:
            financed_amount (Decimal): Amount to be financed
            down_payment (Decimal): Down payment amount
            interest_rate (Decimal): Annual interest rate as percentage
            term_months (int): Loan term in months
            lender_name (str): Name of lending institution
        
        Returns:
            FinancingOption: Created financing option instance
        """
        from .financial_models import FinancingOption
        from datetime import date
        
        # Calculate first payment date (30 days from now)
        first_payment_date = date.today() + timedelta(days=30)
        # Calculate final payment date (term_months * 30 days from first payment)
        final_payment_date = first_payment_date + timedelta(days=term_months * 30)
        
        # Create financing option
        financing = FinancingOption.objects.create(
            deal=self,
            financing_type='partner_lender' if lender_name else 'in_house',
            lender_name=lender_name,
            financed_amount=financed_amount,
            down_payment=down_payment,
            interest_rate=interest_rate,
            term_months=term_months,
            first_payment_date=first_payment_date,
            final_payment_date=final_payment_date
        )
        
        # Calculations are done automatically in save() method
        # Generate installment schedule
        financing.generate_installment_schedule()
        
        # Update deal financial terms to reflect financing
        if hasattr(self, 'financial_terms'):
            self.financial_terms.is_financed = True
            self.financial_terms.save()
        
        return financing
    
    def get_payment_status_summary(self):
        """
        Get comprehensive payment status summary.
        
        Returns:
            dict: Payment status information including totals, milestones, financing
        """
        if not hasattr(self, 'financial_terms'):
            return {
                'status': 'not_configured',
                'message': 'Financial terms not set up for this deal'
            }
        
        terms = self.financial_terms
        milestones = terms.milestones.all()
        
        summary = {
            'total_price': terms.total_price,
            'currency': terms.currency.code,
            'total_paid': terms.total_paid,
            'balance_remaining': terms.balance_remaining,
            'payment_progress_percentage': terms.get_payment_progress_percentage(),
            'deposit': {
                'amount': terms.deposit_amount,
                'percentage': terms.deposit_percentage,
                'paid': terms.deposit_paid,
                'paid_at': terms.deposit_paid_at.isoformat() if terms.deposit_paid_at else None,
                'due_date': terms.deposit_due_date.isoformat(),
                'overdue': terms.is_deposit_overdue()
            },
            'balance': {
                'amount': terms.balance_remaining,
                'due_date': terms.balance_due_date.isoformat() if terms.balance_due_date else None,
                'overdue': terms.is_balance_overdue()
            },
            'milestones': {
                'total': milestones.count(),
                'paid': milestones.filter(status='paid').count(),
                'pending': milestones.filter(status='pending').count(),
                'overdue': milestones.filter(status='overdue').count(),
                'list': [
                    {
                        'name': m.name,
                        'type': m.milestone_type,
                        'amount_due': m.amount_due,
                        'amount_paid': m.amount_paid,
                        'due_date': m.due_date.isoformat(),
                        'status': m.status,
                        'sequence': m.sequence
                    }
                    for m in milestones
                ]
            },
            'is_financed': terms.is_financed,
            'fully_paid': terms.is_fully_paid()
        }
        
        # Add financing info if applicable
        if hasattr(self, 'financing') and terms.is_financed:
            financing = self.financing
            summary['financing'] = {
                'type': financing.financing_type,
                'lender': financing.lender_name,
                'financed_amount': financing.financed_amount,
                'down_payment': financing.down_payment,
                'interest_rate': financing.interest_rate,
                'term_months': financing.term_months,
                'monthly_payment': financing.monthly_payment,
                'total_interest': financing.total_interest,
                'total_amount': financing.total_amount,
                'status': financing.status,
                'first_payment_date': financing.first_payment_date.isoformat(),
                'installments_paid': financing.installments.filter(status='paid').count(),
                'installments_total': financing.installments.count()
            }
        
        return summary
    
    def process_payment(self, payment_obj):
        """
        Process a payment and allocate to milestones.
        
        This method:
        1. Updates financial terms with payment amount
        2. Allocates payment to pending milestones in sequence
        3. Updates deal payment status
        
        Args:
            payment_obj: Payment model instance
        """
        if not hasattr(self, 'financial_terms'):
            raise ValueError("Financial terms not set up for this deal")
        
        # Update financial terms
        self.financial_terms.record_payment(payment_obj.amount)
        
        # Allocate to pending milestones
        remaining_payment = Decimal(str(payment_obj.amount))
        pending_milestones = self.financial_terms.milestones.filter(
            status__in=['pending', 'partial', 'overdue']
        ).order_by('sequence')
        
        for milestone in pending_milestones:
            if remaining_payment <= 0:
                break
            
            milestone_balance = milestone.get_amount_remaining()
            allocation = min(remaining_payment, milestone_balance)
            
            # Create a "virtual" payment object for milestone recording
            # The actual payment record is already in DB
            milestone.record_payment(payment_obj)
            remaining_payment -= allocation
        
        # Update deal payment status
        if self.financial_terms.is_fully_paid():
            self.payment_status = 'paid'
        elif self.financial_terms.total_paid > 0:
            self.payment_status = 'partial'
        
        self.save()
    
    def get_next_payment_due(self):
        """
        Get the next payment milestone that is due.
        
        Returns:
            PaymentMilestone or None: Next pending milestone
        """
        if not hasattr(self, 'financial_terms'):
            return None
        
        return self.financial_terms.milestones.filter(
            status__in=['pending', 'partial', 'overdue']
        ).order_by('due_date').first()



class Document(models.Model):
    """Document model for deal verification"""
    
    TYPE_CHOICES = [
        ('title', _('Vehicle Title')),
        ('id', _('Buyer ID')),
        ('payment_proof', _('Payment Proof')),
        ('export_permit', _('Export Permit')),
        ('customs', _('Customs Declaration')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('verified', _('Verified')),
        ('rejected', _('Rejected')),
    ]
    
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Deal')
    )
    document_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_('Document Type')
    )
    file = models.FileField(
        upload_to='documents/',
        verbose_name=_('File')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        verbose_name=_('Uploaded By')
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents',
        verbose_name=_('Verified By')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Verified At')
    )
    
    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-uploaded_at']
    
    def save(self, *args, **kwargs):
        """Sanitize user-generated content before saving"""
        if self.notes:
            self.notes = sanitize_html(self.notes)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - Deal #{self.deal.id}"


# Import financial models to make them part of deals app
from .financial_models import (
    DealFinancialTerms,
    PaymentMilestone,
    FinancingOption,
    FinancingInstallment
)

__all__ = [
    'Lead',
    'Deal',
    'Document',
    'DealFinancialTerms',
    'PaymentMilestone',
    'FinancingOption',
    'FinancingInstallment'
]

