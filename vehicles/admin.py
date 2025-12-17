from django.contrib import admin
from .models import Vehicle, VehicleImage, Offer


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
    fields = ['media_type', 'image', 'video', 'thumbnail', 'duration_seconds', 'caption', 'order']
    readonly_fields = ['thumbnail']
    list_display = ['media_type', 'order']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vin', 'make', 'model', 'year', 'dealer', 'status', 'price_cad', 'created_at']
    list_filter = ['status', 'condition', 'make', 'year', 'dealer']
    search_fields = ['vin', 'make', 'model', 'dealer__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [VehicleImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('dealer', 'make', 'model', 'year', 'vin')
        }),
        ('Details', {
            'fields': ('condition', 'mileage', 'color', 'fuel_type', 'transmission', 'description')
        }),
        ('Location & Pricing', {
            'fields': ('location', 'price_cad')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Images', {
            'fields': ('main_image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'buyer', 'offer_amount_cad', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['vehicle__vin', 'vehicle__make', 'vehicle__model', 'buyer__email']
    readonly_fields = ['created_at', 'updated_at', 'responded_at', 'is_expired']
    
    fieldsets = (
        ('Offer Details', {
            'fields': ('vehicle', 'buyer', 'offer_amount_cad', 'message', 'status')
        }),
        ('Counter Offer', {
            'fields': ('counter_amount_cad', 'counter_message')
        }),
        ('Dealer Response', {
            'fields': ('dealer_notes', 'responded_at')
        }),
        ('Validity', {
            'fields': ('valid_until', 'is_expired')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vehicle', 'buyer')
