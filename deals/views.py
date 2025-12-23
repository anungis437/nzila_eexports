from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from .models import Lead, Deal, Document
from .financial_models import DealFinancialTerms, FinancingOption
from .serializers import (
    LeadSerializer, DealSerializer, DocumentSerializer, BuyerDealSerializer,
    DealFinancialTermsSerializer, PaymentMilestoneSerializer,
    FinancingOptionSerializer, ProcessPaymentSerializer, ApplyFinancingSerializer
)
from payments.models import Payment


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
    filterset_fields = ['status', 'dealer', 'broker', 'payment_status', 'payment_method']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use simplified serializer for buyers"""
        if self.request.user.is_buyer():
            return BuyerDealSerializer
        return DealSerializer
    
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
    
    @action(detail=True, methods=['get'])
    def financial_terms(self, request, pk=None):
        """Get financial terms for a deal."""
        deal = self.get_object()
        
        if not hasattr(deal, 'financial_terms'):
            return Response(
                {'error': 'Financial terms not configured for this deal'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DealFinancialTermsSerializer(deal.financial_terms)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_schedule(self, request, pk=None):
        """Get payment schedule (milestones) for a deal."""
        deal = self.get_object()
        
        if not hasattr(deal, 'financial_terms'):
            return Response(
                {'error': 'Financial terms not configured for this deal'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        milestones = deal.financial_terms.milestones.all()
        serializer = PaymentMilestoneSerializer(milestones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def financing(self, request, pk=None):
        """Get financing option for a deal."""
        deal = self.get_object()
        
        if not hasattr(deal, 'financing'):
            return Response(
                {'error': 'Financing not configured for this deal'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FinancingOptionSerializer(deal.financing)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process a payment for a deal."""
        deal = self.get_object()
        serializer = ProcessPaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not hasattr(deal, 'financial_terms'):
            return Response(
                {'error': 'Financial terms not configured for this deal'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record
        payment = Payment.objects.create(
            deal=deal,
            user=request.user,
            amount=serializer.validated_data['amount'],
            currency=deal.financial_terms.currency,
            amount_in_usd=serializer.validated_data['amount'],  # Simplified for testing
            payment_method=None,  # Can be set later with actual PaymentMethod instance
            description=serializer.validated_data.get('notes', ''),
            status='succeeded'
        )
        
        # Process payment through deal
        deal.process_payment(payment)
        
        # Return updated payment summary
        return Response({
            'success': True,
            'payment_id': payment.id,
            'payment_summary': deal.get_payment_status_summary()
        })
    
    @action(detail=True, methods=['post'])
    def apply_financing(self, request, pk=None):
        """Apply financing to a deal."""
        deal = self.get_object()
        serializer = ApplyFinancingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(deal, 'financing'):
            return Response(
                {'error': 'Financing already exists for this deal'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Setup financing
        financing = deal.setup_financing(
            financed_amount=serializer.validated_data['financed_amount'],
            down_payment=serializer.validated_data['down_payment'],
            interest_rate=serializer.validated_data['interest_rate'],
            term_months=serializer.validated_data['term_months'],
            lender_name=serializer.validated_data.get('lender_name', '')
        )
        
        # Return financing details
        response_serializer = FinancingOptionSerializer(financing)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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
