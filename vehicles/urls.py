from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, OfferViewSet
from .image_views import VehicleImageViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'vehicle-images', VehicleImageViewSet, basename='vehicle-image')
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)),
]
