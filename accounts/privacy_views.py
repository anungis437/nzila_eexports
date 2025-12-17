"""
GDPR/PIPEDA/Law 25 Compliance Utilities
Provides data export, deletion, consent management, and privacy management
"""
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import json
from datetime import datetime


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    """
    Export all user data (GDPR Article 20 - Right to Data Portability)
    Law 25 (Quebec) and PIPEDA compliance
    """
    user = request.user
    
    # Gather all user-related data
    data = {
        'user_profile': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'company_name': user.company_name,
            'phone': user.phone,
            'address': user.address,
            'country': user.country,
            'preferred_language': user.preferred_language,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        },
        'export_date': datetime.now().isoformat(),
        'export_type': 'complete_user_data'
    }
    
    # Add role-specific data
    if user.is_dealer():
        from vehicles.models import Vehicle
        vehicles = Vehicle.objects.filter(dealer=user)
        data['vehicles'] = [
            {
                'id': v.id,
                'make': v.make,
                'model': v.model,
                'year': v.year,
                'vin': v.vin,
                'price_cad': str(v.price_cad),
                'status': v.status,
            }
            for v in vehicles
        ]
    
    if user.is_buyer():
        from deals.models import Lead, Deal
        leads = Lead.objects.filter(buyer=user)
        deals = Deal.objects.filter(buyer=user)
        
        data['leads'] = [
            {
                'id': l.id,
                'vehicle': str(l.vehicle),
                'status': l.status,
                'created_at': l.created_at.isoformat(),
            }
            for l in leads
        ]
        
        data['deals'] = [
            {
                'id': d.id,
                'vehicle': str(d.vehicle),
                'status': d.status,
                'agreed_price_cad': str(d.agreed_price_cad),
                'created_at': d.created_at.isoformat(),
            }
            for d in deals
        ]
    
    if user.is_broker() or user.is_dealer():
        from commissions.models import Commission
        commissions = Commission.objects.filter(recipient=user)
        
        data['commissions'] = [
            {
                'id': c.id,
                'deal_id': c.deal.id,
                'commission_type': c.commission_type,
                'amount_cad': str(c.amount_cad),
                'status': c.status,
                'created_at': c.created_at.isoformat(),
            }
            for c in commissions
        ]
    
    # Create JSON response
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="user_data_{user.id}_{datetime.now().strftime("%Y%m%d")}.json"'
    
    # Log the export for compliance
    from nzila_export.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action='export',
        model_name='User',
        object_id=str(user.id),
        object_repr=str(user),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_data_deletion(request):
    """
    Request account and data deletion (GDPR Article 17 - Right to Erasure)
    Law 25 and PIPEDA compliance
    """
    user = request.user
    
    # Check if user has any active deals
    from deals.models import Deal
    active_deals = Deal.objects.filter(
        buyer=user,
        status__in=['pending_docs', 'docs_verified', 'payment_pending', 'ready_to_ship']
    ).exists()
    
    if active_deals:
        return Response({
            'error': 'Cannot delete account with active deals',
            'message': 'Please complete or cancel all active deals before requesting deletion',
            'active_deals': True
        }, status=400)
    
    # Mark user for deletion (soft delete)
    from django.utils import timezone
    user.deleted_at = timezone.now()
    user.deleted_by = user
    user.is_active = False
    user.save()
    
    # Log the deletion request
    from nzila_export.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action='delete',
        model_name='User',
        object_id=str(user.id),
        object_repr=str(user),
        changes={'deletion_requested': True},
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Send notification to admins
    from django.core.mail import send_mail
    from django.conf import settings
    send_mail(
        'Account Deletion Request',
        f'User {user.username} (ID: {user.id}) has requested account deletion.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [],
        fail_silently=True
    )
    
    return Response({
        'message': 'Your account deletion request has been received',
        'details': 'Your account has been deactivated. Complete deletion will occur within 30 days as per our privacy policy.',
        'deletion_date': (timezone.now() + timezone.timedelta(days=30)).isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def privacy_settings(request):
    """
    Get user privacy settings and consent information
    PIPEDA Principle 3: Consent must be meaningful
    Law 25 Article 14: Right to access personal information
    """
    user = request.user
    
    return Response({
        'user_id': user.id,
        'email': user.email,
        
        # Consent Status (PIPEDA & Law 25)
        'data_processing_consent': user.data_processing_consent,
        'marketing_consent': user.marketing_consent,
        'third_party_sharing_consent': user.third_party_sharing_consent,
        'data_transfer_consent_africa': user.data_transfer_consent_africa,
        
        # Consent Metadata
        'consent_date': user.consent_date.isoformat() if user.consent_date else None,
        'consent_ip_address': user.consent_ip_address,
        'consent_version': user.consent_version,
        
        # Data Subject Rights Status
        'data_export_requested': user.data_export_requested_date.isoformat() if user.data_export_requested_date else None,
        'data_deletion_requested': user.data_deletion_requested_date.isoformat() if user.data_deletion_requested_date else None,
        'data_rectification_requested': user.data_rectification_requested_date.isoformat() if user.data_rectification_requested_date else None,
        
        'last_updated': user.last_login.isoformat() if user.last_login else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_privacy_settings(request):
    """
    Update user privacy settings and consent preferences
    PIPEDA Principle 3: Consent can be withdrawn at any time
    Law 25 Article 8: Consent must be express for sensitive data
    """
    user = request.user
    
    # Get consent updates from request
    data_processing = request.data.get('data_processing_consent')
    marketing = request.data.get('marketing_consent')
    third_party = request.data.get('third_party_sharing_consent')
    africa_transfer = request.data.get('data_transfer_consent_africa')
    
    changes = {}
    
    # Track consent changes and create audit trail
    from accounts.compliance_models import ConsentHistory
    
    if data_processing is not None and data_processing != user.data_processing_consent:
        user.data_processing_consent = data_processing
        changes['data_processing_consent'] = data_processing
        
        ConsentHistory.objects.create(
            user=user,
            consent_type='data_processing',
            action='granted' if data_processing else 'withdrawn',
            consent_given=data_processing,
            privacy_policy_version=user.consent_version,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    if marketing is not None and marketing != user.marketing_consent:
        user.marketing_consent = marketing
        changes['marketing_consent'] = marketing
        
        ConsentHistory.objects.create(
            user=user,
            consent_type='marketing',
            action='granted' if marketing else 'withdrawn',
            consent_given=marketing,
            privacy_policy_version=user.consent_version,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    if third_party is not None and third_party != user.third_party_sharing_consent:
        user.third_party_sharing_consent = third_party
        changes['third_party_sharing_consent'] = third_party
        
        ConsentHistory.objects.create(
            user=user,
            consent_type='third_party_sharing',
            action='granted' if third_party else 'withdrawn',
            consent_given=third_party,
            privacy_policy_version=user.consent_version,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    if africa_transfer is not None and africa_transfer != user.data_transfer_consent_africa:
        user.data_transfer_consent_africa = africa_transfer
        changes['data_transfer_consent_africa'] = africa_transfer
        
        ConsentHistory.objects.create(
            user=user,
            consent_type='cross_border_africa',
            action='granted' if africa_transfer else 'withdrawn',
            consent_given=africa_transfer,
            privacy_policy_version=user.consent_version,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    # Update consent timestamp if any changes
    if changes:
        user.consent_date = timezone.now()
        user.consent_ip_address = request.META.get('REMOTE_ADDR')
        user.save()
    
    # Log the privacy settings update
    from nzila_export.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action='update',
        model_name='PrivacySettings',
        object_id=str(user.id),
        object_repr=f'Privacy settings for {user}',
        changes=changes,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({
        'message': 'Privacy settings updated successfully',
        'changes': changes,
        'consent_date': user.consent_date.isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grant_initial_consent(request):
    """
    Grant initial consent during account setup or policy update
    PIPEDA Principle 3: Meaningful consent
    Law 25 Article 14: Express consent for sensitive information
    """
    user = request.user
    
    # Get all consent types from request
    data_processing = request.data.get('data_processing_consent', False)
    marketing = request.data.get('marketing_consent', False)
    third_party = request.data.get('third_party_sharing_consent', False)
    africa_transfer = request.data.get('data_transfer_consent_africa', False)
    policy_version = request.data.get('privacy_policy_version', '1.0')
    
    # Update user consent fields
    user.data_processing_consent = data_processing
    user.marketing_consent = marketing
    user.third_party_sharing_consent = third_party
    user.data_transfer_consent_africa = africa_transfer
    user.consent_date = timezone.now()
    user.consent_ip_address = request.META.get('REMOTE_ADDR')
    user.consent_version = policy_version
    user.save()
    
    # Create consent history records
    from accounts.compliance_models import ConsentHistory
    
    consents = [
        ('data_processing', data_processing),
        ('marketing', marketing),
        ('third_party_sharing', third_party),
        ('cross_border_africa', africa_transfer),
    ]
    
    for consent_type, consent_given in consents:
        ConsentHistory.objects.create(
            user=user,
            consent_type=consent_type,
            action='granted' if consent_given else 'withdrawn',
            consent_given=consent_given,
            privacy_policy_version=policy_version,
            consent_method='web_form',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            consent_text=f'User consent for {consent_type} during initial setup'
        )
    
    return Response({
        'message': 'Initial consent recorded successfully',
        'consent_date': user.consent_date.isoformat(),
        'policy_version': policy_version
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consent_history(request):
    """
    View complete consent history for transparency
    PIPEDA Principle 8: Individual Access
    Law 25 Article 14: Right to access
    """
    user = request.user
    from accounts.compliance_models import ConsentHistory
    
    history = ConsentHistory.objects.filter(user=user).order_by('-timestamp')
    
    history_data = [
        {
            'consent_type': entry.get_consent_type_display(),
            'action': entry.get_action_display(),
            'consent_given': entry.consent_given,
            'privacy_policy_version': entry.privacy_policy_version,
            'timestamp': entry.timestamp.isoformat(),
            'ip_address': entry.ip_address,
        }
        for entry in history
    ]
    
    return Response({
        'user_id': user.id,
        'consent_history': history_data,
        'total_entries': len(history_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_retention_info(request):
    """
    Provide information about data retention policies
    Law 25 Article 11: Retention limited to necessary period
    PIPEDA Principle 5: Retention Limits
    """
    from accounts.compliance_models import DataRetentionPolicy
    
    policies = DataRetentionPolicy.objects.all()
    
    policy_data = [
        {
            'category': policy.get_data_category_display(),
            'retention_days': policy.retention_days,
            'retention_years': policy.retention_years(),
            'legal_basis': policy.legal_basis,
            'auto_delete_enabled': policy.auto_delete_enabled,
            'description': policy.description,
        }
        for policy in policies
    ]
    
    return Response({
        'retention_policies': policy_data,
        'note': 'Financial and transaction records retained for 7 years per Canadian tax law (CRA requirements)'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_data_breach(request):
    """
    Internal endpoint for admins to report data breaches
    Law 25 Article 3.5: Must notify within 72 hours
    PIPEDA Breach Regulations: Notify OPC and affected individuals
    """
    user = request.user
    
    # Only admins can report breaches
    if not user.is_admin():
        return Response({
            'error': 'Unauthorized',
            'message': 'Only administrators can report data breaches'
        }, status=403)
    
    from accounts.compliance_models import DataBreachLog
    
    # Create breach log
    breach = DataBreachLog.objects.create(
        breach_date=request.data.get('breach_date'),
        discovery_date=timezone.now(),
        severity=request.data.get('severity', 'medium'),
        affected_users_count=request.data.get('affected_users_count', 0),
        data_types_compromised=request.data.get('data_types_compromised', []),
        description=request.data.get('description', ''),
        attack_vector=request.data.get('attack_vector', ''),
        reported_by=user
    )
    
    # Log the breach report
    from nzila_export.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action='create',
        model_name='DataBreachLog',
        object_id=str(breach.id),
        object_repr=str(breach),
        changes={'breach_reported': True},
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({
        'message': 'Data breach logged successfully',
        'breach_id': breach.id,
        'discovery_date': breach.discovery_date.isoformat(),
        'notification_deadline': (breach.discovery_date + timezone.timedelta(hours=72)).isoformat(),
        'action_required': 'Notify affected users and authorities (CAI/OPC) within 72 hours'
    }, status=201)
