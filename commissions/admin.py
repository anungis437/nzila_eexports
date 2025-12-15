from django.contrib import admin
from .models import Commission


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'deal', 'recipient', 'commission_type', 'amount_cad', 
                    'percentage', 'status', 'created_at']
    list_filter = ['commission_type', 'status', 'created_at']
    search_fields = ['deal__id', 'recipient__username']
    readonly_fields = ['created_at', 'approved_at', 'paid_at']
    
    fieldsets = (
        ('Commission Information', {
            'fields': ('deal', 'recipient', 'commission_type')
        }),
        ('Amount & Status', {
            'fields': ('percentage', 'amount_cad', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'approved_at', 'paid_at')
        }),
    )
