from rest_framework import serializers
from .models import Vehicle, VehicleImage


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'caption', 'uploaded_at']


class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)
    dealer_name = serializers.CharField(source='dealer.username', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'dealer', 'dealer_name', 'make', 'model', 'year', 'vin',
                  'condition', 'mileage', 'color', 'fuel_type', 'transmission',
                  'price_cad', 'status', 'description', 'location', 'main_image',
                  'images', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleListSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.username', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'vin', 'condition', 'mileage',
                  'price_cad', 'status', 'location', 'main_image', 'dealer_name']
