import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from accounts.models import User
from rest_framework.authtoken.models import Token

# Get Moussa
moussa = User.objects.get(email='moussa.traoré@buyer.com')
print(f"User: {moussa.email} (role: {moussa.role})")

# Get or create token
token, created = Token.objects.get_or_create(user=moussa)
print(f"Token: {token.key}")

# Make the HTTP request
import requests
time.sleep(2)  # Wait for server to be ready

try:
    url = 'http://localhost:8000/api/deals/deals/'
    headers = {'Authorization': f'Token {token.key}'}
    
    print(f"\nRequesting: {url}")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Got {len(data.get('results', []))} deals")
    else:
        print(f"Error Response:")
        print(response.text[:1000])
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
