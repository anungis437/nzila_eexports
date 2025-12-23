from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet, OfferViewSet, 
    VehicleInspectionSlotViewSet, InspectionAppointmentViewSet
)
from .image_views import VehicleImageViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'vehicle-images', VehicleImageViewSet, basename='vehicle-image')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'inspection-slots', VehicleInspectionSlotViewSet, basename='inspection-slot')
router.register(r'inspection-appointments', InspectionAppointmentViewSet, basename='inspection-appointment')

urlpatterns = [
    path('', include(router.urls)),
]
