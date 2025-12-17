# Geographic Configuration for Brokers & Dealers

## Overview
The Nzila Export platform serves two distinct user groups with different geographic distributions:

- **Brokers**: Primarily based in **Côte d'Ivoire (CIV)** and other **African countries**
- **Dealers**: Always **Canadian**, distributed across all provinces and territories

## Broker Geographic Configuration

### Primary Markets
**Most brokers operate from West Africa**, with Côte d'Ivoire (Abidjan) as the primary hub:

```python
# Default settings for new brokers
country = 'CI'  # Côte d'Ivoire (default)
timezone = 'Africa/Abidjan'  # GMT (no DST)
preferred_language = 'fr'  # French (bilingual support)
```

### Supported African Countries
The platform supports 16 African countries:

| Country Code | Country Name | Timezone | Currency |
|--------------|--------------|----------|----------|
| **CI** | **Côte d'Ivoire** (Primary) | Africa/Abidjan (GMT) | XOF/USD |
| SN | Senegal | Africa/Abidjan (GMT) | XOF |
| GH | Ghana | Africa/Abidjan (GMT) | GHS |
| NG | Nigeria | Africa/Lagos (WAT) | NGN |
| BJ | Benin | Africa/Lagos (WAT) | XOF |
| TG | Togo | Africa/Abidjan (GMT) | XOF |
| BF | Burkina Faso | Africa/Abidjan (GMT) | XOF |
| ML | Mali | Africa/Abidjan (GMT) | XOF |
| CM | Cameroon | Africa/Lagos (WAT) | XAF |
| CD | DR Congo | Africa/Lagos (WAT) | CDF |
| KE | Kenya | Africa/Nairobi (EAT) | KES |
| ZA | South Africa | Africa/Johannesburg (SAST) | ZAR |
| MA | Morocco | Africa/Casablanca (WET) | MAD |
| TN | Tunisia | Africa/Tunis (CET) | TND |
| EG | Egypt | Africa/Cairo (EET) | EGP |
| OTHER | Other African countries | - | - |

### Broker Tier Model Fields
```python
class BrokerTier(models.Model):
    # Location tracking
    country = models.CharField(max_length=10, default='CI')
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='Africa/Abidjan')
    
    # Buyer network metrics (critical for overseas buyers)
    qualified_buyers_network = models.IntegerField(default=0)
    buyer_conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
```

### Timezone Configuration
**Current system timezone**: `America/Toronto` (Django settings)
- This is **appropriate** as all deals are for Canadian vehicles
- All timestamps stored in UTC (Django `USE_TZ = True`)
- Broker activity displayed in their local timezone:
  - **West Africa (CIV, SN, GH, TG, BF, ML)**: GMT (UTC+0)
  - **West Africa Central (NG, BJ, CM)**: WAT (UTC+1)
  - **East Africa (KE)**: EAT (UTC+3)
  - **South Africa**: SAST (UTC+2)
  - **Egypt**: EET (UTC+2)

### Language Support
```python
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),  # Critical for CIV brokers
]
```

**Recommendation**: 
- Set `preferred_language = 'fr'` for brokers in CIV, SN, BJ, TG, BF, ML, CM, CD, MA, TN
- Set `preferred_language = 'en'` for brokers in GH, NG, KE, ZA, EG

## Dealer Geographic Configuration

### Canadian Provinces & Territories
All dealers are Canadian, tracked by 13 provinces/territories:

```python
PROVINCE_CHOICES = [
    ('ON', 'Ontario'),           # Most dealers
    ('QC', 'Quebec'),            # French-speaking
    ('BC', 'British Columbia'),
    ('AB', 'Alberta'),
    ('SK', 'Saskatchewan'),
    ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'),     # Bilingual
    ('NS', 'Nova Scotia'),
    ('PE', 'Prince Edward Island'),
    ('NL', 'Newfoundland and Labrador'),
    ('YT', 'Yukon'),
    ('NT', 'Northwest Territories'),
    ('NU', 'Nunavut'),
]
```

### Dealer Tier Model Fields
```python
class DealerTier(models.Model):
    # Canadian location tracking
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    is_rural = models.BooleanField(default=False)
    is_first_nations = models.BooleanField(default=False)
    
    # Canadian certifications
    omvic_certified = models.BooleanField(default=False)  # Ontario
    amvic_certified = models.BooleanField(default=False)  # Alberta
```

### Canadian Bonuses
Special bonuses apply to Canadian dealers based on location:
- **Rural Bonus**: +$250 for dealers in rural areas
- **First Nations Partnership**: +$500 for Indigenous partnerships
- **Certification Bonus**: +$1000 one-time for OMVIC/AMVIC certification

## Leaderboard Filtering

### Broker Leaderboard
```
Filter Options:
- Period: Month | All-Time
- Country: All Countries | CI | SN | GH | NG | ... (16 options)

Display Fields:
- Rank, Name, Deals, Volume, Tier, Commission Rate
- Country, City (shows broker location)
```

### Dealer Leaderboard
```
Filter Options:
- Period: Quarter | All-Time
- Province: All Provinces | ON | QC | BC | AB | ... (13 options)

Display Fields:
- Rank, Name, Deals, Volume, Tier, Commission Rate
- Province (shows dealer location)
```

## Critical Business Challenge: Finding Qualified Buyers Overseas

### The Problem
As noted: **"hardest part in all this is finding qualified buyers overseas"**

### Tracking Broker Performance on Buyer Acquisition
New fields added to `BrokerTier` model:

```python
# Broker buyer network metrics
qualified_buyers_network = models.IntegerField(
    default=0,
    help_text='Number of verified buyers this broker has connected'
)

buyer_conversion_rate = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=Decimal('0.00'),
    help_text='% of introductions that result in deals'
)
```

### Recommended Incentives for Buyer Acquisition
Consider implementing:

1. **Buyer Introduction Bonus**: +$100 for each verified buyer added to network
2. **High Conversion Rate Bonus**: Additional 0.5% commission for brokers with >30% conversion rate
3. **Buyer Network Milestone Bonuses**:
   - 10 qualified buyers: +$500
   - 25 qualified buyers: +$1,500
   - 50 qualified buyers: +$3,000
   - 100+ qualified buyers: +$7,500

4. **Regional Expansion Bonus**: +$1,000 for first broker to establish network in new African country

### Buyer Qualification Criteria
Define "qualified buyer" as:
- ✅ Verified contact information
- ✅ Financial pre-qualification (proof of funds or financing approval)
- ✅ Import license/documentation (if required in their country)
- ✅ Shipping/logistics partner identified
- ✅ At least one vehicle inquiry or bid submitted

## Implementation Checklist

### Backend ✅
- [x] Add country, city, timezone fields to BrokerTier model
- [x] Add qualified_buyers_network and buyer_conversion_rate fields
- [x] Update leaderboard API to support country filtering
- [x] Create migration: 0003_add_broker_location_fields.py

### Frontend ✅
- [x] Add AFRICAN_COUNTRIES list to Leaderboard component
- [x] Update locationFilter to support broker countries
- [x] Show country/city in broker leaderboard display
- [x] Conditional rendering: countries for brokers, provinces for dealers

### Database Migration 🔲
```bash
# Run migration to add new fields
python manage.py migrate commissions

# Set default country for existing brokers
python manage.py shell
>>> from commissions.models import BrokerTier
>>> BrokerTier.objects.update(country='CI', timezone='Africa/Abidjan')
```

### Admin Configuration 🔲
Update Django admin to show:
- Broker location (country, city, timezone) in list display
- Filter brokers by country
- Inline editing for qualified_buyers_network
- Display buyer_conversion_rate in broker tier details

### Future Enhancements 🔲
1. **Buyer Dashboard**: Separate portal for qualified buyers to browse inventory
2. **Broker Buyer Network Management**: CRM-style interface for brokers to track buyer leads
3. **Automated Matching**: AI-powered vehicle recommendations based on buyer preferences
4. **Multi-Language Support**: Expand beyond EN/FR to include Portuguese (Angola, Mozambique)
5. **Regional Heatmaps**: Visual analytics showing broker density and performance by country
6. **Shipping Integration**: Partner APIs for freight forwarding to African ports

## Currency Considerations

### Current State
- All commission calculations in **CAD** (Canadian Dollars)
- Multi-currency support exists in `deals` app
- Exchange rates hardcoded (need API integration)

### Recommendations for African Brokers
1. **Display commissions in local currency** with real-time FX rates
2. **Payment methods**: Wire transfer, mobile money (M-Pesa, Orange Money), crypto
3. **Currency zones**:
   - **XOF (West African CFA Franc)**: CI, SN, BJ, TG, BF, ML
   - **NGN (Nigerian Naira)**: Nigeria
   - **GHS (Ghanaian Cedi)**: Ghana
   - **USD (US Dollar)**: Universal fallback

### Exchange Rate API Integration (TODO)
```python
# Recommended: Use exchangerate-api.com or fixer.io
EXCHANGE_RATE_API_KEY = env('EXCHANGE_RATE_API_KEY', default='')
SUPPORTED_CURRENCIES = ['CAD', 'USD', 'EUR', 'XOF', 'NGN', 'GHS', 'ZAR']
```

## Conclusion

The system is now configured to properly track and support:
✅ **African brokers** (primarily CIV-based) with country/timezone/language support  
✅ **Canadian dealers** with full provincial tracking and certification bonuses  
✅ **Buyer network metrics** to address the challenge of finding qualified overseas buyers  
✅ **Geographic leaderboards** to drive competition within regions  

**Next critical steps**:
1. Run migration to apply new broker fields
2. Update Django admin for broker location management
3. Implement buyer introduction bonuses to incentivize broker buyer acquisition
4. Integrate real-time exchange rate API for multi-currency support
