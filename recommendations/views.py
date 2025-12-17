from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Q
from vehicles.models import Vehicle
from .models import ViewHistory
from .serializers import SimilarVehicleSerializer
from .recommendation_engine import get_similar_vehicles, get_collaborative_recommendations


class RecommendationViewSet(viewsets.ViewSet):
    """
    ViewSet for vehicle recommendations.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def similar(self, request):
        """
        Get similar vehicles based on a reference vehicle.
        Required query param: vehicle_id
        """
        vehicle_id = request.query_params.get('vehicle_id')
        
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response(
                {'error': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get similar vehicles using content-based filtering
        similar_vehicles = get_similar_vehicles(vehicle, limit=10)
        
        serializer = SimilarVehicleSerializer(similar_vehicles, many=True)
        return Response({
            'reference_vehicle': {
                'id': vehicle.id,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'price': vehicle.price_cad,
            },
            'similar_vehicles': serializer.data,
            'count': len(similar_vehicles),
        })
    
    @action(detail=False, methods=['get'])
    def collaborative(self, request):
        """
        Get recommendations based on what other users viewed.
        Optional query param: vehicle_id (if provided, returns 'users who viewed this also viewed...')
        """
        vehicle_id = request.query_params.get('vehicle_id')
        
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
            except Vehicle.DoesNotExist:
                return Response(
                    {'error': 'Vehicle not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get collaborative recommendations
            recommendations = get_collaborative_recommendations(vehicle, limit=10)
            
            serializer = SimilarVehicleSerializer(recommendations, many=True)
            return Response({
                'reference_vehicle': {
                    'id': vehicle.id,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                },
                'recommendations': serializer.data,
                'count': len(recommendations),
            })
        
        # If no vehicle_id, return popular/trending vehicles
        popular_vehicles = Vehicle.objects.annotate(
            view_count=Count('view_records')
        ).order_by('-view_count')[:10]
        
        from vehicles.serializers import VehicleSerializer
        serializer = VehicleSerializer(popular_vehicles, many=True)
        return Response({
            'popular_vehicles': serializer.data,
            'count': popular_vehicles.count(),
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def track_view(request):
    """
    Track a vehicle view for recommendation algorithms.
    Expects: vehicle_id in request body
    """
    vehicle_id = request.data.get('vehicle_id')
    
    if not vehicle_id:
        return Response(
            {'error': 'vehicle_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Track view
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key if not user else None
    
    ViewHistory.objects.create(
        user=user,
        session_id=session_id,
        vehicle=vehicle
    )
    
    return Response({'success': True}, status=status.HTTP_201_CREATED)
