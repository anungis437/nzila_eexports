from rest_framework import serializers
from .models import Shipment, ShipmentUpdate
from .tracking_models import ShipmentMilestone, ShipmentPhoto
from vehicles.models import Vehicle


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentUpdate
        fields = ['id', 'location', 'status', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ShipmentMilestoneSerializer(serializers.ModelSerializer):
    milestone_type_display = serializers.CharField(source='get_milestone_type_display', read_only=True)
    
    class Meta:
        model = ShipmentMilestone
        fields = ['id', 'milestone_type', 'milestone_type_display', 'title', 
                  'description', 'location', 'latitude', 'longitude', 
                  'completed_at', 'is_completed', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShipmentPhotoSerializer(serializers.ModelSerializer):
    photo_type_display = serializers.CharField(source='get_photo_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = ShipmentPhoto
        fields = ['id', 'photo', 'photo_type', 'photo_type_display', 'caption', 
                  'description', 'location', 'latitude', 'longitude', 'taken_at',
                  'uploaded_by', 'uploaded_by_name', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class ShipmentSerializer(serializers.ModelSerializer):
    updates = ShipmentUpdateSerializer(many=True, read_only=True)
    milestones = ShipmentMilestoneSerializer(many=True, read_only=True)
    photos = ShipmentPhotoSerializer(many=True, read_only=True)
    deal_id = serializers.IntegerField(source='deal.id', read_only=True)
    vehicle_details = serializers.SerializerMethodField()
    has_gps_tracking = serializers.SerializerMethodField()
    
    # Display values for choice fields
    vgm_method_display = serializers.CharField(source='get_vgm_method_display', read_only=True)
    ams_status_display = serializers.CharField(source='get_ams_status_display', read_only=True)
    aci_status_display = serializers.CharField(source='get_aci_status_display', read_only=True)
    ens_status_display = serializers.CharField(source='get_ens_status_display', read_only=True)
    bill_of_lading_type_display = serializers.CharField(source='get_bill_of_lading_type_display', read_only=True)
    freight_terms_display = serializers.CharField(source='get_freight_terms_display', read_only=True)
    incoterm_display = serializers.CharField(source='get_incoterm_display', read_only=True)
    isps_facility_security_level_display = serializers.CharField(source='get_isps_facility_security_level_display', read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            # Basic shipment info
            'id', 'deal', 'deal_id', 'tracking_number', 'shipping_company',
            'origin_port', 'destination_port', 'destination_country',
            'status', 'estimated_departure', 'actual_departure',
            'estimated_arrival', 'actual_arrival', 'notes', 
            
            # GPS tracking
            'current_latitude', 'current_longitude', 'last_location_update',
            'has_gps_tracking',
            
            # Container & Seal
            'container_number', 'container_type',
            'seal_number', 'seal_type', 'seal_intact',
            
            # PRIORITY 1: SOLAS VGM (CRITICAL)
            'vgm_weight_kg', 'vgm_method', 'vgm_method_display',
            'vgm_certified_by', 'vgm_certification_date', 'vgm_certificate_number',
            
            # PRIORITY 1: AMS - US Customs (CRITICAL)
            'ams_filing_number', 'ams_submission_date', 'ams_status', 'ams_status_display',
            'ams_arrival_notice_date', 'ams_scac_code',
            
            # PRIORITY 1: ACI - Canada Customs (CRITICAL)
            'aci_submission_date', 'cargo_control_document_number', 
            'pars_number', 'paps_number', 'release_notification_number',
            'aci_status', 'aci_status_display',
            
            # PRIORITY 2: AES - US Export System
            'aes_itn_number', 'aes_filing_date', 'aes_exemption_code',
            'schedule_b_code', 'export_license_required', 'export_license_number',
            
            # PRIORITY 2: ENS - EU Entry Summary
            'ens_mrn_number', 'ens_filing_date', 'ens_status', 'ens_status_display',
            'ens_lrn_number',
            
            # PRIORITY 2: ISPS Code - Port Security
            'isps_facility_security_level', 'isps_facility_security_level_display',
            'origin_port_isps_certified', 'destination_port_isps_certified',
            'port_facility_security_officer', 'ship_security_alert_system',
            
            # PRIORITY 3: HS Tariff & Customs
            'hs_tariff_code', 'customs_value_declared', 'customs_value_currency',
            'duty_paid', 'customs_broker_name', 'customs_broker_license',
            
            # PRIORITY 3: Hazmat & Dangerous Goods
            'contains_hazmat', 'un_number', 'imdg_class',
            'hazmat_emergency_contact', 'msds_attached',
            
            # PRIORITY 3: Bill of Lading
            'bill_of_lading_number', 'bill_of_lading_type', 'bill_of_lading_type_display',
            'bill_of_lading_date', 'freight_terms', 'freight_terms_display',
            'incoterm', 'incoterm_display', 'shipper_reference',
            'consignee_name', 'consignee_address', 'notify_party',
            
            # PRIORITY 3: Vessel Information
            'vessel_name', 'voyage_number', 'imo_vessel_number',
            
            # Lloyd's Register
            'lloyd_register_tracking_id', 'lloyd_register_status',
            'lloyd_register_certificate_number',
            
            # ISO 28000 Security
            'security_risk_level', 'ctpat_compliant', 'iso_18602_compliant',
            
            # Relationships
            'updates', 'milestones', 'photos', 'vehicle_details',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'vgm_certification_date', 'ams_submission_date', 'aci_submission_date',
            'aes_filing_date', 'ens_filing_date', 'bill_of_lading_date'
        ]
    
    def get_vehicle_details(self, obj):
        """Get vehicle details from the related deal"""
        if obj.deal and obj.deal.vehicle:
            vehicle = obj.deal.vehicle
            return {
                'id': vehicle.id,
                'year': vehicle.year,
                'make': vehicle.make,
                'model': vehicle.model,
                'vin': vehicle.vin,
                'color': vehicle.color,
            }
        return None
    
    def get_has_gps_tracking(self, obj):
        """Check if shipment has active GPS tracking"""
        return obj.current_latitude is not None and obj.current_longitude is not None
