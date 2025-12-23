"""
PHASE 2 - Feature 6: Third-Party Inspection Integration

URL routing for inspections API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThirdPartyInspectorViewSet, InspectionReportViewSet, InspectorReviewViewSet

router = DefaultRouter()
router.register(r'inspectors', ThirdPartyInspectorViewSet, basename='inspector')
router.register(r'reports', InspectionReportViewSet, basename='inspection-report')
router.register(r'reviews', InspectorReviewViewSet, basename='inspector-review')

app_name = 'inspections'

urlpatterns = [
    path('', include(router.urls)),
]
