from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuditLogViewSet, LoginHistoryViewSet,
    DataChangeLogViewSet, SecurityEventViewSet,
    APIAccessLogViewSet
)

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='audit-log')
router.register(r'login-history', LoginHistoryViewSet, basename='login-history')
router.register(r'data-changes', DataChangeLogViewSet, basename='data-changes')
router.register(r'security-events', SecurityEventViewSet, basename='security-events')
router.register(r'api-access', APIAccessLogViewSet, basename='api-access')

urlpatterns = [
    path('', include(router.urls)),
]
