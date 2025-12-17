from django.contrib import admin
from .models import VehicleHistoryReport, AccidentRecord, ServiceRecord, OwnershipRecord


class AccidentRecordInline(admin.TabularInline):
    model = AccidentRecord
    extra = 0
    fields = [
        'accident_date', 'damage_severity', 'front_damage', 'rear_damage',
        'left_side_damage', 'right_side_damage', 'repair_cost', 'insurance_claim'
    ]


class ServiceRecordInline(admin.TabularInline):
    model = ServiceRecord
    extra = 0
    fields = ['service_date', 'service_type', 'odometer_reading', 'service_cost', 'description']


class OwnershipRecordInline(admin.TabularInline):
    model = OwnershipRecord
    extra = 0
    fields = ['owner_number', 'ownership_start', 'ownership_end', 'state_province', 'ownership_type']


@admin.register(VehicleHistoryReport)
class VehicleHistoryReportAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle', 'title_status', 'accident_severity', 'total_owners',
        'trust_score', 'report_confidence', 'report_updated_at'
    ]
    list_filter = [
        'title_status', 'accident_severity', 'report_confidence',
        'odometer_rollback', 'structural_damage', 'rental_use', 'taxi_use'
    ]
    search_fields = ['vehicle__vin', 'vehicle__make', 'vehicle__model', 'notes']
    readonly_fields = [
        'report_generated_at', 'report_updated_at', 'trust_score',
        'is_clean_title', 'has_accidents', 'is_one_owner', 'has_commercial_use'
    ]
    
    fieldsets = (
        ('Vehicle', {
            'fields': ('vehicle',)
        }),
        ('Title Information', {
            'fields': ('title_status', 'title_issue_date', 'title_state')
        }),
        ('Accident History', {
            'fields': (
                'accident_severity', 'total_accidents', 'last_accident_date',
                'structural_damage', 'frame_damage', 'airbag_deployment'
            )
        }),
        ('Ownership History', {
            'fields': (
                'total_owners', 'personal_use', 'rental_use',
                'taxi_use', 'police_use'
            )
        }),
        ('Odometer', {
            'fields': (
                'odometer_rollback', 'odometer_verified',
                'last_odometer_reading', 'last_odometer_date'
            )
        }),
        ('Service & Recalls', {
            'fields': (
                'total_service_records', 'last_service_date', 'recalls_outstanding'
            )
        }),
        ('Report Metadata', {
            'fields': (
                'report_source', 'report_confidence', 'report_generated_at',
                'report_updated_at', 'notes'
            )
        }),
        ('Computed Values', {
            'fields': (
                'trust_score', 'is_clean_title', 'has_accidents',
                'is_one_owner', 'has_commercial_use'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AccidentRecordInline, ServiceRecordInline, OwnershipRecordInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vehicle')


@admin.register(AccidentRecord)
class AccidentRecordAdmin(admin.ModelAdmin):
    list_display = [
        'history_report', 'accident_date', 'damage_severity',
        'repair_cost', 'repair_completed', 'insurance_claim'
    ]
    list_filter = ['damage_severity', 'repair_completed', 'insurance_claim', 'accident_date']
    search_fields = ['history_report__vehicle__vin', 'description']
    date_hierarchy = 'accident_date'


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'history_report', 'service_date', 'service_type',
        'odometer_reading', 'service_cost'
    ]
    list_filter = ['service_type', 'service_date']
    search_fields = ['history_report__vehicle__vin', 'description', 'service_facility']
    date_hierarchy = 'service_date'


@admin.register(OwnershipRecord)
class OwnershipRecordAdmin(admin.ModelAdmin):
    list_display = [
        'history_report', 'owner_number', 'ownership_start',
        'ownership_end', 'ownership_type', 'state_province'
    ]
    list_filter = ['ownership_type', 'ownership_start']
    search_fields = ['history_report__vehicle__vin', 'state_province']
    date_hierarchy = 'ownership_start'
