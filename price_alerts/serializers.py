from rest_framework import serializers
from .models import PriceHistory
from vehicles.serializers import VehicleSerializer


class PriceHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for price history records.
    """
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    is_price_drop = serializers.BooleanField(read_only=True)
    amount_saved = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = PriceHistory
        fields = [
            'id',
            'vehicle',
            'vehicle_details',
            'old_price',
            'new_price',
            'price_difference',
            'percentage_change',
            'changed_at',
            'is_price_drop',
            'amount_saved',
        ]
        read_only_fields = [
            'id',
            'changed_at',
            'price_difference',
            'percentage_change',
        ]


class PriceHistorySummarySerializer(serializers.Serializer):
    """
    Lightweight serializer for price history summaries (used in vehicle lists).
    """
    has_price_history = serializers.BooleanField()
    latest_price_change = serializers.DecimalField(max_digits=10, decimal_places=2)
    latest_percentage_change = serializers.DecimalField(max_digits=5, decimal_places=2)
    is_recent_drop = serializers.BooleanField()
    days_since_change = serializers.IntegerField()
