from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle, VehicleImage, Offer, VehicleInspectionSlot, InspectionAppointment


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


# PHASE 1: In-Person Inspection Admin


class InspectionAppointmentInline(admin.TabularInline):
    model = InspectionAppointment
    extra = 0
    fields = ['buyer', 'status', 'contact_phone', 'number_of_people', 'interested_in_purchase']
    readonly_fields = ['buyer', 'created_at']
    can_delete = False


@admin.register(VehicleInspectionSlot)
class VehicleInspectionSlotAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'date', 'start_time', 'end_time', 'is_available', 
                    'current_bookings', 'slots_remaining', 'created_at']
    list_filter = ['is_available', 'date', 'vehicle__dealer']
    search_fields = ['vehicle__vin', 'vehicle__make', 'vehicle__model']
    readonly_fields = ['created_at', 'updated_at', 'current_bookings', 'slots_remaining', 'is_past']
    inlines = [InspectionAppointmentInline]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Vehicle', {
            'fields': ('vehicle',)
        }),
        ('Time Slot', {
            'fields': ('date', 'start_time', 'end_time')
        }),
        ('Availability', {
            'fields': ('is_available', 'max_attendees', 'current_bookings', 'slots_remaining', 'is_past')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vehicle', 'vehicle__dealer')


@admin.register(InspectionAppointment)
class InspectionAppointmentAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'vehicle_info', 'slot_date', 'slot_time', 'status', 
                    'interested_in_purchase', 'vehicle_rating', 'dealer_rating', 'created_at']
    list_filter = ['status', 'interested_in_purchase', 'slot__date', 'vehicle_rating', 'dealer_rating']
    search_fields = ['buyer__email', 'buyer__username', 'slot__vehicle__vin', 
                     'slot__vehicle__make', 'slot__vehicle__model', 'contact_phone']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'completed_at', 
                       'cancelled_at', 'vehicle', 'dealer']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Inspection Details', {
            'fields': ('slot', 'buyer', 'status', 'vehicle', 'dealer')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email', 'number_of_people')
        }),
        ('Notes', {
            'fields': ('buyer_notes', 'dealer_notes', 'inspection_feedback')
        }),
        ('Ratings', {
            'fields': ('vehicle_rating', 'dealer_rating')
        }),
        ('Outcome', {
            'fields': ('interested_in_purchase',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_info(self, obj):
        """Display vehicle information"""
        vehicle = obj.slot.vehicle
        return f"{vehicle.year} {vehicle.make} {vehicle.model}"
    vehicle_info.short_description = 'Vehicle'
    
    def slot_date(self, obj):
        """Display slot date"""
        return obj.slot.date
    slot_date.short_description = 'Date'
    slot_date.admin_order_field = 'slot__date'
    
    def slot_time(self, obj):
        """Display slot time"""
        return f"{obj.slot.start_time} - {obj.slot.end_time}"
    slot_time.short_description = 'Time'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'slot', 'slot__vehicle', 'slot__vehicle__dealer', 'buyer'
        )
