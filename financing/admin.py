"""
Financing Admin Interface

Admin interfaces for managing interest rates, loan scenarios, and trade-in estimates
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import InterestRate, LoanScenario, TradeInEstimate


@admin.register(InterestRate)
class InterestRateAdmin(admin.ModelAdmin):
    """Admin interface for interest rate management"""
    
    list_display = [
        'credit_tier_display', 'loan_term_display', 'rate_display',
        'effective_date', 'active_badge', 'created_at'
    ]
    list_filter = ['credit_tier', 'loan_term_months', 'is_active', 'effective_date']
    search_fields = ['credit_tier']
    ordering = ['credit_tier', 'loan_term_months', '-effective_date']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Rate Information', {
            'fields': ('credit_tier', 'loan_term_months', 'annual_interest_rate')
        }),
        ('Status', {
            'fields': ('effective_date', 'is_active')
        }),
    )
    
    def credit_tier_display(self, obj):
        """Display credit tier with color coding"""
        colors = {
            'excellent': '#10B981',  # Green
            'good': '#3B82F6',       # Blue
            'fair': '#F59E0B',       # Orange
            'poor': '#EF4444',       # Red
            'bad': '#DC2626',        # Dark red
        }
        color = colors.get(obj.credit_tier, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_credit_tier_display()
        )
    credit_tier_display.short_description = 'Credit Tier'
    
    def loan_term_display(self, obj):
        """Display loan term"""
        return f"{obj.loan_term_months} months"
    loan_term_display.short_description = 'Loan Term'
    
    def rate_display(self, obj):
        """Display annual interest rate"""
        return format_html(
            '<strong>{:.2f}%</strong> <span style="color: #6B7280;">(monthly: {:.4f}%)</span>',
            obj.annual_interest_rate, obj.monthly_interest_rate
        )
    rate_display.short_description = 'Interest Rate'
    
    def active_badge(self, obj):
        """Display active status with badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #10B981; color: white; padding: 2px 8px; border-radius: 4px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #6B7280; color: white; padding: 2px 8px; border-radius: 4px;">Inactive</span>'
        )
    active_badge.short_description = 'Status'
    
    actions = ['activate_rates', 'deactivate_rates']
    
    def activate_rates(self, request, queryset):
        """Bulk activate rates"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} rate(s) activated successfully.')
    activate_rates.short_description = "Activate selected rates"
    
    def deactivate_rates(self, request, queryset):
        """Bulk deactivate rates"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} rate(s) deactivated successfully.')
    deactivate_rates.short_description = "Deactivate selected rates"


@admin.register(LoanScenario)
class LoanScenarioAdmin(admin.ModelAdmin):
    """Admin interface for loan scenario management"""
    
    list_display = [
        'buyer_email', 'scenario_name_display', 'vehicle_price_display',
        'monthly_payment_display', 'loan_term_display', 'credit_tier_badge',
        'favorite_badge', 'created_at'
    ]
    list_filter = ['credit_tier', 'loan_term_months', 'province', 'is_favorite', 'created_at']
    search_fields = ['buyer__email', 'scenario_name', 'vehicle__vin']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['buyer', 'vehicle']
    
    fieldsets = (
        ('Buyer & Vehicle', {
            'fields': ('buyer', 'vehicle', 'scenario_name', 'is_favorite')
        }),
        ('Loan Parameters', {
            'fields': (
                'vehicle_price', 'down_payment', 'trade_in_value',
                'loan_term_months', 'credit_tier', 'province'
            )
        }),
        ('Calculated Values', {
            'fields': (
                'loan_amount', 'monthly_payment', 'total_interest', 'total_cost',
                'annual_interest_rate'
            ),
            'classes': ['collapse']
        }),
        ('Taxes & Fees', {
            'fields': (
                'pst_amount', 'gst_hst_amount', 'documentation_fee',
                'license_registration_fee'
            ),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = [
        'loan_amount', 'monthly_payment', 'total_interest', 'total_cost',
        'annual_interest_rate', 'pst_amount', 'gst_hst_amount'
    ]
    
    def buyer_email(self, obj):
        """Display buyer email"""
        return obj.buyer.email
    buyer_email.short_description = 'Buyer'
    buyer_email.admin_order_field = 'buyer__email'
    
    def scenario_name_display(self, obj):
        """Display scenario name or default"""
        if obj.scenario_name:
            return format_html('<strong>{}</strong>', obj.scenario_name)
        return format_html('<em>Scenario #{}</em>', obj.id)
    scenario_name_display.short_description = 'Scenario'
    
    def vehicle_price_display(self, obj):
        """Display vehicle price"""
        return format_html('${:,.2f}', obj.vehicle_price)
    vehicle_price_display.short_description = 'Vehicle Price'
    vehicle_price_display.admin_order_field = 'vehicle_price'
    
    def monthly_payment_display(self, obj):
        """Display monthly payment with emphasis"""
        if obj.monthly_payment:
            return format_html(
                '<strong style="font-size: 14px; color: #10B981;">${:,.2f}/mo</strong>',
                obj.monthly_payment
            )
        return '-'
    monthly_payment_display.short_description = 'Monthly Payment'
    monthly_payment_display.admin_order_field = 'monthly_payment'
    
    def loan_term_display(self, obj):
        """Display loan term"""
        return f"{obj.loan_term_months} mo"
    loan_term_display.short_description = 'Term'
    
    def credit_tier_badge(self, obj):
        """Display credit tier with color"""
        colors = {
            'excellent': '#10B981',
            'good': '#3B82F6',
            'fair': '#F59E0B',
            'poor': '#EF4444',
            'bad': '#DC2626',
        }
        color = colors.get(obj.credit_tier, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_credit_tier_display().upper()
        )
    credit_tier_badge.short_description = 'Credit Tier'
    
    def favorite_badge(self, obj):
        """Display favorite status"""
        if obj.is_favorite:
            return format_html('⭐ <strong>Favorite</strong>')
        return '-'
    favorite_badge.short_description = 'Favorite'
    
    actions = ['recalculate_scenarios', 'mark_favorite', 'unmark_favorite']
    
    def recalculate_scenarios(self, request, queryset):
        """Recalculate selected scenarios"""
        count = 0
        for scenario in queryset:
            scenario.calculate()
            count += 1
        self.message_user(request, f'{count} scenario(s) recalculated successfully.')
    recalculate_scenarios.short_description = "Recalculate selected scenarios"
    
    def mark_favorite(self, request, queryset):
        """Mark as favorite"""
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} scenario(s) marked as favorite.')
    mark_favorite.short_description = "Mark as favorite"
    
    def unmark_favorite(self, request, queryset):
        """Unmark as favorite"""
        updated = queryset.update(is_favorite=False)
        self.message_user(request, f'{updated} scenario(s) unmarked as favorite.')
    unmark_favorite.short_description = "Remove favorite"


@admin.register(TradeInEstimate)
class TradeInEstimateAdmin(admin.ModelAdmin):
    """Admin interface for trade-in estimate management"""
    
    list_display = [
        'buyer_email', 'vehicle_display', 'mileage_display',
        'condition_badge', 'trade_in_value_display', 'estimate_date'
    ]
    list_filter = ['condition', 'province', 'year', 'estimate_date']
    search_fields = ['buyer__email', 'make', 'model', 'year']
    ordering = ['-created_at']
    date_hierarchy = 'estimate_date'
    raw_id_fields = ['buyer']
    
    fieldsets = (
        ('Buyer', {
            'fields': ('buyer',)
        }),
        ('Vehicle Details', {
            'fields': ('year', 'make', 'model', 'trim', 'mileage', 'condition', 'province')
        }),
        ('Estimated Values', {
            'fields': ('trade_in_value', 'private_party_value', 'retail_value')
        }),
        ('Metadata', {
            'fields': ('estimate_date', 'data_source', 'notes'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['estimate_date', 'data_source']
    
    def buyer_email(self, obj):
        """Display buyer email"""
        return obj.buyer.email
    buyer_email.short_description = 'Buyer'
    buyer_email.admin_order_field = 'buyer__email'
    
    def vehicle_display(self, obj):
        """Display vehicle description"""
        trim_str = f" {obj.trim}" if obj.trim else ""
        return format_html(
            '<strong>{} {} {}</strong>{}',
            obj.year, obj.make, obj.model, trim_str
        )
    vehicle_display.short_description = 'Vehicle'
    
    def mileage_display(self, obj):
        """Display mileage"""
        return format_html('{:,} km', obj.mileage)
    mileage_display.short_description = 'Mileage'
    mileage_display.admin_order_field = 'mileage'
    
    def condition_badge(self, obj):
        """Display condition with color"""
        colors = {
            'excellent': '#10B981',
            'good': '#3B82F6',
            'fair': '#F59E0B',
            'poor': '#EF4444',
        }
        color = colors.get(obj.condition, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_condition_display().upper()
        )
    condition_badge.short_description = 'Condition'
    
    def trade_in_value_display(self, obj):
        """Display trade-in value range"""
        return format_html(
            '<div><strong style="color: #10B981; font-size: 14px;">${:,.0f}</strong> (trade-in)</div>'
            '<div style="font-size: 11px; color: #6B7280;">${:,.0f} (private) / ${:,.0f} (retail)</div>',
            obj.trade_in_value, obj.private_party_value, obj.retail_value
        )
    trade_in_value_display.short_description = 'Value Estimates'
