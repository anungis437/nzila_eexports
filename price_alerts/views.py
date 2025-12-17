from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import PriceHistory
from .serializers import PriceHistorySerializer
from vehicles.models import Vehicle


class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing price history.
    Users can only view price history for vehicles.
    """
    queryset = PriceHistory.objects.select_related('vehicle').all()
    serializer_class = PriceHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter by vehicle_id query parameter.
        """
        queryset = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle_id')
        
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent_drops(self, request):
        """
        Get recent price drops for favorited vehicles.
        Returns price drops from the last 7 days for vehicles the user has favorited.
        """
        # Get user's favorited vehicles
        from favorites.models import Favorite
        favorited_vehicle_ids = Favorite.objects.filter(
            user=request.user
        ).values_list('vehicle_id', flat=True)
        
        # Get price drops in last 7 days for favorited vehicles
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_drops = PriceHistory.objects.filter(
            vehicle_id__in=favorited_vehicle_ids,
            changed_at__gte=seven_days_ago,
            price_difference__lt=0  # Price drops only
        ).select_related('vehicle').order_by('-changed_at')
        
        serializer = self.get_serializer(recent_drops, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vehicle_history(self, request):
        """
        Get complete price history for a specific vehicle.
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
        
        history = PriceHistory.objects.filter(
            vehicle=vehicle
        ).order_by('-changed_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response({
            'vehicle_id': vehicle.id,
            'current_price': vehicle.price,
            'history': serializer.data,
            'total_changes': history.count(),
        })
