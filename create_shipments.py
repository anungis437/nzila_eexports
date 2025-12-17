"""
Create shipments from existing deals
"""
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from deals.models import Deal
from shipments.models import Shipment
from django.utils import timezone

SHIPPING_COMPANIES = ['DHL', 'FedEx', 'Maersk', 'Mediterranean Shipping', 'CMA CGM', 'Hapag-Lloyd']
ORIGIN_PORTS = ['Vancouver Port', 'Toronto Port', 'Montreal Port', 'Halifax Port']
DESTINATION_PORTS = ['Mombasa Port', 'Lagos Port', 'Dar es Salaam Port', 'Durban Port', 'Accra Port']
DESTINATION_COUNTRIES = ['Kenya', 'Nigeria', 'Tanzania', 'South Africa', 'Ghana']

def create_shipments():
    # Get completed deals without shipments
    deals = Deal.objects.filter(status='completed').exclude(shipment__isnull=False)
    
    created = 0
    for deal in deals:
        # Random tracking number
        tracking_number = f'TRK{random.randint(100000, 999999)}'
        
        # Random dates
        now = timezone.now().date()
        estimated_departure = now - timedelta(days=random.randint(7, 14))
        actual_departure = estimated_departure + timedelta(days=random.randint(0, 2))
        estimated_arrival = actual_departure + timedelta(days=random.randint(25, 35))
        
        # Random status
        status = random.choice(['pending', 'in_transit', 'customs', 'delivered'])
        actual_arrival = actual_departure + timedelta(days=random.randint(28, 33)) if status == 'delivered' else None
        
        shipment = Shipment.objects.create(
            deal=deal,
            tracking_number=tracking_number,
            shipping_company=random.choice(SHIPPING_COMPANIES),
            origin_port=random.choice(ORIGIN_PORTS),
            destination_port=random.choice(DESTINATION_PORTS),
            destination_country=random.choice(DESTINATION_COUNTRIES),
            status=status,
            estimated_departure=estimated_departure,
            actual_departure=actual_departure,
            estimated_arrival=estimated_arrival,
            actual_arrival=actual_arrival
        )
        
        created += 1
        print(f'✅ Created shipment {tracking_number} for deal #{deal.id} ({status})')
    
    print(f'\n✅ Total shipments created: {created}')
    print(f'📦 Total shipments in database: {Shipment.objects.count()}')

if __name__ == '__main__':
    create_shipments()
