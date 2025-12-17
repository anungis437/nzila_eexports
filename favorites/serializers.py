from rest_framework import serializers
from .models import Favorite
from vehicles.serializers import VehicleSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'vehicle', 'vehicle_details', 'created_at']
        read_only_fields = ['user', 'created_at']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['vehicle']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
