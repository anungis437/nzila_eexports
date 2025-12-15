from django.contrib import admin
from .models import Shipment, ShipmentUpdate


class ShipmentUpdateInline(admin.TabularInline):
    model = ShipmentUpdate
    extra = 1
    readonly_fields = ['created_at']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'deal', 'status', 'shipping_company', 
                    'origin_port', 'destination_port', 'estimated_arrival']
    list_filter = ['status', 'destination_country', 'shipping_company']
    search_fields = ['tracking_number', 'deal__id', 'destination_country']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ShipmentUpdateInline]
    
    fieldsets = (
        ('Deal Information', {
            'fields': ('deal',)
        }),
        ('Shipment Details', {
            'fields': ('tracking_number', 'shipping_company', 'status')
        }),
        ('Locations', {
            'fields': ('origin_port', 'destination_port', 'destination_country')
        }),
        ('Schedule', {
            'fields': ('estimated_departure', 'actual_departure', 
                      'estimated_arrival', 'actual_arrival')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ShipmentUpdate)
class ShipmentUpdateAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'location', 'status', 'created_at']
    list_filter = ['created_at']
    search_fields = ['shipment__tracking_number', 'location']
    readonly_fields = ['created_at']
