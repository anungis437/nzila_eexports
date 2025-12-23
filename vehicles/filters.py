"""
Custom Django filters for vehicle proximity search.

Provides filtering vehicles by distance from a user's location.

Phase 2: Proximity Search & Travel Radius
Author: Django Development Team
Date: December 2025
"""

import django_filters
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from .models import Vehicle
from utils.distance_calculator import is_within_radius
import logging

logger = logging.getLogger(__name__)


class VehicleProximityFilter(django_filters.FilterSet):
    """
    Filter vehicles by proximity to user location.
    
    Query parameters:
        - user_latitude: User's latitude coordinate
        - user_longitude: User's longitude coordinate
        - radius_km: Search radius in kilometers (default: 100)
        - min_price: Minimum price in CAD
        - max_price: Maximum price in CAD
        - min_year: Minimum vehicle year
        - max_year: Maximum vehicle year
        - min_mileage: Minimum mileage in km
        - max_mileage: Maximum mileage in km
    
    Example API call:
        GET /api/vehicles/?user_latitude=43.651070&user_longitude=-79.347015&radius_km=50
    """
    
    # Standard filters
    min_price = django_filters.NumberFilter(field_name='price_cad', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_cad', lookup_expr='lte')
    min_year = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    max_year = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    min_mileage = django_filters.NumberFilter(field_name='mileage', lookup_expr='gte')
    max_mileage = django_filters.NumberFilter(field_name='mileage', lookup_expr='lte')
    
    class Meta:
        model = Vehicle
        fields = {
            'status': ['exact'],
            'make': ['exact', 'icontains'],
            'model': ['icontains'],
            'year': ['exact', 'gte', 'lte'],
            'condition': ['exact'],
            'fuel_type': ['exact'],
            'transmission': ['exact'],
            'engine_type': ['exact'],
            'drivetrain': ['exact'],
            'price_cad': ['gte', 'lte'],
            'mileage': ['gte', 'lte'],
        }
    
    def filter_queryset(self, queryset):
        """
        Apply proximity filtering if user location is provided.
        """
        queryset = super().filter_queryset(queryset)
        
        # Get proximity search parameters
        user_lat = self.request.GET.get('user_latitude')
        user_lon = self.request.GET.get('user_longitude')
        radius_km = self.request.GET.get('radius_km', 100)
        
        # If no user location provided, return all results
        if not user_lat or not user_lon:
            return queryset
        
        try:
            user_lat = Decimal(user_lat)
            user_lon = Decimal(user_lon)
            radius_km = float(radius_km)
        except (ValueError, InvalidOperation) as e:
            logger.warning(f"Invalid proximity search parameters: {e}")
            return queryset
        
        # Filter out vehicles without coordinates
        queryset = queryset.exclude(
            Q(latitude__isnull=True) | Q(longitude__isnull=True)
        )
        
        # Apply proximity filter
        nearby_vehicle_ids = []
        
        for vehicle in queryset:
            if is_within_radius(
                user_lat, user_lon,
                vehicle.latitude, vehicle.longitude,
                radius_km
            ):
                nearby_vehicle_ids.append(vehicle.id)
        
        # Filter to only nearby vehicles
        queryset = queryset.filter(id__in=nearby_vehicle_ids)
        
        logger.info(
            f"Proximity search: Found {len(nearby_vehicle_ids)} vehicles "
            f"within {radius_km}km of ({user_lat}, {user_lon})"
        )
        
        return queryset
