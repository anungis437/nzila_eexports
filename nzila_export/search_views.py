from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from vehicles.models import Vehicle
from deals.models import Lead, Deal, Document
from commissions.models import Commission
from shipments.models import Shipment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    """
    Global search across all entities.
    
    Query Parameters:
    - q: Search query string (required, min 2 characters)
    - types: Comma-separated entity types to search (optional)
      - Options: vehicle, lead, deal, commission, shipment, document
      - Default: all types
    - limit: Max results per entity type (default: 5)
    """
    query = request.GET.get('q', '').strip()
    types = request.GET.get('types', '').split(',') if request.GET.get('types') else []
    limit = int(request.GET.get('limit', 5))
    
    if len(query) < 2:
        return Response([])
    
    user = request.user
    results = []
    
    # Search vehicles
    if not types or 'vehicle' in types:
        vehicles = Vehicle.objects.filter(
            Q(make__icontains=query) |
            Q(model__icontains=query) |
            Q(vin__icontains=query) |
            Q(year__icontains=query)
        )[:limit]
        
        for vehicle in vehicles:
            results.append({
                'id': vehicle.id,
                'type': 'vehicle',
                'title': f"{vehicle.year} {vehicle.make} {vehicle.model}",
                'subtitle': f"VIN: {vehicle.vin[:10]}...",
                'metadata': f"${vehicle.price:,.2f} • {vehicle.get_condition_display()}",
                'url': f'/vehicles?id={vehicle.id}'
            })
    
    # Search leads
    if (not types or 'lead' in types) and user.has_perm('deals.view_lead'):
        leads_qs = Lead.objects.all()
        
        # Filter by user permissions
        if user.is_buyer():
            leads_qs = leads_qs.filter(buyer=user)
        elif user.is_dealer():
            leads_qs = leads_qs.filter(vehicle__dealer=user)
        elif user.is_broker():
            leads_qs = leads_qs.filter(broker=user)
        
        leads = leads_qs.filter(
            Q(buyer__username__icontains=query) |
            Q(buyer__email__icontains=query) |
            Q(vehicle__make__icontains=query) |
            Q(vehicle__model__icontains=query)
        )[:limit]
        
        for lead in leads:
            results.append({
                'id': lead.id,
                'type': 'lead',
                'title': f"Lead #{lead.id} - {lead.buyer.username}",
                'subtitle': f"{lead.vehicle.make} {lead.vehicle.model}",
                'metadata': f"{lead.get_status_display()} • {lead.get_source_display()}",
                'url': f'/leads?id={lead.id}'
            })
    
    # Search deals
    if not types or 'deal' in types:
        deals_qs = Deal.objects.all()
        
        # Filter by user permissions
        if user.is_buyer():
            deals_qs = deals_qs.filter(buyer=user)
        elif user.is_dealer():
            deals_qs = deals_qs.filter(dealer=user)
        elif user.is_broker():
            deals_qs = deals_qs.filter(broker=user)
        
        deals = deals_qs.filter(
            Q(vehicle__make__icontains=query) |
            Q(vehicle__model__icontains=query) |
            Q(buyer__username__icontains=query)
        )[:limit]
        
        for deal in deals:
            results.append({
                'id': deal.id,
                'type': 'deal',
                'title': f"Deal #{deal.id} - {deal.vehicle.make} {deal.vehicle.model}",
                'subtitle': f"Buyer: {deal.buyer.username}",
                'metadata': f"{deal.get_status_display()} • ${deal.price:,.2f}",
                'url': f'/deals?id={deal.id}'
            })
    
    # Search commissions
    if (not types or 'commission' in types) and user.has_perm('commissions.view_commission'):
        commissions_qs = Commission.objects.all()
        
        # Filter by user permissions
        if user.is_broker():
            commissions_qs = commissions_qs.filter(deal__broker=user)
        elif user.is_dealer():
            commissions_qs = commissions_qs.filter(deal__dealer=user)
        
        commissions = commissions_qs.filter(
            Q(deal__vehicle__make__icontains=query) |
            Q(deal__vehicle__model__icontains=query)
        )[:limit]
        
        for commission in commissions:
            results.append({
                'id': commission.id,
                'type': 'commission',
                'title': f"Commission #{commission.id}",
                'subtitle': f"Deal #{commission.deal.id} - {commission.deal.vehicle.make} {commission.deal.vehicle.model}",
                'metadata': f"${commission.amount:,.2f} • {commission.get_status_display()}",
                'url': f'/commissions?id={commission.id}'
            })
    
    # Search shipments
    if (not types or 'shipment' in types) and user.has_perm('shipments.view_shipment'):
        shipments_qs = Shipment.objects.all()
        
        # Filter by user permissions
        if user.is_dealer():
            shipments_qs = shipments_qs.filter(deal__dealer=user)
        
        shipments = shipments_qs.filter(
            Q(tracking_number__icontains=query) |
            Q(origin__icontains=query) |
            Q(destination__icontains=query) |
            Q(deal__vehicle__make__icontains=query)
        )[:limit]
        
        for shipment in shipments:
            results.append({
                'id': shipment.id,
                'type': 'shipment',
                'title': f"Shipment #{shipment.tracking_number}",
                'subtitle': f"{shipment.origin} → {shipment.destination}",
                'metadata': f"{shipment.get_status_display()} • {shipment.get_shipping_method_display()}",
                'url': f'/shipments?id={shipment.id}'
            })
    
    # Search documents
    if not types or 'document' in types:
        documents_qs = Document.objects.all()
        
        # Filter by user permissions
        if user.is_buyer():
            documents_qs = documents_qs.filter(deal__buyer=user)
        elif user.is_dealer():
            documents_qs = documents_qs.filter(deal__dealer=user)
        elif user.is_broker():
            documents_qs = documents_qs.filter(deal__broker=user)
        
        documents = documents_qs.filter(
            Q(notes__icontains=query) |
            Q(deal__vehicle__make__icontains=query)
        )[:limit]
        
        for document in documents:
            results.append({
                'id': document.id,
                'type': 'document',
                'title': f"{document.get_document_type_display()}",
                'subtitle': f"Deal #{document.deal.id}",
                'metadata': f"{document.get_status_display()} • Uploaded {document.uploaded_at.strftime('%b %d, %Y')}",
                'url': f'/documents?id={document.id}'
            })
    
    return Response(results)
