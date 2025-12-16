from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shipment, ShipmentUpdate
from .serializers import ShipmentSerializer, ShipmentUpdateSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all().select_related('deal', 'deal__vehicle').prefetch_related('updates')
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'destination_country']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter shipments based on user's deals
        if user.is_buyer():
            queryset = queryset.filter(deal__buyer=user)
        elif user.is_dealer():
            queryset = queryset.filter(deal__dealer=user)
        elif user.is_broker():
            queryset = queryset.filter(deal__broker=user)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        """Public tracking endpoint for buyers"""
        shipment = self.get_object()
        serializer = self.get_serializer(shipment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_update(self, request, pk=None):
        """Add a tracking update to the shipment"""
        shipment = self.get_object()
        
        # Create the shipment update
        serializer = ShipmentUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shipment=shipment)
            
            # Return the updated shipment with all updates
            shipment_serializer = self.get_serializer(shipment)
            return Response(shipment_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def updates(self, request, pk=None):
        """Get all tracking updates for a shipment"""
        shipment = self.get_object()
        updates = shipment.updates.all().order_by('-created_at')
        serializer = ShipmentUpdateSerializer(updates, many=True)
        return Response(serializer.data)
