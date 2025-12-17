from django.contrib import admin
from .models import Commission, BrokerTier, DealerTier, BonusTransaction


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'deal', 'recipient', 'commission_type', 'amount_cad', 
                    'percentage', 'status', 'created_at']
    list_filter = ['commission_type', 'status', 'created_at', 'payment_currency']
    search_fields = ['deal__id', 'recipient__username', 'recipient__email']
    readonly_fields = ['created_at', 'approved_at', 'paid_at']
    
    fieldsets = (
        ('Commission Information', {
            'fields': ('deal', 'recipient', 'commission_type')
        }),
        ('Amount & Currency', {
            'fields': ('percentage', 'amount_cad', 'amount_usd', 'exchange_rate', 'payment_currency')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'approved_at', 'paid_at')
        }),
    )


@admin.register(BrokerTier)
class BrokerTierAdmin(admin.ModelAdmin):
    list_display = ['broker', 'current_tier', 'country', 'city', 'deals_this_month', 
                    'total_deals', 'qualified_buyers_network', 'buyer_conversion_rate', 'updated_at']
    list_filter = ['current_tier', 'country', 'timezone']
    search_fields = ['broker__username', 'broker__email', 'broker__first_name', 'broker__last_name', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Broker Information', {
            'fields': ('broker', 'current_tier')
        }),
        ('Location (African Brokers)', {
            'fields': ('country', 'city', 'timezone'),
            'description': 'Geographic location for broker tracking and timezone support'
        }),
        ('Buyer Network Metrics', {
            'fields': ('qualified_buyers_network', 'buyer_conversion_rate'),
            'description': 'Track broker success at building overseas buyer networks'
        }),
        ('Monthly Performance', {
            'fields': ('deals_this_month', 'volume_this_month')
        }),
        ('All-Time Stats', {
            'fields': ('total_deals', 'total_commissions_earned', 'average_deal_value')
        }),
        ('Gamification', {
            'fields': ('streak_days', 'highest_month', 'last_deal_date', 'achievement_boost')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DealerTier)
class DealerTierAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'current_tier', 'province', 'deals_this_quarter', 
                    'total_deals', 'is_rural', 'is_first_nations', 'updated_at']
    list_filter = ['current_tier', 'province', 'is_rural', 'is_first_nations', 
                   'omvic_certified', 'amvic_certified']
    search_fields = ['dealer__username', 'dealer__email', 'dealer__first_name', 
                    'dealer__last_name', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Dealer Information', {
            'fields': ('dealer', 'current_tier')
        }),
        ('Location & Canadian Bonuses', {
            'fields': ('province', 'city', 'is_rural', 'is_first_nations')
        }),
        ('Certifications', {
            'fields': ('omvic_certified', 'amvic_certified', 'certification_bonus_paid')
        }),
        ('Performance', {
            'fields': ('deals_this_quarter', 'deals_last_quarter', 'total_deals', 
                      'average_deal_value', 'total_commissions_earned')
        }),
        ('Onboarding Bonuses', {
            'fields': ('welcome_bonus_paid', 'first_deal_bonus_paid', 'fast_start_bonus_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'bonus_type', 'amount_cad', 'status', 'created_at']
    list_filter = ['bonus_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'description']
    readonly_fields = ['created_at', 'approved_at', 'paid_at']
    
    fieldsets = (
        ('Bonus Information', {
            'fields': ('user', 'bonus_type', 'amount_cad', 'status')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'approved_at', 'paid_at')
        }),
    )
