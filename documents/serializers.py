"""
PHASE 2 - Feature 5: Export Documents Serializers
"""

from rest_framework import serializers
from .models import ExportDocument, ExportChecklist


class ExportDocumentSerializer(serializers.ModelSerializer):
    """Serializer for export documents"""
    
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    is_expired = serializers.BooleanField(read_only=True)
    
    buyer_name = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportDocument
        fields = [
            'id',
            'vehicle',
            'vehicle_info',
            'buyer',
            'buyer_name',
            'document_type',
            'document_type_display',
            'file',
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'expires_at',
            'is_expired',
            'notes',
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_expired']
    
    def get_buyer_name(self, obj):
        """Get buyer's full name"""
        if obj.buyer:
            return obj.buyer.get_full_name() or obj.buyer.username
        return None
    
    def get_vehicle_info(self, obj):
        """Get vehicle summary"""
        vehicle = obj.vehicle
        return {
            'id': vehicle.id,
            'year': vehicle.year,
            'make': vehicle.make,
            'model': vehicle.model,
            'vin': vehicle.vin,
        }


class ExportChecklistSerializer(serializers.ModelSerializer):
    """Serializer for export readiness checklist"""
    
    completion_percentage = serializers.SerializerMethodField()
    buyer_name = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportChecklist
        fields = [
            'id',
            'vehicle',
            'vehicle_info',
            'buyer',
            'buyer_name',
            'title_verified',
            'lien_checked',
            'insurance_confirmed',
            'payment_cleared',
            'inspection_completed',
            'cbsa_form_generated',
            'title_guide_provided',
            'export_ready',
            'completion_percentage',
            'created_at',
            'updated_at',
            'completed_at',
            'notes',
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_at', 'export_ready']
    
    def get_completion_percentage(self, obj):
        """Get completion percentage"""
        return obj.get_completion_percentage()
    
    def get_buyer_name(self, obj):
        """Get buyer's full name"""
        if obj.buyer:
            return obj.buyer.get_full_name() or obj.buyer.username
        return None
    
    def get_vehicle_info(self, obj):
        """Get vehicle summary"""
        vehicle = obj.vehicle
        return {
            'id': vehicle.id,
            'year': vehicle.year,
            'make': vehicle.make,
            'model': vehicle.model,
            'vin': vehicle.vin,
        }
    
    def update(self, instance, validated_data):
        """Update checklist and auto-check completion"""
        instance = super().update(instance, validated_data)
        instance.check_completion()
        return instance
