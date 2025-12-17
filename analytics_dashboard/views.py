from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from vehicles.models import Vehicle
from deals.models import Deal
from shipments.models import Shipment
from payments.models import Payment


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def revenue_trends(request):
    """
    Get revenue trends over time (daily, weekly, or monthly)
    Query params: period (day/week/month), days (number of days to look back)
    """
    period = request.GET.get('period', 'day')
    days = int(request.GET.get('days', 30))
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Select appropriate truncation function
    trunc_func = {
        'day': TruncDate,
        'week': TruncWeek,
        'month': TruncMonth,
    }.get(period, TruncDate)
    
    # Aggregate payments by period
    revenue_data = (
        Payment.objects
        .filter(
            payment_date__gte=start_date,
            status__in=['completed', 'paid']
        )
        .annotate(period=trunc_func('payment_date'))
        .values('period')
        .annotate(
            total_revenue=Sum('amount'),
            transaction_count=Count('id')
        )
        .order_by('period')
    )
    
    return Response({
        'period_type': period,
        'days': days,
        'data': list(revenue_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def deal_pipeline(request):
    """
    Get deal pipeline metrics by status
    """
    pipeline_data = (
        Deal.objects
        .values('status')
        .annotate(
            count=Count('id'),
            total_value=Sum('final_price'),
            avg_value=Avg('final_price')
        )
        .order_by('-count')
    )
    
    # Total deals and value
    totals = Deal.objects.aggregate(
        total_deals=Count('id'),
        total_value=Sum('final_price'),
        avg_deal_value=Avg('final_price')
    )
    
    return Response({
        'pipeline': list(pipeline_data),
        'totals': totals
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def conversion_funnel(request):
    """
    Get conversion funnel metrics (vehicles -> deals -> completed)
    """
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Count vehicles listed in period
    vehicles_listed = Vehicle.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Count deals created in period
    deals_created = Deal.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Count deals completed in period
    deals_completed = Deal.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).count()
    
    # Count shipments created in period
    shipments_created = Shipment.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Calculate conversion rates
    vehicle_to_deal_rate = (deals_created / vehicles_listed * 100) if vehicles_listed > 0 else 0
    deal_to_completed_rate = (deals_completed / deals_created * 100) if deals_created > 0 else 0
    deal_to_shipment_rate = (shipments_created / deals_created * 100) if deals_created > 0 else 0
    
    return Response({
        'days': days,
        'funnel': {
            'vehicles_listed': vehicles_listed,
            'deals_created': deals_created,
            'deals_completed': deals_completed,
            'shipments_created': shipments_created
        },
        'conversion_rates': {
            'vehicle_to_deal': round(vehicle_to_deal_rate, 2),
            'deal_to_completed': round(deal_to_completed_rate, 2),
            'deal_to_shipment': round(deal_to_shipment_rate, 2)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dealer_performance(request):
    """
    Get dealer performance metrics
    """
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Aggregate by dealer (seller in Deal model)
    dealer_stats = (
        Deal.objects
        .filter(created_at__gte=start_date)
        .values('seller__username', 'seller__first_name', 'seller__last_name')
        .annotate(
            total_deals=Count('id'),
            completed_deals=Count('id', filter=Q(status='completed')),
            total_revenue=Sum('final_price', filter=Q(status='completed')),
            avg_deal_value=Avg('final_price', filter=Q(status='completed')),
            conversion_rate=Count('id', filter=Q(status='completed')) * 100.0 / Count('id')
        )
        .order_by('-total_revenue')
    )
    
    return Response({
        'days': days,
        'dealers': list(dealer_stats)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def buyer_behavior(request):
    """
    Get buyer behavior insights (popular makes, models, price ranges)
    """
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Most popular makes
    popular_makes = (
        Vehicle.objects
        .filter(created_at__gte=start_date)
        .values('make')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Most popular models
    popular_models = (
        Vehicle.objects
        .filter(created_at__gte=start_date)
        .values('make', 'model')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Price range distribution
    price_ranges = {
        'under_10k': Vehicle.objects.filter(created_at__gte=start_date, price__lt=10000).count(),
        '10k_20k': Vehicle.objects.filter(created_at__gte=start_date, price__gte=10000, price__lt=20000).count(),
        '20k_30k': Vehicle.objects.filter(created_at__gte=start_date, price__gte=20000, price__lt=30000).count(),
        '30k_50k': Vehicle.objects.filter(created_at__gte=start_date, price__gte=30000, price__lt=50000).count(),
        'over_50k': Vehicle.objects.filter(created_at__gte=start_date, price__gte=50000).count(),
    }
    
    # Condition preference
    condition_stats = (
        Vehicle.objects
        .filter(created_at__gte=start_date)
        .values('condition')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    return Response({
        'days': days,
        'popular_makes': list(popular_makes),
        'popular_models': list(popular_models),
        'price_ranges': price_ranges,
        'condition_preferences': list(condition_stats)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def inventory_insights(request):
    """
    Get inventory insights (days to sell, turnover rate, pricing trends)
    """
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Average days to sell (vehicles that got deals in the period)
    completed_deals = Deal.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).select_related('vehicle')
    
    days_to_sell = []
    for deal in completed_deals:
        if deal.vehicle and deal.vehicle.created_at:
            days_diff = (deal.created_at - deal.vehicle.created_at).days
            days_to_sell.append(days_diff)
    
    avg_days_to_sell = sum(days_to_sell) / len(days_to_sell) if days_to_sell else 0
    
    # Current inventory stats
    total_inventory = Vehicle.objects.filter(status='available').count()
    
    # Vehicles by status
    inventory_by_status = (
        Vehicle.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Price trends (average price over time)
    price_trends = (
        Vehicle.objects
        .filter(created_at__gte=start_date)
        .annotate(period=TruncDate('created_at'))
        .values('period')
        .annotate(
            avg_price=Avg('price'),
            vehicle_count=Count('id')
        )
        .order_by('period')
    )
    
    # Turnover rate (deals closed / total inventory)
    deals_closed = Deal.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).count()
    turnover_rate = (deals_closed / total_inventory * 100) if total_inventory > 0 else 0
    
    return Response({
        'days': days,
        'avg_days_to_sell': round(avg_days_to_sell, 1),
        'total_inventory': total_inventory,
        'inventory_by_status': list(inventory_by_status),
        'price_trends': list(price_trends),
        'turnover_rate': round(turnover_rate, 2),
        'deals_closed_in_period': deals_closed
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard_summary(request):
    """
    Get a comprehensive dashboard summary with key metrics
    """
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Key metrics
    total_revenue = Payment.objects.filter(
        payment_date__gte=start_date,
        status__in=['completed', 'paid']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_deals = Deal.objects.filter(created_at__gte=start_date).count()
    completed_deals = Deal.objects.filter(created_at__gte=start_date, status='completed').count()
    
    total_vehicles = Vehicle.objects.filter(created_at__gte=start_date).count()
    available_vehicles = Vehicle.objects.filter(status='available').count()
    
    total_shipments = Shipment.objects.filter(created_at__gte=start_date).count()
    
    # Growth rates (compare to previous period)
    previous_start = start_date - timedelta(days=days)
    previous_revenue = Payment.objects.filter(
        payment_date__gte=previous_start,
        payment_date__lt=start_date,
        status__in=['completed', 'paid']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_growth = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    
    previous_deals = Deal.objects.filter(
        created_at__gte=previous_start,
        created_at__lt=start_date
    ).count()
    deals_growth = ((total_deals - previous_deals) / previous_deals * 100) if previous_deals > 0 else 0
    
    return Response({
        'days': days,
        'metrics': {
            'total_revenue': total_revenue,
            'revenue_growth': round(revenue_growth, 2),
            'total_deals': total_deals,
            'deals_growth': round(deals_growth, 2),
            'completed_deals': completed_deals,
            'conversion_rate': round((completed_deals / total_deals * 100) if total_deals > 0 else 0, 2),
            'total_vehicles': total_vehicles,
            'available_vehicles': available_vehicles,
            'total_shipments': total_shipments,
        }
    })
