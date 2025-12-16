from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from vehicles.models import Vehicle
from deals.models import Deal, Lead
from commissions.models import Commission
from shipments.models import Shipment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_stats(request):
    """Get comprehensive analytics statistics"""
    user = request.user
    now = timezone.now()
    last_month = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    
    # Filter based on user role
    if user.role == 'dealer':
        deals_qs = Deal.objects.filter(dealer=user)
        vehicles_qs = Vehicle.objects.filter(dealer=user)
        commissions_qs = Commission.objects.filter(deal__dealer=user)
    elif user.role == 'broker':
        deals_qs = Deal.objects.filter(broker=user)
        vehicles_qs = Vehicle.objects.all()
        commissions_qs = Commission.objects.filter(recipient=user)
    else:
        deals_qs = Deal.objects.all()
        vehicles_qs = Vehicle.objects.all()
        commissions_qs = Commission.objects.all()
    
    # Current period stats
    current_revenue = deals_qs.filter(
        status__in=['completed', 'shipped'],
        created_at__gte=last_month
    ).aggregate(total=Sum('agreed_price_cad'))['total'] or Decimal('0')
    
    current_deals = deals_qs.filter(
        status__in=['pending_docs', 'docs_verified', 'payment_pending', 'payment_received', 'ready_to_ship']
    ).count()
    
    current_vehicles_sold = deals_qs.filter(
        status__in=['completed', 'shipped'],
        created_at__gte=last_month
    ).count()
    
    current_shipments = Shipment.objects.filter(
        status='in_transit'
    ).count()
    
    current_commissions = commissions_qs.filter(
        status__in=['approved', 'paid'],
        created_at__gte=last_month
    ).aggregate(total=Sum('amount_cad'))['total'] or Decimal('0')
    
    current_leads = Lead.objects.filter(
        created_at__gte=last_month
    ).count()
    
    # Previous period stats for comparison
    prev_revenue = deals_qs.filter(
        status__in=['completed', 'shipped'],
        created_at__gte=two_months_ago,
        created_at__lt=last_month
    ).aggregate(total=Sum('agreed_price_cad'))['total'] or Decimal('0')
    
    prev_deals = deals_qs.filter(
        status__in=['pending_docs', 'docs_verified', 'payment_pending', 'payment_received', 'ready_to_ship'],
        created_at__gte=two_months_ago,
        created_at__lt=last_month
    ).count()
    
    prev_vehicles_sold = deals_qs.filter(
        status__in=['completed', 'shipped'],
        created_at__gte=two_months_ago,
        created_at__lt=last_month
    ).count()
    
    prev_commissions = commissions_qs.filter(
        status__in=['approved', 'paid'],
        created_at__gte=two_months_ago,
        created_at__lt=last_month
    ).aggregate(total=Sum('amount_cad'))['total'] or Decimal('0')
    
    prev_leads = Lead.objects.filter(
        created_at__gte=two_months_ago,
        created_at__lt=last_month
    ).count()
    
    # Calculate percentage changes
    def calc_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)
    
    return Response({
        'totalRevenue': float(current_revenue),
        'revenueChange': calc_change(float(current_revenue), float(prev_revenue)),
        'activeDeals': current_deals,
        'dealsChange': calc_change(current_deals, prev_deals),
        'vehiclesSold': current_vehicles_sold,
        'vehiclesChange': calc_change(current_vehicles_sold, prev_vehicles_sold),
        'shipmentsInTransit': current_shipments,
        'shipmentsChange': 0,  # No previous data for shipments
        'totalCommissions': float(current_commissions),
        'commissionsChange': calc_change(float(current_commissions), float(prev_commissions)),
        'newLeads': current_leads,
        'leadsChange': calc_change(current_leads, prev_leads),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_revenue_chart(request):
    """Get revenue and deals data for the last 6 months"""
    user = request.user
    now = timezone.now()
    
    # Filter based on user role
    if user.role == 'dealer':
        deals_qs = Deal.objects.filter(dealer=user)
    elif user.role == 'broker':
        deals_qs = Deal.objects.filter(broker=user)
    else:
        deals_qs = Deal.objects.all()
    
    data = []
    months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for i in range(6):
        month_start = now - timedelta(days=(6-i)*30)
        month_end = now - timedelta(days=(5-i)*30)
        
        revenue = deals_qs.filter(
            status__in=['completed', 'shipped'],
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('agreed_price_cad'))['total'] or Decimal('0')
        
        deals_count = deals_qs.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        data.append({
            'month': months[i],
            'revenue': float(revenue),
            'deals': deals_count
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pipeline_chart(request):
    """Get deal pipeline distribution"""
    user = request.user
    
    # Filter based on user role
    if user.role == 'dealer':
        deals_qs = Deal.objects.filter(dealer=user)
    elif user.role == 'broker':
        deals_qs = Deal.objects.filter(broker=user)
    else:
        deals_qs = Deal.objects.all()
    
    statuses = [
        ('pending_docs', '#64748b'),
        ('docs_verified', '#3b82f6'),
        ('payment_pending', '#f59e0b'),
        ('payment_received', '#10b981'),
        ('ready_to_ship', '#8b5cf6'),
        ('shipped', '#6366f1'),
        ('completed', '#22c55e'),
    ]
    
    data = []
    for status, color in statuses:
        count = deals_qs.filter(status=status).count()
        data.append({
            'status': status,
            'count': count,
            'color': color
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_activities(request):
    """Get recent activities across all entities"""
    user = request.user
    activities = []
    
    # Recent deals
    recent_deals = Deal.objects.select_related('vehicle', 'dealer').order_by('-updated_at')[:3]
    for deal in recent_deals:
        activities.append({
            'id': f'deal-{deal.id}',
            'type': 'deal',
            'action': 'completed' if deal.status == 'completed' else 'updated',
            'description': f'{deal.vehicle.year} {deal.vehicle.make} {deal.vehicle.model}',
            'timestamp': deal.updated_at.isoformat(),
            'user': deal.dealer.get_full_name() if deal.dealer else 'Unknown'
        })
    
    # Recent shipments
    recent_shipments = Shipment.objects.select_related('deal').order_by('-updated_at')[:2]
    for shipment in recent_shipments:
        activities.append({
            'id': f'shipment-{shipment.id}',
            'type': 'shipment',
            'action': 'shipped' if shipment.status == 'in_transit' else 'updated',
            'description': f'Shipment {shipment.tracking_number}',
            'timestamp': shipment.updated_at.isoformat(),
            'user': 'System'
        })
    
    # Recent commissions
    recent_commissions = Commission.objects.select_related('recipient').order_by('-updated_at')[:2]
    for commission in recent_commissions:
        activities.append({
            'id': f'commission-{commission.id}',
            'type': 'commission',
            'action': 'approved' if commission.status == 'approved' else 'created',
            'description': f'Commission ${commission.amount_cad}',
            'timestamp': commission.updated_at.isoformat(),
            'user': commission.recipient.get_full_name() if commission.recipient else 'Unknown'
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response(activities[:10])
