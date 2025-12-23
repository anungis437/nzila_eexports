from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from decimal import Decimal, InvalidOperation
from .models import Vehicle, VehicleImage, Offer, VehicleInspectionSlot, InspectionAppointment
from .serializers import (
    VehicleSerializer, VehicleListSerializer, VehicleImageSerializer,
    OfferSerializer, OfferCreateSerializer,
    VehicleInspectionSlotSerializer, InspectionAppointmentSerializer,
    InspectionAppointmentCreateSerializer
)
from .filters import VehicleProximityFilter
from utils.distance_calculator import haversine_distance, get_distance_display


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VehicleProximityFilter  # Use custom proximity filter
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
    
    def list(self, request, *args, **kwargs):
        """
        Override list to add distance calculation and sorting for proximity search.
        """
        # Get proximity search parameters
        user_lat = request.GET.get('user_latitude')
        user_lon = request.GET.get('user_longitude')
        
        # Get the filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate distances and add to results
        if user_lat and user_lon:
            try:
                user_lat = Decimal(user_lat)
                user_lon = Decimal(user_lon)
                
                # Calculate distance for each vehicle
                vehicles_with_distance = []
                for vehicle in queryset:
                    if vehicle.latitude and vehicle.longitude:
                        distance_km = haversine_distance(
                            user_lat, user_lon,
                            vehicle.latitude, vehicle.longitude
                        )
                        vehicles_with_distance.append((vehicle, distance_km))
                    else:
                        # Vehicles without coordinates go to the end
                        vehicles_with_distance.append((vehicle, float('inf')))
                
                # Sort by distance (closest first)
                vehicles_with_distance.sort(key=lambda x: x[1])
                
                # Apply pagination
                page = self.paginate_queryset([v[0] for v in vehicles_with_distance])
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    response_data = serializer.data
                    
                    # Add distance to each vehicle
                    distance_map = {v[0].id: v[1] for v in vehicles_with_distance}
                    for item in response_data:
                        vehicle_id = item['id']
                        if vehicle_id in distance_map:
                            distance = distance_map[vehicle_id]
                            if distance != float('inf'):
                                item['distance_km'] = round(distance, 2)
                                item['distance_display'] = get_distance_display(distance)
                    
                    return self.get_paginated_response(response_data)
                
                serializer = self.get_serializer([v[0] for v in vehicles_with_distance], many=True)
                response_data = serializer.data
                
                # Add distance to each vehicle
                distance_map = {v[0].id: v[1] for v in vehicles_with_distance}
                for item in response_data:
                    vehicle_id = item['id']
                    if vehicle_id in distance_map:
                        distance = distance_map[vehicle_id]
                        if distance != float('inf'):
                            item['distance_km'] = round(distance, 2)
                            item['distance_display'] = get_distance_display(distance)
                
                return Response(response_data)
            
            except (ValueError, InvalidOperation):
                pass  # Fall through to normal list behavior
        
        # Normal list behavior (no proximity search)
        # Generate cache key based on user role and filters
        cache_key = f"vehicle_list_{request.user.role}_{request.user.id}_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Get fresh data
        response = super().list(request, *args, **kwargs)
        
        # Cache the response data
        cache_ttl = getattr(settings, 'CACHE_TTL', {}).get('vehicle_list', 900)
        cache.set(cache_key, response.data, cache_ttl)
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add caching for vehicle details"""
        vehicle_id = kwargs.get('pk')
        cache_key = f"vehicle_detail_{vehicle_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Get fresh data
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the response data
        cache_ttl = getattr(settings, 'CACHE_TTL', {}).get('vehicle_detail', 3600)
        cache.set(cache_key, response.data, cache_ttl)
        
        return response
    
    def perform_create(self, serializer):
        # Set dealer to current user if they're a dealer
        if self.request.user.is_dealer():
            serializer.save(dealer=self.request.user)
        elif self.request.user.is_admin() and 'dealer' in self.request.data:
            serializer.save()
        else:
            serializer.save(dealer=self.request.user)
        
        # Invalidate vehicle list cache for all users
        cache.delete_pattern("vehicle_list_*")
    
    def perform_update(self, serializer):
        """Override update to invalidate cache"""
        instance = serializer.save()
        
        # Invalidate both list and detail caches
        cache.delete_pattern("vehicle_list_*")
        cache.delete(f"vehicle_detail_{instance.id}")
    
    def perform_destroy(self, instance):
        """Override destroy to invalidate cache"""
        vehicle_id = instance.id
        instance.delete()
        
        # Invalidate both list and detail caches
        cache.delete_pattern("vehicle_list_*")
        cache.delete(f"vehicle_detail_{vehicle_id}")
    
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
    def inspection_slots(self, request, pk=None):
        """Get available inspection slots for a vehicle"""
        vehicle = self.get_object()
        slots = vehicle.inspection_slots.filter(
            is_available=True,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')
        
        serializer = VehicleInspectionSlotSerializer(slots, many=True)
        return Response(serializer.data)
    
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


class VehicleInspectionSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vehicle inspection slots.
    Dealers can create and manage slots, buyers can view available slots.
    """
    queryset = VehicleInspectionSlot.objects.all()
    serializer_class = VehicleInspectionSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vehicle', 'date', 'is_available']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all slots
        if user.is_admin():
            return queryset
        
        # Dealers see only their vehicles' slots
        if user.is_dealer():
            return queryset.filter(vehicle__dealer=user)
        
        # Buyers see only available future slots
        if user.is_buyer():
            return queryset.filter(
                is_available=True,
                date__gte=timezone.now().date()
            )
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Only dealers and admins can create inspection slots"""
        if not (self.request.user.is_dealer() or self.request.user.is_admin()):
            raise permissions.PermissionDenied("Only dealers can create inspection slots")
        
        serializer.save()


class InspectionAppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inspection appointments.
    Buyers can create appointments, dealers can view and manage them.
    """
    queryset = InspectionAppointment.objects.select_related(
        'buyer', 'slot', 'slot__vehicle', 'slot__vehicle__dealer'
    ).all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'slot__vehicle', 'interested_in_purchase']
    ordering_fields = ['created_at', 'slot__date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InspectionAppointmentCreateSerializer
        return InspectionAppointmentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all appointments
        if user.is_admin():
            return queryset
        
        # Dealers see only appointments for their vehicles
        if user.is_dealer():
            return queryset.filter(slot__vehicle__dealer=user)
        
        # Buyers see only their own appointments
        if user.is_buyer():
            return queryset.filter(buyer=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Auto-assign buyer when creating appointment"""
        if not self.request.user.is_buyer():
            raise permissions.PermissionDenied("Only buyers can book inspection appointments")
        
        serializer.save(buyer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment (dealers only)"""
        appointment = self.get_object()
        
        if request.user != appointment.dealer and not request.user.is_admin():
            return Response(
                {'error': 'Only the vehicle dealer can confirm appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status != 'pending':
            return Response(
                {'error': 'Can only confirm pending appointments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'confirmed'
        appointment.confirmed_at = timezone.now()
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed (dealers only)"""
        appointment = self.get_object()
        
        if request.user != appointment.dealer and not request.user.is_admin():
            return Response(
                {'error': 'Only the vehicle dealer can complete appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status != 'confirmed':
            return Response(
                {'error': 'Can only complete confirmed appointments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        
        # Update dealer notes if provided
        if 'dealer_notes' in request.data:
            appointment.dealer_notes = request.data['dealer_notes']
        
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        
        # Buyers can cancel their own appointments, dealers can cancel any
        if (request.user != appointment.buyer and 
            request.user != appointment.dealer and 
            not request.user.is_admin()):
            return Response(
                {'error': 'You do not have permission to cancel this appointment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status in ['completed', 'cancelled', 'no_show']:
            return Response(
                {'error': 'Cannot cancel this appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'cancelled'
        appointment.cancelled_at = timezone.now()
        
        # Save cancellation reason if provided
        if 'cancellation_reason' in request.data:
            if request.user == appointment.buyer:
                appointment.buyer_notes = f"{appointment.buyer_notes}\nCancellation: {request.data['cancellation_reason']}"
            else:
                appointment.dealer_notes = f"{appointment.dealer_notes}\nCancellation: {request.data['cancellation_reason']}"
        
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_feedback(self, request, pk=None):
        """Add feedback and ratings after inspection (buyers only)"""
        appointment = self.get_object()
        
        if request.user != appointment.buyer:
            return Response(
                {'error': 'Only the buyer can add feedback'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status != 'completed':
            return Response(
                {'error': 'Can only add feedback for completed appointments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update feedback fields
        appointment.inspection_feedback = request.data.get('inspection_feedback', appointment.inspection_feedback)
        appointment.vehicle_rating = request.data.get('vehicle_rating', appointment.vehicle_rating)
        appointment.dealer_rating = request.data.get('dealer_rating', appointment.dealer_rating)
        appointment.interested_in_purchase = request.data.get('interested_in_purchase', appointment.interested_in_purchase)
        
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
