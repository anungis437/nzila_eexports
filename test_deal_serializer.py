import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from deals.models import Deal
from deals.serializers import DealSerializer
from accounts.models import User

# Get Moussa (buyer)
moussa = User.objects.get(email='moussa.traoré@buyer.com')
print(f"Found user: {moussa.email}")

# Get Moussa's deals
deals = Deal.objects.filter(buyer=moussa)
print(f"Found {deals.count()} deals for Moussa")

# Try to serialize them
for deal in deals:
    print(f"\nSerializing Deal #{deal.id}...")
    try:
        serializer = DealSerializer(deal)
        data = serializer.data
        print(f"  Success! Deal #{deal.id} serialized")
        print(f"  Buyer: {data.get('buyer_name')}")
        print(f"  Dealer: {data.get('dealer_name')}")
        print(f"  Broker: {data.get('broker_name')}")
        print(f"  Payment Method: {data.get('payment_method')}")
        print(f"  Payment Status: {data.get('payment_status')}")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
