from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum
from vehicles.models import Vehicle
from deals.models import Deal, Lead
from commissions.models import Commission
from shipments.models import Shipment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the current user
    """
    user = request.user
    
    # Initialize broker-specific metrics
    conversion_rate = 0
    closed_deals = 0
    
    # Get counts based on user role
    if user.role == 'admin':
        vehicles_count = Vehicle.objects.count()
        deals_count = Deal.objects.count()
        leads_count = Lead.objects.count()
        shipments_count = Shipment.objects.count()
        
        # Commission totals
        total_commissions = Commission.objects.aggregate(
            total=Sum('amount_cad')
        )['total'] or 0
        
        # Active deals
        active_deals = Deal.objects.filter(status__in=['pending', 'negotiating', 'contract']).count()
        
    elif user.role == 'dealer':
        vehicles_count = Vehicle.objects.filter(dealer=user).count()
        deals_count = Deal.objects.filter(vehicle__dealer=user).count()
        leads_count = Lead.objects.filter(dealer=user).count()
        shipments_count = Shipment.objects.filter(deal__vehicle__dealer=user).count()
        
        total_commissions = Commission.objects.filter(
            recipient=user
        ).aggregate(total=Sum('amount_cad'))['total'] or 0
        
        active_deals = Deal.objects.filter(
            vehicle__dealer=user,
            status__in=['pending', 'negotiating', 'contract']
        ).count()
        
    elif user.role == 'broker':
        vehicles_count = 0
        deals_count = Deal.objects.filter(broker=user).count()
        leads_count = Lead.objects.filter(broker=user).count()
        shipments_count = Shipment.objects.filter(deal__broker=user).count()
        
        # Calculate conversion rate (leads that converted to deals)
        converted_leads_count = Deal.objects.filter(
            lead__broker=user
        ).count()
        conversion_rate = (converted_leads_count / leads_count * 100) if leads_count > 0 else 0
        
        # Get total commissions earned (broker type commissions)
        total_commissions = Commission.objects.filter(
            recipient=user,
            commission_type='broker'
        ).aggregate(total=Sum('amount_cad'))['total'] or 0
        
        # Break down active vs closed deals
        active_deals = Deal.objects.filter(
            broker=user,
            status__in=['pending_docs', 'docs_verified', 'payment_pending', 'payment_received', 'ready_to_ship', 'shipped']
        ).count()
        
        closed_deals = Deal.objects.filter(
            broker=user,
            status__in=['completed', 'cancelled']
        ).count()
        
    else:  # buyer
        vehicles_count = 0
        deals_count = Deal.objects.filter(buyer=user).count()
        leads_count = Lead.objects.filter(buyer=user).count()
        shipments_count = Shipment.objects.filter(deal__buyer=user).count()
        
        total_commissions = 0
        active_deals = Deal.objects.filter(
            buyer=user,
            status__in=['pending_docs', 'docs_verified', 'payment_pending', 'payment_received', 'ready_to_ship', 'shipped']
        ).count()
    
    return Response({
        'vehicles_count': vehicles_count,
        'deals_count': deals_count,
        'leads_count': leads_count,
        'shipments_count': shipments_count,
        'total_commissions': float(total_commissions),
        'active_deals': active_deals,
        'user_role': user.role,
        # Broker-specific metrics
        'conversion_rate': round(conversion_rate, 2) if user.role == 'broker' else None,
        'closed_deals': closed_deals if user.role == 'broker' else None,
    })
