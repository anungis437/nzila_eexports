# Q1 2026 Features - Quick Start Guide 🚀

This guide helps you test the newly implemented Q1 2026 features.

---

## Prerequisites

### 1. Install Redis (Required for WebSocket Chat)

**Windows (via Chocolatey)**:
```powershell
choco install redis-64
```

**Or download from**: https://github.com/tporadowski/redis/releases

**Verify Installation**:
```powershell
redis-cli ping
# Should return: PONG
```

### 2. Install Python Dependencies
```powershell
cd d:\APPS\nzila_eexports
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```powershell
python manage.py migrate
```

---

## Feature 1: Multi-Image Gallery 📸

### Test Bulk Upload API

**1. Create Test Vehicle** (if needed):
```python
python manage.py shell

from vehicles.models import Vehicle
from accounts.models import User

dealer = User.objects.filter(is_dealer=True).first()
vehicle = Vehicle.objects.create(
    vin='1HGBH41JXMN109186',
    year=2023,
    make='Toyota',
    model='Camry',
    price=25000.00,
    status='available',
    dealer=dealer
)
print(f"Created vehicle ID: {vehicle.id}")
```

**2. Test Bulk Upload** (via curl or Postman):
```bash
# Upload multiple images at once
curl -X POST http://localhost:8000/api/vehicles/vehicle-images/bulk-upload/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "vehicle_id=1" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "images=@image3.jpg"
```

**3. Test Reorder Images**:
```bash
curl -X POST http://localhost:8000/api/vehicles/vehicle-images/reorder/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "images": [
      {"id": 1, "order": 2},
      {"id": 2, "order": 0},
      {"id": 3, "order": 1}
    ]
  }'
```

**4. Test Set Primary Image**:
```bash
curl -X POST http://localhost:8000/api/vehicles/vehicle-images/2/set-primary/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Results**:
- ✅ All images uploaded successfully
- ✅ Images reordered correctly
- ✅ Primary image set (others automatically unmarked)
- ✅ Maximum 50 images per vehicle enforced

---

## Feature 2: Real-Time WebSocket Chat 💬

### Start Redis Server
```powershell
# Terminal 1: Start Redis
redis-server

# Should see: "Ready to accept connections"
```

### Start Django with ASGI
```powershell
# Terminal 2: Start Django (with WebSocket support)
cd d:\APPS\nzila_eexports
python manage.py runserver

# Or use Daphne (production ASGI server):
daphne -b 127.0.0.1 -p 8000 nzila_export.asgi_channels:application
```

### Test WebSocket Connection

**1. Create Test Conversation**:
```python
python manage.py shell

from chat.models import Conversation
from accounts.models import User

buyer = User.objects.filter(is_buyer=True).first()
dealer = User.objects.filter(is_dealer=True).first()

conversation = Conversation.objects.create(
    participant_1=buyer,
    participant_2=dealer
)
print(f"Created conversation ID: {conversation.id}")
```

**2. Test WebSocket in Browser Console**:

Open two browser windows (one for buyer, one for dealer):

**Window 1 (Buyer)**:
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat/1/'); // Use conversation ID

ws.onopen = () => {
  console.log('Connected!');
  
  // Send a message
  ws.send(JSON.stringify({
    type: 'message',
    message: 'Hello, I am interested in the vehicle!'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send typing indicator
ws.send(JSON.stringify({
  type: 'typing',
  is_typing: true
}));

// Send read receipt
ws.send(JSON.stringify({
  type: 'read',
  message_ids: [1, 2, 3]
}));
```

**Window 2 (Dealer)**:
```javascript
// Same WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/chat/1/');

ws.onopen = () => {
  console.log('Connected!');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  if (data.type === 'message') {
    console.log(`${data.sender_name}: ${data.content}`);
  }
  
  if (data.type === 'typing') {
    console.log(`${data.user_name} is typing...`);
  }
};
```

**Expected Results**:
- ✅ Both clients connect successfully
- ✅ Messages appear instantly in both windows
- ✅ Typing indicators show in real-time
- ✅ Read receipts update message status
- ✅ Auto-reconnect after connection drop

---

## Feature 3: Carfax Vehicle History (Mock Mode) 🔍

### Test Carfax Service

```python
python manage.py shell

from vehicle_history.carfax_service import carfax_service

# Test VIN validation
is_valid = carfax_service.validate_vin('1HGBH41JXMN109186')
print(f"VIN valid: {is_valid}")

# Fetch report (mock mode - no API key required)
report = carfax_service.fetch_report('1HGBH41JXMN109186')

print("Title Status:", report['title_status'])
print("Accidents:", report['accidents'])
print("Owners:", report['ownership']['number_of_owners'])
print("Odometer:", report['odometer']['current_reading'])

# Test caching (should return instantly on second call)
import time
start = time.time()
report2 = carfax_service.fetch_report('1HGBH41JXMN109186')
print(f"Cache hit: {time.time() - start < 0.1}s")
```

**Expected Results**:
- ✅ VIN validation works
- ✅ Mock report returns realistic data
- ✅ Cache speeds up subsequent requests
- ✅ Report format is standardized

**Add Real API Key** (when available):
```python
# In .env file:
CARFAX_API_KEY=your_api_key_here
CARFAX_API_URL=https://api.carfax.com/v1

# Service automatically switches to live API!
```

---

## Feature 4: WhatsApp Business API (Mock Mode) 📱

### Test WhatsApp Service

```python
python manage.py shell

from notifications.whatsapp_service import whatsapp_service

# Test send message (mock mode - logs to console)
result = whatsapp_service.send_message(
    to='+19051234567',
    message='Your vehicle inquiry has been received!',
    vehicle_id=1
)
print("Mock message logged:", result)

# Test vehicle inquiry
vehicle_data = {
    'year': 2023,
    'make': 'Toyota',
    'model': 'Camry',
    'vin': '1HGBH41JXMN109186',
    'price': 25000,
    'url': 'https://nzila.com/vehicles/123'
}

result = whatsapp_service.send_vehicle_inquiry('+19051234567', vehicle_data)
print("Inquiry sent:", result)

# Test template message
result = whatsapp_service.send_template_message(
    to='+19051234567',
    template_name='vehicle_inquiry_confirmation',
    language_code='en',
    parameters=['Toyota Camry', '2023']
)
print("Template message sent:", result)
```

**Expected Results**:
- ✅ Mock mode logs messages to console
- ✅ Vehicle inquiry formats correctly
- ✅ Template messages structure properly
- ✅ All methods work without API credentials

**Check Console Output**:
```
[WhatsApp Mock] Sending message to +19051234567
Vehicle ID: 1
Message: Your vehicle inquiry has been received!
[WhatsApp Mock] Message logged successfully
```

**Add Real API Credentials** (when approved):
```python
# In .env file:
WHATSAPP_API_TOKEN=your_business_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_webhook_token

# Service automatically switches to live API!
```

---

## Feature 5: Progressive Web App (PWA) 📱

### Test PWA Locally

**1. Start Development Server**:
```powershell
cd d:\APPS\nzila_eexports\frontend
npm run dev
```

**2. Register Service Worker**:

Add to `frontend/src/main.ts`:
```typescript
import { registerServiceWorker } from './services/pwa';

// Register service worker
registerServiceWorker();

// Check if PWA is installed
import { isAppInstalled, canShowInstallPrompt, showInstallPrompt } from './services/pwa';

if (isAppInstalled()) {
  console.log('App is installed as PWA!');
}

if (canShowInstallPrompt()) {
  console.log('Install prompt available');
  // Show install button in UI
}
```

**3. Test Offline Mode**:
```javascript
// In browser DevTools:
// Application tab → Service Workers → Check "Offline"

// App should still work with cached data
// Navigate to: http://localhost:5173/offline.html
```

**4. Test Push Notifications**:
```typescript
import { requestNotificationPermission, subscribeToPushNotifications } from './services/pwa';

// Request permission
const granted = await requestNotificationPermission();
console.log('Notification permission:', granted);

// Subscribe to push
const subscription = await subscribeToPushNotifications();
console.log('Push subscription:', subscription);
```

**5. Test Install Prompt**:
```typescript
import { showInstallPrompt } from './services/pwa';

// Show install prompt when button clicked
document.getElementById('install-btn').addEventListener('click', async () => {
  const installed = await showInstallPrompt();
  console.log('App installed:', installed);
});
```

**Expected Results**:
- ✅ Service worker registers successfully
- ✅ Offline page loads when network unavailable
- ✅ Install prompt appears (Chrome/Edge)
- ✅ Notification permission requested
- ✅ Push subscription created
- ✅ App works offline with cached data

**Check Service Worker**:
1. Open DevTools → Application tab
2. Service Workers section should show registered worker
3. Cache Storage should show cached assets
4. Manifest section should show app details

---

## Testing Checklist ✅

### Multi-Image Gallery
- [ ] Upload single image
- [ ] Bulk upload 10+ images
- [ ] Reorder images via API
- [ ] Set primary image
- [ ] Delete image (auto-promote next)
- [ ] Verify max 50 images enforced
- [ ] Check thumbnails in admin

### WebSocket Chat
- [ ] Connect to WebSocket
- [ ] Send/receive messages in real-time
- [ ] Test typing indicators
- [ ] Test read receipts
- [ ] Test presence (online/offline)
- [ ] Test auto-reconnect (kill connection)
- [ ] Verify message queue works offline

### Carfax Integration
- [ ] Validate VIN format
- [ ] Fetch mock report
- [ ] Verify report structure
- [ ] Test 7-day cache
- [ ] Check error handling (invalid VIN)

### WhatsApp Service
- [ ] Send text message (mock)
- [ ] Send vehicle inquiry (mock)
- [ ] Send template message (mock)
- [ ] Verify console logging
- [ ] Check message formatting

### PWA
- [ ] Service worker registers
- [ ] Offline page loads
- [ ] Install prompt appears
- [ ] Notification permission works
- [ ] Push subscription created
- [ ] Cache strategy works
- [ ] App shortcuts appear

---

## Troubleshooting 🔧

### Redis Connection Issues
```powershell
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running:
redis-server

# Check Redis logs
redis-cli info
```

### WebSocket Connection Fails
```javascript
// Check browser console for errors
// Common issues:
// - Redis not running
// - Wrong conversation ID
// - User not authenticated
// - CORS issues (check ALLOWED_HOSTS)
```

### Service Worker Not Registering
```javascript
// Check DevTools Console for errors
// Common issues:
// - Not on HTTPS (use localhost for testing)
// - Service worker file not found (check path)
// - Syntax errors in sw.js
```

### Images Not Uploading
```python
# Check settings:
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Verify folder exists and is writable
import os
print(os.path.exists('media/'))
```

---

## Performance Benchmarks 📊

### Expected Response Times

**Multi-Image Upload** (10 images):
- First upload: <5 seconds
- Subsequent: <3 seconds (S3 optimization)

**WebSocket Chat**:
- Message delivery: <100ms
- Typing indicator: <50ms
- Read receipt: <100ms

**Carfax Report** (mock):
- First fetch: <200ms
- Cache hit: <10ms

**WhatsApp Message** (mock):
- Send: <50ms (logging)
- Live API: <500ms (network)

**PWA**:
- Service worker registration: <100ms
- Cache hit: <10ms
- Offline page load: <50ms

---

## Next Steps 🎯

1. **Test All Features**: Complete the testing checklist above
2. **Monitor Performance**: Check response times match benchmarks
3. **Obtain API Keys**: Apply for Carfax and WhatsApp Business APIs
4. **Build Frontend UI**: Create React components for new features
5. **Deploy to Staging**: Test in production-like environment
6. **Train Team**: Document processes and train users
7. **Launch to Production**: Deploy with monitoring in place

---

## Support & Documentation

- **Implementation Summary**: `docs/Q1_2026_IMPLEMENTATION_COMPLETE.md`
- **WebSocket Service**: `frontend/src/services/websocket.ts`
- **PWA Utilities**: `frontend/src/services/pwa.ts`
- **Carfax Service**: `vehicle_history/carfax_service.py`
- **WhatsApp Service**: `notifications/whatsapp_service.py`
- **Image API**: `vehicles/image_views.py`

---

**Ready to test? Start Redis and fire up the WebSocket chat!** 🚀

```powershell
# Terminal 1: Redis
redis-server

# Terminal 2: Django
python manage.py runserver

# Terminal 3: Frontend
cd frontend
npm run dev

# Open: http://localhost:5173
```
