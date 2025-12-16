# Notifications Feature

## Overview

The Notifications feature provides real-time updates to users about important events and activities across the Nzila Export Hub platform. Users receive notifications for new leads, deal status changes, commission earnings, shipment updates, vehicle additions, document verifications, and system messages.

## Key Features

### 1. Real-Time Notification Bell
- **Bell Icon Button**: Displays in both desktop sidebar and mobile header
- **Unread Badge**: Red circular badge showing count of unread notifications (1-9+)
- **Dropdown Panel**: 396px wide panel with max 480px height and scrollable content
- **Auto-Refresh**: Automatically fetches new notifications every 30 seconds
- **Click-Outside-to-Close**: Dropdown closes when clicking anywhere outside

### 2. Notification Types
Six distinct notification types, each with unique icon and color scheme:

#### Lead Notifications (Blue)
- **Icon**: TrendingUp
- **Color**: Blue to Indigo gradient (`from-blue-500 to-indigo-600`)
- **Triggered by**: New lead assignment
- **Example**: "John Doe is interested in the 2020 Toyota Camry"

#### Deal Notifications (Green)
- **Icon**: FileText
- **Color**: Green to Emerald gradient (`from-green-500 to-emerald-600`)
- **Triggered by**: Deal status changes
- **Example**: "Deal for Honda Accord moved to 'pending_docs'"

#### Commission Notifications (Amber)
- **Icon**: DollarSign
- **Color**: Amber to Orange gradient (`from-amber-500 to-orange-600`)
- **Triggered by**: Commission earnings
- **Example**: "You earned $500.00 CAD commission on deal #123"

#### Shipment Notifications (Purple)
- **Icon**: Package
- **Color**: Purple to Pink gradient (`from-purple-500 to-pink-600`)
- **Triggered by**: Shipment status updates
- **Example**: "Shipment SHIP123456 has arrived at port"

#### Vehicle Notifications (Slate)
- **Icon**: Car
- **Color**: Slate gradient (`from-slate-500 to-slate-600`)
- **Triggered by**: New vehicle additions (currently disabled for bulk imports)
- **Example**: "New vehicle Ford F-150 2021 added"

#### Document Notifications (Red)
- **Icon**: FileText
- **Color**: Red to Rose gradient (`from-red-500 to-rose-600`)
- **Triggered by**: Document upload, verification, or signature requests
- **Example**: "Document verification required for Deal #456"

### 3. Notification Interactions

#### Mark as Read
- **Individual**: Click checkmark button on any notification
- **Bulk**: "Mark all read" button in header (only visible when unread notifications exist)
- **Auto-mark**: Clicking notification card marks it as read and navigates to link

#### Visual States
- **Unread**: Light blue background (`bg-blue-50/50`), blue dot indicator (top-right)
- **Read**: White background, no indicator
- **Hover**: Slate background on hover (`hover:bg-slate-50`)

#### Timestamps
- Human-readable format using `date-fns` formatDistanceToNow
- Examples: "15 min ago", "2 hours ago", "3 days ago"

### 4. Empty & Loading States
- **Loading**: Skeleton loaders (3 shimmer placeholders)
- **Empty**: Bell icon with "No notifications" message in both English and French

### 5. Bilingual Support
Full support for English and French:
- "Notifications" / "Notifications"
- "Mark all read" / "Tout marquer comme lu"
- "Mark as read" / "Marquer comme lu"
- "No notifications" / "Aucune notification"

## Component Architecture

### Frontend Component: `NotificationBell.tsx`

```typescript
interface Notification {
  id: number
  type: 'lead' | 'deal' | 'commission' | 'shipment' | 'vehicle' | 'document' | 'system'
  title: string
  message: string
  is_read: boolean
  link?: string
  created_at: string
}
```

**State Management:**
- React Query for data fetching with 30-second refetch interval
- useMutation for mark-as-read operations
- Local state for dropdown open/close
- useEffect for click-outside detection

**Key Functions:**
- `getNotificationIcon()`: Returns appropriate Lucide icon for notification type
- `getNotificationColor()`: Returns Tailwind gradient classes for notification type
- `handleNotificationClick()`: Marks as read and navigates to link
- `markAsReadMutation`: Mutation for marking single notification as read
- `markAllAsReadMutation`: Mutation for marking all notifications as read

### Layout Integration: `Layout.tsx`

**Desktop Sidebar:**
Positioned in user profile footer section, before language selector and logout button:
```tsx
<div className="flex gap-2">
  <NotificationBell />
  <DropdownMenu>...</DropdownMenu> {/* Language selector */}
  <Button>...</Button> {/* Logout */}
</div>
```

**Mobile Header:**
Positioned next to hamburger menu button:
```tsx
<div className="flex items-center gap-2">
  <NotificationBell />
  <Button>...</Button> {/* Menu toggle */}
</div>
```

## Backend API

### Database Model: `notifications/models.py`

```python
class Notification(models.Model):
    user = ForeignKey(User)
    type = CharField(max_length=20)  # lead, deal, commission, shipment, vehicle, document, system
    title = CharField(max_length=200)
    message = TextField()
    is_read = BooleanField(default=False)
    link = CharField(max_length=500, blank=True, null=True)
    related_id = IntegerField(blank=True, null=True)
    related_model = CharField(max_length=50, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    read_at = DateTimeField(blank=True, null=True)
```

**Indexes:**
- `user` + `is_read` for fast unread queries
- `user` + `-created_at` for efficient ordering

**Methods:**
- `mark_as_read()`: Sets `is_read=True` and `read_at=timezone.now()`

### API Endpoints

#### 1. List Notifications
**Endpoint:** `GET /api/v1/notifications/`

**Query Parameters:**
- `unread_only` (boolean): Return only unread notifications
- `limit` (int, default: 50): Maximum number to return
- `type` (string): Filter by notification type

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "type": "lead",
      "title": "New Lead",
      "message": "John Doe is interested in the 2020 Toyota Camry",
      "is_read": false,
      "link": "/leads/123",
      "related_id": 123,
      "related_model": "lead",
      "created_at": "2024-01-15T10:30:00Z",
      "read_at": null
    }
  ],
  "unread_count": 3
}
```

#### 2. Mark Notification as Read
**Endpoint:** `POST /api/v1/notifications/{id}/read/`

**Response:**
```json
{
  "id": 1,
  "type": "lead",
  "is_read": true,
  "read_at": "2024-01-15T11:00:00Z",
  ...
}
```

#### 3. Mark All as Read
**Endpoint:** `POST /api/v1/notifications/mark-all-read/`

**Response:**
```json
{
  "success": true,
  "marked_read": 5
}
```

#### 4. Delete Notification
**Endpoint:** `DELETE /api/v1/notifications/{id}/delete/`

**Response:**
```json
{
  "success": true
}
```

#### 5. Get Unread Count
**Endpoint:** `GET /api/v1/notifications/unread-count/`

**Response:**
```json
{
  "unread_count": 3
}
```

### Django Signals: `notifications/signals.py`

Automatic notification creation via Django signals:

**Lead Signal:**
```python
@receiver(post_save, sender=Lead)
def create_lead_notification(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to,
            type='lead',
            title=f"New Lead: {instance.customer_name}",
            message=f"A new lead has been assigned to you from {instance.customer_name}.",
            link=f'/leads/{instance.id}',
            related_id=instance.id,
            related_model='lead'
        )
```

**Deal Signal:**
```python
@receiver(post_save, sender=Deal)
def create_deal_notification(sender, instance, created, **kwargs):
    if not created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to,
            type='deal',
            title=f"Deal Updated: {instance.vehicle.make} {instance.vehicle.model}",
            message=f"Deal status changed to {instance.get_status_display()}.",
            link=f'/deals/{instance.id}',
            related_id=instance.id,
            related_model='deal'
        )
```

**Commission Signal:**
```python
@receiver(post_save, sender=Commission)
def create_commission_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.deal.assigned_to,
            type='commission',
            title="Commission Earned!",
            message=f"You earned a commission of ${instance.amount:,.2f} on deal #{instance.deal.id}.",
            link=f'/commissions',
            related_id=instance.id,
            related_model='commission'
        )
```

**Shipment Signal:**
```python
@receiver(post_save, sender=Shipment)
def create_shipment_notification(sender, instance, created, **kwargs):
    if not created and instance.deal and instance.deal.assigned_to:
        Notification.objects.create(
            user=instance.deal.assigned_to,
            type='shipment',
            title=f"Shipment Update: {instance.tracking_number}",
            message=f"Shipment status changed to {instance.get_status_display()}.",
            link=f'/shipments/{instance.id}',
            related_id=instance.id,
            related_model='shipment'
        )
```

**Helper Function:**
```python
def create_notification(user, notification_type, title, message, link=None, related_id=None, related_model=None):
    """Manually create a notification"""
    return Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        link=link,
        related_id=related_id,
        related_model=related_model
    )
```

## Design System

### Color Palette
- **Lead**: Blue (#3B82F6) to Indigo (#4F46E5)
- **Deal**: Green (#10B981) to Emerald (#059669)
- **Commission**: Amber (#F59E0B) to Orange (#EA580C)
- **Shipment**: Purple (#8B5CF6) to Pink (#EC4899)
- **Vehicle**: Slate (#64748B) to Slate (#475569)
- **Document**: Red (#EF4444) to Rose (#F43F5E)

### Typography
- **Title**: 14px (text-sm), font-semibold, slate-900
- **Message**: 14px (text-sm), regular, slate-600
- **Timestamp**: 12px (text-xs), regular, slate-400
- **Button Text**: 12px (text-xs), medium, blue-600

### Spacing
- **Dropdown width**: 396px (w-96)
- **Dropdown max height**: 480px (scrollable)
- **Notification padding**: 16px (p-4)
- **Icon size**: 40px × 40px (w-10 h-10)
- **Badge size**: 20px × 20px (w-5 h-5)
- **Gap between elements**: 12px (gap-3)

### Animations
- **Transitions**: All interactive elements use `transition-colors`
- **Hover states**: Subtle background color changes
- **Badge pulse**: Could add `animate-pulse` for new notifications (future enhancement)

## Testing Checklist

### Unit Tests
- [ ] NotificationBell component renders correctly
- [ ] Dropdown opens and closes on bell button click
- [ ] Dropdown closes when clicking outside
- [ ] Unread badge displays correct count (1-9+)
- [ ] Notification icons render based on type
- [ ] Notification colors apply based on type
- [ ] Mark as read mutation updates UI correctly
- [ ] Mark all as read clears unread count
- [ ] Clicking notification navigates to link
- [ ] Empty state displays when no notifications
- [ ] Loading state displays skeleton loaders
- [ ] Language switching updates all text

### API Tests
- [ ] List notifications returns correct data
- [ ] Filter by unread_only returns only unread notifications
- [ ] Filter by type returns correct notification types
- [ ] Limit parameter restricts result count
- [ ] Mark as read updates is_read and read_at fields
- [ ] Mark all as read updates all user's notifications
- [ ] Delete notification removes from database
- [ ] Unread count returns accurate count
- [ ] Only authenticated users can access endpoints
- [ ] Users can only see their own notifications

### Integration Tests
- [ ] New lead creates notification for assigned user
- [ ] Deal status change creates notification
- [ ] Commission creation creates notification
- [ ] Shipment status change creates notification
- [ ] Notifications appear in real-time (30-second refresh)
- [ ] Notification click marks as read and navigates
- [ ] Mark all read clears all unread notifications
- [ ] Unread badge updates after marking as read
- [ ] Notifications persist after page refresh
- [ ] Mobile and desktop layouts both work correctly

### Browser Testing
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

### Accessibility Testing
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Screen reader announces notification count
- [ ] ARIA labels on interactive elements
- [ ] Focus states visible on all buttons
- [ ] Color contrast meets WCAG AA standards

## Security Considerations

### Authentication
- All notification endpoints require authentication via JWT
- Users can only access their own notifications
- Permission checks on every API request

### Data Privacy
- Notifications contain no sensitive financial data
- Personal information limited to names and vehicle details
- Links use internal paths, not exposing sensitive IDs in URLs

### SQL Injection Prevention
- Django ORM prevents SQL injection
- All user inputs sanitized
- No raw SQL queries in notification endpoints

### XSS Prevention
- React automatically escapes HTML in notification titles and messages
- No `dangerouslySetInnerHTML` used in notification rendering
- Links validated before navigation

## Performance Optimization

### Database
- Indexes on `user` + `is_read` for fast unread queries
- Indexes on `user` + `-created_at` for efficient ordering
- Limit queries to 50 notifications by default
- Pagination support for large notification lists

### Frontend
- React Query caching reduces API calls
- 30-second refetch interval balances real-time updates with performance
- Lazy loading of notification images (if added in future)
- Skeleton loaders for perceived performance

### API
- Response compression (gzip)
- Efficient serialization with DRF
- Database query optimization (select_related, prefetch_related)

## Future Enhancements

### Real-Time Updates (WebSocket)
- Replace 30-second polling with WebSocket connections
- Instant notification delivery via Django Channels
- Push notifications to all open browser tabs

### Rich Notifications
- Image thumbnails for vehicle notifications
- User avatars for lead/deal notifications
- Progress bars for shipment tracking
- Currency formatting for commission amounts

### Notification Preferences
- User settings to enable/disable notification types
- Email digest for unread notifications
- SMS notifications for urgent events
- Desktop browser notifications

### Advanced Features
- Notification categories and filtering
- Search within notifications
- Archive instead of delete
- Notification templates for consistency
- Bulk actions (select multiple, delete multiple)

### Analytics
- Track notification open rates
- Measure time-to-action on notifications
- Identify most engaging notification types
- User engagement metrics

### Mobile App Integration
- Push notifications via Firebase Cloud Messaging
- Deep linking to app screens
- Badge count on app icon
- Background notification sync

## Deployment Notes

### Environment Variables
No specific environment variables required for notifications feature.

### Database Migration
```bash
python manage.py makemigrations notifications
python manage.py migrate notifications
```

### Static Files
No additional static files required (uses existing Lucide icons).

### Dependencies
- **Frontend**: date-fns (already installed)
- **Backend**: None (uses Django's built-in features)

### Monitoring
- Monitor notification creation rates
- Track unread notification counts
- Alert on high unread counts per user
- Monitor API response times for notification endpoints

## Troubleshooting

### Notifications Not Appearing
1. Check if user is authenticated
2. Verify backend signals are enabled in `apps.py`
3. Check browser console for API errors
4. Verify notification creation in Django admin

### Real-Time Updates Not Working
1. Confirm React Query refetch interval is set (30 seconds)
2. Check network tab for API calls every 30 seconds
3. Verify user has active session (JWT not expired)

### Mark as Read Not Working
1. Check mutation is calling correct API endpoint
2. Verify user has permission to modify notification
3. Check database for `is_read` and `read_at` updates
4. Inspect React Query cache invalidation

### Performance Issues
1. Reduce refetch interval if too aggressive
2. Implement pagination for large notification lists
3. Add database indexes if missing
4. Optimize notification queries in backend

## Related Documentation
- [API Documentation](API_DOCS.md)
- [Analytics Feature](ANALYTICS_FEATURE.md)
- [Settings Feature](SETTINGS_FEATURE.md)
- [Buyer Portal Feature](BUYER_PORTAL_FEATURE.md)

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ Notification bell component with unread badge
- ✅ Six notification types with unique icons and colors
- ✅ Mark as read (individual and bulk)
- ✅ Real-time updates every 30 seconds
- ✅ Backend API with 5 endpoints
- ✅ Django signals for automatic notification creation
- ✅ Bilingual support (EN/FR)
- ✅ Mobile and desktop layouts
- ✅ Loading and empty states

### Planned for Version 1.1.0
- WebSocket integration for real-time updates
- User notification preferences
- Rich notifications with images
- Desktop browser notifications
