from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Vehicle, VehicleImage, Offer
from .serializers import (
    VehicleSerializer, VehicleListSerializer, VehicleImageSerializer,
    OfferSerializer, OfferCreateSerializer
)


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
            media_type='image',
            order=vehicle.images.count()
        )
        
        serializer = VehicleImageSerializer(vehicle_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def upload_video(self, request, pk=None):
        """Upload video walkaround for a vehicle"""
        vehicle = self.get_object()
        
        serializer = VehicleImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                vehicle=vehicle,
                media_type='video',
                order=vehicle.images.filter(media_type='video').count()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def videos(self, request, pk=None):
        """Get all video walkarounds for a vehicle"""
        vehicle = self.get_object()
        videos = vehicle.images.filter(media_type='video').order_by('order')
        serializer = VehicleImageSerializer(videos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """Delete a vehicle image or video"""
        vehicle = self.get_object()
        try:
            vehicle_image = vehicle.images.get(id=image_id)
            vehicle_image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VehicleImage.DoesNotExist:
            return Response(
                {'error': 'Media not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for vehicle offers"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'vehicle']
    ordering_fields = ['created_at', 'offer_amount_cad']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OfferCreateSerializer
        return OfferSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Offer.objects.select_related('vehicle', 'buyer')
        
        # Admins see all offers
        if user.role == 'admin':
            return queryset
        
        # Dealers see offers on their vehicles
        elif user.role == 'dealer':
            return queryset.filter(vehicle__dealer=user)
        
        # Buyers see only their own offers
        elif user.role == 'buyer':
            return queryset.filter(buyer=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Set buyer to current user when creating offer"""
        serializer.save(buyer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept an offer (dealers only)"""
        offer = self.get_object()
        
        if request.user != offer.vehicle.dealer and request.user.role != 'admin':
            return Response(
                {'error': 'Only the vehicle dealer can accept offers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if offer.status != 'pending':
            return Response(
                {'error': 'Can only accept pending offers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = 'accepted'
        offer.responded_at = timezone.now()
        offer.save()
        
        serializer = self.get_serializer(offer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an offer (dealers only)"""
        offer = self.get_object()
        
        if request.user != offer.vehicle.dealer and request.user.role != 'admin':
            return Response(
                {'error': 'Only the vehicle dealer can reject offers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if offer.status not in ['pending', 'countered']:
            return Response(
                {'error': 'Can only reject pending or countered offers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = 'rejected'
        offer.responded_at = timezone.now()
        offer.dealer_notes = request.data.get('dealer_notes', '')
        offer.save()
        
        serializer = self.get_serializer(offer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def counter(self, request, pk=None):
        """Make a counter offer (dealers only)"""
        offer = self.get_object()
        
        if request.user != offer.vehicle.dealer and request.user.role != 'admin':
            return Response(
                {'error': 'Only the vehicle dealer can counter offers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if offer.status != 'pending':
            return Response(
                {'error': 'Can only counter pending offers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        counter_amount = request.data.get('counter_amount_cad')
        if not counter_amount:
            return Response(
                {'error': 'Counter amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = 'countered'
        offer.counter_amount_cad = counter_amount
        offer.counter_message = request.data.get('counter_message', '')
        offer.responded_at = timezone.now()
        offer.save()
        
        serializer = self.get_serializer(offer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """Withdraw an offer (buyers only)"""
        offer = self.get_object()
        
        if request.user != offer.buyer:
            return Response(
                {'error': 'Only the offer creator can withdraw it'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if offer.status not in ['pending', 'countered']:
            return Response(
                {'error': 'Can only withdraw pending or countered offers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = 'withdrawn'
        offer.save()
        
        serializer = self.get_serializer(offer)
        return Response(serializer.data)
