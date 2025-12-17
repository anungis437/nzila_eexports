import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicles.models import Vehicle

print("Vehicle Status Distribution:")
for status in ['available', 'reserved', 'sold', 'pending']:
    count = Vehicle.objects.filter(status=status).count()
    print(f"  {status}: {count}")

print(f"\nTotal vehicles: {Vehicle.objects.count()}")
print(f"\nFirst 3 available vehicles:")
for v in Vehicle.objects.filter(status='available')[:3]:
    print(f"  - {v.year} {v.make} {v.model} (ID: {v.id}, Status: {v.status})")
