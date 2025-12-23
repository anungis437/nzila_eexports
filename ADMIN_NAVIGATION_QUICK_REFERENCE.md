# Admin Navigation Quick Reference

## 🗺️ Complete Navigation Structure

### Security & Compliance Section
**Permission**: Admin only  
**Icon**: Shield, FileCheck, Package

| Route | Page | Purpose | Key Features |
|-------|------|---------|--------------|
| `/security` | SecurityDashboard | SOC 2 audit trails | 5 tabs: Audit Logs, Login History, Security Events, Data Changes, API Access |
| `/compliance` | ComplianceDashboard | PIPEDA & Law 25 compliance | 4 tabs: Data Breaches, Consent History, Retention Policies, Privacy Assessments |
| `/shipment-security` | ShipmentSecurityDashboard | ISO 28000 shipping security | 3 tabs: Risk Assessments, Security Incidents, Port Verifications |

---

### Financial Operations Section
**Permission**: Admin only  
**Icon**: Percent, FileText, Activity

| Route | Page | Purpose | Key Features |
|-------|------|---------|--------------|
| `/interest-rates` | InterestRateManagement | Dynamic rate management ⭐ | CRUD by province/credit tier, replaces hardcoded Financing.tsx rates |
| `/invoices` | InvoiceManagement | Invoice tracking & reminders | View, mark paid, send reminders, PDF download |
| `/transactions` | TransactionViewer | Real-time transaction monitoring | 30s auto-refresh, CSV export, performance alerts |

---

### Operations Management Section
**Permission**: Admin only  
**Icon**: ClipboardCheck, DollarSign, TrendingUp, MessageSquare

| Route | Page | Purpose | Key Features |
|-------|------|---------|--------------|
| `/inspections` | InspectionManagement | Inspector & inspection workflow | 3 tabs: Inspectors, Slots, Reports & Reviews |
| `/offers` | OfferManagement | Vehicle offer negotiation | Accept/Reject/Counter workflow, negotiation history |
| `/tiers` | TierManagement | Commission tier configuration | 2 tabs: Broker Tiers, Dealer Tiers, bonus management |
| `/review-moderation` | ReviewModeration | Review approval queue | Approve/Reject/Flag workflow, helpfulness votes |

---

## 🔐 Access Control

### Role-Based Visibility
- **Admin**: All 10 admin pages visible + standard user pages
- **Dealer**: Standard pages only (vehicles, deals, commissions, etc.)
- **Broker**: Standard pages only (leads, deals, commissions, etc.)
- **Buyer**: Buyer portal only

### Implementation
```typescript
// Layout.tsx navigation sections
{
  title: 'Security & Compliance',
  permission: ['admin'],  // Only visible to admin role
  items: [...]
}
```

### Route Protection
- All routes wrapped in `<ProtectedRoute>` (authentication check)
- Admin role check happens at navigation visibility level
- Backend enforces admin permission on all endpoints

---

## 🎨 UI Patterns

### Common Components
- **Stats Cards**: 4 per page showing key metrics
- **Tabs**: Multi-tab interface for related data (2-5 tabs)
- **Filters**: Search, status dropdown, time range selector
- **Actions**: CRUD operations, workflow buttons, export
- **Dialogs**: View details, create/edit forms, confirmation

### Badge Colors
```typescript
// Status badges
pending: 'bg-yellow-100 text-yellow-800'
completed/approved: 'bg-green-100 text-green-800'
failed/rejected: 'bg-red-100 text-red-800'
cancelled: 'bg-gray-100 text-gray-800'

// Severity badges
critical: 'bg-red-100 text-red-800'
high: 'bg-orange-100 text-orange-800'
medium: 'bg-yellow-100 text-yellow-800'
low: 'bg-blue-100 text-blue-800'

// Rating badges
4-5 stars: 'bg-green-100 text-green-800'
3 stars: 'bg-yellow-100 text-yellow-800'
1-2 stars: 'bg-red-100 text-red-800'
```

---

## 🔄 Real-Time Features

### TransactionViewer Auto-Refresh
```typescript
const { data: transactions, isLoading, error } = useQuery({
  queryKey: ['transactions', timeRange, type, status, searchTerm],
  queryFn: () => api.getTransactions({ 
    time_range: timeRange, 
    type, 
    status, 
    search: searchTerm 
  }),
  refetchInterval: 30000,  // 30 seconds
})
```

**Performance Monitoring**:
- Response time >1000ms highlighted in red
- Average response time in stats card
- Failed transaction alerts

---

## 📤 Export Functionality

### CSV Export
- **Pages**: SecurityDashboard (all tabs), TransactionViewer
- **Format**: CSV with headers
- **Trigger**: "Export" button
- **API**: Returns blob, downloaded client-side

### PDF Export
- **Pages**: InvoiceManagement
- **Format**: PDF with logo, line items, totals
- **Trigger**: "Download PDF" button per invoice
- **API**: Returns blob, downloaded client-side

---

## 🔔 Notification Triggers

### Email Notifications
1. **Invoice Reminders**: Manual trigger from InvoiceManagement
2. **Breach Notifications**: Auto-trigger when `regulatory_notification_required=true`
3. **Offer Updates**: Auto-send on accept/reject/counter
4. **Inspection Approvals**: Notify inspector on approval

### In-App Alerts
1. **Security Events**: Critical severity events show alert badge
2. **Transaction Failures**: Failed transactions highlighted in red
3. **Overdue Invoices**: Overdue status badge in red

---

## 🛠️ Developer Quick Reference

### File Locations
```
frontend/src/
├── pages/
│   ├── SecurityDashboard.tsx (654 lines)
│   ├── ComplianceDashboard.tsx (507 lines)
│   ├── ShipmentSecurityDashboard.tsx (214 lines)
│   ├── InterestRateManagement.tsx (254 lines)
│   ├── InvoiceManagement.tsx (263 lines)
│   ├── TransactionViewer.tsx (241 lines)
│   ├── InspectionManagement.tsx (365 lines)
│   ├── OfferManagement.tsx (367 lines)
│   ├── TierManagement.tsx (371 lines)
│   └── ReviewModeration.tsx (349 lines)
├── components/
│   └── Layout.tsx (updated with 3 admin sections)
├── lib/
│   └── api.ts (added 46 admin API methods)
└── Routes.tsx (added 10 admin routes)
```

### API Endpoint Pattern
```
/api/{app}/{resource}/
/api/{app}/{resource}/{id}/
/api/{app}/{resource}/{id}/{action}/
```

**Examples**:
```
GET /api/audit/logs/
GET /api/audit/logs/export/{type}/
GET /api/commissions/interest-rates/
POST /api/commissions/interest-rates/
PATCH /api/commissions/interest-rates/{id}/
DELETE /api/commissions/interest-rates/{id}/
GET /api/payments/invoices/
GET /api/payments/invoices/{id}/pdf/
POST /api/payments/invoices/{id}/send-reminder/
```

### TypeScript Interface Pattern
```typescript
interface Resource {
  id: number
  // Basic fields
  name: string
  status: 'pending' | 'active' | 'completed'
  created_at: string
  updated_at: string
  
  // Relationships
  user: string | User
  related_items: RelatedItem[]
  
  // Optional fields
  notes?: string
  metadata?: Record<string, any>
}
```

### Query Hook Pattern
```typescript
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['resource', filter1, filter2],
  queryFn: () => api.getResources({ 
    filter1, 
    filter2 
  }),
  refetchInterval: 30000, // Optional: real-time updates
})
```

### Mutation Hook Pattern
```typescript
const createMutation = useMutation({
  mutationFn: (data: CreateData) => api.createResource(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['resources'] })
    setDialogOpen(false)
  },
})
```

---

## 📚 Related Documentation

### Full Documentation
- **ADMIN_IMPLEMENTATION_SUMMARY.md** - Complete technical documentation (400+ lines)
- **ADMIN_IMPLEMENTATION_EXECUTIVE_SUMMARY.md** - Executive summary for stakeholders
- **ADMIN_FRONTEND_VALIDATION.md** - Original gap analysis and 6-week plan

### Testing
- See "Testing Checklist" section in ADMIN_IMPLEMENTATION_SUMMARY.md
- Manual testing steps for each page
- Automated test examples (unit tests)

### Backend Requirements
- See "Backend Implementation Checklist" in ADMIN_IMPLEMENTATION_SUMMARY.md
- Django model definitions
- ViewSet examples
- Permission class setup
- Email/PDF/CSV configuration

### Deployment
- See "Deployment Considerations" in ADMIN_IMPLEMENTATION_SUMMARY.md
- Environment variables
- CORS configuration
- File storage setup
- Celery configuration
- Monitoring setup

---

## 🚀 Quick Start for New Developers

### 1. Understand the Architecture
Read ADMIN_IMPLEMENTATION_EXECUTIVE_SUMMARY.md (15 min)

### 2. Set Up Development Environment
```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (pending implementation)
cd ..
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Test a Page
Navigate to `/security` or `/interest-rates` and explore the UI

### 4. Review Code Patterns
- Open any admin page file (e.g., InterestRateManagement.tsx)
- Review structure: imports → interfaces → main component → queries/mutations → UI
- Note common patterns: tabs, stats cards, filters, dialogs

### 5. Make a Change
- Try adding a new filter or stat card to an existing page
- Follow existing patterns (TypeScript interfaces, query hooks, UI components)

### 6. Backend Development (when ready)
- See ADMIN_IMPLEMENTATION_SUMMARY.md "Backend Implementation Checklist"
- Start with P0 endpoints: interest-rates, audit logs, data breaches
- Use provided ViewSet examples as templates

---

## 💡 Pro Tips

### Performance
- Use `refetchInterval` sparingly (only TransactionViewer needs real-time)
- Lazy load all pages (already configured in Routes.tsx)
- Use pagination for large datasets (backend implementation)

### UX Best Practices
- Always show loading states (`isLoading` check)
- Always show error states (`error` check)
- Confirm destructive actions (delete, reject)
- Show success messages (toast notifications)

### Security
- Never bypass admin role checks in frontend (backend enforces anyway)
- Sanitize all user input (React does this by default)
- Use HTTPS in production (enforce in nginx/load balancer)

### Code Quality
- Follow existing TypeScript patterns
- Use Shadcn UI components (Button, Card, Dialog, etc.)
- Extract reusable logic into custom hooks
- Write JSDoc comments for complex functions

---

*Quick Reference Generated: 2025-06-12*  
*For questions or issues, see: ADMIN_IMPLEMENTATION_SUMMARY.md*
