from django.contrib import admin
from .models import Currency, PaymentMethod, Payment, Invoice, InvoiceItem, Transaction, ExchangeRateLog


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate_to_usd', 'is_active', 'is_african', 'stripe_supported']
    list_filter = ['is_active', 'is_african', 'stripe_supported']
    search_fields = ['code', 'name', 'country']
    list_editable = ['is_active', 'exchange_rate_to_usd']
    ordering = ['code']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'display_info', 'is_default', 'is_verified', 'created_at']
    list_filter = ['type', 'is_default', 'is_verified']
    search_fields = ['user__username', 'user__email', 'card_last4', 'bank_name']
    readonly_fields = ['stripe_payment_method_id', 'created_at', 'updated_at']
    
    def display_info(self, obj):
        return str(obj)
    display_info.short_description = 'Payment Info'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'currency', 'status', 'payment_for', 'created_at']
    list_filter = ['status', 'payment_for', 'currency']
    search_fields = ['user__username', 'stripe_payment_intent_id', 'stripe_charge_id']
    readonly_fields = ['stripe_payment_intent_id', 'stripe_charge_id', 'stripe_customer_id', 
                       'amount_in_usd', 'created_at', 'updated_at', 'succeeded_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'deal', 'shipment', 'payment_method', 'payment_for')
        }),
        ('Amount', {
            'fields': ('amount', 'currency', 'amount_in_usd')
        }),
        ('Stripe Details', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id', 'stripe_customer_id')
        }),
        ('Status', {
            'fields': ('status', 'failure_reason', 'description', 'receipt_url')
        }),
        ('Refund', {
            'fields': ('refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'succeeded_at'),
            'classes': ('collapse',)
        }),
    )


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'amount', 'order']
    readonly_fields = ['amount']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'total', 'currency', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['invoice_number', 'user__username', 'user__email']
    readonly_fields = ['invoice_number', 'amount_paid', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'user', 'deal', 'shipment', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total', 'amount_paid', 'currency')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date', 'sent_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms', 'pdf_file'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'user', 'transaction_type', 'amount', 'currency', 'created_at']
    list_filter = ['transaction_type', 'currency']
    search_fields = ['reference_number', 'user__username', 'description']
    readonly_fields = ['reference_number', 'balance_before', 'balance_after', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(ExchangeRateLog)
class ExchangeRateLogAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate_to_usd', 'source', 'timestamp']
    list_filter = ['currency', 'source']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
