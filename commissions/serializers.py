from rest_framework import serializers
from .models import Commission, BrokerTier, DealerTier, BonusTransaction, InterestRate
from accounts.serializers import UserSerializer


class CommissionSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    deal_id = serializers.IntegerField(source='deal.id', read_only=True)
    
    class Meta:
        model = Commission
        fields = ['id', 'deal', 'deal_id', 'recipient', 'commission_type',
                  'amount_cad', 'amount_usd', 'exchange_rate', 'payment_currency',
                  'percentage', 'status', 'notes',
                  'created_at', 'approved_at', 'paid_at']
        read_only_fields = ['id', 'created_at', 'approved_at', 'paid_at']


class BrokerTierSerializer(serializers.ModelSerializer):
    broker_name = serializers.CharField(source='broker.get_full_name', read_only=True)
    broker_email = serializers.EmailField(source='broker.email', read_only=True)
    commission_rate = serializers.DecimalField(
        source='get_commission_rate',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    deals_needed_next_tier = serializers.IntegerField(
        source='deals_needed_for_next_tier',
        read_only=True
    )
    earnings_potential = serializers.SerializerMethodField()
    tier_display = serializers.CharField(source='get_current_tier_display', read_only=True)
    country_display = serializers.CharField(source='get_country_display', read_only=True)
    timezone_display = serializers.CharField(source='get_timezone_display', read_only=True)
    
    class Meta:
        model = BrokerTier
        fields = [
            'id', 'broker', 'broker_name', 'broker_email',
            'current_tier', 'tier_display', 'commission_rate',
            'deals_this_month', 'volume_this_month',
            'total_deals', 'total_commissions_earned', 'average_deal_value',
            'streak_days', 'highest_month', 'last_deal_date',
            'achievement_boost', 'deals_needed_next_tier', 'earnings_potential',
            # Geographic fields for African brokers
            'country', 'country_display', 'city', 'timezone', 'timezone_display',
            # Buyer network metrics (critical for overseas buyer acquisition)
            'qualified_buyers_network', 'buyer_conversion_rate',
            'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'broker', 'updated_at', 'created_at']
    
    def get_earnings_potential(self, obj):
        return obj.monthly_earnings_potential()


class DealerTierSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.get_full_name', read_only=True)
    dealer_email = serializers.EmailField(source='dealer.email', read_only=True)
    base_rate = serializers.DecimalField(
        source='get_base_commission_rate',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    market_bonus = serializers.DecimalField(
        source='get_market_bonus',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    total_rate = serializers.DecimalField(
        source='get_total_commission_rate',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    tier_display = serializers.CharField(source='get_current_tier_display', read_only=True)
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    
    class Meta:
        model = DealerTier
        fields = [
            'id', 'dealer', 'dealer_name', 'dealer_email',
            'current_tier', 'tier_display',
            'base_rate', 'market_bonus', 'total_rate',
            'province', 'province_display', 'city', 'is_rural', 'is_first_nations',
            'omvic_certified', 'amvic_certified',
            'deals_this_quarter', 'deals_last_quarter', 'total_deals',
            'average_deal_value', 'total_commissions_earned',
            'welcome_bonus_paid', 'first_deal_bonus_paid', 'fast_start_bonus_paid',
            'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'dealer', 'updated_at', 'created_at']


class BonusTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    bonus_type_display = serializers.CharField(source='get_bonus_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BonusTransaction
        fields = [
            'id', 'user', 'user_name', 
            'bonus_type', 'bonus_type_display',
            'amount_cad', 'status', 'status_display',
            'description', 'created_at', 'approved_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at', 'approved_at', 'paid_at']


class LeaderboardSerializer(serializers.Serializer):
    """Serializer for leaderboard data"""
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    deals = serializers.IntegerField()
    volume = serializers.DecimalField(max_digits=12, decimal_places=2)
    tier = serializers.CharField()
    tier_display = serializers.CharField()
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class InterestRateSerializer(serializers.ModelSerializer):
    """Serializer for interest rate management"""
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    credit_tier_display = serializers.CharField(source='get_credit_tier_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = InterestRate
        fields = [
            'id', 'province', 'province_display',
            'credit_tier', 'credit_tier_display',
            'rate_percentage', 'effective_date', 'is_active',
            'notes', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Set created_by to current user"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class InterestRateMatrixSerializer(serializers.Serializer):
    """Serializer for returning rate matrix for a province"""
    province = serializers.CharField()
    rates = serializers.DictField(
        child=serializers.DecimalField(max_digits=5, decimal_places=2)
    )
    effective_date = serializers.DateField()


