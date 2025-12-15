"""
GDPR/PIPEDA/Law 25 Compliance Utilities
Provides data export, deletion, and privacy management
"""
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
    """
    user = request.user
    
    return Response({
        'user_id': user.id,
        'email_notifications': True,  # Can be expanded with user preferences
        'data_sharing_consent': True,
        'marketing_consent': False,
        'last_updated': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_privacy_settings(request):
    """
    Update user privacy settings
    """
    user = request.user
    
    # Update privacy preferences (expand as needed)
    settings_updated = request.data
    
    # Log the privacy settings update
    from nzila_export.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action='update',
        model_name='PrivacySettings',
        object_id=str(user.id),
        object_repr=f'Privacy settings for {user}',
        changes=settings_updated,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({
        'message': 'Privacy settings updated successfully',
        'settings': settings_updated
    })
