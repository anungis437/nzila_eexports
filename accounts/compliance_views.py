"""
Compliance ViewSets for PIPEDA, Law 25, and SOC 2 compliance
"""
from typing import Any
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import QuerySet
from datetime import datetime
import csv

from utils.permissions import IsAdmin, IsAdminOrReadOnly
from .compliance_models import (
    DataBreachLog, ConsentHistory, 
    DataRetentionPolicy, PrivacyImpactAssessment
)
from .serializers import (
    DataBreachLogSerializer, ConsentHistorySerializer,
    DataRetentionPolicySerializer, PrivacyImpactAssessmentSerializer
)


class DataBreachLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for data breach tracking (Law 25, PIPEDA)
    
    Law 25 requires notification to CAI within 72 hours of discovery.
    PIPEDA requires notification to OPC for material breaches.
    
    Admin-only access for security reasons.
    """
    queryset = DataBreachLog.objects.all().select_related('reported_by')
    serializer_class = DataBreachLogSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'breach_date']
    search_fields = ['description', 'data_types_compromised', 'attack_vector']
    ordering_fields = ['discovery_date', 'severity', 'affected_users_count']
    ordering = ['-discovery_date']
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export data breaches to CSV for compliance reporting"""
        breaches = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="data_breaches_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Breach Date', 'Discovery Date', 'Severity', 'Status',
            'Affected Users', 'Data Types', 'Attack Vector',
            'Users Notified', 'CAI Notified', 'OPC Notified',
            'Days Since Discovery', 'Within 72h', 'Reported By'
        ])
        
        for breach in breaches:
            writer.writerow([
                breach.breach_date.strftime('%Y-%m-%d'),
                breach.discovery_date.strftime('%Y-%m-%d'),
                breach.get_severity_display(),
                breach.get_status_display(),
                breach.affected_users_count,
                breach.data_types_compromised,
                breach.attack_vector or '',
                breach.users_notified_date.strftime('%Y-%m-%d') if breach.users_notified_date else 'Not yet',
                breach.cai_notified_date.strftime('%Y-%m-%d') if breach.cai_notified_date else 'Not yet',
                breach.opc_notified_date.strftime('%Y-%m-%d') if breach.opc_notified_date else 'Not yet',
                breach.days_since_discovery(),
                'Yes' if breach.is_within_72_hours() else 'No',
                breach.reported_by.get_full_name() if breach.reported_by else 'Unknown'
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def active_breaches(self, request):
        """Get all active/unresolved breaches"""
        active = self.queryset.filter(
            status__in=['discovered', 'investigating', 'containing', 'notifying']
        ).order_by('-discovery_date')
        
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_notifications(self, request):
        """Get breaches with overdue 72-hour notification requirement"""
        from django.db.models import F, ExpressionWrapper, DurationField
        from datetime import timedelta
        
        now = timezone.now()
        overdue = self.queryset.filter(
            cai_notified_date__isnull=True
        ).annotate(
            hours_since_discovery=ExpressionWrapper(
                now - F('discovery_date'),
                output_field=DurationField()
            )
        ).filter(
            hours_since_discovery__gt=timedelta(hours=72)
        )
        
        serializer = self.get_serializer(overdue, many=True)
        return Response({
            'count': overdue.count(),
            'breaches': serializer.data
        })


class ConsentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for consent history (PIPEDA Principle 8)
    
    Consent records are immutable (ReadOnly) for audit trail.
    Users can view their own consent history, admins can view all.
    """
    queryset = ConsentHistory.objects.all().select_related('user')
    serializer_class = ConsentHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['consent_type', 'action', 'consent_given', 'consent_method']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self) -> QuerySet[ConsentHistory]:  # type: ignore[override]
        """Users see only their own consent history, admins see all"""
        user = self.request.user
        if getattr(user, 'role', None) == 'admin':
            return self.queryset
        return self.queryset.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export consent history to CSV for compliance audit"""
        consents = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="consent_history_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'User', 'Email', 'Consent Type', 'Action',
            'Consent Given', 'Method', 'IP Address', 'Privacy Policy Version'
        ])
        
        for consent in consents:
            writer.writerow([
                consent.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                consent.user.get_full_name(),
                consent.user.email,
                consent.get_consent_type_display(),
                consent.get_action_display(),
                'Yes' if consent.consent_given else 'No',
                consent.consent_method,
                consent.ip_address or '',
                consent.privacy_policy_version
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def my_consents(self, request):
        """Get current user's consent summary"""
        user = request.user
        consents = self.queryset.filter(user=user)
        
        # Get latest consent for each type
        consent_summary = {}
        for consent_type, display in ConsentHistory.CONSENT_TYPE_CHOICES:
            latest = consents.filter(consent_type=consent_type).order_by('-timestamp').first()
            consent_summary[consent_type] = {
                'display': display,
                'granted': latest.consent_given if latest else False,
                'last_updated': latest.timestamp if latest else None
            }
        
        return Response(consent_summary)


class DataRetentionPolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for data retention policies (Law 25 Article 11)
    
    Defines how long different types of data should be retained.
    Admin-only for policy management.
    """
    queryset = DataRetentionPolicy.objects.all()
    serializer_class = DataRetentionPolicySerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['data_category', 'auto_delete_enabled']
    ordering_fields = ['data_category', 'retention_days']
    ordering = ['data_category']
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export retention policies to CSV for documentation"""
        policies = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="retention_policies_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Data Category', 'Retention Days', 'Retention Years',
            'Legal Basis', 'Auto Delete', 'Last Cleanup', 'Description'
        ])
        
        for policy in policies:
            writer.writerow([
                policy.get_data_category_display(),
                policy.retention_days,
                policy.retention_years(),
                policy.legal_basis,
                'Yes' if policy.auto_delete_enabled else 'No',
                policy.last_cleanup_date.strftime('%Y-%m-%d') if policy.last_cleanup_date else 'Never',
                policy.description or ''
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of retention policies by category"""
        policies = self.queryset.all()
        
        summary = {}
        for policy in policies:
            summary[policy.data_category] = {
                'display': policy.get_data_category_display(),  # type: ignore[attr-defined]
                'retention_days': policy.retention_days,
                'retention_years': policy.retention_years(),
                'auto_delete': policy.auto_delete_enabled,
                'last_cleanup': policy.last_cleanup_date
            }
        
        return Response(summary)


class PrivacyImpactAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Privacy Impact Assessments (Law 25 Article 3.3)
    
    PIAs are required for projects involving sensitive data processing.
    Admin-only for security and compliance reasons.
    """
    queryset = PrivacyImpactAssessment.objects.all().select_related(
        'assessed_by', 'approved_by'
    )
    serializer_class = PrivacyImpactAssessmentSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'risk_level', 'cross_border_transfer']
    search_fields = ['title', 'description', 'project_name']
    ordering_fields = ['created_at', 'risk_level', 'review_due_date']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a PIA (requires admin with approval authority)"""
        pia = self.get_object()
        
        if pia.status == 'approved':
            return Response(
                {'error': 'PIA already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pia.status = 'approved'
        pia.approved_by = request.user
        pia.approval_date = timezone.now()
        pia.save()
        
        serializer = self.get_serializer(pia)
        return Response({
            'message': 'PIA approved successfully',
            'pia': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def request_changes(self, request, pk=None):
        """Request changes to a PIA"""
        pia = self.get_object()
        
        pia.status = 'needs_revision'
        pia.save()
        
        serializer = self.get_serializer(pia)
        return Response({
            'message': 'Changes requested',
            'pia': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export PIAs to CSV for compliance reporting"""
        pias = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="privacy_assessments_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Project', 'Risk Level', 'Status', 'Cross-Border',
            'Assessed By', 'Approved By', 'Approval Date', 'Review Due',
            'Created At'
        ])
        
        for pia in pias:
            writer.writerow([
                pia.title,
                pia.project_name or '',
                pia.get_risk_level_display(),
                pia.get_status_display(),
                'Yes' if pia.cross_border_transfer else 'No',
                pia.assessed_by.get_full_name() if pia.assessed_by else '',
                pia.approved_by.get_full_name() if pia.approved_by else 'Not yet',
                pia.approval_date.strftime('%Y-%m-%d') if pia.approval_date else '',
                pia.review_due_date.strftime('%Y-%m-%d') if pia.review_due_date else '',
                pia.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """Get PIAs pending review (overdue or due soon)"""
        from datetime import timedelta
        
        now = timezone.now().date()
        upcoming_threshold = now + timedelta(days=30)
        
        pending = self.queryset.filter(
            status='approved',
            review_due_date__lte=upcoming_threshold
        ).order_by('review_due_date')
        
        serializer = self.get_serializer(pending, many=True)
        return Response({
            'count': pending.count(),
            'assessments': serializer.data
        })
