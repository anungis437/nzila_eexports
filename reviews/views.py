from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Review, ReviewHelpfulness, DealerRating
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewResponseSerializer,
    DealerRatingSerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('buyer', 'dealer', 'vehicle').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dealer', 'vehicle', 'review_type', 'rating', 'is_approved', 'is_featured']
    search_fields = ['title', 'comment']
    ordering_fields = ['created_at', 'rating', 'helpful_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action == 'respond':
            return ReviewResponseSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Only show approved reviews to non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        # Filter by dealer if specified
        dealer_id = self.request.query_params.get('dealer')
        if dealer_id:
            queryset = queryset.filter(dealer_id=dealer_id)
        
        # Filter by vehicle if specified
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        # Filter by buyer if specified (for "my reviews")
        if self.request.query_params.get('my_reviews') == 'true':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(buyer=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        """Mark a review as helpful or not helpful"""
        review = self.get_object()
        is_helpful = request.data.get('is_helpful', True)
        
        # Can't vote on own review
        if review.buyer == request.user:
            return Response(
                {'error': 'You cannot vote on your own review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create helpfulness vote
        vote, created = ReviewHelpfulness.objects.get_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': is_helpful}
        )
        
        if not created:
            # Update existing vote if changed
            if vote.is_helpful != is_helpful:
                old_is_helpful = vote.is_helpful
                vote.is_helpful = is_helpful
                vote.save()
                
                # Update counts
                if old_is_helpful:
                    review.helpful_count -= 1
                    review.not_helpful_count += 1
                else:
                    review.helpful_count += 1
                    review.not_helpful_count -= 1
                review.save()
        else:
            # New vote, update counts
            if is_helpful:
                review.helpful_count += 1
            else:
                review.not_helpful_count += 1
            review.save()
        
        return Response({
            'success': True,
            'helpful_count': review.helpful_count,
            'not_helpful_count': review.not_helpful_count
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def respond(self, request, pk=None):
        """Allow dealer to respond to a review"""
        review = self.get_object()
        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured reviews"""
        reviews = self.get_queryset().filter(is_featured=True, is_approved=True)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class DealerRatingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DealerRating.objects.select_related('dealer').all()
    serializer_class = DealerRatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Manually refresh dealer rating stats"""
        rating = self.get_object()
        rating.update_stats()
        serializer = self.get_serializer(rating)
        return Response(serializer.data)
