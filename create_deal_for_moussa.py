import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from accounts.models import User
from deals.models import Deal
from vehicles.models import Vehicle

# Get Moussa
moussa = User.objects.get(email='moussa.traoré@buyer.com')
print(f"Checking deals for: {moussa.username} ({moussa.email})")

# Check existing deals
existing_deals = Deal.objects.filter(buyer=moussa)
print(f"\nExisting deals for Moussa: {existing_deals.count()}")

if existing_deals.exists():
    print("\nMoussa's deals:")
    for deal in existing_deals:
        print(f"  - Deal #{deal.id}: {deal.vehicle.year} {deal.vehicle.make} {deal.vehicle.model}")
        print(f"    Status: {deal.status}, Payment: {deal.payment_status}")
        print(f"    Price: ${deal.agreed_price_cad:,.2f} CAD")
else:
    print("\nNo deals found for Moussa. Creating one...")
    
    # Get an available vehicle
    vehicle = Vehicle.objects.filter(status='available').first()
    
    if vehicle:
        # Create a deal for Moussa
        deal = Deal.objects.create(
            buyer=moussa,
            dealer=vehicle.dealer,
            vehicle=vehicle,
            agreed_price_cad=vehicle.price_cad * 0.95,  # 5% discount
            agreed_price_usd=vehicle.price_usd * 0.95,
            status='payment_pending',
            payment_status='pending',
            notes='Deal created for buyer demo - Moussa reviewing vehicle purchase'
        )
        print(f"\n✓ Created Deal #{deal.id}")
        print(f"  Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}")
        print(f"  Dealer: {vehicle.dealer.get_full_name()}")
        print(f"  Price: ${deal.agreed_price_cad:,.2f} CAD")
        print(f"  Status: {deal.status}")
        
        # Update vehicle status to reserved
        vehicle.status = 'reserved'
        vehicle.save()
        print(f"  Vehicle status updated to: reserved")
