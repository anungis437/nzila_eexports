from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lead, Deal, Document
from .serializers import LeadSerializer, DealSerializer, DocumentSerializer


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'broker']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Buyers see only their leads
        if user.is_buyer():
            queryset = queryset.filter(buyer=user)
        # Dealers see leads for their vehicles
        elif user.is_dealer():
            queryset = queryset.filter(vehicle__dealer=user)
        # Brokers see their brokered leads
        elif user.is_broker():
            queryset = queryset.filter(broker=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # Set buyer to current user if they're a buyer
        if self.request.user.is_buyer():
            serializer.save(buyer=self.request.user)
        else:
            serializer.save()


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'dealer', 'broker']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Buyers see only their deals
        if user.is_buyer():
            queryset = queryset.filter(buyer=user)
        # Dealers see their deals
        elif user.is_dealer():
            queryset = queryset.filter(dealer=user)
        # Brokers see their brokered deals
        elif user.is_broker():
            queryset = queryset.filter(broker=user)
        
        return queryset


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['deal', 'document_type', 'status']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter documents based on user's deals
        if user.is_buyer():
            queryset = queryset.filter(deal__buyer=user)
        elif user.is_dealer():
            queryset = queryset.filter(deal__dealer=user)
        elif user.is_broker():
            queryset = queryset.filter(deal__broker=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
