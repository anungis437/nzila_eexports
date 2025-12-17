# Geographic Configuration - Quick Reference Card

## 📍 Broker Location Setup (Django Admin)

### Create New Broker with Location
1. Navigate to: http://127.0.0.1:8000/admin/commissions/brokertier/
2. Click "Add Broker Tier"
3. Fill required fields:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOCATION & NETWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Country:  [Côte d'Ivoire ▼]  (16 African choices)
City:     [Abidjan________]
Timezone: [Africa/Abidjan ▼]  (7 African zones)
Qualified Buyers Network: [15]
Buyer Conversion Rate: [12.50]%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Country Codes (Most Common)
```
CI = Côte d'Ivoire  [DEFAULT]
SN = Senegal
NG = Nigeria
GH = Ghana
KE = Kenya
```

### Timezone Codes (Most Common)
```
Africa/Abidjan = GMT (CI, GH, SN, BJ, TG)  [DEFAULT]
Africa/Lagos   = WAT (NG, CM) = GMT+1
Africa/Nairobi = EAT (KE, TZ, UG) = GMT+3
```

---

## 🌍 Frontend Filtering (Browser)

### Broker View
```
URL: http://localhost:5174/commissions
Login as: broker user
See: [Filter by Country ▼]
Options:
  • All Countries
  • Côte d'Ivoire
  • Senegal
  • Nigeria
  • Ghana
  • ... (12 more)
```

### Dealer View
```
URL: http://localhost:5174/commissions
Login as: dealer user
See: [Filter by Province ▼]
Options:
  • All Provinces
  • Ontario
  • Quebec
  • British Columbia
  • ... (10 more)
```

---

## 🔌 API Endpoints (Direct Testing)

### Get All Brokers
```http
GET http://127.0.0.1:8000/api/v1/commissions/broker-tiers/leaderboard/

Returns: All brokers (top 50 by volume)
```

### Filter by Country
```http
GET http://127.0.0.1:8000/api/v1/commissions/broker-tiers/leaderboard/?country=CI

Returns: Only Côte d'Ivoire brokers
```

### Filter by Specific Country
```http
?country=CI  → Côte d'Ivoire
?country=SN  → Senegal
?country=NG  → Nigeria
?country=GH  → Ghana
?country=KE  → Kenya
```

---

## 💾 Database Quick Queries

### Django Shell Commands
```bash
python manage.py shell
```

```python
# Count brokers by country
from commissions.models import BrokerTier
for country in ['CI', 'SN', 'NG', 'GH', 'KE']:
    count = BrokerTier.objects.filter(country=country).count()
    print(f"{country}: {count} brokers")

# List all brokers with locations
brokers = BrokerTier.objects.all().values(
    'broker__username', 'country', 'city', 'timezone',
    'qualified_buyers_network', 'buyer_conversion_rate'
)
for b in brokers:
    print(b)

# Get top broker from Côte d'Ivoire
top_ci_broker = BrokerTier.objects.filter(country='CI').order_by('-total_volume').first()
print(f"Top CI broker: {top_ci_broker.broker.username}, Volume: {top_ci_broker.total_volume}")
```

---

## 🧪 Test Data Templates

### Côte d'Ivoire Broker
```
Username: broker_abidjan
Email: abidjan@nzila-export.com
Country: CI (Côte d'Ivoire)
City: Abidjan
Timezone: Africa/Abidjan
Qualified Buyers: 15
Conversion Rate: 12.50%
Current Tier: Bronze
Deals This Month: 3
Volume This Month: 45,000.00 CAD
```

### Senegalese Broker
```
Username: broker_dakar
Email: dakar@nzila-export.com
Country: SN (Senegal)
City: Dakar
Timezone: Africa/Dakar
Qualified Buyers: 22
Conversion Rate: 18.00%
Current Tier: Silver
Deals This Month: 8
Volume This Month: 120,000.00 CAD
```

### Nigerian Broker
```
Username: broker_lagos
Email: lagos@nzila-export.com
Country: NG (Nigeria)
City: Lagos
Timezone: Africa/Lagos
Qualified Buyers: 8
Conversion Rate: 8.30%
Current Tier: Bronze
Deals This Month: 2
Volume This Month: 28,000.00 CAD
```

### Ghanaian Broker
```
Username: broker_accra
Email: accra@nzila-export.com
Country: GH (Ghana)
City: Accra
Timezone: Africa/Abidjan  (Ghana uses GMT like CI)
Qualified Buyers: 12
Conversion Rate: 15.75%
Current Tier: Silver
Deals This Month: 6
Volume This Month: 85,000.00 CAD
```

---

## 🛠️ Geolocation Utilities (Python)

### Geocode Location
```python
from commissions.geo_utils import geocode_location

coords = geocode_location('Abidjan', 'Côte d\'Ivoire')
# Returns: {'latitude': 5.3411, 'longitude': -4.0289}
```

### Calculate Distance
```python
from commissions.geo_utils import calculate_distance

# Abidjan → Dakar
distance = calculate_distance((5.3411, -4.0289), (14.6937, -17.4441))
# Returns: ~1800.0 km
```

### Shipping Distance to Canada
```python
from commissions.geo_utils import get_shipping_distance_to_canada

shipping = get_shipping_distance_to_canada((5.3411, -4.0289))
# Returns: {
#   'nearest_port': 'Halifax',
#   'distance_km': 6670,
#   'distance_nm': 3600,
#   'estimated_days': 7
# }
```

### Get Currency for Country
```python
from commissions.geo_utils import get_currency_for_country

currency_ci = get_currency_for_country('CI')
# Returns: {'code': 'XOF', 'name': 'CFA Franc BCEAO', 'symbol': 'CFA'}

currency_ng = get_currency_for_country('NG')
# Returns: {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦'}
```

### Convert to Local Time
```python
from django.utils import timezone
from commissions.geo_utils import convert_to_local_time

utc_now = timezone.now()
local_time = convert_to_local_time(utc_now, 'Africa/Abidjan')
# Returns: datetime in GMT timezone
```

---

## 🚨 Common Issues & Solutions

### ❌ Country dropdown not showing
```
Problem: Logged in as dealer instead of broker
Solution: Verify user.user_type === 'broker'
```

### ❌ API returns empty leaderboard
```
Problem: No broker tiers created yet
Solution: Create test brokers in Django admin (see Test Data Templates)
```

### ❌ Country filter doesn't work
```
Problem: API call missing country parameter
Solution: Check Network tab, verify ?country=CI is sent
```

### ❌ Geocoding fails
```
Problem: No internet or rate limit
Solution: Wait 1-2 seconds between requests, results are cached
```

### ❌ Migration not applied
```
Problem: Database out of sync
Solution: python manage.py migrate commissions
```

---

## 📊 Expected Response Schema

### Broker Leaderboard API Response
```json
[
  {
    "id": 1,
    "broker": 1,
    "broker_name": "broker_abidjan",
    "broker_email": "abidjan@nzila-export.com",
    "current_tier": "bronze",
    "commission_rate": "5.00",
    
    // NEW FIELDS
    "country": "CI",
    "city": "Abidjan",
    "timezone": "Africa/Abidjan",
    "qualified_buyers_network": 15,
    "buyer_conversion_rate": "12.50",
    
    "deals_this_month": 3,
    "volume_this_month": "45000.00",
    "total_deals": 3,
    "total_volume": "45000.00",
    "last_reset": "2025-05-01T00:00:00Z"
  }
]
```

---

## ✅ Quick Testing Checklist

### Phase 1: Frontend (5 min)
- [ ] Open http://localhost:5174/commissions
- [ ] Login as broker → see country dropdown
- [ ] Login as dealer → see province dropdown
- [ ] No console errors

### Phase 2: Create Data (10 min)
- [ ] Open http://127.0.0.1:8000/admin/
- [ ] Create 4 test brokers (CI, SN, NG, GH)
- [ ] Set location fields for each
- [ ] Set buyer network metrics

### Phase 3: Test Filtering (5 min)
- [ ] Refresh leaderboard
- [ ] Filter by Côte d'Ivoire → see CI brokers only
- [ ] Filter by Senegal → see SN brokers only
- [ ] Filter by All Countries → see all brokers

### Phase 4: API Testing (5 min)
- [ ] Test /leaderboard/ → returns all
- [ ] Test /leaderboard/?country=CI → returns CI only
- [ ] Verify response includes location fields

---

## 📖 Full Documentation

- **Implementation Guide**: `docs/AFRICAN_BROKER_SUPPORT.md`
- **Configuration Guide**: `docs/GEOGRAPHIC_CONFIGURATION.md`
- **Package Usage**: `docs/GEOLOCATION_PACKAGES_GUIDE.md`
- **Testing Guide**: `docs/TESTING_GEOGRAPHIC_CONFIG.md`
- **Visual Reference**: `docs/GEOGRAPHIC_VISUAL_REFERENCE.md`
- **Phase Summary**: `docs/PHASE_11_COMPLETE.md`

---

## 🎯 Next Steps

### P0 - Test in Browser (Now)
```
1. Open http://localhost:5174
2. Verify country/province filtering works
3. Check for console errors
```

### P1 - Create Test Data (Today)
```
1. Create 4 broker tiers with African locations
2. Test country filtering with real data
3. Verify buyer network metrics display
```

### P2 - Advanced Features (This Week)
```
1. Add IP-based country detection
2. Show shipping distance in UI
3. Display buyer network stats
4. Add currency conversion
```

---

**Status**: ✅ Ready for Testing
**Priority**: P0 - Critical
**Time Estimate**: 25 minutes for complete validation
