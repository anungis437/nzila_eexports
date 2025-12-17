from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta


class BrokerTier(models.Model):
    """Performance tiers for broker commission rates"""
    
    TIER_CHOICES = [
        ('starter', 'Starter'),          # 0-4 deals/month
        ('bronze', 'Bronze'),            # 5-9 deals/month
        ('silver', 'Silver'),            # 10-19 deals/month
        ('gold', 'Gold'),                # 20-39 deals/month
        ('platinum', 'Platinum'),        # 40-79 deals/month
        ('diamond', 'Diamond'),          # 80+ deals/month
    ]
    
    # Geographic data for African brokers (mostly CIV-based)
    COUNTRY_CHOICES = [
        ('CI', 'Côte d\'Ivoire'),        # Primary broker hub
        ('SN', 'Senegal'),
        ('GH', 'Ghana'),
        ('NG', 'Nigeria'),
        ('BJ', 'Benin'),
        ('TG', 'Togo'),
        ('BF', 'Burkina Faso'),
        ('ML', 'Mali'),
        ('CM', 'Cameroon'),
        ('CD', 'Democratic Republic of Congo'),
        ('KE', 'Kenya'),
        ('ZA', 'South Africa'),
        ('MA', 'Morocco'),
        ('TN', 'Tunisia'),
        ('EG', 'Egypt'),
        ('OTHER', 'Other'),
    ]
    
    TIMEZONE_CHOICES = [
        ('Africa/Abidjan', 'West Africa (GMT)'),           # Côte d'Ivoire, Ghana, Senegal
        ('Africa/Lagos', 'West Africa Central (WAT)'),     # Nigeria, Benin, Cameroon
        ('Africa/Nairobi', 'East Africa (EAT)'),          # Kenya, Tanzania
        ('Africa/Cairo', 'Egypt (EET)'),                  # Egypt
        ('Africa/Johannesburg', 'South Africa (SAST)'),   # South Africa
        ('Africa/Casablanca', 'Morocco (WET)'),           # Morocco
        ('America/Toronto', 'Canada (EST/EDT)'),          # Canadian brokers (rare)
    ]
    
    broker = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='broker_tier',
        verbose_name=_('Broker')
    )
    current_tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default='starter',
        verbose_name=_('Current Tier')
    )
    
    # Location data (mostly African countries)
    country = models.CharField(
        max_length=10,
        choices=COUNTRY_CHOICES,
        default='CI',
        verbose_name=_('Country'),
        help_text=_('Most brokers are based in Côte d\'Ivoire')
    )
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default='Africa/Abidjan',
        verbose_name=_('Timezone'),
        help_text=_('Used for activity tracking and leaderboard rankings')
    )
    
    # Buyer network strength (critical for overseas qualified buyers)
    qualified_buyers_network = models.IntegerField(
        default=0,
        verbose_name=_('Qualified Buyers in Network'),
        help_text=_('Number of verified buyers this broker has connected')
    )
    buyer_conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Buyer Conversion Rate %'),
        help_text=_('% of introductions that result in deals')
    )
    
    # Current month performance
    deals_this_month = models.IntegerField(default=0, verbose_name=_('Deals This Month'))
    volume_this_month = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Volume This Month (CAD)')
    )
    
    # All-time stats
    total_deals = models.IntegerField(default=0, verbose_name=_('Total Deals'))
    total_commissions_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Total Commissions Earned (CAD)')
    )
    average_deal_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Average Deal Value')
    )
    
    # Gamification
    streak_days = models.IntegerField(default=0, help_text=_("Consecutive days with activity"))
    highest_month = models.IntegerField(default=0, help_text=_("Most deals in a single month"))
    last_deal_date = models.DateField(null=True, blank=True, verbose_name=_('Last Deal Date'))
    
    # Achievement boost (cumulative from badges)
    achievement_boost = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Permanent % boost from achievements')
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Broker Tier')
        verbose_name_plural = _('Broker Tiers')
        ordering = ['-deals_this_month']
    
    def __str__(self):
        return f"{self.broker.get_full_name()} - {self.get_current_tier_display()}"
    
    def get_commission_rate(self):
        """Return commission % based on tier + achievement boost"""
        tier_rates = {
            'starter': Decimal('3.0'),
            'bronze': Decimal('3.5'),
            'silver': Decimal('4.0'),
            'gold': Decimal('4.5'),
            'platinum': Decimal('5.0'),
            'diamond': Decimal('5.5'),
        }
        base_rate = tier_rates.get(self.current_tier, Decimal('3.0'))
        return base_rate + self.achievement_boost
    
    def calculate_tier(self):
        """Auto-calculate tier based on monthly volume"""
        if self.deals_this_month >= 80:
            return 'diamond'
        elif self.deals_this_month >= 40:
            return 'platinum'
        elif self.deals_this_month >= 20:
            return 'gold'
        elif self.deals_this_month >= 10:
            return 'silver'
        elif self.deals_this_month >= 5:
            return 'bronze'
        else:
            return 'starter'
    
    def update_tier(self):
        """Update tier based on performance"""
        new_tier = self.calculate_tier()
        if new_tier != self.current_tier:
            self.current_tier = new_tier
            self.save()
        return new_tier
    
    def deals_needed_for_next_tier(self):
        """Calculate deals needed to reach next tier"""
        tier_thresholds = {
            'starter': 5,
            'bronze': 10,
            'silver': 20,
            'gold': 40,
            'platinum': 80,
            'diamond': 0,
        }
        next_threshold = tier_thresholds.get(self.current_tier, 0)
        if next_threshold == 0:
            return 0
        return max(0, next_threshold - self.deals_this_month)
    
    def monthly_earnings_potential(self):
        """Show potential earnings at next tier"""
        current_rate = self.get_commission_rate()
        avg_deal = self.average_deal_value or Decimal('25000')
        
        tier_order = ['starter', 'bronze', 'silver', 'gold', 'platinum', 'diamond']
        current_index = tier_order.index(self.current_tier)
        
        if current_index < len(tier_order) - 1:
            next_tier = tier_order[current_index + 1]
            temp_tier = BrokerTier(current_tier=next_tier)
            next_rate = temp_tier.get_commission_rate()
        else:
            next_rate = current_rate
        
        current_monthly = self.deals_this_month * avg_deal * (current_rate / 100)
        next_monthly = self.deals_this_month * avg_deal * (next_rate / 100)
        
        return {
            'current': current_monthly,
            'next_tier': next_monthly,
            'increase': next_monthly - current_monthly,
            'deals_needed': self.deals_needed_for_next_tier()
        }
    
    def update_streak(self):
        """Update consecutive days streak"""
        today = timezone.now().date()
        if self.last_deal_date:
            days_diff = (today - self.last_deal_date).days
            if days_diff == 1:
                # Consecutive day
                self.streak_days += 1
            elif days_diff > 1:
                # Streak broken
                self.streak_days = 1
            # Same day doesn't change streak
        else:
            self.streak_days = 1
        
        self.last_deal_date = today
        self.save()


class DealerTier(models.Model):
    """Performance tiers for dealer commission rates + Canadian bonuses"""
    
    TIER_CHOICES = [
        ('standard', 'Standard'),        # 0-9 deals/quarter
        ('preferred', 'Preferred'),      # 10-24 deals/quarter
        ('elite', 'Elite'),              # 25-49 deals/quarter
        ('premier', 'Premier'),          # 50+ deals/quarter
    ]
    
    PROVINCE_CHOICES = [
        ('ON', 'Ontario'),
        ('QC', 'Quebec'),
        ('BC', 'British Columbia'),
        ('AB', 'Alberta'),
        ('SK', 'Saskatchewan'),
        ('MB', 'Manitoba'),
        ('NB', 'New Brunswick'),
        ('NS', 'Nova Scotia'),
        ('PE', 'Prince Edward Island'),
        ('NL', 'Newfoundland and Labrador'),
        ('YT', 'Yukon'),
        ('NT', 'Northwest Territories'),
        ('NU', 'Nunavut'),
    ]
    
    dealer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dealer_tier',
        verbose_name=_('Dealer')
    )
    current_tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default='standard',
        verbose_name=_('Current Tier')
    )
    
    # Location data for Canadian bonuses
    province = models.CharField(
        max_length=2,
        choices=PROVINCE_CHOICES,
        blank=True,
        verbose_name=_('Province')
    )
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    is_rural = models.BooleanField(default=False, verbose_name=_('Rural Dealer'))
    is_first_nations = models.BooleanField(default=False, verbose_name=_('First Nations Partnership'))
    
    # Certifications
    omvic_certified = models.BooleanField(
        default=False,
        help_text=_("Ontario Motor Vehicle Industry Council"),
        verbose_name=_('OMVIC Certified')
    )
    amvic_certified = models.BooleanField(
        default=False,
        help_text=_("Alberta Motor Vehicle Industry Council"),
        verbose_name=_('AMVIC Certified')
    )
    certification_bonus_paid = models.BooleanField(default=False)
    
    # Performance tracking
    deals_this_quarter = models.IntegerField(default=0, verbose_name=_('Deals This Quarter'))
    deals_last_quarter = models.IntegerField(default=0, verbose_name=_('Deals Last Quarter'))
    total_deals = models.IntegerField(default=0, verbose_name=_('Total Deals'))
    average_deal_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Average Deal Value')
    )
    total_commissions_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Total Commissions Earned')
    )
    
    # Onboarding bonuses tracking
    welcome_bonus_paid = models.BooleanField(default=False)
    first_deal_bonus_paid = models.BooleanField(default=False)
    fast_start_bonus_paid = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Dealer Tier')
        verbose_name_plural = _('Dealer Tiers')
        ordering = ['-deals_this_quarter']
    
    def __str__(self):
        return f"{self.dealer.get_full_name()} - {self.get_current_tier_display()}"
    
    def get_base_commission_rate(self):
        """Base rate by tier"""
        tier_rates = {
            'standard': Decimal('5.0'),
            'preferred': Decimal('5.5'),
            'elite': Decimal('6.0'),
            'premier': Decimal('6.5'),
        }
        return tier_rates.get(self.current_tier, Decimal('5.0'))
    
    def get_market_bonus(self):
        """Calculate total market bonus based on location"""
        bonus = Decimal('0.0')
        
        # Provincial bonuses
        if self.province in ['ON', 'QC', 'BC', 'AB', 'SK', 'MB']:
            bonus += Decimal('0.5')  # Major provinces
        elif self.province in ['NB', 'NS', 'PE', 'NL']:
            bonus += Decimal('0.75')  # Maritime provinces (smaller markets)
        
        # Special bonuses
        if self.is_rural:
            bonus += Decimal('1.0')
        if self.is_first_nations:
            bonus += Decimal('1.5')
        
        return bonus
    
    def get_total_commission_rate(self):
        """Total rate = base + market bonuses"""
        return self.get_base_commission_rate() + self.get_market_bonus()
    
    def calculate_tier(self):
        """Auto-calculate tier based on quarterly volume"""
        if self.deals_this_quarter >= 50:
            return 'premier'
        elif self.deals_this_quarter >= 25:
            return 'elite'
        elif self.deals_this_quarter >= 10:
            return 'preferred'
        else:
            return 'standard'
    
    def update_tier(self):
        """Update tier based on performance"""
        new_tier = self.calculate_tier()
        if new_tier != self.current_tier:
            self.current_tier = new_tier
            self.save()
        return new_tier


class BonusTransaction(models.Model):
    """Track one-time bonuses for dealers and brokers"""
    
    BONUS_TYPE_CHOICES = [
        # Dealer bonuses
        ('welcome', 'Welcome Bonus'),
        ('first_deal', 'First Deal Bonus'),
        ('fast_start', 'Fast Start Bonus (5 deals in 30 days)'),
        ('certification', 'Certification Bonus (OMVIC/AMVIC)'),
        ('referral', 'Dealer Referral Bonus'),
        
        # Broker bonuses (from achievements)
        ('achievement', 'Achievement Bonus'),
        ('milestone', 'Milestone Bonus'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bonuses',
        verbose_name=_('User')
    )
    bonus_type = models.CharField(
        max_length=30,
        choices=BONUS_TYPE_CHOICES,
        verbose_name=_('Bonus Type')
    )
    amount_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Amount (CAD)')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Bonus Transaction')
        verbose_name_plural = _('Bonus Transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_bonus_type_display()} - {self.user.get_full_name()} - ${self.amount_cad}"


class Commission(models.Model):
    """Commission model for tracking broker/dealer earnings"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    ]
    
    deal = models.ForeignKey(
        'deals.Deal',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Deal')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Recipient')
    )
    
    # Commission Details
    commission_type = models.CharField(
        max_length=20,
        choices=[
            ('broker', _('Broker Commission')),
            ('dealer', _('Dealer Commission')),
        ],
        verbose_name=_('Commission Type')
    )
    
    amount_cad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Amount (CAD)')
    )
    
    # Multi-currency support
    amount_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Amount (USD)')
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('1.0'),
        help_text=_('CAD to USD exchange rate at time of deal'),
        verbose_name=_('Exchange Rate')
    )
    payment_currency = models.CharField(
        max_length=3,
        default='CAD',
        choices=[('CAD', 'Canadian Dollar'), ('USD', 'US Dollar')],
        verbose_name=_('Payment Currency')
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_('Commission percentage'),
        verbose_name=_('Percentage')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Approved At')
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Paid At')
    )
    
    class Meta:
        verbose_name = _('Commission')
        verbose_name_plural = _('Commissions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_commission_type_display()} - Deal #{self.deal.id} - ${self.amount_cad}"


@receiver(post_save, sender='deals.Deal')
def create_commissions_on_deal_completion(sender, instance, created, **kwargs):
    """Auto-create commissions when deal is completed with tier-based rates"""
    
    if instance.status == 'completed' and not instance.commissions.exists():
        
        # Get or create dealer tier
        dealer_tier, _ = DealerTier.objects.get_or_create(dealer=instance.dealer)
        dealer_rate = dealer_tier.get_total_commission_rate()
        
        # Create dealer commission with tier-based rate
        dealer_commission = Commission.objects.create(
            deal=instance,
            recipient=instance.dealer,
            commission_type='dealer',
            percentage=dealer_rate,
            amount_cad=instance.agreed_price_cad * (dealer_rate / 100),
            status='pending'
        )
        
        # Update dealer stats
        dealer_tier.deals_this_quarter += 1
        dealer_tier.total_deals += 1
        dealer_tier.total_commissions_earned += dealer_commission.amount_cad
        if dealer_tier.total_deals > 0:
            dealer_tier.average_deal_value = (
                (dealer_tier.average_deal_value * (dealer_tier.total_deals - 1) + instance.agreed_price_cad)
                / dealer_tier.total_deals
            )
        dealer_tier.update_tier()
        dealer_tier.save()
        
        # Process dealer bonuses
        process_dealer_bonuses(instance.dealer, dealer_tier)
        
        # Broker commission if broker is involved
        if instance.broker:
            # Get or create broker tier
            broker_tier, _ = BrokerTier.objects.get_or_create(broker=instance.broker)
            broker_rate = broker_tier.get_commission_rate()
            
            # Create broker commission with tier-based rate
            broker_commission = Commission.objects.create(
                deal=instance,
                recipient=instance.broker,
                commission_type='broker',
                percentage=broker_rate,
                amount_cad=instance.agreed_price_cad * (broker_rate / 100),
                status='pending'
            )
            
            # Update broker stats
            broker_tier.deals_this_month += 1
            broker_tier.total_deals += 1
            broker_tier.volume_this_month += instance.agreed_price_cad
            broker_tier.total_commissions_earned += broker_commission.amount_cad
            if broker_tier.total_deals > 0:
                broker_tier.average_deal_value = (
                    (broker_tier.average_deal_value * (broker_tier.total_deals - 1) + instance.agreed_price_cad)
                    / broker_tier.total_deals
                )
            broker_tier.update_streak()
            broker_tier.update_tier()
            
            # Update highest month if current month is higher
            if broker_tier.deals_this_month > broker_tier.highest_month:
                broker_tier.highest_month = broker_tier.deals_this_month
            
            broker_tier.save()


def process_dealer_bonuses(dealer, dealer_tier):
    """Process and create dealer onboarding bonuses"""
    
    # Welcome bonus - $500 CAD on verification + certification
    if not dealer_tier.welcome_bonus_paid and (dealer_tier.omvic_certified or dealer_tier.amvic_certified):
        BonusTransaction.objects.create(
            user=dealer,
            bonus_type='welcome',
            amount_cad=Decimal('500.00'),
            status='approved',
            description='Welcome bonus for verified Canadian dealer with OMVIC/AMVIC certification'
        )
        dealer_tier.welcome_bonus_paid = True
        dealer_tier.save()
    
    # First deal bonus - $1000 CAD
    if dealer_tier.total_deals == 1 and not dealer_tier.first_deal_bonus_paid:
        BonusTransaction.objects.create(
            user=dealer,
            bonus_type='first_deal',
            amount_cad=Decimal('1000.00'),
            status='approved',
            description='First deal completion bonus'
        )
        dealer_tier.first_deal_bonus_paid = True
        dealer_tier.save()
    
    # Fast start bonus - $2500 CAD for 5 deals in first 30 days
    if dealer_tier.total_deals >= 5 and not dealer_tier.fast_start_bonus_paid:
        days_since_creation = (timezone.now() - dealer_tier.created_at).days
        if days_since_creation <= 30:
            BonusTransaction.objects.create(
                user=dealer,
                bonus_type='fast_start',
                amount_cad=Decimal('2500.00'),
                status='approved',
                description='Fast Start: 5 deals completed in first 30 days'
            )
            dealer_tier.fast_start_bonus_paid = True
            dealer_tier.save()
    
    # Certification bonus - $500 if not paid as part of welcome
    if (dealer_tier.omvic_certified or dealer_tier.amvic_certified) and not dealer_tier.certification_bonus_paid and dealer_tier.welcome_bonus_paid:
        BonusTransaction.objects.create(
            user=dealer,
            bonus_type='certification',
            amount_cad=Decimal('500.00'),
            status='approved',
            description='OMVIC/AMVIC certification verification bonus'
        )
        dealer_tier.certification_bonus_paid = True
        dealer_tier.save()

