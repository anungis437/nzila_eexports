from rest_framework import serializers
from .models import Shipment, ShipmentUpdate
from vehicles.models import Vehicle


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentUpdate
        fields = ['id', 'location', 'status', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ShipmentSerializer(serializers.ModelSerializer):
    updates = ShipmentUpdateSerializer(many=True, read_only=True)
    deal_id = serializers.IntegerField(source='deal.id', read_only=True)
    vehicle_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipment
        fields = ['id', 'deal', 'deal_id', 'tracking_number', 'shipping_company',
                  'origin_port', 'destination_port', 'destination_country',
                  'status', 'estimated_departure', 'actual_departure',
                  'estimated_arrival', 'actual_arrival', 'notes', 'updates',
                  'vehicle_details', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
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
