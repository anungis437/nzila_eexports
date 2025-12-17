"""
Enhanced ViewSets for Vehicles API with Multi-Image Bulk Operations

This module extends the existing vehicles API with:
- Bulk image upload functionality
- Image reordering API
- Primary image management
- Enhanced image gallery support
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

from .models import VehicleImage, Vehicle
from .serializers import VehicleImageSerializer


class VehicleImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vehicle images with bulk operations.
    
    Provides:
    - Standard CRUD operations for single images
    - Bulk upload of multiple images
    - Batch reordering of images
    - Primary image designation
    """
    
    queryset = VehicleImage.objects.select_related('vehicle').all()
    serializer_class = VehicleImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter images by vehicle if vehicle_id param provided."""
        queryset = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle_id')
        
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        return queryset.order_by('order', '-uploaded_at')
    
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """
        Bulk upload multiple images for a vehicle.
        
        Request format (multipart/form-data):
        {
            "vehicle_id": 123,
            "images": [file1, file2, file3, ...]
        }
        
        Returns list of created image objects.
        """
        vehicle_id = request.data.get('vehicle_id')
        
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify vehicle exists
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response(
                {'error': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get uploaded files
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check current image count
        current_count = VehicleImage.objects.filter(vehicle=vehicle).count()
        if current_count + len(images) > 50:
            return Response(
                {'error': f'Vehicle can have maximum 50 images. Current: {current_count}, Uploading: {len(images)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        errors = []
        
        with transaction.atomic():
            for idx, image_file in enumerate(images):
                # Create image object
                order = current_count + idx
                is_primary = (current_count == 0 and idx == 0)  # First image becomes primary
                
                try:
                    vehicle_image = VehicleImage.objects.create(
                        vehicle=vehicle,
                        image=image_file,
                        media_type='image',
                        order=order,
                        is_primary=is_primary
                    )
                    created_images.append(vehicle_image)
                except Exception as e:
                    errors.append({
                        'file': image_file.name,
                        'error': str(e)
                    })
        
        # Serialize created images
        serializer = self.get_serializer(created_images, many=True)
        
        response_data = {
            'created': len(created_images),
            'images': serializer.data,
        }
        
        if errors:
            response_data['errors'] = errors
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """
        Batch update image order.
        
        Request format:
        {
            "vehicle_id": 123,
            "images": [
                {"id": 1, "order": 0},
                {"id": 2, "order": 1},
                {"id": 3, "order": 2}
            ]
        }
        """
        vehicle_id = request.data.get('vehicle_id')
        images_data = request.data.get('images', [])
        
        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not images_data:
            return Response(
                {'error': 'images array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify vehicle exists
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response(
                {'error': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update order for each image
        updated_images = []
        errors = []
        
        with transaction.atomic():
            for item in images_data:
                image_id = item.get('id')
                order = item.get('order')
                
                if not image_id or order is None:
                    errors.append({
                        'item': item,
                        'error': 'Both id and order are required'
                    })
                    continue
                
                try:
                    vehicle_image = VehicleImage.objects.get(
                        id=image_id,
                        vehicle=vehicle
                    )
                    vehicle_image.order = order
                    vehicle_image.save(update_fields=['order'])
                    updated_images.append(vehicle_image)
                except VehicleImage.DoesNotExist:
                    errors.append({
                        'id': image_id,
                        'error': 'Image not found'
                    })
                except Exception as e:
                    errors.append({
                        'id': image_id,
                        'error': str(e)
                    })
        
        # Serialize updated images
        serializer = self.get_serializer(updated_images, many=True)
        
        response_data = {
            'updated': len(updated_images),
            'images': serializer.data,
        }
        
        if errors:
            response_data['errors'] = errors
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='set-primary')
    def set_primary(self, request, pk=None):
        """
        Set an image as the primary image for its vehicle.
        Automatically unsets other primary images for the same vehicle.
        """
        vehicle_image = self.get_object()
        vehicle = vehicle_image.vehicle
        
        with transaction.atomic():
            # Unset all other primary images for this vehicle
            VehicleImage.objects.filter(
                vehicle=vehicle,
                is_primary=True
            ).update(is_primary=False)
            
            # Set this image as primary
            vehicle_image.is_primary = True
            vehicle_image.save(update_fields=['is_primary'])
        
        serializer = self.get_serializer(vehicle_image)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an image. If it was primary, promote the next image to primary.
        """
        instance = self.get_object()
        vehicle = instance.vehicle
        was_primary = instance.is_primary
        
        with transaction.atomic():
            instance.delete()
            
            # If deleted image was primary, promote next image
            if was_primary:
                next_image = VehicleImage.objects.filter(
                    vehicle=vehicle
                ).order_by('order', '-uploaded_at').first()
                
                if next_image:
                    next_image.is_primary = True
                    next_image.save(update_fields=['is_primary'])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
