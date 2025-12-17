from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceHistoryViewSet

router = DefaultRouter()
router.register(r'price-history', PriceHistoryViewSet, basename='price-history')

urlpatterns = [
    path('', include(router.urls)),
]
