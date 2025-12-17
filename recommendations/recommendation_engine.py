"""
Recommendation engine for vehicle suggestions.
Uses content-based filtering and collaborative filtering.
"""
from django.db.models import Count, Q
from vehicles.models import Vehicle
from .models import ViewHistory


def get_similar_vehicles(reference_vehicle, limit=10):
    """
    Content-based filtering: Find vehicles similar to the reference vehicle.
    Similarity is based on:
    - Same make/model (highest priority)
    - Similar year (+/- 3 years)
    - Similar price (+/- 20%)
    - Same condition
    """
    results = []
    
    # Get all vehicles except the reference
    all_vehicles = Vehicle.objects.exclude(id=reference_vehicle.id)
    
    # Calculate similarity scores
    for vehicle in all_vehicles[:50]:  # Limit to 50 for performance
        score = 0
        reasons = []
        
        # Same make (30 points)
        if vehicle.make == reference_vehicle.make:
            score += 30
            reasons.append('Same make')
            
            # Same model (additional 25 points)
            if vehicle.model == reference_vehicle.model:
                score += 25
                reasons.append('Same model')
        
        # Similar year (up to 20 points)
        year_diff = abs(vehicle.year - reference_vehicle.year)
        if year_diff == 0:
            score += 20
            reasons.append('Same year')
        elif year_diff <= 1:
            score += 15
            reasons.append('Similar year')
        elif year_diff <= 2:
            score += 10
            reasons.append('Similar year')
        elif year_diff <= 3:
            score += 5
        
        # Similar price (up to 15 points)
        try:
            ref_price = float(reference_vehicle.price_cad)
            veh_price = float(vehicle.price_cad)
            price_diff_percentage = abs((veh_price - ref_price) / ref_price) * 100
            
            if price_diff_percentage <= 10:
                score += 15
                reasons.append('Similar price')
            elif price_diff_percentage <= 20:
                score += 10
                reasons.append('Comparable price')
            elif price_diff_percentage <= 30:
                score += 5
        except (ValueError, ZeroDivisionError):
            pass
        
        # Same condition (10 points)
        if vehicle.condition == reference_vehicle.condition:
            score += 10
            reasons.append('Same condition')
        
        # Only include vehicles with score > 20
        if score > 20:
            results.append({
                'vehicle': vehicle,
                'similarity_score': score,
                'reason': ', '.join(reasons) if reasons else 'Similar specifications'
            })
    
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return results[:limit]


def get_collaborative_recommendations(reference_vehicle, limit=10):
    """
    Collaborative filtering: Find vehicles viewed by users who also viewed the reference vehicle.
    Algorithm: "Users who viewed this also viewed..."
    """
    # Get users who viewed the reference vehicle
    user_ids = ViewHistory.objects.filter(
        vehicle=reference_vehicle,
        user__isnull=False
    ).values_list('user_id', flat=True).distinct()
    
    session_ids = ViewHistory.objects.filter(
        vehicle=reference_vehicle,
        session_id__isnull=False
    ).values_list('session_id', flat=True).distinct()
    
    # Get vehicles viewed by these users (excluding the reference)
    related_views = ViewHistory.objects.filter(
        Q(user_id__in=user_ids) | Q(session_id__in=session_ids)
    ).exclude(
        vehicle=reference_vehicle
    ).values('vehicle').annotate(
        view_count=Count('id')
    ).order_by('-view_count')
    
    results = []
    
    for view_data in related_views[:limit]:
        vehicle_id = view_data['vehicle']
        view_count = view_data['view_count']
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            
            # Calculate score based on view count (normalize to 0-100)
            # More views = higher score
            score = min(view_count * 10, 100)
            
            results.append({
                'vehicle': vehicle,
                'similarity_score': score,
                'reason': f'Viewed by {view_count} users who also viewed this vehicle'
            })
        except Vehicle.DoesNotExist:
            continue
    
    return results


def get_hybrid_recommendations(reference_vehicle, limit=10):
    """
    Hybrid approach: Combine content-based and collaborative filtering.
    """
    # Get both types of recommendations
    similar_vehicles = get_similar_vehicles(reference_vehicle, limit=limit * 2)
    collaborative_vehicles = get_collaborative_recommendations(reference_vehicle, limit=limit * 2)
    
    # Combine results with weighted scores
    combined = {}
    
    # Add content-based results (weight: 0.6)
    for item in similar_vehicles:
        vehicle_id = item['vehicle'].id
        combined[vehicle_id] = {
            'vehicle': item['vehicle'],
            'similarity_score': item['similarity_score'] * 0.6,
            'reason': item['reason']
        }
    
    # Add collaborative results (weight: 0.4)
    for item in collaborative_vehicles:
        vehicle_id = item['vehicle'].id
        if vehicle_id in combined:
            # Vehicle appears in both - boost score
            combined[vehicle_id]['similarity_score'] += item['similarity_score'] * 0.4
            combined[vehicle_id]['reason'] += f" + {item['reason']}"
        else:
            combined[vehicle_id] = {
                'vehicle': item['vehicle'],
                'similarity_score': item['similarity_score'] * 0.4,
                'reason': item['reason']
            }
    
    # Sort by combined score
    results = sorted(
        combined.values(),
        key=lambda x: x['similarity_score'],
        reverse=True
    )
    
    return results[:limit]
