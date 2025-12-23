"""
PHASE 2 - Feature 5: Export Documents Views and API Endpoints
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

from vehicles.models import Vehicle
from .models import ExportDocument, ExportChecklist
from .serializers import ExportDocumentSerializer, ExportChecklistSerializer
from .cbsa_form_generator import CBSAForm1Generator
from .title_guides import ProvincialTitleGuides
from .lien_check_service import PPSALienCheckService


class ExportDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing export documents
    
    Supports CRUD operations on export documents and generation of CBSA forms
    """
    serializer_class = ExportDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter documents by user role"""
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            # Staff can see all documents
            return ExportDocument.objects.select_related('vehicle', 'buyer').all()
        else:
            # Regular users see only their documents
            return ExportDocument.objects.filter(buyer=user).select_related('vehicle', 'buyer')
    
    @action(detail=False, methods=['post'], url_path='generate-cbsa-form')
    def generate_cbsa_form(self, request):
        """
        Generate CBSA Form 1 for a vehicle
        
        POST /api/export-documents/generate-cbsa-form/
        Body: {
            "vehicle_id": 123,
            "export_date": "2025-01-15"  (optional, defaults to today)
        }
        """
        vehicle_id = request.data.get('vehicle_id')
        export_date_str = request.data.get('export_date')
        
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get vehicle
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        
        # Parse export date
        if export_date_str:
            try:
                export_date = timezone.datetime.fromisoformat(export_date_str.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid export_date format. Use ISO format (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            export_date = timezone.now()
        
        # Generate CBSA Form 1
        try:
            generator = CBSAForm1Generator(vehicle, request.user, export_date)
            pdf_buffer = generator.generate_pdf()
            
            # Create ExportDocument record
            filename = f"CBSA_Form_1_{vehicle.vin}_{timezone.now().strftime('%Y%m%d')}.pdf"
            expires_at = timezone.now() + timedelta(days=30)  # CBSA forms valid 30 days
            
            export_doc = ExportDocument.objects.create(
                vehicle=vehicle,
                buyer=request.user,
                document_type='CBSA_FORM_1',
                status='GENERATED',
                expires_at=expires_at,
                notes=f'Generated on {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
            )
            
            # Save PDF file
            export_doc.file.save(filename, ContentFile(pdf_buffer.read()), save=True)
            
            serializer = self.get_serializer(export_doc)
            return Response({
                'message': 'CBSA Form 1 generated successfully',
                'document': serializer.data,
                'expires_at': expires_at.isoformat(),
                'validity_days': 30,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate CBSA form: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='title-guide/(?P<province_code>[A-Z]{2})')
    def title_guide(self, request, province_code=None):
        """
        Get provincial title transfer guide
        
        GET /api/export-documents/title-guide/ON/
        GET /api/export-documents/title-guide/QC/
        """
        if not province_code:
            return Response(
                {'error': 'province_code is required (e.g., ON, QC, BC)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        guide = ProvincialTitleGuides.get_guide(province_code)
        
        return Response({
            'province': guide['province'],
            'province_code': guide['province_code'],
            'guide': guide,
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='all-title-guides')
    def all_title_guides(self, request):
        """
        Get title transfer guides for all provinces
        
        GET /api/export-documents/all-title-guides/
        """
        province_codes = ['ON', 'QC', 'BC', 'AB', 'MB', 'SK', 'NS', 'NB', 'NL', 'PE', 'NT', 'YT', 'NU']
        
        guides = {}
        for code in province_codes:
            guide = ProvincialTitleGuides.get_guide(code)
            guides[code] = {
                'province': guide['province'],
                'authority': guide['authority'],
                'website': guide['website'],
                'contact': guide['contact'],
            }
        
        return Response({
            'guides': guides,
            'count': len(guides),
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='check-lien')
    def check_lien(self, request):
        """
        Check PPSA lien status for a vehicle
        
        POST /api/export-documents/check-lien/
        Body: {
            "vehicle_id": 123,
            "force_refresh": false  (optional)
        }
        """
        vehicle_id = request.data.get('vehicle_id')
        force_refresh = request.data.get('force_refresh', False)
        
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get vehicle
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        
        if not vehicle.vin:
            return Response(
                {'error': 'Vehicle does not have a VIN'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract province from vehicle location
        province_code = self._extract_province(vehicle.location)
        if not province_code:
            return Response(
                {'error': 'Cannot determine vehicle province from location'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform lien check
        lien_result = PPSALienCheckService.check_lien(
            vehicle.vin,
            province_code,
            force_refresh=force_refresh
        )
        
        # Update vehicle lien status if fields exist
        if hasattr(vehicle, 'lien_checked'):
            vehicle.lien_checked = True
            vehicle.lien_status = lien_result['lien_status']
            vehicle.save(update_fields=['lien_checked', 'lien_status'])
        
        return Response({
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'lien_check': lien_result,
        }, status=status.HTTP_200_OK)
    
    def _extract_province(self, location):
        """Extract province code from location string"""
        if not location:
            return None
        
        province_mapping = {
            'ON': 'ON', 'ONTARIO': 'ON',
            'QC': 'QC', 'QUEBEC': 'QC',
            'BC': 'BC', 'BRITISH COLUMBIA': 'BC',
            'AB': 'AB', 'ALBERTA': 'AB',
            'MB': 'MB', 'MANITOBA': 'MB',
            'SK': 'SK', 'SASKATCHEWAN': 'SK',
            'NS': 'NS', 'NOVA SCOTIA': 'NS',
            'NB': 'NB', 'NEW BRUNSWICK': 'NB',
            'NL': 'NL', 'NEWFOUNDLAND': 'NL',
            'PE': 'PE', 'PEI': 'PE', 'PRINCE EDWARD ISLAND': 'PE',
            'NT': 'NT', 'NWT': 'NT', 'NORTHWEST TERRITORIES': 'NT',
            'YT': 'YT', 'YUKON': 'YT',
            'NU': 'NU', 'NUNAVUT': 'NU',
        }
        
        # Location format: "City, Province" or "City, ON"
        parts = location.split(',')
        if len(parts) >= 2:
            province_part = parts[-1].strip().upper()
            return province_mapping.get(province_part)
        
        return None


class ExportChecklistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing export readiness checklists
    """
    serializer_class = ExportChecklistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter checklists by user role"""
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            # Staff can see all checklists
            return ExportChecklist.objects.select_related('vehicle', 'buyer').all()
        else:
            # Regular users see only their checklists
            return ExportChecklist.objects.filter(buyer=user).select_related('vehicle', 'buyer')
    
    @action(detail=True, methods=['post'], url_path='check-completion')
    def check_completion(self, request, pk=None):
        """
        Manually trigger completion check
        
        POST /api/export-checklists/{id}/check-completion/
        """
        checklist = self.get_object()
        is_ready = checklist.check_completion()
        
        serializer = self.get_serializer(checklist)
        return Response({
            'export_ready': is_ready,
            'completion_percentage': checklist.get_completion_percentage(),
            'checklist': serializer.data,
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='vehicle/(?P<vehicle_id>[0-9]+)')
    def by_vehicle(self, request, vehicle_id=None):
        """
        Get export checklist for a specific vehicle
        
        GET /api/export-checklists/vehicle/123/
        """
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        
        try:
            checklist = ExportChecklist.objects.get(vehicle=vehicle)
            serializer = self.get_serializer(checklist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExportChecklist.DoesNotExist:
            return Response(
                {
                    'message': 'No export checklist exists for this vehicle',
                    'vehicle_id': vehicle_id,
                },
                status=status.HTTP_404_NOT_FOUND
            )
