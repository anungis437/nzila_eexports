"""
Financing Calculator Models

Provides comprehensive financing calculations for Canadian vehicle purchases including:
- Interest rate management by credit tier
- Monthly payment calculations with taxes and fees
- Trade-in value estimation
- Loan scenario comparisons
- Down payment analysis
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from decimal import Decimal
import datetime


class InterestRate(models.Model):
    """
    Canadian market interest rates by credit tier
    
    Credit Tiers (Canadian):
    - EXCELLENT: 750+ (Prime Rate + 0-2%)
    - GOOD: 650-749 (Prime Rate + 2-4%)
    - FAIR: 600-649 (Prime Rate + 4-7%)
    - POOR: 550-599 (Prime Rate + 7-10%)
    - BAD: <550 (Sub-prime, 12-18%)
    """
    
    CREDIT_TIER_CHOICES = [
        ('excellent', 'Excellent (750+)'),
        ('good', 'Good (650-749)'),
        ('fair', 'Fair (600-649)'),
        ('poor', 'Poor (550-599)'),
        ('bad', 'Bad (<550)'),
    ]
    
    LOAN_TERM_CHOICES = [
        (12, '12 months'),
        (24, '24 months'),
        (36, '36 months'),
        (48, '48 months'),
        (60, '60 months'),
        (72, '72 months'),
        (84, '84 months'),
    ]
    
    credit_tier = models.CharField(max_length=20, choices=CREDIT_TIER_CHOICES)
    loan_term_months = models.IntegerField(choices=LOAN_TERM_CHOICES)
    annual_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('25.00'))],
        help_text="Annual interest rate percentage (e.g., 5.99 for 5.99%)"
    )
    effective_date = models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financing_interest_rates'
        unique_together = ['credit_tier', 'loan_term_months', 'effective_date']
        indexes = [
            models.Index(fields=['credit_tier', 'loan_term_months']),
            models.Index(fields=['is_active', 'effective_date']),
        ]
        ordering = ['credit_tier', 'loan_term_months']
    
    def __str__(self):
        return f"{self.get_credit_tier_display()} - {self.loan_term_months}mo @ {self.annual_interest_rate}%"
    
    @property
    def monthly_interest_rate(self):
        """Convert annual rate to monthly rate"""
        return self.annual_interest_rate / Decimal('1200')  # Divide by 12 and convert to decimal


class LoanScenario(models.Model):
    """
    Saved loan calculation scenarios for comparison
    
    Allows buyers to compare different financing options:
    - Different down payments
    - Different loan terms
    - Different vehicles
    - Trade-in vs. no trade-in
    """
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_scenarios'
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='loan_scenarios',
        null=True,
        blank=True
    )
    
    # Loan parameters
    vehicle_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    trade_in_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    loan_term_months = models.IntegerField(
        choices=InterestRate.LOAN_TERM_CHOICES,
        default=48
    )
    credit_tier = models.CharField(
        max_length=20,
        choices=InterestRate.CREDIT_TIER_CHOICES,
        default='good'
    )
    
    # Provincial details
    province = models.CharField(max_length=2, default='ON')
    
    # Calculated fields (stored for comparison)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Taxes and fees
    pst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst_hst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    documentation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('500.00'))
    license_registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('120.00'))
    
    # Metadata
    scenario_name = models.CharField(max_length=100, blank=True, help_text="Optional name for this scenario")
    is_favorite = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financing_loan_scenarios'
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['is_favorite']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.scenario_name:
            return f"{self.buyer.email} - {self.scenario_name}"
        return f"{self.buyer.email} - ${self.vehicle_price} @ {self.loan_term_months}mo"
    
    def calculate(self):
        """
        Calculate loan payments and costs
        
        Formula: Monthly Payment = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
        - P = Principal (loan amount)
        - r = Monthly interest rate (annual rate / 12)
        - n = Number of payments (loan term in months)
        """
        
        # Get provincial tax rates
        tax_rates = self.get_provincial_tax_rates()
        
        # Calculate taxes
        taxable_amount = self.vehicle_price
        self.pst_amount = (taxable_amount * tax_rates['pst'] / Decimal('100')).quantize(Decimal('0.01'))
        self.gst_hst_amount = (taxable_amount * tax_rates['gst_hst'] / Decimal('100')).quantize(Decimal('0.01'))
        
        # Calculate total amount needed
        total_price = self.vehicle_price + self.pst_amount + self.gst_hst_amount + self.documentation_fee + self.license_registration_fee
        
        # Calculate loan amount after down payment and trade-in
        self.loan_amount = total_price - self.down_payment - self.trade_in_value
        
        # Get interest rate for credit tier and loan term
        try:
            rate_obj = InterestRate.objects.filter(
                credit_tier=self.credit_tier,
                loan_term_months=self.loan_term_months,
                is_active=True
            ).order_by('-effective_date').first()
            
            if rate_obj:
                self.annual_interest_rate = rate_obj.annual_interest_rate
            else:
                # Default rates if not found
                default_rates = {
                    'excellent': Decimal('4.99'),
                    'good': Decimal('6.99'),
                    'fair': Decimal('8.99'),
                    'poor': Decimal('10.99'),
                    'bad': Decimal('14.99'),
                }
                self.annual_interest_rate = default_rates.get(self.credit_tier, Decimal('8.99'))
        except Exception:
            self.annual_interest_rate = Decimal('8.99')
        
        # Calculate monthly payment
        if self.loan_amount > 0:
            monthly_rate = self.annual_interest_rate / Decimal('1200')
            
            if monthly_rate > 0:
                # Standard loan formula
                numerator = monthly_rate * (1 + monthly_rate) ** self.loan_term_months
                denominator = (1 + monthly_rate) ** self.loan_term_months - 1
                self.monthly_payment = (self.loan_amount * numerator / denominator).quantize(Decimal('0.01'))
            else:
                # 0% financing
                self.monthly_payment = (self.loan_amount / self.loan_term_months).quantize(Decimal('0.01'))
            
            # Calculate total costs
            self.total_cost = self.monthly_payment * self.loan_term_months
            self.total_interest = self.total_cost - self.loan_amount
        else:
            # No loan needed (paid in full)
            self.monthly_payment = Decimal('0.00')
            self.total_cost = Decimal('0.00')
            self.total_interest = Decimal('0.00')
        
        self.save()
        return self
    
    def get_provincial_tax_rates(self):
        """
        Get PST and GST/HST rates by province
        
        Canadian Provincial Tax Rates (2025):
        - HST Provinces: ON (13%), NB (15%), NS (15%), NL (15%), PE (15%)
        - GST+PST Provinces: BC (5%+7%), SK (5%+6%), MB (5%+7%), QC (5%+9.975%)
        - GST Only: AB (5%), NT (5%), NU (5%), YT (5%)
        """
        
        tax_rates = {
            # HST provinces
            'ON': {'pst': Decimal('0'), 'gst_hst': Decimal('13.00')},
            'NB': {'pst': Decimal('0'), 'gst_hst': Decimal('15.00')},
            'NS': {'pst': Decimal('0'), 'gst_hst': Decimal('15.00')},
            'NL': {'pst': Decimal('0'), 'gst_hst': Decimal('15.00')},
            'PE': {'pst': Decimal('0'), 'gst_hst': Decimal('15.00')},
            
            # GST + PST provinces
            'BC': {'pst': Decimal('7.00'), 'gst_hst': Decimal('5.00')},
            'SK': {'pst': Decimal('6.00'), 'gst_hst': Decimal('5.00')},
            'MB': {'pst': Decimal('7.00'), 'gst_hst': Decimal('5.00')},
            'QC': {'pst': Decimal('9.975'), 'gst_hst': Decimal('5.00')},
            
            # GST only (no PST)
            'AB': {'pst': Decimal('0'), 'gst_hst': Decimal('5.00')},
            'NT': {'pst': Decimal('0'), 'gst_hst': Decimal('5.00')},
            'NU': {'pst': Decimal('0'), 'gst_hst': Decimal('5.00')},
            'YT': {'pst': Decimal('0'), 'gst_hst': Decimal('5.00')},
        }
        
        return tax_rates.get(self.province, {'pst': Decimal('0'), 'gst_hst': Decimal('5.00')})
    
    @property
    def down_payment_percentage(self):
        """Calculate down payment as percentage of vehicle price"""
        if self.vehicle_price > 0:
            return ((self.down_payment / self.vehicle_price) * 100).quantize(Decimal('0.01'))
        return Decimal('0.00')
    
    @property
    def loan_to_value_ratio(self):
        """Calculate LTV ratio (lower is better for lender)"""
        if self.vehicle_price > 0:
            return ((self.loan_amount / self.vehicle_price) * 100).quantize(Decimal('0.01'))
        return Decimal('0.00')


class TradeInEstimate(models.Model):
    """
    Trade-in value estimates for vehicles
    
    Mock integration with Kelley Blue Book (KBB) Canada for MVP
    Production: Use actual KBB Canada API
    """
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent - Like new, no visible wear'),
        ('good', 'Good - Minor cosmetic issues'),
        ('fair', 'Fair - Noticeable wear and tear'),
        ('poor', 'Poor - Significant damage or mechanical issues'),
    ]
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trade_in_estimates'
    )
    
    # Vehicle details
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2030)])
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    trim = models.CharField(max_length=50, blank=True)
    mileage = models.IntegerField(validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    province = models.CharField(max_length=2, default='ON')
    
    # Estimate values (in CAD)
    trade_in_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Dealer trade-in value"
    )
    private_party_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Private sale value (higher)"
    )
    retail_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Dealer retail value (highest)"
    )
    
    # Metadata
    estimate_date = models.DateField(auto_now_add=True)
    data_source = models.CharField(max_length=50, default='KBB Canada (Mock)')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financing_trade_in_estimates'
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['year', 'make', 'model']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} - Trade-in: ${self.trade_in_value}"
    
    @classmethod
    def generate_estimate(cls, year, make, model, mileage, condition='good', province='ON'):
        """
        Generate trade-in estimate (mock KBB integration)
        
        Mock algorithm based on:
        - Year depreciation (20% first year, 15% subsequent years)
        - Mileage adjustment ($0.10/km over average)
        - Condition adjustment (excellent: +15%, good: 0%, fair: -20%, poor: -40%)
        - Provincial market adjustment
        """
        
        # Base MSRP estimates by popular vehicles (simplified)
        base_values = {
            'toyota': {'camry': 28000, 'corolla': 22000, 'rav4': 32000, 'highlander': 42000},
            'honda': {'civic': 24000, 'accord': 30000, 'cr-v': 33000, 'pilot': 45000},
            'ford': {'f-150': 38000, 'escape': 30000, 'explorer': 45000, 'mustang': 35000},
            'chevrolet': {'silverado': 40000, 'equinox': 29000, 'tahoe': 55000, 'malibu': 26000},
            'nissan': {'sentra': 21000, 'altima': 27000, 'rogue': 30000, 'pathfinder': 40000},
        }
        
        # Get base value
        make_lower = make.lower()
        model_lower = model.lower()
        
        if make_lower in base_values and model_lower in base_values[make_lower]:
            base_value = Decimal(str(base_values[make_lower][model_lower]))
        else:
            # Default to average mid-size sedan
            base_value = Decimal('30000')
        
        # Calculate depreciation
        current_year = datetime.date.today().year
        vehicle_age = current_year - year
        
        depreciated_value = base_value
        for age in range(vehicle_age):
            if age == 0:
                depreciated_value *= Decimal('0.80')  # 20% first year
            else:
                depreciated_value *= Decimal('0.85')  # 15% subsequent years
        
        # Mileage adjustment (average: 20,000 km/year)
        average_mileage = vehicle_age * 20000
        excess_mileage = max(0, mileage - average_mileage)
        mileage_penalty = Decimal(str(excess_mileage)) * Decimal('0.10')
        depreciated_value -= mileage_penalty
        
        # Condition adjustment
        condition_multipliers = {
            'excellent': Decimal('1.15'),
            'good': Decimal('1.00'),
            'fair': Decimal('0.80'),
            'poor': Decimal('0.60'),
        }
        depreciated_value *= condition_multipliers.get(condition, Decimal('1.00'))
        
        # Provincial market adjustment (mock)
        provincial_multipliers = {
            'ON': Decimal('1.00'),  # Baseline
            'BC': Decimal('1.05'),  # Higher prices in BC
            'AB': Decimal('1.03'),  # Oil economy affects prices
            'QC': Decimal('0.98'),  # Lower prices in Quebec
        }
        depreciated_value *= provincial_multipliers.get(province, Decimal('1.00'))
        
        # Calculate different values
        trade_in_value = (depreciated_value * Decimal('0.80')).quantize(Decimal('0.01'))  # Dealer pays 80%
        private_party_value = (depreciated_value * Decimal('0.95')).quantize(Decimal('0.01'))  # Private sale 95%
        retail_value = (depreciated_value * Decimal('1.20')).quantize(Decimal('0.01'))  # Dealer sells at 120%
        
        return {
            'trade_in_value': trade_in_value,
            'private_party_value': private_party_value,
            'retail_value': retail_value,
        }
