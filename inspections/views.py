"""
PHASE 2 - Feature 6: Third-Party Inspection Integration

DRF views and viewsets for inspection APIs
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Avg
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
from decimal import Decimal

from .models import ThirdPartyInspector, InspectionReport, InspectorReview
from .serializers import (
    ThirdPartyInspectorListSerializer,
    ThirdPartyInspectorDetailSerializer,
    InspectionReportListSerializer,
    InspectionReportDetailSerializer,
    InspectionReportCreateSerializer,
    InspectionReportUpdateSerializer,
    InspectorReviewSerializer,
)


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


class ThirdPartyInspectorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for third-party inspector directory
    
    Endpoints:
    - GET /api/inspections/inspectors/ - List all inspectors
    - GET /api/inspections/inspectors/{id}/ - Get inspector details
    - POST /api/inspections/inspectors/ - Create inspector (admin)
    - PUT/PATCH /api/inspections/inspectors/{id}/ - Update inspector
    - DELETE /api/inspections/inspectors/{id}/ - Delete inspector (admin)
    - GET /api/inspections/inspectors/search_nearby/ - Search by location
    - GET /api/inspections/inspectors/{id}/stats/ - Get inspector statistics
    """
    
    queryset = ThirdPartyInspector.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company', 'name', 'city', 'specializations']
    ordering_fields = ['rating', 'total_inspections', 'inspection_fee', 'years_experience']
    ordering = ['-rating', '-total_inspections']
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'search_nearby':
            return ThirdPartyInspectorListSerializer
        return ThirdPartyInspectorDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search_nearby', 'stats']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by province
        province = self.request.query_params.get('province', None)
        if province:
            queryset = queryset.filter(province=province)
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by certification
        certification = self.request.query_params.get('certification', None)
        if certification:
            queryset = queryset.filter(
                Q(certifications=certification) | 
                Q(additional_certifications__icontains=certification)
            )
        
        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=Decimal(min_rating))
            except (ValueError, TypeError):
                pass
        
        # Filter by mobile service
        mobile_service = self.request.query_params.get('mobile_service', None)
        if mobile_service in ['true', 'True', '1']:
            queryset = queryset.filter(mobile_service=True)
        
        # Filter by verified status
        verified = self.request.query_params.get('verified', None)
        if verified in ['true', 'True', '1']:
            queryset = queryset.filter(is_verified=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def search_nearby(self, request):
        """
        Search for inspectors near a specific location
        
        Query params:
        - latitude: Location latitude
        - longitude: Location longitude
        - radius: Search radius in km (default: 50)
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius', 50)
        
        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)
        except ValueError:
            return Response(
                {'error': 'Invalid latitude, longitude, or radius values'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all inspectors with coordinates
        inspectors = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        # Calculate distances and filter by radius
        nearby_inspectors = []
        for inspector in inspectors:
            distance = haversine_distance(
                longitude, latitude,
                float(inspector.longitude), float(inspector.latitude)
            )
            if distance <= radius:
                inspector_data = self.get_serializer(inspector).data
                inspector_data['distance_km'] = round(distance, 2)
                nearby_inspectors.append(inspector_data)
        
        # Sort by distance
        nearby_inspectors.sort(key=lambda x: x['distance_km'])
        
        return Response({
            'count': len(nearby_inspectors),
            'radius_km': radius,
            'results': nearby_inspectors
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get detailed statistics for an inspector
        """
        inspector = self.get_object()
        
        # Get review statistics
        reviews = inspector.reviews.filter(is_published=True)
        review_stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            average_professionalism=Avg('professionalism_rating'),
            average_thoroughness=Avg('thoroughness_rating'),
            average_communication=Avg('communication_rating'),
            average_value=Avg('value_rating'),
        )
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[f'{i}_star'] = reviews.filter(rating=i).count()
        
        # Recent inspections
        recent_inspections = inspector.inspections.filter(
            status='completed'
        ).order_by('-inspection_date')[:10]
        
        return Response({
            'inspector': self.get_serializer(inspector).data,
            'statistics': {
                'total_inspections': inspector.total_inspections,
                'total_reviews': review_stats['total_reviews'] or 0,
                'average_rating': round(review_stats['average_rating'] or 0, 2),
                'rating_distribution': rating_distribution,
                'detailed_ratings': {
                    'professionalism': round(review_stats['average_professionalism'] or 0, 2),
                    'thoroughness': round(review_stats['average_thoroughness'] or 0, 2),
                    'communication': round(review_stats['average_communication'] or 0, 2),
                    'value': round(review_stats['average_value'] or 0, 2),
                },
            },
            'recent_inspections_count': recent_inspections.count(),
        })


class InspectionReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inspection reports
    
    Endpoints:
    - GET /api/inspections/reports/ - List reports (buyer's reports)
    - GET /api/inspections/reports/{id}/ - Get report details
    - POST /api/inspections/reports/ - Create/upload new report
    - PUT/PATCH /api/inspections/reports/{id}/ - Update report findings
    - DELETE /api/inspections/reports/{id}/ - Delete report
    - POST /api/inspections/reports/{id}/complete/ - Mark inspection complete
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['inspection_date', 'created_at']
    ordering = ['-inspection_date']
    
    def get_queryset(self):
        user = self.request.user
        
        # Users can only see their own requested inspections
        queryset = InspectionReport.objects.filter(buyer=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by inspector
        inspector_id = self.request.query_params.get('inspector', None)
        if inspector_id:
            queryset = queryset.filter(inspector_id=inspector_id)
        
        # Filter by vehicle
        vehicle_id = self.request.query_params.get('vehicle', None)
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        return queryset.select_related('vehicle', 'inspector', 'buyer')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InspectionReportListSerializer
        elif self.action == 'create':
            return InspectionReportCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InspectionReportUpdateSerializer
        return InspectionReportDetailSerializer
    
    def perform_create(self, serializer):
        """Set buyer to current user"""
        serializer.save(buyer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark inspection as completed
        Updates inspector statistics
        """
        report = self.get_object()
        
        if report.status == 'completed':
            return Response(
                {'message': 'Inspection already marked as completed'},
                status=status.HTTP_200_OK
            )
        
        report.mark_completed()
        
        serializer = self.get_serializer(report)
        return Response({
            'message': 'Inspection marked as completed',
            'report': serializer.data
        })


class InspectorReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inspector reviews
    
    Endpoints:
    - GET /api/inspections/reviews/ - List all reviews
    - GET /api/inspections/reviews/{id}/ - Get review details
    - POST /api/inspections/reviews/ - Create new review
    - PUT/PATCH /api/inspections/reviews/{id}/ - Update review
    - DELETE /api/inspections/reviews/{id}/ - Delete review
    - POST /api/inspections/reviews/{id}/mark_helpful/ - Mark review helpful
    """
    
    serializer_class = InspectorReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'helpful_votes', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = InspectorReview.objects.filter(is_published=True)
        
        # Filter by inspector
        inspector_id = self.request.query_params.get('inspector', None)
        if inspector_id:
            queryset = queryset.filter(inspector_id=inspector_id)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=int(min_rating))
            except ValueError:
                pass
        
        # Filter by verified purchases only
        verified_only = self.request.query_params.get('verified_only', None)
        if verified_only in ['true', 'True', '1']:
            queryset = queryset.filter(is_verified_purchase=True)
        
        return queryset.select_related('inspector', 'buyer', 'inspection_report')
    
    def perform_create(self, serializer):
        """Set buyer to current user"""
        serializer.save(buyer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """
        Mark a review as helpful
        Increments helpful_votes counter
        """
        review = self.get_object()
        review.helpful_votes += 1
        review.save(update_fields=['helpful_votes'])
        
        return Response({
            'message': 'Review marked as helpful',
            'helpful_votes': review.helpful_votes
        })
