import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from analytics.views import dashboard_stats

User = get_user_model()

# Get Moussa
moussa = User.objects.get(email='moussa.traoré@buyer.com')
print(f"Testing dashboard stats for: {moussa.email}")
print(f"Role: {moussa.role}")

# Create a mock request
factory = RequestFactory()
request = factory.get('/api/analytics/dashboard-stats/')
request.user = moussa

# Call the view
response = dashboard_stats(request)
print(f"\nResponse status: {response.status_code}")
print(f"Response data:")
for key, value in response.data.items():
    print(f"  {key}: {value}")

# Verify deals count directly
from deals.models import Deal
deals_for_moussa = Deal.objects.filter(buyer=moussa).count()
print(f"\nDirect query - Deals for Moussa: {deals_for_moussa}")

active_deals = Deal.objects.filter(
    buyer=moussa,
    status__in=['pending_docs', 'docs_verified', 'payment_pending', 'payment_received', 'ready_to_ship', 'shipped']
).count()
print(f"Direct query - Active deals: {active_deals}")
