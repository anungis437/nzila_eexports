"""
Audit Trail Views - API endpoints for audit logs
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from .models import (
    AuditLog, LoginHistory, DataChangeLog,
    SecurityEvent, APIAccessLog
)
from .serializers import (
    AuditLogSerializer, LoginHistorySerializer,
    DataChangeLogSerializer, SecurityEventSerializer,
    APIAccessLogSerializer, AuditStatsSerializer,
    UserActivitySerializer
)
from .services import AuditService


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs
    Read-only access - logs cannot be modified through API
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'severity', 'user']
    search_fields = ['description', 'user__email', 'ip_address']
    ordering_fields = ['timestamp', 'severity', 'action']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter logs based on user role"""
        user = self.request.user
        queryset = super().get_queryset()

        # Non-admin users can only see their own logs
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        # Filter by date range if provided
        days = self.request.query_params.get('days')
        if days:
            try:
                days = int(days)
                since = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(timestamp__gte=since)
            except ValueError:
                pass

        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get audit statistics"""
        days = int(request.query_params.get('days', 7))
        stats = AuditService.get_system_stats(days=days)
        serializer = AuditStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_activity(self, request):
        """Get current user's activity"""
        days = int(request.query_params.get('days', 30))
        activity = AuditService.get_user_activity(request.user, days=days)
        serializer = UserActivitySerializer(activity)
        return Response(serializer.data)


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing login history
    """
    queryset = LoginHistory.objects.all()
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'two_factor_used', 'user']
    search_fields = ['ip_address', 'location', 'user__email']
    ordering_fields = ['login_timestamp']
    ordering = ['-login_timestamp']

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        queryset = super().get_queryset()

        # Non-admin users can only see their own login history
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset

    @action(detail=False, methods=['get'])
    def failed_attempts(self, request):
        """Get recent failed login attempts"""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        failed = LoginHistory.objects.filter(
            status='failed',
            login_timestamp__gte=since
        ).values('ip_address').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response(failed)


class DataChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing data change logs
    """
    queryset = DataChangeLog.objects.all()
    serializer_class = DataChangeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'model_name', 'user']
    search_fields = ['object_repr', 'field_name', 'old_value', 'new_value']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        queryset = super().get_queryset()

        # Non-admin users can only see their own changes
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        # Filter by model and object_id if provided
        model_name = self.request.query_params.get('model_name')
        object_id = self.request.query_params.get('object_id')
        
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        if object_id:
            queryset = queryset.filter(object_id=object_id)

        return queryset

    @action(detail=False, methods=['get'])
    def recent_changes(self, request):
        """Get most recent changes across all models"""
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        changes = self.get_queryset().filter(
            timestamp__gte=since
        ).select_related('user')[:50]
        
        serializer = self.get_serializer(changes, many=True)
        return Response(serializer.data)


class SecurityEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing security events
    """
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    permission_classes = [IsAdminUser]  # Only admins can view security events
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'risk_level', 'resolved', 'blocked']
    search_fields = ['description', 'ip_address', 'user__email']
    ordering_fields = ['timestamp', 'risk_level']
    ordering = ['-timestamp']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a security event as resolved"""
        event = self.get_object()
        event.resolved = True
        event.resolved_by = request.user
        event.resolved_at = timezone.now()
        event.save()

        # Log the resolution
        AuditService.log_action(
            user=request.user,
            action='other',
            description=f'Resolved security event: {event.event_type}',
            content_object=event,
            severity='info',
            request=request
        )

        serializer = self.get_serializer(event)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved security events"""
        events = self.get_queryset().filter(resolved=False)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high and critical risk events"""
        events = self.get_queryset().filter(
            risk_level__in=['high', 'critical'],
            resolved=False
        )
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)


class APIAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing API access logs
    """
    queryset = APIAccessLog.objects.all()
    serializer_class = APIAccessLogSerializer
    permission_classes = [IsAdminUser]  # Only admins can view API logs
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'status_code', 'user']
    search_fields = ['path', 'ip_address', 'user__email']
    ordering_fields = ['timestamp', 'response_time_ms', 'status_code']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter logs"""
        queryset = super().get_queryset()

        # Filter by date range
        hours = self.request.query_params.get('hours')
        if hours:
            try:
                hours = int(hours)
                since = timezone.now() - timedelta(hours=hours)
                queryset = queryset.filter(timestamp__gte=since)
            except ValueError:
                pass

        # Filter by slow requests (>1000ms)
        slow_only = self.request.query_params.get('slow_only')
        if slow_only == 'true':
            queryset = queryset.filter(response_time_ms__gt=1000)

        # Filter by errors (status >= 400)
        errors_only = self.request.query_params.get('errors_only')
        if errors_only == 'true':
            queryset = queryset.filter(status_code__gte=400)

        return queryset

    @action(detail=False, methods=['get'])
    def slowest_endpoints(self, request):
        """Get slowest API endpoints"""
        from django.db.models import Avg, Count
        
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        slow_endpoints = APIAccessLog.objects.filter(
            timestamp__gte=since
        ).values('path').annotate(
            avg_response_time=Avg('response_time_ms'),
            call_count=Count('id')
        ).order_by('-avg_response_time')[:10]
        
        return Response(slow_endpoints)

    @action(detail=False, methods=['get'])
    def error_summary(self, request):
        """Get summary of error responses"""
        from django.db.models import Count
        
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        errors = APIAccessLog.objects.filter(
            timestamp__gte=since,
            status_code__gte=400
        ).values('status_code', 'path').annotate(
            count=Count('id')
        ).order_by('-count')[:20]
        
        return Response(errors)
