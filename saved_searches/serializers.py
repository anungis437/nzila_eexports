from rest_framework import serializers
from .models import SavedSearch


class SavedSearchSerializer(serializers.ModelSerializer):
    """Serializer for SavedSearch model with search criteria display"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    criteria_display = serializers.CharField(source='get_search_criteria_display', read_only=True)
    
    class Meta:
        model = SavedSearch
        fields = [
            'id',
            'user',
            'user_email',
            'name',
            'make',
            'model',
            'year_min',
            'year_max',
            'price_min',
            'price_max',
            'condition',
            'mileage_max',
            'email_notifications',
            'notification_frequency',
            'is_active',
            'match_count',
            'criteria_display',
            'created_at',
            'updated_at',
            'last_notified_at',
        ]
        read_only_fields = ['user', 'match_count', 'last_notified_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate year and price ranges"""
        year_min = data.get('year_min')
        year_max = data.get('year_max')
        if year_min and year_max and year_min > year_max:
            raise serializers.ValidationError({
                'year_max': 'Maximum year must be greater than or equal to minimum year'
            })
        
        price_min = data.get('price_min')
        price_max = data.get('price_max')
        if price_min and price_max and price_min > price_max:
            raise serializers.ValidationError({
                'price_max': 'Maximum price must be greater than or equal to minimum price'
            })
        
        return data


class SavedSearchCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating saved searches"""
    
    class Meta:
        model = SavedSearch
        fields = [
            'name',
            'make',
            'model',
            'year_min',
            'year_max',
            'price_min',
            'price_max',
            'condition',
            'mileage_max',
            'email_notifications',
            'notification_frequency',
        ]
    
    def validate(self, data):
        """Validate year and price ranges"""
        year_min = data.get('year_min')
        year_max = data.get('year_max')
        if year_min and year_max and year_min > year_max:
            raise serializers.ValidationError({
                'year_max': 'Maximum year must be greater than or equal to minimum year'
            })
        
        price_min = data.get('price_min')
        price_max = data.get('price_max')
        if price_min and price_max and price_min > price_max:
            raise serializers.ValidationError({
                'price_max': 'Maximum price must be greater than or equal to minimum price'
            })
        
        # Require at least one search criterion
        if not any([
            data.get('make'),
            data.get('model'),
            data.get('year_min'),
            data.get('year_max'),
            data.get('price_min'),
            data.get('price_max'),
            data.get('condition'),
            data.get('mileage_max'),
        ]):
            raise serializers.ValidationError(
                'At least one search criterion must be specified'
            )
        
        return data
