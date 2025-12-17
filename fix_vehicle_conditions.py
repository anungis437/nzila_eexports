"""
Script to fix vehicle condition values in the database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicles.models import Vehicle

print("=" * 60)
print("FIXING VEHICLE CONDITION VALUES")
print("=" * 60)

# Bulk update using QuerySet.update() for efficiency
excellent_count = Vehicle.objects.filter(condition='excellent').update(condition='used_excellent')
good_count = Vehicle.objects.filter(condition='good').update(condition='used_good')
fair_count = Vehicle.objects.filter(condition='fair').update(condition='used_fair')

print(f"\n✅ Updated vehicles:")
print(f"  excellent → used_excellent: {excellent_count}")
print(f"  good → used_good: {good_count}")
print(f"  fair → used_fair: {fair_count}")
print(f"  Total fixed: {excellent_count + good_count + fair_count}")

# Verify the fix
print("\n" + "=" * 60)
print("VERIFICATION - Vehicle counts by condition:")
print("=" * 60)
conditions = ['new', 'used_excellent', 'used_good', 'used_fair']
total = 0
for condition in conditions:
    count = Vehicle.objects.filter(condition=condition).count()
    total += count
    print(f"  {condition.ljust(20)}: {count} vehicles")

print(f"  {'TOTAL'.ljust(20)}: {total} vehicles")

# Check for any remaining invalid conditions
print("\n" + "=" * 60)
print("CHECKING FOR INVALID CONDITIONS:")
print("=" * 60)
all_vehicles = Vehicle.objects.all()
valid_conditions = ['new', 'used_excellent', 'used_good', 'used_fair']
invalid = [v for v in all_vehicles if v.condition not in valid_conditions]

if invalid:
    print(f"⚠️  Found {len(invalid)} vehicles with invalid conditions:")
    for v in invalid[:10]:
        print(f"   - ID {v.id}: {v.year} {v.make} {v.model} (condition: '{v.condition}')")
else:
    print("✅ All vehicles have valid conditions!")

print("\n" + "=" * 60)
print("✅ CONDITION VALUES FIXED SUCCESSFULLY")
print("=" * 60)
