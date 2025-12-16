# Analytics Dashboard Feature Documentation

## Overview
Comprehensive analytics dashboard providing real-time insights into business performance, revenue trends, deal pipeline distribution, and recent activities across the platform.

## Components

### 1. StatCard Component
**File:** `/frontend/src/components/StatCard.tsx` (110 lines)

**Features:**
- **6 Color Themes:** Blue, Green, Amber, Purple, Red, Indigo
- **Dynamic Icons:** Custom icon support via lucide-react
- **Trend Indicators:** Up/Down arrows with percentage change
- **Loading States:** Skeleton animation for data loading
- **Gradient Backgrounds:** Beautiful gradient cards with borders
- **Comparison Data:** Shows "vs last month" for context

**Color Schemes:**
- Blue: Active/current data (deals, shipments)
- Green: Positive metrics (revenue, new leads)
- Amber: Financial data (commissions)
- Purple: Inventory (vehicles)
- Red: Alert metrics
- Indigo: Transit/shipments

**Usage:**
```tsx
<StatCard
  title="Total Revenue"
  value="$1,250,000"
  change={{ value: 12.5, trend: 'up' }}
  icon={DollarSign}
  color="green"
  loading={false}
/>
```

**Props:**
- `title` (string) - Card title
- `value` (string | number) - Main metric value
- `change` (optional) - { value: number, trend: 'up' | 'down' }
- `icon` (LucideIcon) - Icon component
- `color` - Color theme
- `loading` (optional) - Shows skeleton state

### 2. RevenueChart Component
**File:** `/frontend/src/components/RevenueChart.tsx` (110 lines)

**Features:**
- **Dual Y-Axis Chart:** Revenue (left) + Deals count (right)
- **Last 6 Months:** Monthly revenue and deal data
- **Interactive Tooltips:** Hover to see exact values
- **Custom Formatting:** Currency formatting for revenue
- **Responsive Design:** Adapts to container width
- **Legend:** Color-coded data series
- **Smooth Lines:** Monotone curve interpolation

**Chart Details:**
- Line type: Monotone (smooth curves)
- Revenue line: Blue (#3b82f6), 3px stroke
- Deals line: Purple (#8b5cf6), 3px stroke
- Grid: Dashed lines (#e2e8f0)
- Active dots: 7px radius on hover
- Height: 350px

**Data Structure:**
```typescript
interface RevenueData {
  month: string        // e.g., "Jul", "Aug"
  revenue: number      // Revenue in CAD
  deals: number        // Number of deals
}
```

**Usage:**
```tsx
<RevenueChart 
  data={revenueData} 
  loading={isLoading} 
/>
```

### 3. DealPipelineChart Component
**File:** `/frontend/src/components/DealPipelineChart.tsx` (95 lines)

**Features:**
- **Bar Chart:** Vertical bars with rounded tops
- **7 Status Stages:** Complete deal pipeline visualization
- **Color-Coded Status:** Each status has unique color
- **Angled Labels:** 45° rotation for readability
- **Interactive Tooltips:** Show deal count per status
- **Responsive Design:** Adapts to container width

**Status Colors:**
- Pending Docs: Slate (#64748b)
- Docs Verified: Blue (#3b82f6)
- Payment Pending: Amber (#f59e0b)
- Payment Received: Green (#10b981)
- Ready to Ship: Purple (#8b5cf6)
- Shipped: Indigo (#6366f1)
- Completed: Green (#22c55e)

**Data Structure:**
```typescript
interface PipelineData {
  status: string       // e.g., "pending_docs"
  count: number        // Number of deals in this status
  color: string        // Hex color code
}
```

**Usage:**
```tsx
<DealPipelineChart 
  data={pipelineData} 
  loading={isLoading} 
/>
```

### 4. RecentActivity Component
**File:** `/frontend/src/components/RecentActivity.tsx` (165 lines)

**Features:**
- **Activity Timeline:** Reverse chronological order
- **5 Activity Types:** Vehicle, Lead, Deal, Commission, Shipment
- **Color-Coded Icons:** Each type has unique icon and color
- **Action Badges:** Created, Updated, Completed, Approved, Shipped
- **User Attribution:** Shows who performed the action
- **Relative Timestamps:** "2 hours ago" format
- **Bilingual Support:** EN/FR labels and messages
- **Empty State:** Friendly message when no activities

**Activity Icons:**
- Vehicle: Car icon (blue)
- Lead: Users icon (green)
- Deal: FileText icon (purple)
- Commission: DollarSign icon (amber)
- Shipment: Ship icon (indigo)

**Activity Structure:**
```typescript
interface Activity {
  id: number
  type: 'vehicle' | 'lead' | 'deal' | 'commission' | 'shipment'
  action: string       // e.g., "created", "updated", "completed"
  description: string  // Human-readable description
  timestamp: string    // ISO datetime
  user?: string        // User who performed the action
}
```

**Usage:**
```tsx
<RecentActivity 
  activities={activities} 
  loading={isLoading} 
/>
```

### 5. Analytics Page
**File:** `/frontend/src/pages/Analytics.tsx` (260 lines)

**Features:**
- **6 Stat Cards:** Key metrics with trend indicators
- **Revenue Chart:** 6-month revenue and deal trends
- **Pipeline Chart:** Deal distribution by status
- **Recent Activity:** Last 10 platform activities
- **Quick Links:** 4 navigation cards to main features
- **Real-time Data:** TanStack Query with auto-refresh
- **Loading States:** Skeleton loaders for all components
- **Responsive Grid:** Adapts from 1 to 6 columns

**Page Layout:**
1. Header with gradient title
2. 6-column stat cards grid
3. 2-column charts grid (Revenue + Pipeline)
4. Full-width recent activity
5. 4-column quick links grid

**Metrics Displayed:**
- Total Revenue (CAD, vs last month)
- Active Deals (count, vs last month)
- Vehicles Sold (count, vs last month)
- Shipments In Transit (count, vs last month)
- Total Commissions (CAD, vs last month)
- New Leads (count, vs last month)

**Quick Links:**
- Vehicles → `/vehicles`
- Deals → `/deals`
- Shipments → `/shipments`
- Commissions → `/commissions`

## Backend Implementation

### Analytics Views
**File:** `/nzila_export/analytics_views.py` (220 lines)

**Endpoints:**

#### 1. get_analytics_stats()
**Route:** `GET /api/analytics/stats/`

**Functionality:**
- Calculates key metrics for current and previous periods
- Compares last 30 days vs 30-60 days ago
- Filters data by user role (dealer, broker, admin)
- Returns percentage changes for all metrics

**Calculations:**
- Total revenue from completed/shipped deals
- Active deals in progress
- Vehicles sold (completed deals)
- Shipments currently in transit
- Approved/paid commissions
- New leads created

**Response:**
```json
{
  "totalRevenue": 1250000.00,
  "revenueChange": 12.5,
  "activeDeals": 24,
  "dealsChange": 8.3,
  "vehiclesSold": 156,
  "vehiclesChange": -3.2,
  "shipmentsInTransit": 18,
  "shipmentsChange": 0.0,
  "totalCommissions": 87500.00,
  "commissionsChange": 9.8,
  "newLeads": 42,
  "leadsChange": 22.1
}
```

#### 2. get_revenue_chart()
**Route:** `GET /api/analytics/revenue/`

**Functionality:**
- Returns last 6 months of revenue and deal data
- Calculates monthly totals from completed deals
- Filters by user role
- Uses 30-day intervals for months

**Response:**
```json
[
  { "month": "Jul", "revenue": 180000.00, "deals": 18 },
  { "month": "Aug", "revenue": 220000.00, "deals": 22 },
  ...
]
```

#### 3. get_pipeline_chart()
**Route:** `GET /api/analytics/pipeline/`

**Functionality:**
- Counts deals in each status stage
- Assigns color codes for visualization
- Filters by user role
- Returns all 7 status stages

**Response:**
```json
[
  { "status": "pending_docs", "count": 8, "color": "#64748b" },
  { "status": "docs_verified", "count": 12, "color": "#3b82f6" },
  ...
]
```

#### 4. get_recent_activities()
**Route:** `GET /api/analytics/activities/`

**Functionality:**
- Fetches recent deals, shipments, and commissions
- Combines and sorts by timestamp
- Returns last 10 activities
- Includes user information and descriptions

**Response:**
```json
[
  {
    "id": "deal-123",
    "type": "deal",
    "action": "completed",
    "description": "2019 Toyota Camry",
    "timestamp": "2024-12-16T10:30:00Z",
    "user": "Sarah Johnson"
  },
  ...
]
```

### URL Configuration
**File:** `/nzila_export/urls.py`

**Added Routes:**
```python
path('api/analytics/stats/', get_analytics_stats, name='analytics-stats'),
path('api/analytics/revenue/', get_revenue_chart, name='analytics-revenue'),
path('api/analytics/pipeline/', get_pipeline_chart, name='analytics-pipeline'),
path('api/analytics/activities/', get_recent_activities, name='analytics-activities'),
```

### Role-Based Filtering

**Dealer:**
- Sees only their own deals and vehicles
- Commissions from their deals
- Limited to their inventory

**Broker:**
- Sees deals they're involved with
- All vehicles (for prospecting)
- Only their own commissions

**Admin:**
- Sees all data across the platform
- No filtering applied
- Complete visibility

## API Client Methods
**File:** `/frontend/src/lib/api.ts`

```typescript
async getAnalyticsStats()         // Fetch key metrics
async getRevenueChart()            // Fetch 6-month revenue data
async getPipelineChart()           // Fetch pipeline distribution
async getRecentActivities()        // Fetch recent activities
```

## Data Flow

### Frontend Query Flow:
1. **Component Mounts** → TanStack Query triggers API call
2. **API Client** → Makes authenticated request to backend
3. **Backend View** → Calculates metrics based on user role
4. **Database Queries** → Aggregates data from multiple tables
5. **Response** → JSON data returned to frontend
6. **React Query Cache** → Data cached for 5 minutes
7. **Component Renders** → Charts and cards display data

### Auto-Refresh:
- Stats: Refetch every 5 minutes
- Charts: Refetch every 10 minutes
- Activities: Refetch every 2 minutes
- Manual refresh available

## Dependencies

### Frontend:
- **recharts** (2.x) - Chart library for React
- **@tanstack/react-query** - Data fetching and caching
- **lucide-react** - Icon library
- **date-fns** - Date formatting and localization

### Backend:
- **Django ORM** - Database aggregations
- **DRF** - API views and serialization
- **django.db.models** - Sum, Count, Avg functions

## Performance Optimizations

### Frontend:
1. **Query Caching:** TanStack Query caches data to reduce API calls
2. **Loading States:** Skeleton loaders prevent layout shift
3. **Lazy Loading:** Charts only render when data is available
4. **Responsive Design:** Charts adapt to viewport without re-fetching

### Backend:
1. **Aggregation Queries:** Single queries with Sum/Count instead of loops
2. **Date Filtering:** Indexed created_at/updated_at fields
3. **Role-Based Queries:** Early filtering reduces data processing
4. **Select Related:** Minimal joins for related data

## Testing Guide

### Manual Testing Checklist

#### 1. Stat Cards
- [ ] All 6 cards display correct data
- [ ] Trend arrows show up (↑) or down (↓) correctly
- [ ] Percentage changes calculate accurately
- [ ] Loading states show skeleton animations
- [ ] Cards are responsive (1-6 columns based on viewport)

#### 2. Revenue Chart
- [ ] Last 6 months display with correct data
- [ ] Hover tooltip shows exact values
- [ ] Revenue formatted as currency ($XXX,XXX)
- [ ] Dual Y-axis works (revenue left, deals right)
- [ ] Legend displays correctly (Revenue, Deals)
- [ ] Chart is responsive to width changes

#### 3. Pipeline Chart
- [ ] All 7 status bars display
- [ ] Colors match status definitions
- [ ] Bar heights represent correct counts
- [ ] X-axis labels readable (angled 45°)
- [ ] Tooltip shows deal count on hover
- [ ] Empty statuses show as 0-height bars

#### 4. Recent Activity
- [ ] Activities display in reverse chronological order
- [ ] Icons match activity types
- [ ] Action badges show correct colors
- [ ] Relative timestamps update ("2 hours ago")
- [ ] User attribution displays
- [ ] Empty state shows when no activities

#### 5. Role-Based Filtering
- [ ] Dealer sees only their deals/vehicles
- [ ] Broker sees only their deals/commissions
- [ ] Admin sees all platform data
- [ ] Stats reflect filtered data
- [ ] Charts show filtered data

#### 6. Quick Links
- [ ] All 4 cards navigate correctly
- [ ] Hover states work
- [ ] Icons display properly
- [ ] Bilingual labels show correctly

## Design Patterns

### Color Palette:
- **Green:** Revenue, positive growth, new leads
- **Blue:** Active deals, in-transit shipments
- **Purple:** Vehicles, pipeline stages
- **Amber:** Commissions, financial metrics
- **Indigo:** Shipments, logistics
- **Red:** Alerts, negative trends

### Typography:
- Header: 3xl bold, gradient text (purple → indigo)
- Stat values: 3xl bold
- Card titles: sm font-medium
- Chart labels: xs
- Activity descriptions: sm

### Spacing:
- Page padding: 8 (2rem)
- Section margins: 8
- Card gaps: 4-6
- Component padding: 5-6

## Future Enhancements

1. **Custom Date Ranges**
   - Date picker for custom periods
   - Compare any two time ranges
   - Export data as CSV

2. **More Charts**
   - Top selling vehicles (pie chart)
   - Commission breakdown by user
   - Geographic distribution (map)
   - Conversion funnel (lead → deal)

3. **Predictive Analytics**
   - AI-powered revenue forecasting
   - Deal closure probability
   - Inventory recommendations

4. **Real-time Updates**
   - WebSocket connection for live data
   - Push notifications for milestones
   - Live activity stream

5. **Advanced Filters**
   - Filter by date range
   - Filter by user/team
   - Filter by vehicle type
   - Filter by region

6. **Export & Reporting**
   - PDF report generation
   - Email scheduled reports
   - Excel exports
   - Custom dashboard builder

7. **KPI Alerts**
   - Set threshold alerts
   - Email/SMS notifications
   - Performance targets

## Troubleshooting

### Common Issues

**Issue:** Charts not displaying
- **Solution:** Check recharts installation: `npm list recharts`
- Verify data structure matches interface definitions
- Check browser console for errors

**Issue:** Stats showing 0 or incorrect values
- **Solution:** Verify user has data in the system
- Check role-based filtering in backend
- Ensure date ranges are correct

**Issue:** Loading states stuck
- **Solution:** Check API endpoint responses
- Verify authentication token is valid
- Check network tab for failed requests

**Issue:** Percentage changes incorrect
- **Solution:** Verify previous period data exists
- Check calc_change() function logic
- Ensure date calculations are correct

## Conclusion

The Analytics Dashboard provides a comprehensive view of business performance with real-time data, beautiful visualizations, and role-based insights. With 6 key metrics, interactive charts, and recent activity tracking, users can make informed decisions quickly.

**Key Strengths:**
- ✅ Real-time data with TanStack Query
- ✅ Beautiful recharts visualizations
- ✅ Role-based data filtering
- ✅ Responsive design (mobile-friendly)
- ✅ Bilingual support (EN/FR)
- ✅ Comprehensive backend analytics
- ✅ Performance optimized queries

**Total Implementation:**
- 4 frontend components (540 lines)
- 1 analytics page (260 lines)
- 4 backend views (220 lines)
- 5 API methods
- Complete documentation
