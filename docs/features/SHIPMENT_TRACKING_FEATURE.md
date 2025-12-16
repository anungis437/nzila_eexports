# Shipment Tracking Feature Documentation

## Overview
Complete shipment tracking system for monitoring vehicle exports from origin to destination with real-time updates and status progression.

## Components

### 1. ShipmentCard Component
**File:** `/frontend/src/components/ShipmentCard.tsx` (184 lines)

**Features:**
- **5 Status Colors:** Pending (slate), In Transit (blue), At Customs (amber), Delivered (green), Delayed (red)
- **Progress Bar:** Visual representation (10% → 100% based on status)
- **Route Display:** Origin port → Destination port with country flag
- **Vehicle Info:** Year, make, model, VIN display
- **Date Tracking:** Shows estimated vs actual arrival dates
- **Deal Reference:** Links to parent deal for context
- **Status Icons:** Ship, CheckCircle, AlertTriangle, Clock, Package

**Usage:**
```tsx
<ShipmentCard shipment={shipment} />
```

**Status Workflow:**
1. **Pending** (10% progress) - Awaiting departure
2. **In Transit** (40% progress) - En route to destination
3. **At Customs** (70% progress) - Customs clearance processing
4. **Delivered** (100% progress) - Successfully delivered
5. **Delayed** (red indicator) - Experiencing delays

### 2. ShipmentFormModal Component
**File:** `/frontend/src/components/ShipmentFormModal.tsx` (330 lines)

**Features:**
- **Deal Integration:** Auto-fills vehicle details from deal
- **Required Fields:** Tracking number (unique), shipping company, origin/destination ports
- **Optional Fields:** Destination country, status, estimated dates, notes
- **Date Pickers:** Estimated departure and arrival with Calendar icon
- **Status Dropdown:** 5 status options
- **Form Validation:** Real-time field validation with bilingual errors
- **TanStack Query:** Fetches deal data for context

**Form Fields:**
- `tracking_number` (string, unique, required)
- `shipping_company` (string, required)
- `origin_port` (string, required)
- `destination_port` (string, required)
- `destination_country` (string, optional)
- `status` (enum, default: pending)
- `estimated_departure` (date, optional)
- `estimated_arrival` (date, optional)
- `notes` (text, optional)

**Usage:**
```tsx
<ShipmentFormModal 
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  dealId={dealId}  // Optional - for creating from deal
  shipmentId={id}  // Optional - for editing existing
/>
```

### 3. ShipmentDetailModal Component
**File:** `/frontend/src/components/ShipmentDetailModal.tsx` (425 lines)

**Features:**
- **Two Tabs:** Details and Tracking History
- **Status Advancement:** "Advance to Next Status" button for workflow progression
- **Route Card:** Visual origin → destination with blue gradient
- **Dates Card:** Shows all departure/arrival dates (estimated + actual)
- **Vehicle Card:** Full vehicle details if available
- **Tracking Timeline:** Reverse chronological updates with MapPin icons
- **Add Update Form:** Quick form to add new tracking updates
- **Real-time Updates:** Invalidates queries on status changes

**Details Tab Shows:**
- Route (origin port → destination port)
- All dates (estimated/actual departure and arrival)
- Vehicle information
- Notes

**Tracking Tab Shows:**
- Timeline of all tracking updates
- Location, status, and description for each update
- "Add Tracking Update" form
- Relative timestamps (e.g., "2 hours ago")

**Usage:**
```tsx
<ShipmentDetailModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  shipmentId={shipmentId}
/>
```

### 4. Shipments Page
**File:** `/frontend/src/pages/Shipments.tsx` (260 lines)

**Features:**
- **5 Stat Cards:** Total, In Transit, At Customs, Delivered, Delayed
- **Search:** By tracking number, shipping company, or destination country
- **Status Filter:** Dropdown with all 5 statuses + "All"
- **View Modes:** Grid (3 columns) or List view
- **Empty States:** Contextual messages for no shipments or filtered results
- **Click to Detail:** Opens ShipmentDetailModal on card click

**Stats Display:**
- Total shipments (slate card with Ship icon)
- In Transit count (blue card with TrendingUp icon)
- At Customs count (amber card with Package icon)
- Delivered count (green card with CheckCircle2 icon)
- Delayed count (red card with AlertTriangle icon)

**Filters:**
- Search input (full-text search)
- Status dropdown (all, pending, in_transit, customs, delivered, delayed)
- View toggle (Grid/List icons)

## Backend Implementation

### Models
**File:** `/shipments/models.py`

**Shipment Model:**
```python
class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('customs', 'At Customs'),
        ('delivered', 'Delivered'),
        ('delayed', 'Delayed'),
    ]
    
    deal = models.OneToOneField('deals.Deal', on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, unique=True)
    shipping_company = models.CharField(max_length=200)
    origin_port = models.CharField(max_length=200)
    destination_port = models.CharField(max_length=200)
    destination_country = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_departure = models.DateField(null=True, blank=True)
    actual_departure = models.DateField(null=True, blank=True)
    estimated_arrival = models.DateField(null=True, blank=True)
    actual_arrival = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
```

**ShipmentUpdate Model:**
```python
class ShipmentUpdate(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='updates')
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Serializers
**File:** `/shipments/serializers.py`

**ShipmentSerializer:**
- Includes all shipment fields
- Nested `updates` (ShipmentUpdateSerializer, read-only)
- `vehicle_details` (SerializerMethodField) - Fetches from related deal
- `deal_id` for easy reference

**ShipmentUpdateSerializer:**
- Simple serializer for tracking updates
- Fields: location, status, description, created_at

### ViewSet
**File:** `/shipments/views.py`

**ShipmentViewSet:**
- Extends `ModelViewSet` for full CRUD
- **Filters:** status, destination_country
- **Permissions:** Authenticated users only
- **Query Optimization:** `select_related('deal', 'deal__vehicle')` + `prefetch_related('updates')`

**Custom Actions:**

1. **track** (GET `/shipments/{id}/track/`)
   - Public tracking endpoint
   - Returns full shipment details including updates
   
2. **add_update** (POST `/shipments/{id}/add_update/`)
   - Adds a new tracking update
   - Request body: `{ location, status, description? }`
   - Returns updated shipment with all updates
   
3. **updates** (GET `/shipments/{id}/updates/`)
   - Returns all tracking updates for a shipment
   - Ordered by created_at descending (most recent first)

**User-based Filtering:**
- Buyers see only their shipments (`deal__buyer=user`)
- Dealers see shipments for their deals (`deal__dealer=user`)
- Brokers see shipments they're involved with (`deal__broker=user`)

## API Endpoints

### Shipment CRUD
```
GET    /api/shipments/shipments/          - List all shipments (filtered by user)
POST   /api/shipments/shipments/          - Create new shipment
GET    /api/shipments/shipments/{id}/     - Get shipment details
PATCH  /api/shipments/shipments/{id}/     - Update shipment
DELETE /api/shipments/shipments/{id}/     - Delete shipment
```

### Custom Actions
```
GET    /api/shipments/shipments/{id}/track/      - Track shipment (public)
POST   /api/shipments/shipments/{id}/add_update/ - Add tracking update
GET    /api/shipments/shipments/{id}/updates/    - Get all updates
```

### API Methods
**File:** `/frontend/src/lib/api.ts`

```typescript
async createShipment(data: any)
async updateShipment(id: number, data: any)
async getShipments(params?: any)
async getShipment(id: number)
async addShipmentUpdate(shipmentId: number, data: any)
async getShipmentUpdates(shipmentId: number)
```

## Workflow

### 1. Creating a Shipment
1. Navigate to Shipments page
2. Click "New Shipment" button
3. Fill in required fields (tracking number, company, ports)
4. Optionally link to a deal (auto-fills vehicle details)
5. Set estimated dates
6. Click "Create Shipment"

### 2. Tracking a Shipment
1. View shipment card on Shipments page
2. See current status and progress bar
3. Click card to open detail modal
4. View route, dates, and vehicle info in Details tab
5. Switch to Tracking tab to see update history

### 3. Adding Tracking Updates
1. Open ShipmentDetailModal
2. Navigate to "Tracking" tab
3. Fill in "Add Tracking Update" form:
   - Location (e.g., "Port of Los Angeles")
   - Status (e.g., "Loaded onto vessel")
   - Description (optional details)
4. Click "Add Update"
5. New update appears in timeline immediately

### 4. Advancing Status
1. Open ShipmentDetailModal
2. See current status badge at top
3. Click "Advance to [Next Status]" button
4. Status updates automatically
5. Progress bar updates accordingly

**Status Progression:**
```
Pending → In Transit → At Customs → Delivered
         ↓
      Delayed (can happen at any stage)
```

## Testing Guide

### Manual Testing Checklist

#### 1. Shipment Creation
- [ ] Create shipment without deal reference
- [ ] Create shipment linked to a deal (verify vehicle auto-fill)
- [ ] Verify tracking number uniqueness validation
- [ ] Test with all required fields
- [ ] Test date picker functionality
- [ ] Verify form validation errors

#### 2. Shipment Display
- [ ] View shipments in grid mode
- [ ] View shipments in list mode
- [ ] Verify all 5 stat cards calculate correctly
- [ ] Test search functionality (tracking number, company, country)
- [ ] Test status filter (all 5 statuses + "All")
- [ ] Verify empty state when no shipments

#### 3. Status Management
- [ ] Advance from Pending → In Transit
- [ ] Advance from In Transit → At Customs
- [ ] Advance from At Customs → Delivered
- [ ] Mark as Delayed at any status
- [ ] Verify progress bar updates correctly
- [ ] Check status badge colors

#### 4. Tracking Updates
- [ ] Add update with all fields
- [ ] Add update with only required fields (location, status)
- [ ] Verify timeline displays updates in reverse chronological order
- [ ] Check relative timestamps (e.g., "2 hours ago")
- [ ] Verify MapPin icons appear on timeline

#### 5. User Permissions
- [ ] Buyer sees only their shipments
- [ ] Dealer sees only their deal's shipments
- [ ] Broker sees shipments they're involved with
- [ ] Admin sees all shipments

#### 6. Integration Testing
- [ ] Create deal → Mark as ready_to_ship → Create shipment
- [ ] Verify vehicle details appear in shipment card
- [ ] Track shipment through all statuses
- [ ] Verify real-time updates (query invalidation)

## TypeScript Interfaces

**File:** `/frontend/src/types/index.ts`

```typescript
export interface Shipment {
  id: number
  deal: number
  deal_id: number
  tracking_number: string
  shipping_company: string
  origin_port: string
  destination_port: string
  destination_country?: string
  status: 'pending' | 'in_transit' | 'customs' | 'delivered' | 'delayed'
  estimated_departure?: string
  actual_departure?: string
  estimated_arrival?: string
  actual_arrival?: string
  notes?: string
  updates?: ShipmentUpdate[]
  vehicle_details?: {
    id: number
    year: number
    make: string
    model: string
    vin: string
    color: string
  }
  created_at: string
  updated_at: string
}

export interface ShipmentUpdate {
  id: number
  shipment: number
  location: string
  status: string
  description?: string
  created_at: string
}
```

## Design Patterns

### Color Scheme
- **Pending:** Slate (neutral, waiting)
- **In Transit:** Blue (active movement)
- **At Customs:** Amber (caution, processing)
- **Delivered:** Green (success)
- **Delayed:** Red (alert)

### Icons Used
- **Ship:** Main shipment icon, in-transit status
- **Package:** Vehicle/cargo representation, customs status
- **CheckCircle2:** Delivered status
- **AlertTriangle:** Delayed status
- **Clock:** Pending status
- **MapPin:** Location markers in timeline
- **TrendingUp:** In-transit stat card, route arrow
- **Calendar:** Date fields
- **Plus:** Add shipment/update buttons
- **Navigation:** Route card icon
- **Search, Filter, Grid3x3, List:** UI controls

### Progress Calculation
```typescript
const progressPercentages = {
  pending: 10,
  in_transit: 40,
  customs: 70,
  delivered: 100,
  delayed: 40 // Same as in_transit but with red color
}
```

## Future Enhancements

1. **Google Maps Integration**
   - Show real-time shipment location on map
   - Display route visualization
   - Port location markers

2. **Email Notifications**
   - Status change alerts to buyers
   - Arrival/departure notifications
   - Delay alerts

3. **SMS Tracking**
   - Text message updates for buyers
   - Tracking link via SMS

4. **Document Attachments**
   - Bill of lading upload
   - Customs documents
   - Delivery confirmation photos

5. **Estimated Delivery Calculator**
   - AI-powered arrival predictions
   - Historical data analysis
   - Weather/route-based adjustments

6. **Batch Shipment Creation**
   - Create multiple shipments at once
   - CSV import for bulk shipping

7. **Carrier API Integration**
   - Auto-fetch updates from shipping companies
   - Real-time tracking without manual entry

8. **Customer Portal**
   - Public tracking page with access code
   - No login required for buyers
   - Branded tracking experience

## Troubleshooting

### Common Issues

**Issue:** Tracking updates not appearing
- **Solution:** Check that `add_update` action is properly configured in backend
- Verify `updates` relationship is prefetched in queryset

**Issue:** Vehicle details not showing
- **Solution:** Ensure deal has a vehicle associated
- Check `vehicle_details` SerializerMethodField in ShipmentSerializer

**Issue:** Status advancement not working
- **Solution:** Verify user has permission (dealer/admin)
- Check status workflow logic in ShipmentDetailModal

**Issue:** Search not finding shipments
- **Solution:** Verify lowercase conversion in filter
- Check that fields being searched exist

## Performance Optimizations

1. **Query Optimization:**
   - `select_related('deal', 'deal__vehicle')` - Reduces N+1 queries
   - `prefetch_related('updates')` - Loads all updates in one query

2. **Frontend Caching:**
   - TanStack Query caches shipment data
   - Invalidates on mutations (create, update, add_update)

3. **Component Design:**
   - Cards are stateless and re-render efficiently
   - Modals lazy-load data only when opened

## Conclusion

The Shipment Tracking feature provides a complete solution for monitoring vehicle exports from origin to destination. With real-time status updates, tracking timeline, and user-friendly interface, it ensures transparency and efficiency in the logistics process.

**Key Strengths:**
- ✅ Complete status workflow (pending → delivered)
- ✅ Real-time tracking updates with timeline
- ✅ User-based filtering (buyer, dealer, broker)
- ✅ Bilingual support (EN/FR)
- ✅ Responsive design (mobile-friendly)
- ✅ Integration with deals and vehicles
- ✅ Role-based permissions

**Total Implementation:**
- 4 frontend components (1,199 lines)
- 2 backend models
- 2 serializers with nested relationships
- 1 ViewSet with 3 custom actions
- 6 API methods
- Comprehensive documentation
