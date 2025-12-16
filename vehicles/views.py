from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, VehicleImage
from .serializers import VehicleSerializer, VehicleListSerializer, VehicleImageSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'make', 'year', 'condition', 'dealer']
    search_fields = ['make', 'model', 'vin', 'location']
    ordering_fields = ['price_cad', 'year', 'mileage', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleListSerializer
        return VehicleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all vehicles
        if user.is_admin():
            return queryset
        
        # Dealers see only their vehicles
        if user.is_dealer():
            queryset = queryset.filter(dealer=user)
        # Buyers see only available vehicles
        elif user.is_buyer():
            queryset = queryset.filter(status='available')
        
        return queryset
    
    def perform_create(self, serializer):
        # Set dealer to current user if they're a dealer
        if self.request.user.is_dealer():
            serializer.save(dealer=self.request.user)
        elif self.request.user.is_admin() and 'dealer' in self.request.data:
            serializer.save()
        else:
            serializer.save(dealer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload additional images for a vehicle"""
        vehicle = self.get_object()
        image_file = request.FILES.get('image')
        
        if not image_file:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create vehicle image
        vehicle_image = VehicleImage.objects.create(
            vehicle=vehicle,
            image=image_file,
            order=vehicle.images.count()
        )
        
        serializer = VehicleImageSerializer(vehicle_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """Delete a vehicle image"""
        vehicle = self.get_object()
        try:
            vehicle_image = vehicle.images.get(id=image_id)
            vehicle_image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VehicleImage.DoesNotExist:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
