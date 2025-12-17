import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from deals.views import DealViewSet
from accounts.models import User

# Get Moussa
moussa = User.objects.get(email='moussa.traoré@buyer.com')
print(f"Testing API as: {moussa.email}")

# Create a request
factory = RequestFactory()
request = factory.get('/api/deals/deals/')
force_authenticate(request, user=moussa)

# Get the viewset
view = DealViewSet.as_view({'get': 'list'})

# Make the request
try:
    print("Making API request...")
    response = view(request)
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        # Check if it's paginated or a list
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            deals = data['results']
        else:
            deals = data
        
        print(f"Success! Returned {len(deals)} deals")
        for deal in deals:
            print(f"  Deal #{deal['id']}")
            print(f"    Vehicle: {deal.get('vehicle_details', {}).get('make', 'N/A') if isinstance(deal.get('vehicle_details'), dict) else 'N/A'}")
            print(f"    Status: {deal.get('status', 'N/A')}")
            print(f"    Has commission_cad: {'commission_cad' in deal}")
            print(f"    Has buyer_name: {'buyer_name' in deal}")
            print(f"    Has broker_name: {'broker_name' in deal}")
    else:
        print(f"Error response: {response.data}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
