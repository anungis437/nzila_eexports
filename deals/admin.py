from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Lead, Deal, Document


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'vehicle', 'broker', 'status', 'source', 'created_at', 'is_stalled']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['buyer__username', 'vehicle__vin', 'broker__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Lead Information', {
            'fields': ('buyer', 'vehicle', 'broker', 'status', 'source')
        }),
        ('Details', {
            'fields': ('notes', 'last_contacted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def is_stalled(self, obj):
        return obj.is_stalled()
    is_stalled.boolean = True
    is_stalled.short_description = _('Stalled')


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    readonly_fields = ['uploaded_at', 'verified_at']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'buyer', 'dealer', 'broker', 'status', 'agreed_price_cad', 'created_at', 'is_stalled']
    list_filter = ['status', 'created_at']
    search_fields = ['vehicle__vin', 'buyer__username', 'dealer__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    inlines = [DocumentInline]
    
    fieldsets = (
        ('Deal Information', {
            'fields': ('lead', 'vehicle', 'buyer', 'dealer', 'broker')
        }),
        ('Status & Pricing', {
            'fields': ('status', 'agreed_price_cad')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def is_stalled(self, obj):
        return obj.is_stalled()
    is_stalled.boolean = True
    is_stalled.short_description = _('Stalled')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'deal', 'document_type', 'status', 'uploaded_by', 'verified_by', 'uploaded_at']
    list_filter = ['document_type', 'status', 'uploaded_at']
    search_fields = ['deal__id', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'verified_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('deal', 'document_type', 'file', 'status')
        }),
        ('Verification', {
            'fields': ('uploaded_by', 'verified_by', 'notes')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'verified_at')
        }),
    )
