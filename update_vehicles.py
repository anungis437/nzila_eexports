import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicles.models import Vehicle

# Make more vehicles available for buyers to see
reserved = Vehicle.objects.filter(status='reserved')
count1 = reserved[:5].update(status='available')

sold = Vehicle.objects.filter(status='sold')
count2 = sold[:2].update(status='available')

print(f'Updated {count1 + count2} vehicles to available status')
print(f'Total available vehicles: {Vehicle.objects.filter(status="available").count()}')
print(f'Total vehicles: {Vehicle.objects.count()}')
