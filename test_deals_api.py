import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from accounts.models import User
from deals.models import Deal
from rest_framework.test import APIRequestFactory
from deals.views import DealViewSet
from rest_framework.request import Request

# Get Moussa
moussa = User.objects.get(email='moussa.traoré@buyer.com')
print(f"Testing as user: {moussa.email} (role: {moussa.role})")

# Create a test request
factory = APIRequestFactory()
request = factory.get('/api/deals/deals/')
request.user = moussa

# Try to get the queryset
try:
    viewset = DealViewSet()
    viewset.request = Request(request)
    viewset.format_kwarg = None
    queryset = viewset.get_queryset()
    print(f"\nQueryset count: {queryset.count()}")
    for deal in queryset:
        print(f"  Deal #{deal.id}: {deal.vehicle} - Status: {deal.status}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
