# Sentry Configuration Guide

## Overview

Sentry is configured for error tracking and performance monitoring across both backend (Django) and frontend (React) applications. This guide covers setup, configuration, and usage.

## Prerequisites

- Sentry account (free tier available at [sentry.io](https://sentry.io))
- Two projects in Sentry: one for backend (Python/Django) and one for frontend (JavaScript/React)

## Quick Setup

### 1. Create Sentry Account & Projects

1. Sign up at [https://sentry.io/signup/](https://sentry.io/signup/)
2. Create an organization (e.g., "Nzila Exports")
3. Create two projects:
   - **Backend Project**: Select "Django" platform
   - **Frontend Project**: Select "React" platform

### 2. Get Your DSN Keys

After creating each project, you'll receive a DSN (Data Source Name) that looks like:
```
https://abc123def456@o123456.ingest.sentry.io/789012
```

### 3. Configure Environment Variables

#### Backend (.env)
```bash
# Sentry Configuration
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development  # or staging, production
APP_VERSION=1.0.0
```

#### Frontend (frontend/.env)
```bash
# Sentry Configuration
VITE_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
VITE_ENVIRONMENT=development  # or staging, production
```

## Current Implementation

### Backend (Django)

**Location**: `nzila_export/settings.py` (lines 222-245)

**Features**:
- ✅ Automatic error tracking
- ✅ Django integration for request context
- ✅ Celery integration for background tasks
- ✅ Performance monitoring (10% sample rate)
- ✅ Profiling (10% sample rate)
- ✅ GDPR compliant (PII not sent by default)
- ✅ Release tracking

**Configuration**:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT', default='development')

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        environment=SENTRY_ENVIRONMENT,
        release=config('APP_VERSION', default='1.0.0'),
        send_default_pii=False,
    )
```

### Frontend (React)

**Location**: `frontend/src/main.tsx` (lines 7-30)

**Features**:
- ✅ Automatic error tracking
- ✅ Browser tracing for performance monitoring
- ✅ Session replay (on errors only)
- ✅ Privacy-first (masks text and blocks media)
- ✅ Disabled in development mode
- ✅ Error boundary integration

**Configuration**:
```typescript
import * as Sentry from '@sentry/react'

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: ENVIRONMENT,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    enabled: ENVIRONMENT !== 'development',
  })
}
```

**Error Boundary**: `frontend/src/components/ErrorBoundary.tsx`
- Catches React component errors
- Logs to Sentry automatically
- Displays user-friendly error UI

## Production Deployment

### Docker Compose (Production)

**Location**: `docker-compose.prod.yml`

The production configuration includes Sentry DSNs:

```yaml
# Backend
backend:
  environment:
    - SENTRY_DSN=${SENTRY_DSN}
    - SENTRY_ENVIRONMENT=production

# Celery Worker
celery_worker:
  environment:
    - SENTRY_DSN=${SENTRY_DSN}
    - SENTRY_ENVIRONMENT=production

# Frontend
frontend:
  build:
    args:
      - VITE_SENTRY_DSN=${VITE_SENTRY_DSN}
```

### GitHub Actions (CI/CD)

The deploy workflow can be configured to create Sentry releases (currently commented out in `.github/workflows/deploy.yml`).

To enable:

1. Add GitHub repository secrets:
   - `SENTRY_AUTH_TOKEN`: Create at [Sentry Settings → Auth Tokens](https://sentry.io/settings/account/api/auth-tokens/)
   - Select scopes: `project:read`, `project:releases`, `org:read`

2. Add GitHub repository variables:
   - `SENTRY_ORG`: Your Sentry organization slug
   - `SENTRY_PROJECT`: Your Sentry project slug (backend or frontend)

3. Uncomment the Sentry release step in the workflow

## Environment-Specific Configuration

### Development
```bash
# Backend
SENTRY_DSN=  # Leave empty to disable
SENTRY_ENVIRONMENT=development

# Frontend
VITE_SENTRY_DSN=  # Leave empty to disable
VITE_ENVIRONMENT=development
```
- Sentry is automatically disabled in frontend when DSN is not set
- Backend will skip initialization if DSN is empty

### Staging
```bash
# Backend
SENTRY_DSN=https://your-backend-staging-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=staging

# Frontend
VITE_SENTRY_DSN=https://your-frontend-staging-dsn@sentry.io/project-id
VITE_ENVIRONMENT=staging
```
- Use separate projects or environments for staging
- Higher sample rates recommended (e.g., 0.5 or 50%)

### Production
```bash
# Backend
SENTRY_DSN=https://your-backend-prod-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
APP_VERSION=1.2.3  # Semantic versioning

# Frontend
VITE_SENTRY_DSN=https://your-frontend-prod-dsn@sentry.io/project-id
VITE_ENVIRONMENT=production
```
- Use production-specific DSNs
- Lower sample rates to control quota (10% is recommended)

## Manual Error Reporting

### Backend (Python)
```python
from sentry_sdk import capture_exception, capture_message

try:
    # Your code
    risky_operation()
except Exception as e:
    # Automatically captured, but you can add context
    capture_exception(e)

# Manual messages
capture_message("Something important happened", level="info")
```

### Frontend (TypeScript)
```typescript
import * as Sentry from '@sentry/react'

try {
  // Your code
  riskyOperation()
} catch (error) {
  // Automatically captured, but you can add context
  Sentry.captureException(error)
}

// Manual messages
Sentry.captureMessage("Something important happened", "info")
```

## Adding Context

### Backend
```python
from sentry_sdk import set_user, set_tag, set_context

# User context (automatically added in Django)
set_user({"id": user.id, "email": user.email})

# Custom tags
set_tag("payment_method", "stripe")

# Custom context
set_context("vehicle", {
    "id": vehicle.id,
    "make": vehicle.make,
    "model": vehicle.model
})
```

### Frontend
```typescript
import * as Sentry from '@sentry/react'

// User context
Sentry.setUser({ id: user.id, email: user.email })

// Custom tags
Sentry.setTag("payment_method", "stripe")

// Custom context
Sentry.setContext("vehicle", {
  id: vehicle.id,
  make: vehicle.make,
  model: vehicle.model
})
```

## Breadcrumbs

Breadcrumbs automatically track:
- Backend: Database queries, HTTP requests, console logs
- Frontend: Navigation, console logs, XHR/fetch requests, user clicks

Add custom breadcrumbs:

```python
# Backend
from sentry_sdk import add_breadcrumb

add_breadcrumb(
    category='vehicle',
    message='Vehicle listing viewed',
    level='info',
    data={'vehicle_id': 123}
)
```

```typescript
// Frontend
Sentry.addBreadcrumb({
  category: 'vehicle',
  message: 'Vehicle listing viewed',
  level: 'info',
  data: { vehicleId: 123 }
})
```

## Performance Monitoring

### Backend
```python
from sentry_sdk import start_transaction

# Transaction for a specific operation
with start_transaction(op="task", name="process_vehicle_images"):
    # Your code
    process_images()
```

### Frontend
```typescript
import * as Sentry from '@sentry/react'

// Wrap components for automatic performance tracking
export default Sentry.withProfiler(MyComponent)

// Manual transactions
const transaction = Sentry.startTransaction({
  op: "task",
  name: "Process Vehicle Images"
})

try {
  // Your code
  await processImages()
} finally {
  transaction.finish()
}
```

## Quota Management

Free tier includes:
- 5,000 errors per month
- 10,000 performance units per month
- 50 replay sessions per month

**Optimization strategies**:
1. Sample rates: Adjust based on traffic (current: 10%)
2. Environment filtering: Only enable in staging/production
3. Error grouping: Similar errors are grouped automatically
4. Ignore common errors:

```python
# Backend - settings.py
sentry_sdk.init(
    # ... other config
    ignore_errors=[
        'Http404',
        'PermissionDenied',
    ],
    before_send=filter_events,  # Custom filter function
)
```

```typescript
// Frontend - main.tsx
Sentry.init({
  // ... other config
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Network request failed',
  ],
  beforeSend(event) {
    // Custom filter logic
    return event
  }
})
```

## Dashboard & Alerts

### Recommended Dashboards
1. **Error Overview**: Errors by environment, browser, OS
2. **Performance**: Transaction durations, throughput
3. **Releases**: Compare error rates across releases

### Recommended Alerts
1. **High Error Rate**: >50 errors in 1 hour
2. **New Error Type**: First occurrence of new error
3. **Performance Degradation**: P95 response time >2s

Set up at: [Sentry → Alerts](https://sentry.io/alerts/)

## Integrations

### Slack
1. Go to [Sentry → Settings → Integrations](https://sentry.io/settings/integrations/)
2. Add Slack integration
3. Configure alerts to send to specific channels

### GitHub
1. Add GitHub integration
2. Link issues to Sentry errors
3. Auto-resolve errors when PR is merged

## Testing Configuration

### Backend Test
```bash
python manage.py shell
>>> from sentry_sdk import capture_message
>>> capture_message("Test error from Django", level="error")
```

### Frontend Test
```bash
# In browser console
Sentry.captureMessage("Test error from React", "error")
```

Check Sentry dashboard to confirm events are received.

## Troubleshooting

### Errors Not Appearing

1. **Check DSN is set correctly**:
   ```bash
   # Backend
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.SENTRY_DSN)
   
   # Frontend
   console.log(import.meta.env.VITE_SENTRY_DSN)
   ```

2. **Verify environment**:
   - Frontend errors are disabled in development mode by default
   - Check `enabled: ENVIRONMENT !== 'development'` in `main.tsx`

3. **Check rate limiting**:
   - Sample rates may cause some events to be dropped
   - Increase sample rates for testing

4. **Network issues**:
   - Verify firewall/proxy allows connections to `*.sentry.io`
   - Check browser developer tools Network tab

### High Quota Usage

1. **Reduce sample rates**:
   ```python
   traces_sample_rate=0.01  # 1% instead of 10%
   ```

2. **Filter noisy errors**:
   ```python
   ignore_errors=['SpecificError']
   ```

3. **Disable replays in production**:
   ```typescript
   replaysSessionSampleRate: 0.01  // Reduce to 1%
   ```

## Security Considerations

1. **PII (Personal Identifiable Information)**:
   - `send_default_pii=False` prevents sending user IPs, cookies
   - Session replay masks all text by default
   - Review [Sentry Data Scrubbing](https://docs.sentry.io/product/data-management-settings/scrubbing/)

2. **Source Maps**:
   - Upload source maps for better error traces (production only)
   - Keep source maps private to Sentry

3. **Authentication Tokens**:
   - Store `SENTRY_AUTH_TOKEN` securely in GitHub Secrets
   - Use scoped tokens with minimal permissions

## Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Django Integration](https://docs.sentry.io/platforms/python/integrations/django/)
- [React Integration](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Best Practices](https://docs.sentry.io/product/best-practices/)

## Support

For issues or questions:
1. Check [Sentry Status](https://status.sentry.io/)
2. Review [Sentry Community Forum](https://forum.sentry.io/)
3. Contact Sentry support (paid plans)
