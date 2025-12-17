from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteCreateSerializer
from vehicles.models import Vehicle


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user favorites/watchlist
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('vehicle', 'vehicle__dealer')

    def get_serializer_class(self):
        if self.action == 'create':
            return FavoriteCreateSerializer
        return FavoriteSerializer

    def create(self, request, *args, **kwargs):
        """Add vehicle to favorites"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if already favorited
        vehicle_id = serializer.validated_data['vehicle'].id
        if Favorite.objects.filter(user=request.user, vehicle_id=vehicle_id).exists():
            return Response(
                {'detail': 'Vehicle already in favorites'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['delete'], url_path='vehicle/(?P<vehicle_id>[^/.]+)')
    def remove_by_vehicle(self, request, vehicle_id=None):
        """Remove vehicle from favorites by vehicle ID"""
        favorite = get_object_or_404(Favorite, user=request.user, vehicle_id=vehicle_id)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='check/(?P<vehicle_id>[^/.]+)')
    def check(self, request, vehicle_id=None):
        """Check if vehicle is favorited"""
        is_favorited = Favorite.objects.filter(user=request.user, vehicle_id=vehicle_id).exists()
        return Response({'is_favorited': is_favorited})

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle favorite status for a vehicle"""
        vehicle_id = request.data.get('vehicle')
        if not vehicle_id:
            return Response(
                {'detail': 'vehicle field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            vehicle=vehicle
        )

        if not created:
            favorite.delete()
            return Response({'is_favorited': False}, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(favorite)
        return Response({
            'is_favorited': True,
            'favorite': serializer.data
        }, status=status.HTTP_201_CREATED)
