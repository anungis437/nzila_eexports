import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from accounts.models import User
from vehicles.models import Vehicle
from vehicles.serializers import VehicleListSerializer

# Get buyer user
buyer = User.objects.get(email='moussa.traoré@buyer.com')
print(f"Testing API for user: {buyer.username} (role: {buyer.role})")

# Test queryset filtering (what the API does)
from vehicles.views import VehicleViewSet

viewset = VehicleViewSet()
queryset = Vehicle.objects.all()

# Simulate what get_queryset does for buyer
if buyer.is_buyer():
    filtered_queryset = queryset.filter(status='available')
    print(f"\nFiltered queryset count: {filtered_queryset.count()}")
    
    # Serialize the data
    serializer = VehicleListSerializer(filtered_queryset, many=True)
    print(f"\nSerialized data count: {len(serializer.data)}")
    
    if serializer.data:
        print("\nFirst 3 vehicles:")
        for vehicle in serializer.data[:3]:
            print(f"  - ID {vehicle['id']}: {vehicle['year']} {vehicle['make']} {vehicle['model']} (status: {vehicle['status']})")
    else:
        print("\nNo vehicles in serialized data!")
        
    # Check if there's pagination
    print(f"\nTotal available vehicles in DB: {Vehicle.objects.filter(status='available').count()}")
else:
    print(f"User is not a buyer!")
