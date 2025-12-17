# Geolocation Packages Guide

## Packages Added to requirements.txt

### 1. **pytz** (Timezone Database)
**Purpose**: Complete IANA timezone database  
**Use Cases**:
- Convert broker activity timestamps from UTC to local African time
- Display leaderboard updates in broker's timezone
- Schedule notifications based on broker's local time

**Example Usage**:
```python
import pytz
from django.utils import timezone

# Get broker's local time
broker_tz = pytz.timezone(broker_tier.timezone)  # 'Africa/Abidjan'
local_time = timezone.now().astimezone(broker_tz)

# Display in broker's timezone
print(f"Deal completed at: {local_time.strftime('%I:%M %p %Z')}")
# Output: "Deal completed at: 03:45 PM GMT"
```

**Integration with BrokerTier**:
```python
def get_local_time(self):
    """Return current time in broker's timezone"""
    import pytz
    from django.utils import timezone
    
    tz = pytz.timezone(self.timezone)
    return timezone.now().astimezone(tz)
```

---

### 2. **geopy** (Geocoding & Distance Calculations)
**Purpose**: Convert addresses to coordinates, calculate distances  
**Use Cases**:
- Calculate distance between broker and nearest port (shipping logistics)
- Geocode broker city to get coordinates for maps
- Find nearest dealers to a buyer's location
- Calculate shipping routes from Canadian dealers to African ports

**Example Usage**:
```python
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Geocode broker's city
geolocator = Nominatim(user_agent="nzila_export")
location = geolocator.geocode(f"{broker_tier.city}, {broker_tier.get_country_display()}")
print(f"Coordinates: {location.latitude}, {location.longitude}")

# Calculate distance from Abidjan to Toronto
abidjan = (5.3600, -4.0083)
toronto = (43.6532, -79.3832)
distance = geodesic(abidjan, toronto).kilometers
print(f"Distance: {distance:.0f} km")  # ~7,900 km
```

**Shipping Distance Calculator**:
```python
# Add to BrokerTier model
def distance_to_nearest_canadian_port(self):
    """Calculate shipping distance to Halifax or Vancouver"""
    from geopy.distance import geodesic
    from geopy.geocoders import Nominatim
    
    geolocator = Nominatim(user_agent="nzila_export")
    broker_location = geolocator.geocode(f"{self.city}, {self.get_country_display()}")
    
    if not broker_location:
        return None
    
    # Major Canadian ports
    halifax = (44.6488, -63.5752)
    vancouver = (49.2827, -123.1207)
    
    broker_coords = (broker_location.latitude, broker_location.longitude)
    
    dist_halifax = geodesic(broker_coords, halifax).nautical
    dist_vancouver = geodesic(broker_coords, vancouver).nautical
    
    return min(dist_halifax, dist_vancouver)
```

---

### 3. **django-timezone-field** (Better Timezone Model Field)
**Purpose**: Enhanced timezone field for Django models  
**Use Cases**:
- Replace CharField with proper TimeZoneField
- Form validation for timezone selection
- Automatic timezone conversion in admin

**Migration**:
```python
# Before (current)
timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES)

# After (recommended)
from timezone_field import TimeZoneField

timezone = TimeZoneField(default='Africa/Abidjan')
```

**Benefits**:
- No need for hardcoded TIMEZONE_CHOICES
- Form widgets automatically validate
- Stores timezone objects, not strings

**Update BrokerTier Model**:
```python
from timezone_field import TimeZoneField

class BrokerTier(models.Model):
    # ... existing fields ...
    
    timezone = TimeZoneField(
        default='Africa/Abidjan',
        verbose_name=_('Timezone'),
        help_text=_('Broker local timezone for activity tracking')
    )
```

---

### 4. **geoip2** (IP-Based Geolocation)
**Purpose**: Detect user location from IP address  
**Use Cases**:
- Auto-detect broker country during registration
- Verify broker location matches claimed country (fraud prevention)
- Default timezone based on IP location
- Show localized content based on detected region

**Setup** (requires MaxMind GeoLite2 database):
```python
# settings.py
GEOIP_PATH = BASE_DIR / 'geoip'

# Download GeoLite2 databases (free)
# 1. Sign up at https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
# 2. Download GeoLite2-Country.mmdb and GeoLite2-City.mmdb
# 3. Place in D:\APPS\nzila_eexports\geoip\
```

**Example Usage**:
```python
from django.contrib.gis.geoip2 import GeoIP2

def detect_broker_location(request):
    """Auto-detect broker country from IP"""
    g = GeoIP2()
    ip = get_client_ip(request)
    
    try:
        country = g.country(ip)
        city = g.city(ip)
        
        return {
            'country_code': country['country_code'],  # 'CI'
            'country_name': country['country_name'],  # 'Côte d'Ivoire'
            'city': city['city'],                     # 'Abidjan'
            'timezone': city['time_zone'],            # 'Africa/Abidjan'
        }
    except:
        return None

# In broker registration view
location = detect_broker_location(request)
if location:
    broker_tier.country = location['country_code']
    broker_tier.city = location['city']
    broker_tier.timezone = location['timezone']
    broker_tier.save()
```

**Helper Function**:
```python
def get_client_ip(request):
    """Get real IP address (handles proxies)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

### 5. **pycountry** (ISO Country/Currency/Language Data)
**Purpose**: Complete ISO 3166-1 country database  
**Use Cases**:
- Validate country codes (CI, SN, GH, etc.)
- Get official country names and currencies
- Map currencies to countries for commission payments
- Language detection for broker preferences

**Example Usage**:
```python
import pycountry

# Get country details
country = pycountry.countries.get(alpha_2='CI')
print(country.name)           # 'Côte d'Ivoire'
print(country.alpha_3)        # 'CIV'
print(country.numeric)        # '384'

# Get currency for country
currency = pycountry.currencies.get(alpha_3='XOF')
print(currency.name)          # 'CFA Franc BCEAO'
print(currency.numeric)       # '952'

# Get languages spoken
languages = [l for l in pycountry.languages if 'fr' in l.alpha_2]
```

**Commission Payment Currency Mapping**:
```python
def get_broker_payment_currency(broker_tier):
    """Get preferred payment currency based on broker country"""
    import pycountry
    
    # Currency mapping for African countries
    COUNTRY_CURRENCIES = {
        'CI': 'XOF',  # West African CFA Franc
        'SN': 'XOF',
        'BJ': 'XOF',
        'TG': 'XOF',
        'BF': 'XOF',
        'ML': 'XOF',
        'NG': 'NGN',  # Nigerian Naira
        'GH': 'GHS',  # Ghanaian Cedi
        'CM': 'XAF',  # Central African CFA Franc
        'CD': 'CDF',  # Congolese Franc
        'KE': 'KES',  # Kenyan Shilling
        'ZA': 'ZAR',  # South African Rand
        'MA': 'MAD',  # Moroccan Dirham
        'TN': 'TND',  # Tunisian Dinar
        'EG': 'EGP',  # Egyptian Pound
    }
    
    currency_code = COUNTRY_CURRENCIES.get(broker_tier.country, 'USD')
    currency = pycountry.currencies.get(alpha_3=currency_code)
    
    return {
        'code': currency.alpha_3,
        'name': currency.name,
        'symbol': get_currency_symbol(currency.alpha_3),
    }
```

---

## Installation

```bash
cd D:\APPS\nzila_eexports
pip install pytz geopy django-timezone-field geoip2 pycountry
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

---

## Recommended Model Updates

### BrokerTier Model Enhancements

```python
from timezone_field import TimeZoneField
from django.contrib.postgres.fields import JSONField  # For coordinates

class BrokerTier(models.Model):
    # ... existing fields ...
    
    # Enhanced timezone field
    timezone = TimeZoneField(
        default='Africa/Abidjan',
        verbose_name=_('Timezone')
    )
    
    # Store geocoded coordinates
    coordinates = JSONField(
        null=True,
        blank=True,
        help_text=_('{"latitude": 5.36, "longitude": -4.01}')
    )
    
    # Detected vs claimed location (fraud prevention)
    claimed_country = models.CharField(max_length=10, choices=COUNTRY_CHOICES)
    detected_country = models.CharField(max_length=10, blank=True)
    location_verified = models.BooleanField(default=False)
    
    def verify_location(self, request):
        """Check if claimed location matches IP location"""
        from django.contrib.gis.geoip2 import GeoIP2
        
        g = GeoIP2()
        ip = get_client_ip(request)
        
        try:
            detected = g.country(ip)
            self.detected_country = detected['country_code']
            self.location_verified = (self.claimed_country == self.detected_country)
            self.save()
        except:
            pass
    
    def geocode_location(self):
        """Get coordinates from city name"""
        from geopy.geocoders import Nominatim
        
        geolocator = Nominatim(user_agent="nzila_export")
        location = geolocator.geocode(f"{self.city}, {self.get_country_display()}")
        
        if location:
            self.coordinates = {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
            self.save()
```

---

## Django Settings Updates

```python
# settings.py

# Timezone support
USE_TZ = True
TIME_ZONE = 'America/Toronto'  # Default for Canadian operations

# GeoIP2 configuration (for IP-based location detection)
GEOIP_PATH = BASE_DIR / 'geoip'

# Geopy settings (for geocoding)
GEOPY_TIMEOUT = 10
GEOPY_USER_AGENT = 'nzila_export_v1'
```

---

## Frontend Integration

### Display Broker's Local Time
```javascript
// frontend/src/utils/timezone.ts
export function convertToLocalTime(utcTime: string, timezone: string): string {
  const date = new Date(utcTime);
  
  return date.toLocaleString('en-US', {
    timeZone: timezone,
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });
}

// Usage in Leaderboard
<span className="text-sm text-gray-500">
  Last active: {convertToLocalTime(broker.last_activity, broker.timezone)}
</span>
```

### Display Distance from Canada
```javascript
// Show shipping distance estimate
<Badge variant="secondary">
  <Ship className="w-3 h-3 mr-1" />
  ~{broker.shipping_distance_km.toLocaleString()} km from Canada
</Badge>
```

---

## Use Case Examples

### 1. **Auto-Detect Broker Location on Registration**
```python
@api_view(['POST'])
def register_broker(request):
    # Auto-detect location
    location = detect_broker_location(request)
    
    user = User.objects.create(
        username=request.data['username'],
        email=request.data['email'],
        role='broker',
        country=location['country_code'] if location else 'CI',
    )
    
    BrokerTier.objects.create(
        broker=user,
        country=location['country_code'] if location else 'CI',
        city=location['city'] if location else '',
        timezone=location['timezone'] if location else 'Africa/Abidjan',
    )
```

### 2. **Calculate Optimal Shipping Routes**
```python
def suggest_shipping_route(broker_tier, vehicle):
    """Suggest best Canadian port for shipping"""
    from geopy.distance import geodesic
    
    # Broker location
    broker_coords = (broker_tier.coordinates['latitude'], 
                    broker_tier.coordinates['longitude'])
    
    # Canadian ports
    ports = {
        'Halifax': (44.6488, -63.5752),
        'Montreal': (45.5017, -73.5673),
        'Vancouver': (49.2827, -123.1207),
    }
    
    distances = {
        port: geodesic(broker_coords, coords).nautical
        for port, coords in ports.items()
    }
    
    nearest_port = min(distances, key=distances.get)
    
    return {
        'port': nearest_port,
        'distance_nm': distances[nearest_port],
        'estimated_days': int(distances[nearest_port] / 500),  # Avg 500 nm/day
    }
```

### 3. **Regional Leaderboard Heat Maps**
```python
def get_broker_heatmap_data():
    """Get broker density by region for analytics"""
    from collections import Counter
    
    broker_locations = BrokerTier.objects.values_list('country', 'city')
    
    country_counts = Counter([loc[0] for loc in broker_locations])
    
    return [
        {
            'country': code,
            'count': count,
            'country_name': dict(BrokerTier.COUNTRY_CHOICES)[code]
        }
        for code, count in country_counts.most_common()
    ]
```

### 4. **Timezone-Aware Notifications**
```python
from celery import shared_task
import pytz
from django.utils import timezone

@shared_task
def send_tier_upgrade_notification(broker_id):
    """Send notification in broker's local business hours"""
    broker_tier = BrokerTier.objects.get(broker_id=broker_id)
    
    # Get broker's local time
    broker_tz = pytz.timezone(broker_tier.timezone)
    local_time = timezone.now().astimezone(broker_tz)
    
    # Only send during business hours (9am - 9pm)
    if 9 <= local_time.hour <= 21:
        send_email_notification(broker_tier.broker)
    else:
        # Reschedule for 9am local time
        next_morning = local_time.replace(hour=9, minute=0) + timedelta(days=1)
        send_tier_upgrade_notification.apply_async(
            args=[broker_id],
            eta=next_morning
        )
```

---

## Next Steps

1. **Install packages**: `pip install -r requirements.txt`
2. **Download GeoIP2 databases**: Sign up at MaxMind, download GeoLite2-City.mmdb
3. **Update BrokerTier model**: Add TimeZoneField and coordinates field
4. **Create migration**: `python manage.py makemigrations`
5. **Geocode existing brokers**: Run script to populate coordinates
6. **Add location verification**: Implement IP-based fraud detection
7. **Build analytics dashboard**: Show broker distribution heat map
8. **Optimize shipping routes**: Calculate nearest port for each broker

---

## Security Considerations

- **GeoIP database updates**: Set up monthly cron job to download latest MaxMind DB
- **Rate limiting**: Geopy/Nominatim has rate limits (1 req/sec for free tier)
- **Caching**: Cache geocoding results to avoid repeated API calls
- **Privacy**: Store only city-level location, not exact coordinates (GDPR compliance)
- **VPN detection**: Some brokers may use VPNs, causing location mismatches

---

## Performance Optimization

```python
# Cache geocoding results
from django.core.cache import cache

def geocode_with_cache(city, country):
    """Geocode with Redis caching"""
    cache_key = f"geocode:{city}:{country}"
    result = cache.get(cache_key)
    
    if not result:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="nzila_export")
        location = geolocator.geocode(f"{city}, {country}")
        
        if location:
            result = {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
            cache.set(cache_key, result, timeout=86400*30)  # Cache 30 days
    
    return result
```

---

## Summary

✅ **pytz** - Handle 7 African timezones + Canadian time  
✅ **geopy** - Calculate shipping distances, geocode cities  
✅ **django-timezone-field** - Better timezone model field  
✅ **geoip2** - Auto-detect broker location from IP (fraud prevention)  
✅ **pycountry** - ISO country/currency data for payments  

These packages address:
- Multi-timezone support (Africa/Abidjan vs America/Toronto)
- Shipping logistics (distance calculations)
- Location verification (detect fraudulent claims)
- Currency mapping (XOF for CIV, NGN for Nigeria, etc.)
- Regional analytics (broker heat maps)
