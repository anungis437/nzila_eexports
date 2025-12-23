"""
Distance calculation utilities for proximity search.

This module provides functions for calculating distances between geographic coordinates
using the Haversine formula. Used for proximity search and filtering vehicles by distance.

Phase 2: Proximity Search & Travel Radius
Author: Django Development Team
Date: December 2025
"""

from decimal import Decimal
from math import radians, cos, sin, asin, sqrt
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def haversine_distance(
    lat1: Decimal, lon1: Decimal,
    lat2: Decimal, lon2: Decimal
) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Uses the Haversine formula to calculate distance in kilometers.
    
    Args:
        lat1: Latitude of first point (decimal degrees)
        lon1: Longitude of first point (decimal degrees)
        lat2: Latitude of second point (decimal degrees)
        lon2: Longitude of second point (decimal degrees)
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> # Toronto to Montreal
        >>> distance = haversine_distance(
        ...     Decimal('43.651070'), Decimal('-79.347015'),
        ...     Decimal('45.501690'), Decimal('-73.567253')
        ... )
        >>> print(f"{distance:.2f} km")
        504.08 km
    """
    # Convert decimal degrees to radians
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(
        radians,
        [float(lat1), float(lon1), float(lat2), float(lon2)]
    )
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def filter_by_distance(
    origin_lat: Decimal,
    origin_lon: Decimal,
    points: list[Tuple[Decimal, Decimal, any]],
    max_distance_km: float
) -> list[Tuple[Decimal, Decimal, any, float]]:
    """
    Filter a list of points by distance from an origin point.
    
    Args:
        origin_lat: Latitude of origin point
        origin_lon: Longitude of origin point
        points: List of tuples (lat, lon, data)
        max_distance_km: Maximum distance in kilometers
    
    Returns:
        List of tuples (lat, lon, data, distance_km) within radius, sorted by distance
    
    Example:
        >>> # Filter vehicles within 100km of Toronto
        >>> vehicles = [
        ...     (Decimal('43.7'), Decimal('-79.4'), {'vin': 'ABC123'}),
        ...     (Decimal('45.5'), Decimal('-73.6'), {'vin': 'XYZ789'}),
        ... ]
        >>> nearby = filter_by_distance(
        ...     Decimal('43.651070'), Decimal('-79.347015'),
        ...     vehicles, 100
        ... )
        >>> for lat, lon, data, dist in nearby:
        ...     print(f"{data['vin']}: {dist:.2f} km")
        ABC123: 7.24 km
    """
    results = []
    
    for lat, lon, data in points:
        try:
            distance = haversine_distance(origin_lat, origin_lon, lat, lon)
            
            if distance <= max_distance_km:
                results.append((lat, lon, data, distance))
        
        except (ValueError, TypeError) as e:
            logger.warning(f"Error calculating distance for point ({lat}, {lon}): {e}")
            continue
    
    # Sort by distance (closest first)
    results.sort(key=lambda x: x[3])
    
    return results


def is_within_radius(
    origin_lat: Decimal,
    origin_lon: Decimal,
    target_lat: Decimal,
    target_lon: Decimal,
    radius_km: float
) -> bool:
    """
    Check if a target point is within a given radius of an origin point.
    
    Args:
        origin_lat: Latitude of origin point
        origin_lon: Longitude of origin point
        target_lat: Latitude of target point
        target_lon: Longitude of target point
        radius_km: Radius in kilometers
    
    Returns:
        True if target is within radius, False otherwise
    
    Example:
        >>> # Check if Montreal is within 600km of Toronto
        >>> is_within_radius(
        ...     Decimal('43.651070'), Decimal('-79.347015'),
        ...     Decimal('45.501690'), Decimal('-73.567253'),
        ...     600
        ... )
        True
    """
    try:
        distance = haversine_distance(origin_lat, origin_lon, target_lat, target_lon)
        return distance <= radius_km
    except (ValueError, TypeError) as e:
        logger.error(f"Error checking radius for points: {e}")
        return False


def get_distance_display(distance_km: float) -> str:
    """
    Format distance for user-friendly display.
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        Formatted distance string
    
    Example:
        >>> get_distance_display(0.5)
        '500 m'
        >>> get_distance_display(45.7)
        '46 km'
        >>> get_distance_display(523.4)
        '523 km'
    """
    if distance_km < 1:
        # Show in meters for distances under 1 km
        return f"{int(distance_km * 1000)} m"
    elif distance_km < 10:
        # Show one decimal place for distances under 10 km
        return f"{distance_km:.1f} km"
    else:
        # Show integer for larger distances
        return f"{int(distance_km)} km"
