from rest_framework import serializers
from .models import Shipment, ShipmentUpdate
from deals.serializers import DealSerializer


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentUpdate
        fields = ['id', 'location', 'status', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ShipmentSerializer(serializers.ModelSerializer):
    updates = ShipmentUpdateSerializer(many=True, read_only=True)
    deal_id = serializers.IntegerField(source='deal.id', read_only=True)
    
    class Meta:
        model = Shipment
        fields = ['id', 'deal', 'deal_id', 'tracking_number', 'shipping_company',
                  'origin_port', 'destination_port', 'destination_country',
                  'status', 'estimated_departure', 'actual_departure',
                  'estimated_arrival', 'actual_arrival', 'notes', 'updates',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
