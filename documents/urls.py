"""
PHASE 2 - Feature 5: Export Documents URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExportDocumentViewSet, ExportChecklistViewSet

app_name = 'documents'

router = DefaultRouter()
router.register(r'export-documents', ExportDocumentViewSet, basename='exportdocument')
router.register(r'export-checklists', ExportChecklistViewSet, basename='exportchecklist')

urlpatterns = [
    path('', include(router.urls)),
]
