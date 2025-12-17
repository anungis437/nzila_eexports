# Testing Geographic Configuration - Step-by-Step Guide

## Overview
This guide walks through testing the new African broker support and geographic configuration features.

## Prerequisites
- ✅ Django server running on http://127.0.0.1:8000 (external PowerShell)
- ✅ React server running on http://localhost:5174 (external PowerShell)
- ✅ Migration 0003 applied successfully
- ✅ All geolocation packages installed

## Phase 1: Frontend Validation (10 minutes)

### Step 1: Open Browser
1. Open browser at http://localhost:5174
2. Login with existing credentials
3. Navigate to `/commissions` page

### Step 2: Verify Broker Leaderboard
**If logged in as broker:**
1. Look for "Filter by Country" dropdown (NOT "Filter by Province")
2. Verify dropdown contains:
   - All Countries
   - Côte d'Ivoire
   - Senegal
   - Nigeria
   - Ghana
   - Kenya
   - Tanzania
   - Uganda
   - Rwanda
   - Benin
   - Togo
   - Cameroon
   - South Africa
   - Morocco
   - Tunisia
   - Egypt
   - Other African Country

3. Select different countries and verify:
   - Leaderboard updates (or shows empty state if no data)
   - API call includes `?country=CI` parameter
   - No console errors

### Step 3: Verify Dealer Leaderboard
**If logged in as dealer:**
1. Look for "Filter by Province" dropdown (NOT "Filter by Country")
2. Verify dropdown still contains:
   - All Provinces
   - Ontario
   - Quebec
   - British Columbia
   - Alberta
   - Manitoba
   - Saskatchewan
   - Nova Scotia
   - New Brunswick
   - Newfoundland and Labrador
   - Prince Edward Island
   - Northwest Territories
   - Yukon
   - Nunavut

### Step 4: Check Browser Console
1. Open Developer Tools (F12)
2. Check Console tab for errors
3. Verify no errors related to:
   - Radix UI Select
   - Country/province state
   - API calls

## Phase 2: Create Test Broker Data (20 minutes)

### Step 5: Open Django Admin
1. Navigate to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Go to "Commissions" → "Broker tiers"

### Step 6: Create Ivorian Broker
1. Click "Add Broker Tier"
2. Select or create broker user:
   - Username: `broker_abidjan`
   - Email: `abidjan@nzila-export.com`
3. Fill location fields:
   - **Country**: Côte d'Ivoire
   - **City**: Abidjan
   - **Timezone**: GMT - Abidjan (Côte d'Ivoire)
   - **Qualified Buyers Network**: 15
   - **Buyer Conversion Rate**: 12.50
4. Set tier data:
   - Current Tier: Bronze
   - Deals This Month: 3
   - Volume This Month: 45000.00
5. Save

### Step 7: Create Senegalese Broker
1. Click "Add Broker Tier" again
2. Select or create broker user:
   - Username: `broker_dakar`
   - Email: `dakar@nzila-export.com`
3. Fill location fields:
   - **Country**: Senegal
   - **City**: Dakar
   - **Timezone**: GMT - Dakar (Senegal)
   - **Qualified Buyers Network**: 22
   - **Buyer Conversion Rate**: 18.00
4. Set tier data:
   - Current Tier: Silver
   - Deals This Month: 8
   - Volume This Month: 120000.00
5. Save

### Step 8: Create Nigerian Broker
1. Click "Add Broker Tier" again
2. Select or create broker user:
   - Username: `broker_lagos`
   - Email: `lagos@nzila-export.com`
3. Fill location fields:
   - **Country**: Nigeria
   - **City**: Lagos
   - **Timezone**: WAT - Lagos (Nigeria)
   - **Qualified Buyers Network**: 8
   - **Buyer Conversion Rate**: 8.30
4. Set tier data:
   - Current Tier: Bronze
   - Deals This Month: 2
   - Volume This Month: 28000.00
5. Save

### Step 9: Create Ghanaian Broker (Optional)
1. Click "Add Broker Tier" again
2. Select or create broker user:
   - Username: `broker_accra`
   - Email: `accra@nzila-export.com`
3. Fill location fields:
   - **Country**: Ghana
   - **City**: Accra
   - **Timezone**: GMT - Abidjan (Côte d'Ivoire) [Ghana uses same timezone]
   - **Qualified Buyers Network**: 12
   - **Buyer Conversion Rate**: 15.75
4. Set tier data:
   - Current Tier: Silver
   - Deals This Month: 6
   - Volume This Month: 85000.00
5. Save

## Phase 3: Test Filtering with Real Data (15 minutes)

### Step 10: Refresh Leaderboard
1. Go back to http://localhost:5174/commissions
2. Refresh page (Ctrl+F5)
3. Verify all 4 brokers appear in leaderboard

### Step 11: Test Country Filtering
**Filter by Côte d'Ivoire:**
1. Select "Côte d'Ivoire" from dropdown
2. Verify only `broker_abidjan` appears
3. Check API call: `/api/v1/commissions/broker-tiers/leaderboard/?country=CI`

**Filter by Senegal:**
1. Select "Senegal" from dropdown
2. Verify only `broker_dakar` appears
3. Check API call: `/api/v1/commissions/broker-tiers/leaderboard/?country=SN`

**Filter by Nigeria:**
1. Select "Nigeria" from dropdown
2. Verify only `broker_lagos` appears
3. Check API call: `/api/v1/commissions/broker-tiers/leaderboard/?country=NG`

**Filter by Ghana:**
1. Select "Ghana" from dropdown
2. Verify only `broker_accra` appears
3. Check API call: `/api/v1/commissions/broker-tiers/leaderboard/?country=GH`

**Filter by All Countries:**
1. Select "All Countries" from dropdown
2. Verify all 4 brokers appear
3. Check API call: `/api/v1/commissions/broker-tiers/leaderboard/` (no country param)

### Step 12: Verify Leaderboard Data Display
Check that each broker entry shows:
- ✅ Broker name
- ✅ Email
- ✅ Current tier (Bronze/Silver/Gold/Platinum)
- ✅ Deals this month
- ✅ Volume this month (formatted as currency)
- ✅ Total deals
- ✅ Total volume

**NEW FIELDS (if displayed):**
- ✅ Country (CI, SN, NG, GH)
- ✅ City (Abidjan, Dakar, Lagos, Accra)
- ✅ Timezone (GMT, WAT)
- ✅ Qualified Buyers Network (15, 22, 8, 12)
- ✅ Buyer Conversion Rate (12.50%, 18.00%, 8.30%, 15.75%)

## Phase 4: Test API Directly (10 minutes)

### Step 13: Test API Endpoints
Open browser or Postman and test:

**Get all brokers:**
```
GET http://127.0.0.1:8000/api/v1/commissions/broker-tiers/leaderboard/
```
Expected: Returns all 4 brokers with location fields

**Filter by country (Côte d'Ivoire):**
```
GET http://127.0.0.1:8000/api/v1/commissions/broker-tiers/leaderboard/?country=CI
```
Expected: Returns only `broker_abidjan`

**Filter by country (Senegal):**
```
GET http://127.0.0.1:8000/api/v1/commissions/broker-tiers/leaderboard/?country=SN
```
Expected: Returns only `broker_dakar`

**Invalid country:**
```
GET http://127.0.0.1:8000/api/v1/commissions/broker-tiers/leaderboard/?country=US
```
Expected: Returns empty list (no US brokers)

### Step 14: Verify Response Schema
Check that API response includes new fields:
```json
{
  "id": 1,
  "broker": 1,
  "broker_name": "broker_abidjan",
  "broker_email": "abidjan@nzila-export.com",
  "current_tier": "bronze",
  "country": "CI",
  "city": "Abidjan",
  "timezone": "Africa/Abidjan",
  "qualified_buyers_network": 15,
  "buyer_conversion_rate": "12.50",
  "deals_this_month": 3,
  "volume_this_month": "45000.00",
  "total_deals": 3,
  "total_volume": "45000.00"
}
```

## Phase 5: Test Geolocation Utilities (Optional - 15 minutes)

### Step 15: Test Geocoding
Open Django shell:
```bash
python manage.py shell
```

```python
from commissions.geo_utils import geocode_location, calculate_distance, get_shipping_distance_to_canada

# Geocode Abidjan
coords_abidjan = geocode_location('Abidjan', 'Côte d\'Ivoire')
print(f"Abidjan coordinates: {coords_abidjan}")
# Expected: {'latitude': 5.3411, 'longitude': -4.0289}

# Geocode Dakar
coords_dakar = geocode_location('Dakar', 'Senegal')
print(f"Dakar coordinates: {coords_dakar}")
# Expected: {'latitude': 14.6937, 'longitude': -17.4441}

# Calculate distance between Abidjan and Dakar
if coords_abidjan and coords_dakar:
    distance = calculate_distance(
        (coords_abidjan['latitude'], coords_abidjan['longitude']),
        (coords_dakar['latitude'], coords_dakar['longitude'])
    )
    print(f"Distance Abidjan → Dakar: {distance:.0f} km")
    # Expected: ~1,800 km

# Calculate shipping distance to Canada
shipping = get_shipping_distance_to_canada(
    (coords_abidjan['latitude'], coords_abidjan['longitude'])
)
print(f"Nearest Canadian port: {shipping['nearest_port']}")
print(f"Distance: {shipping['distance_nm']:.0f} nautical miles")
print(f"Estimated shipping: {shipping['estimated_days']} days")
# Expected: Halifax, ~3,600 nm, ~7 days
```

### Step 16: Test Currency Mapping
```python
from commissions.geo_utils import get_currency_for_country

# Test CFA countries (CI, SN, BJ, TG)
print(get_currency_for_country('CI'))
# Expected: {'code': 'XOF', 'name': 'CFA Franc BCEAO', 'symbol': 'CFA'}

print(get_currency_for_country('NG'))
# Expected: {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦'}

print(get_currency_for_country('GH'))
# Expected: {'code': 'GHS', 'name': 'Ghanaian Cedi', 'symbol': '₵'}

print(get_currency_for_country('KE'))
# Expected: {'code': 'KES', 'name': 'Kenyan Shilling', 'symbol': 'KSh'}
```

### Step 17: Test Timezone Conversion
```python
from django.utils import timezone
from commissions.geo_utils import convert_to_local_time

# Get current UTC time
utc_now = timezone.now()
print(f"UTC time: {utc_now}")

# Convert to Abidjan time (GMT)
abidjan_time = convert_to_local_time(utc_now, 'Africa/Abidjan')
print(f"Abidjan time: {abidjan_time}")

# Convert to Lagos time (WAT = GMT+1)
lagos_time = convert_to_local_time(utc_now, 'Africa/Lagos')
print(f"Lagos time: {lagos_time}")

# Convert to Nairobi time (EAT = GMT+3)
nairobi_time = convert_to_local_time(utc_now, 'Africa/Nairobi')
print(f"Nairobi time: {nairobi_time}")
```

## Expected Results Summary

### ✅ Success Criteria
1. **Frontend:**
   - Broker users see country dropdown (16 African countries)
   - Dealer users see province dropdown (13 Canadian provinces)
   - Country filtering works correctly
   - No console errors

2. **Backend:**
   - Migration applied successfully
   - BrokerTier model has 5 new fields (country, city, timezone, qualified_buyers_network, buyer_conversion_rate)
   - API returns location data in leaderboard
   - Country filtering parameter works

3. **Admin Interface:**
   - Location & Network fieldset visible
   - Can create broker tiers with African locations
   - Can filter brokers by country/timezone

4. **Geolocation Utilities:**
   - Geocoding returns valid coordinates
   - Distance calculations work
   - Shipping distance calculator works
   - Currency mapping returns correct codes
   - Timezone conversion works

## Common Issues and Solutions

### Issue: Country dropdown not showing
**Cause:** Logged in as dealer instead of broker
**Solution:** Login as broker user or check user role

### Issue: API returns empty leaderboard
**Cause:** No broker tiers created yet
**Solution:** Create test broker data in Django admin (Step 6-9)

### Issue: Country filter not working
**Cause:** API endpoint not receiving country parameter
**Solution:** Check API call in Network tab, verify country parameter is sent

### Issue: Geocoding fails
**Cause:** No internet connection or Nominatim API limit
**Solution:** Check internet connection, wait a few seconds between requests

### Issue: GeoIP2 detection fails
**Cause:** GeoIP2 database not configured
**Solution:** This is expected - GeoIP2 requires separate database download (optional feature)

## Next Steps After Testing

Once all tests pass:

1. **P1 - Enhance Leaderboard Display:**
   - Show country flags next to broker names
   - Display buyer network stats (qualified_buyers_network, buyer_conversion_rate)
   - Add timezone indicator in leaderboard

2. **P2 - Implement Auto-Detection:**
   - Add IP-based country detection on broker registration
   - Show warning if detected country differs from claimed country
   - Optional: Auto-populate city based on IP

3. **P3 - Add Shipping Calculator:**
   - Show estimated shipping distance/time to nearest Canadian port
   - Calculate shipping costs based on distance
   - Display in broker dashboard

4. **P4 - Currency Support:**
   - Show broker commission values in local currency (XOF, NGN, GHS, etc.)
   - Add currency conversion rates
   - Support multi-currency payouts

5. **P5 - Regional Analytics:**
   - Create heat map of broker distribution
   - Show top countries by deal volume
   - Regional leaderboards (West Africa, East Africa, etc.)

## Testing Completion Checklist

- [ ] Frontend leaderboard shows correct dropdown (countries for brokers, provinces for dealers)
- [ ] Country filtering updates leaderboard correctly
- [ ] No browser console errors
- [ ] Created 4 test broker tiers with African locations
- [ ] All brokers appear in leaderboard with location data
- [ ] API country filtering works (tested with ?country=CI, ?country=SN, etc.)
- [ ] Admin interface displays Location & Network fields
- [ ] Geocoding utility returns valid coordinates
- [ ] Distance calculator works (Abidjan → Dakar)
- [ ] Shipping distance calculator returns nearest Canadian port
- [ ] Currency mapping returns correct codes (XOF, NGN, GHS, KES)
- [ ] Timezone conversion works (UTC → GMT, WAT, EAT)

---

**Status:** Ready for testing
**Estimated Time:** 1 hour for complete testing
**Priority:** P0 - Critical validation before continuing development
