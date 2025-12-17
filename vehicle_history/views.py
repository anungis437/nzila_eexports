from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from vehicles.models import Vehicle
from .models import VehicleHistoryReport, AccidentRecord, ServiceRecord, OwnershipRecord
from .serializers import (
    VehicleHistoryReportSerializer,
    VehicleHistoryReportSummarySerializer,
    AccidentRecordSerializer,
    ServiceRecordSerializer,
    OwnershipRecordSerializer
)
from .services import VehicleDataAggregator, CarFaxService, TransportCanadaService
from .throttles import VehicleHistoryRateThrottle, TransportCanadaRateThrottle
import logging

logger = logging.getLogger(__name__)


class VehicleHistoryReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for vehicle history reports
    Read-only for public access
    """
    queryset = VehicleHistoryReport.objects.all()
    serializer_class = VehicleHistoryReportSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='by-vehicle/(?P<vehicle_id>[^/.]+)')
    def by_vehicle(self, request, vehicle_id=None):
        """Get history report for a specific vehicle"""
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        
        try:
            report = VehicleHistoryReport.objects.get(vehicle=vehicle)
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        except VehicleHistoryReport.DoesNotExist:
            return Response(
                {'detail': 'No history report available for this vehicle.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='by-vin/(?P<vin>[^/.]+)')
    def by_vin(self, request, vin=None):
        """Get history report by VIN"""
        vehicle = get_object_or_404(Vehicle, vin=vin)
        
        try:
            report = VehicleHistoryReport.objects.get(vehicle=vehicle)
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        except VehicleHistoryReport.DoesNotExist:
            return Response(
                {'detail': 'No history report available for this VIN.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get lightweight summary of history report"""
        report = self.get_object()
        serializer = VehicleHistoryReportSummarySerializer(report)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def clean_titles(self, request):
        """Get all vehicles with clean titles"""
        reports = self.queryset.filter(title_status='clean', accident_severity='none')
        serializer = VehicleHistoryReportSummarySerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def one_owner(self, request):
        """Get all one-owner vehicles"""
        reports = self.queryset.filter(total_owners=1)
        serializer = VehicleHistoryReportSummarySerializer(reports, many=True)
        return Response(serializer.data)


class AccidentRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for accident records"""
    queryset = AccidentRecord.objects.all()
    serializer_class = AccidentRecordSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle', None)
        if vehicle_id:
            queryset = queryset.filter(history_report__vehicle_id=vehicle_id)
        return queryset


class ServiceRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service records"""
    queryset = ServiceRecord.objects.all()
    serializer_class = ServiceRecordSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle', None)
        if vehicle_id:
            queryset = queryset.filter(history_report__vehicle_id=vehicle_id)
        return queryset


class OwnershipRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ownership records"""
    queryset = OwnershipRecord.objects.all()
    serializer_class = OwnershipRecordSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle', None)
        if vehicle_id:
            queryset = queryset.filter(history_report__vehicle_id=vehicle_id)
        return queryset


# Canadian Data Integration Endpoints

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([VehicleHistoryRateThrottle])
def get_comprehensive_history(request, vehicle_id):
    """
    Get comprehensive vehicle history from all Canadian sources
    Rate limited to prevent API abuse (100 req/hour)
    
    GET /api/vehicle-history/<vehicle_id>/comprehensive/
    """
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # Check permissions
        if not (request.user.is_staff or 
                request.user == vehicle.dealer or
                request.user.role in ['buyer', 'broker']):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get comprehensive report from all sources
        report = VehicleDataAggregator.get_comprehensive_report(
            vin=vehicle.vin,
            year=vehicle.year,
            make=vehicle.make,
            model=vehicle.model
        )
        
        # Add vehicle basic info
        report['vehicle'] = {
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'vin': vehicle.vin,
            'dealer': vehicle.dealer.username if vehicle.dealer else None
        }
        
        return Response(report, status=status.HTTP_200_OK)
        
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching comprehensive history: {e}")
        return Response(
            {'error': 'Failed to fetch vehicle history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([VehicleHistoryRateThrottle])
def get_carfax_report(request, vehicle_id):
    """
    Get CarFax report for specific vehicle
    Rate limited to 100 requests/hour
    
    GET /api/vehicle-history/<vehicle_id>/carfax/
    """
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # Check permissions - only dealers and admins
        if not (request.user.is_staff or request.user == vehicle.dealer):
            return Response(
                {'error': 'Only dealers and admins can access CarFax reports'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        carfax_data = CarFaxService.get_vehicle_history(vehicle.vin)
        
        return Response({
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'carfax': carfax_data
        }, status=status.HTTP_200_OK)
        
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching CarFax report: {e}")
        return Response(
            {'error': 'Failed to fetch CarFax report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([TransportCanadaRateThrottle])
def get_transport_canada_recalls(request, vehicle_id):
    """
    Get Transport Canada recalls for vehicle
    Rate limited to 1000 requests/hour
    
    GET /api/vehicle-history/<vehicle_id>/recalls/
    """
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        recalls = TransportCanadaService.get_recalls(
            vin=vehicle.vin,
            year=vehicle.year,
            make=vehicle.make,
            model=vehicle.model
        )
        
        return Response({
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'year': vehicle.year,
            'make': vehicle.make,
            'model': vehicle.model,
            'recalls': recalls,
            'recall_count': len(recalls)
        }, status=status.HTTP_200_OK)
        
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching recalls: {e}")
        return Response(
            {'error': 'Failed to fetch recalls'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quick_summary(request, vehicle_id):
    """
    Get summarized vehicle history (key facts only)
    No rate limit - uses cached data only
    
    GET /api/vehicle-history/<vehicle_id>/summary/
    """
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # Try to get from cache
        cache_key = f'vehicle_summary_{vehicle.id}'
        cached_summary = cache.get(cache_key)
        
        if cached_summary:
            return Response(cached_summary, status=status.HTTP_200_OK)
        
        # Build summary from available data
        carfax_data = CarFaxService.get_vehicle_history(vehicle.vin)
        recalls = TransportCanadaService.get_recalls(
            year=vehicle.year,
            make=vehicle.make,
            model=vehicle.model
        )
        
        summary = {
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'highlights': {
                'accidents': carfax_data.get('accidents', 'Unknown'),
                'owners': carfax_data.get('owners', 'Unknown'),
                'title_status': carfax_data.get('title_status', 'Unknown'),
                'recall_count': len(recalls),
                'has_active_recalls': len(recalls) > 0
            },
            'last_updated': carfax_data.get('status', 'Unknown')
        }
        
        # Cache for 24 hours
        cache.set(cache_key, summary, 86400)
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching history summary: {e}")
        return Response(
            {'error': 'Failed to fetch history summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
