from django.contrib import admin
from .models import Vehicle, VehicleImage


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


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
