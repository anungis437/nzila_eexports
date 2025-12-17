from rest_framework import serializers
from .models import (
    VehicleHistoryReport,
    AccidentRecord,
    ServiceRecord,
    OwnershipRecord
)


class AccidentRecordSerializer(serializers.ModelSerializer):
    damage_areas = serializers.SerializerMethodField()
    
    class Meta:
        model = AccidentRecord
        fields = [
            'id', 'accident_date', 'damage_severity', 'damage_areas',
            'front_damage', 'rear_damage', 'left_side_damage', 'right_side_damage',
            'roof_damage', 'undercarriage_damage', 'repair_cost', 'repair_facility',
            'repair_completed', 'insurance_claim', 'description'
        ]
    
    def get_damage_areas(self, obj):
        """Return list of damaged areas"""
        areas = []
        if obj.front_damage:
            areas.append('front')
        if obj.rear_damage:
            areas.append('rear')
        if obj.left_side_damage:
            areas.append('left_side')
        if obj.right_side_damage:
            areas.append('right_side')
        if obj.roof_damage:
            areas.append('roof')
        if obj.undercarriage_damage:
            areas.append('undercarriage')
        return areas


class ServiceRecordSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    class Meta:
        model = ServiceRecord
        fields = [
            'id', 'service_date', 'service_type', 'service_type_display',
            'odometer_reading', 'service_facility', 'service_cost', 'description'
        ]


class OwnershipRecordSerializer(serializers.ModelSerializer):
    ownership_type_display = serializers.CharField(source='get_ownership_type_display', read_only=True)
    ownership_duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = OwnershipRecord
        fields = [
            'id', 'owner_number', 'ownership_start', 'ownership_end',
            'state_province', 'ownership_type', 'ownership_type_display',
            'estimated_annual_miles', 'ownership_duration_days'
        ]
    
    def get_ownership_duration_days(self, obj):
        """Calculate ownership duration in days"""
        if obj.ownership_end:
            return (obj.ownership_end - obj.ownership_start).days
        return None


class VehicleHistoryReportSerializer(serializers.ModelSerializer):
    accident_records = AccidentRecordSerializer(many=True, read_only=True)
    service_records = ServiceRecordSerializer(many=True, read_only=True)
    ownership_records = OwnershipRecordSerializer(many=True, read_only=True)
    
    title_status_display = serializers.CharField(source='get_title_status_display', read_only=True)
    accident_severity_display = serializers.CharField(source='get_accident_severity_display', read_only=True)
    report_confidence_display = serializers.CharField(source='get_report_confidence_display', read_only=True)
    
    # Computed properties
    is_clean_title = serializers.BooleanField(read_only=True)
    has_accidents = serializers.BooleanField(read_only=True)
    is_one_owner = serializers.BooleanField(read_only=True)
    has_commercial_use = serializers.BooleanField(read_only=True)
    trust_score = serializers.IntegerField(read_only=True)
    
    # Vehicle info
    vehicle_vin = serializers.CharField(source='vehicle.vin', read_only=True)
    vehicle_make = serializers.CharField(source='vehicle.make', read_only=True)
    vehicle_model = serializers.CharField(source='vehicle.model', read_only=True)
    vehicle_year = serializers.IntegerField(source='vehicle.year', read_only=True)
    
    class Meta:
        model = VehicleHistoryReport
        fields = [
            'id', 'vehicle', 'vehicle_vin', 'vehicle_make', 'vehicle_model', 'vehicle_year',
            # Title
            'title_status', 'title_status_display', 'title_issue_date', 'title_state',
            # Accidents
            'accident_severity', 'accident_severity_display', 'total_accidents',
            'last_accident_date', 'accident_records',
            # Ownership
            'total_owners', 'personal_use', 'rental_use', 'taxi_use', 'police_use',
            'ownership_records',
            # Odometer
            'odometer_rollback', 'odometer_verified', 'last_odometer_reading',
            'last_odometer_date',
            # Service
            'total_service_records', 'last_service_date', 'recalls_outstanding',
            'service_records',
            # Damage
            'structural_damage', 'frame_damage', 'airbag_deployment',
            # Report metadata
            'report_generated_at', 'report_updated_at', 'report_source',
            'report_confidence', 'report_confidence_display', 'notes',
            # Computed
            'is_clean_title', 'has_accidents', 'is_one_owner', 'has_commercial_use',
            'trust_score'
        ]


class VehicleHistoryReportSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for embedding in vehicle listings"""
    
    title_status_display = serializers.CharField(source='get_title_status_display', read_only=True)
    trust_score = serializers.IntegerField(read_only=True)
    is_clean_title = serializers.BooleanField(read_only=True)
    has_accidents = serializers.BooleanField(read_only=True)
    is_one_owner = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = VehicleHistoryReport
        fields = [
            'id', 'title_status', 'title_status_display', 'total_accidents',
            'total_owners', 'trust_score', 'is_clean_title', 'has_accidents',
            'is_one_owner', 'report_confidence'
        ]
