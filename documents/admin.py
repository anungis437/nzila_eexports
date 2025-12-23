"""
PHASE 2 - Feature 5: Export Documents Admin Interface
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ExportDocument, ExportChecklist


@admin.register(ExportDocument)
class ExportDocumentAdmin(admin.ModelAdmin):
    """Admin interface for Export Documents"""
    
    list_display = [
        'id',
        'document_type',
        'vehicle_link',
        'buyer_link',
        'status',
        'created_at',
        'expires_at',
        'is_expired',
        'download_link',
    ]
    
    list_filter = [
        'document_type',
        'status',
        'created_at',
    ]
    
    search_fields = [
        'vehicle__vin',
        'vehicle__make',
        'vehicle__model',
        'buyer__username',
        'buyer__email',
        'notes',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_expired',
    ]
    
    fieldsets = (
        ('Document Information', {
            'fields': ('document_type', 'status', 'file')
        }),
        ('Related Records', {
            'fields': ('vehicle', 'buyer')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'expires_at', 'is_expired')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_link(self, obj):
        """Link to vehicle admin page"""
        if obj.vehicle:
            url = f'/admin/vehicles/vehicle/{obj.vehicle.id}/change/'
            return format_html('<a href="{}">{}</a>', url, str(obj.vehicle))
        return '-'
    vehicle_link.short_description = 'Vehicle'
    
    def buyer_link(self, obj):
        """Link to buyer admin page"""
        if obj.buyer:
            url = f'/admin/accounts/user/{obj.buyer.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.buyer.username)
        return '-'
    buyer_link.short_description = 'Buyer'
    
    def download_link(self, obj):
        """Download link for document file"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">Download</a>',
                obj.file.url
            )
        return '-'
    download_link.short_description = 'File'
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('vehicle', 'buyer')


@admin.register(ExportChecklist)
class ExportChecklistAdmin(admin.ModelAdmin):
    """Admin interface for Export Checklists"""
    
    list_display = [
        'id',
        'vehicle_link',
        'buyer_link',
        'completion_bar',
        'export_ready',
        'created_at',
        'completed_at',
    ]
    
    list_filter = [
        'export_ready',
        'title_verified',
        'lien_checked',
        'payment_cleared',
        'created_at',
    ]
    
    search_fields = [
        'vehicle__vin',
        'vehicle__make',
        'vehicle__model',
        'buyer__username',
        'buyer__email',
        'notes',
    ]
    
    readonly_fields = [
        'export_ready',
        'created_at',
        'updated_at',
        'completed_at',
        'completion_percentage_display',
    ]
    
    fieldsets = (
        ('Vehicle and Buyer', {
            'fields': ('vehicle', 'buyer')
        }),
        ('Checklist Items', {
            'fields': (
                'title_verified',
                'lien_checked',
                'insurance_confirmed',
                'payment_cleared',
                'inspection_completed',
                'cbsa_form_generated',
                'title_guide_provided',
            )
        }),
        ('Status', {
            'fields': (
                'export_ready',
                'completion_percentage_display',
            )
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_link(self, obj):
        """Link to vehicle admin page"""
        if obj.vehicle:
            url = f'/admin/vehicles/vehicle/{obj.vehicle.id}/change/'
            return format_html('<a href="{}">{}</a>', url, str(obj.vehicle))
        return '-'
    vehicle_link.short_description = 'Vehicle'
    
    def buyer_link(self, obj):
        """Link to buyer admin page"""
        if obj.buyer:
            url = f'/admin/accounts/user/{obj.buyer.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.buyer.username)
        return '-'
    buyer_link.short_description = 'Buyer'
    
    def completion_bar(self, obj):
        """Visual completion percentage"""
        percentage = obj.get_completion_percentage()
        
        if percentage == 100:
            color = '#28a745'  # Green
        elif percentage >= 50:
            color = '#ffc107'  # Yellow
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<div style="width:100px; background:#f0f0f0; border:1px solid #ccc;">'
            '<div style="width:{}px; background:{}; height:20px; line-height:20px; text-align:center; color:white; font-weight:bold;">{}</div>'
            '</div>',
            percentage,
            color,
            f'{percentage}%'
        )
    completion_bar.short_description = 'Completion'
    
    def completion_percentage_display(self, obj):
        """Display completion percentage as text"""
        return f"{obj.get_completion_percentage()}%"
    completion_percentage_display.short_description = 'Completion Percentage'
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('vehicle', 'buyer')
    
    def save_model(self, request, obj, form, change):
        """Auto-check completion on save"""
        super().save_model(request, obj, form, change)
        obj.check_completion()
