from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, VehicleImage
from .serializers import VehicleSerializer, VehicleListSerializer


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
        else:
            serializer.save()
