from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shipment, ShipmentUpdate
from .serializers import ShipmentSerializer, ShipmentUpdateSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
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
