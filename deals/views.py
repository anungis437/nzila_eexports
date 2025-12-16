from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
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
    filterset_fields = ['status', 'dealer', 'broker', 'payment_status']
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
    
    def perform_create(self, serializer):
        # Auto-set dealer from the vehicle
        vehicle = serializer.validated_data.get('vehicle')
        if vehicle and not serializer.validated_data.get('dealer'):
            serializer.save(dealer=vehicle.dealer)
        else:
            serializer.save()


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
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share document via email"""
        document = self.get_object()
        email = request.data.get('email')
        message = request.data.get('message', '')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send email with document link
        subject = f'Nzila Export Hub - Document Shared: {document.get_document_type_display()}'
        email_message = f"""
        A document has been shared with you from Nzila Export Hub.
        
        Document Type: {document.get_document_type_display()}
        Deal ID: {document.deal.id}
        
        {message}
        
        You can access the document through your Nzila Export Hub account.
        
        Best regards,
        Nzila Export Hub Team
        """
        
        try:
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'success': True, 'message': 'Document shared successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
