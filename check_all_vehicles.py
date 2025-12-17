import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicles.models import Vehicle

print("All vehicles with their statuses:")
for v in Vehicle.objects.all():
    print(f"  ID {v.id}: {v.year} {v.make} {v.model} - Status: {v.status}")
