from django.contrib import admin
from .models import PriceHistory


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'vehicle',
        'old_price',
        'new_price',
        'price_difference',
        'percentage_change',
        'changed_at',
        'is_price_drop_display',
    ]
    list_filter = [
        'changed_at',
        'vehicle__make',
        'vehicle__condition',
    ]
    search_fields = [
        'vehicle__vin',
        'vehicle__make',
        'vehicle__model',
    ]
    readonly_fields = [
        'price_difference',
        'percentage_change',
        'changed_at',
    ]
    date_hierarchy = 'changed_at'
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('vehicle',)
        }),
        ('Price Change', {
            'fields': (
                'old_price',
                'new_price',
                'price_difference',
                'percentage_change',
                'changed_at',
            )
        }),
        ('Notifications', {
            'fields': ('notified_users',)
        }),
    )
    
    def is_price_drop_display(self, obj):
        """Display icon for price drops"""
        return '\u2193 Drop' if obj.is_price_drop else '\u2191 Increase'
    is_price_drop_display.short_description = 'Change Type'
