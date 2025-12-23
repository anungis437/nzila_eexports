"""
Financing API URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InterestRateViewSet, LoanScenarioViewSet, TradeInEstimateViewSet

router = DefaultRouter()
router.register(r'rates', InterestRateViewSet, basename='interest-rate')
router.register(r'scenarios', LoanScenarioViewSet, basename='loan-scenario')
router.register(r'trade-in', TradeInEstimateViewSet, basename='trade-in-estimate')

urlpatterns = [
    path('', include(router.urls)),
]
