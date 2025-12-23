"""
Dealer Verification URLs
Phase 3 - Feature 9
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.dealer_verification_views import (
    DealerLicenseViewSet,
    DealerVerificationViewSet,
)

# Create router
router = DefaultRouter()
router.register(r'dealer-licenses', DealerLicenseViewSet, basename='dealer-license')
router.register(r'dealer-verification', DealerVerificationViewSet, basename='dealer-verification')

urlpatterns = [
    path('', include(router.urls)),
]
