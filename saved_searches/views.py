from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import SavedSearch
from .serializers import SavedSearchSerializer, SavedSearchCreateSerializer
from vehicles.models import Vehicle


class SavedSearchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved searches.
    
    Endpoints:
    - GET /api/saved-searches/ - List user's saved searches
    - POST /api/saved-searches/ - Create new saved search
    - GET /api/saved-searches/{id}/ - Retrieve specific saved search
    - PUT/PATCH /api/saved-searches/{id}/ - Update saved search
    - DELETE /api/saved-searches/{id}/ - Delete saved search
    - GET /api/saved-searches/{id}/matches/ - Get vehicles matching this search
    - POST /api/saved-searches/{id}/toggle-active/ - Toggle active status
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the authenticated user's saved searches"""
        return SavedSearch.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use create serializer for POST, standard for other actions"""
        if self.action == 'create':
            return SavedSearchCreateSerializer
        return SavedSearchSerializer
    
    def perform_create(self, serializer):
        """Set the user to the authenticated user and calculate initial match count"""
        saved_search = serializer.save(user=self.request.user)
        # Update match count
        match_count = self._get_matching_vehicles(saved_search).count()
        saved_search.match_count = match_count
        saved_search.save(update_fields=['match_count'])
    
    def perform_update(self, serializer):
        """Recalculate match count when search criteria changes"""
        saved_search = serializer.save()
        match_count = self._get_matching_vehicles(saved_search).count()
        saved_search.match_count = match_count
        saved_search.save(update_fields=['match_count'])
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Get vehicles matching this saved search
        """
        saved_search = self.get_object()
        vehicles = self._get_matching_vehicles(saved_search)
        
        # Simple pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        vehicles_data = vehicles[start:end].values(
            'id', 'vin', 'make', 'model', 'year', 'price',
            'condition', 'mileage', 'color', 'image', 'created_at'
        )
        
        return Response({
            'count': vehicles.count(),
            'results': list(vehicles_data),
            'page': page,
            'page_size': page_size,
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a saved search"""
        saved_search = self.get_object()
        saved_search.is_active = not saved_search.is_active
        saved_search.save(update_fields=['is_active'])
        
        serializer = self.get_serializer(saved_search)
        return Response(serializer.data)
    
    def _get_matching_vehicles(self, saved_search):
        """
        Build queryset of vehicles matching the saved search criteria
        """
        queryset = Vehicle.objects.filter(status='available')
        
        if saved_search.make:
            queryset = queryset.filter(make__iexact=saved_search.make)
        
        if saved_search.model:
            queryset = queryset.filter(model__icontains=saved_search.model)
        
        if saved_search.year_min:
            queryset = queryset.filter(year__gte=saved_search.year_min)
        
        if saved_search.year_max:
            queryset = queryset.filter(year__lte=saved_search.year_max)
        
        if saved_search.price_min:
            queryset = queryset.filter(price__gte=saved_search.price_min)
        
        if saved_search.price_max:
            queryset = queryset.filter(price__lte=saved_search.price_max)
        
        if saved_search.condition:
            queryset = queryset.filter(condition=saved_search.condition)
        
        if saved_search.mileage_max:
            queryset = queryset.filter(mileage__lte=saved_search.mileage_max)
        
        return queryset.order_by('-created_at')
