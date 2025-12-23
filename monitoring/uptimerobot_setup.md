# UptimeRobot Monitoring Setup

## Overview
UptimeRobot monitors critical API endpoints with 5-minute intervals to ensure 99.9% uptime SLA.

## Critical Endpoints to Monitor

### 1. API Health Check
- **URL**: `https://nzila-export.com/api/health/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200
- **Keyword Monitoring**: `"status":"healthy"`
- **Alert Contacts**: dev-team@nzila-export.com, ops@nzila-export.com
- **Alert After**: 1 down check (5 minutes)

### 2. Authentication Service
- **URL**: `https://nzila-export.com/api/auth/login/`
- **Type**: HTTP(s)
- **Method**: POST
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200, 400 (both indicate service is up)
- **Alert After**: 2 down checks (10 minutes)
- **Payload**: `{"username":"healthcheck","password":"test"}`

### 3. Deals API
- **URL**: `https://nzila-export.com/api/deals/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200, 401 (service is up even if unauthorized)
- **Alert After**: 1 down check (5 minutes)

### 4. Vehicles API
- **URL**: `https://nzila-export.com/api/vehicles/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200
- **Alert After**: 1 down check (5 minutes)

### 5. Payments API
- **URL**: `https://nzila-export.com/api/payments/health/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200
- **Keyword Monitoring**: `"stripe_connected":true`
- **Alert After**: 1 down check (5 minutes)
- **CRITICAL**: Payment failures require immediate response

### 6. Database Connection
- **URL**: `https://nzila-export.com/api/db-health/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200
- **Keyword Monitoring**: `"database":"connected"`
- **Alert After**: 1 down check (5 minutes)
- **CRITICAL**: Database issues affect entire platform

### 7. Redis Cache
- **URL**: `https://nzila-export.com/api/cache-health/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200
- **Keyword Monitoring**: `"redis":"connected"`
- **Alert After**: 2 down checks (10 minutes)

### 8. Celery Worker
- **URL**: `https://nzila-export.com/api/celery-health/`
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Expected HTTP Code**: 200
- **Keyword Monitoring**: `"workers_active":true`
- **Alert After**: 2 down checks (10 minutes)

### 9. WebSocket Server
- **URL**: `wss://nzila-export.com/ws/`
- **Type**: Port (443)
- **Interval**: 5 minutes
- **Alert After**: 2 down checks (10 minutes)

### 10. Admin Portal
- **URL**: `https://nzila-export.com/admin/`
- **Type**: HTTP(s)
- **Interval**: 10 minutes
- **Expected HTTP Code**: 200, 302
- **Alert After**: 2 down checks (20 minutes)

## Alert Contacts Configuration

### Primary Contacts
1. **Dev Team Email**
   - Email: dev-team@nzila-export.com
   - Alert for: All monitors
   - Threshold: After 1 down check

2. **Operations Team Email**
   - Email: ops@nzila-export.com
   - Alert for: Critical monitors (Payments, Database, API Health)
   - Threshold: After 1 down check

3. **On-Call Engineer SMS**
   - Phone: +1-XXX-XXX-XXXX
   - Alert for: P0/P1 incidents only
   - Threshold: After 2 down checks or 3+ monitors down

4. **PagerDuty Integration**
   - Webhook: https://events.pagerduty.com/integration/[key]/enqueue
   - Alert for: All critical monitors
   - Auto-escalate: Yes

### Secondary Contacts
5. **Slack #incidents Channel**
   - Webhook: https://hooks.slack.com/services/[your-webhook]
   - Alert for: All monitors
   - Format: JSON with incident details

## Response Time SLA

| Monitor Type | Target Response Time | Alert After | Escalate After |
|-------------|---------------------|-------------|----------------|
| API Health | < 500ms | 5 min | 10 min |
| Database | < 200ms | 5 min | 10 min |
| Payments | < 1000ms | 5 min | 5 min |
| Authentication | < 500ms | 10 min | 15 min |
| Other APIs | < 1000ms | 10 min | 20 min |

## Uptime SLA Targets

### Monthly Targets
- **Overall Platform**: 99.9% uptime (43.8 minutes downtime/month allowed)
- **Critical Services** (Payments, Auth, DB): 99.95% uptime (21.9 minutes/month)
- **Non-Critical Services**: 99.5% uptime (3.6 hours/month)

### Incident Response Times
- **P0 (Complete Outage)**: < 5 minutes detection, < 15 minutes response
- **P1 (Critical Service Down)**: < 5 minutes detection, < 30 minutes response
- **P2 (Degraded Performance)**: < 10 minutes detection, < 1 hour response
- **P3 (Minor Issues)**: < 30 minutes detection, < 4 hours response

## Dashboard Configuration

### UptimeRobot Dashboard URL
- Public Status Page: `https://stats.uptimerobot.com/[your-key]`
- Display: All monitors, current status, 30-day uptime %
- Branding: Nzila Export Hub logo
- Custom domain: `status.nzila-export.com` (optional)

### Status Page Customization
```json
{
  "title": "Nzila Export Hub Status",
  "logo_url": "https://nzila-export.com/logo.png",
  "custom_domain": "status.nzila-export.com",
  "monitors_to_show": [1, 2, 3, 4, 5, 6, 7, 8],
  "show_timezone": true,
  "timezone": "America/New_York",
  "refresh_interval": 60,
  "layout": "list",
  "theme": "dark"
}
```

## Setup Instructions

### Step 1: Create UptimeRobot Account
1. Go to https://uptimerobot.com
2. Sign up for Pro plan ($7/month for 50 monitors)
3. Verify email and login

### Step 2: Add Alert Contacts
1. Navigate to "My Settings" → "Alert Contacts"
2. Add email contacts:
   - dev-team@nzila-export.com
   - ops@nzila-export.com
3. Add Slack webhook (optional)
4. Add PagerDuty integration webhook
5. Test each contact

### Step 3: Create Monitors
Run the following script to create all monitors via API:

```bash
python scripts/setup_uptimerobot.py
```

Or manually create each monitor using the configuration above.

### Step 4: Configure Maintenance Windows
1. Navigate to "Maintenance Windows"
2. Add weekly maintenance window:
   - Day: Sunday
   - Time: 02:00 - 04:00 AM ET
   - Monitors: All
   - Reason: "Scheduled maintenance and updates"

### Step 5: Set Up Status Page
1. Navigate to "Public Status Pages"
2. Click "Add New"
3. Select monitors to display
4. Customize branding
5. Enable incident history (30 days)
6. Copy public URL and share with team

### Step 6: Test Alerts
1. Use "Test Alert" feature for each contact
2. Verify emails are received
3. Verify Slack notifications work
4. Verify PagerDuty integration escalates correctly
5. Document response times

## API Automation Script

Create `scripts/setup_uptimerobot.py`:

```python
import requests
import os

UPTIMEROBOT_API_KEY = os.getenv('UPTIMEROBOT_API_KEY')
API_URL = 'https://api.uptimerobot.com/v2/'

monitors = [
    {
        'friendly_name': 'API Health Check',
        'url': 'https://nzila-export.com/api/health/',
        'type': 1,  # HTTP(s)
        'interval': 300,  # 5 minutes
        'keyword_type': 2,  # Exists
        'keyword_value': '"status":"healthy"',
        'alert_contacts': '[alert_contact_ids]'
    },
    # Add other monitors...
]

def create_monitor(monitor_config):
    """Create a single monitor in UptimeRobot."""
    response = requests.post(
        f'{API_URL}newMonitor',
        data={
            'api_key': UPTIMEROBOT_API_KEY,
            'format': 'json',
            **monitor_config
        }
    )
    return response.json()

def setup_all_monitors():
    """Create all monitors."""
    for monitor in monitors:
        result = create_monitor(monitor)
        print(f"Created monitor: {monitor['friendly_name']} - {result['stat']}")

if __name__ == '__main__':
    setup_all_monitors()
```

## Monitoring Best Practices

### 1. Alert Fatigue Prevention
- Don't alert on every single down check
- Use 2-check threshold for non-critical services
- Group related alerts (e.g., if DB is down, don't alert on every dependent service)
- Implement alert aggregation in PagerDuty

### 2. False Positive Reduction
- Use keyword monitoring to verify actual functionality
- Allow 400/401 responses for auth endpoints (service is up, just requires authentication)
- Exclude maintenance windows from uptime calculations
- Monitor from multiple global locations

### 3. Incident Correlation
- When multiple monitors go down simultaneously, escalate immediately (likely infrastructure issue)
- Database down = expect cascade failures in dependent services
- Payment failures = immediate P0 escalation (revenue impact)

### 4. Response Time Optimization
- API response times should be < 500ms (p95)
- Database queries should be < 100ms (p95)
- If response times consistently exceed thresholds, investigate performance optimization

### 5. Uptime Reporting
- Generate monthly uptime reports
- Share with stakeholders
- Track trends (improving or degrading?)
- Use as input for capacity planning

## Integration with Sentry

UptimeRobot should complement Sentry APM:
- **UptimeRobot**: External availability monitoring (is the site up?)
- **Sentry**: Internal performance monitoring (are requests fast? any errors?)

When UptimeRobot detects downtime:
1. Alert is sent to on-call engineer
2. Engineer checks Sentry for related errors/performance issues
3. Engineer follows incident response playbook
4. Root cause is identified and fixed
5. Post-mortem is conducted

## Maintenance Schedule

### Daily
- Review overnight alerts
- Check uptime percentages
- Verify all monitors are green

### Weekly
- Review response time trends
- Analyze any incidents
- Update monitor configurations if needed
- Test alert contacts

### Monthly
- Generate uptime report
- Review SLA compliance
- Optimize alert thresholds
- Plan infrastructure improvements

### Quarterly
- Audit all monitors (are they still relevant?)
- Review and update escalation policies
- Conduct DR drill (simulate total outage)
- Update documentation

## Costs

### UptimeRobot Pro Plan
- **Monthly Cost**: $7/month
- **Monitors Included**: 50
- **Check Interval**: Down to 1 minute
- **Alert Contacts**: Unlimited
- **Status Pages**: 1 included
- **Annual Cost**: $84/year

### ROI Calculation
- **Cost**: $84/year
- **Value**: Prevents downtime (1 hour downtime = $8,800 revenue loss based on $77K annual risk)
- **ROI**: 10,400% (one prevented outage pays for 105 years of monitoring)
- **Additional Benefits**:
  - Customer trust maintained
  - SLA compliance ensured
  - Proactive issue detection
  - Reduced MTTR (Mean Time To Recovery)

## Support & Troubleshooting

### UptimeRobot Support
- Email: support@uptimerobot.com
- Documentation: https://uptimerobot.com/api/
- Response Time: < 24 hours

### Common Issues

**Issue**: Monitor shows down but site is accessible
- **Cause**: Firewall blocking UptimeRobot IPs
- **Fix**: Whitelist UptimeRobot IP ranges in firewall

**Issue**: Too many false positive alerts
- **Cause**: Overly aggressive thresholds
- **Fix**: Increase alert_after to 2 checks (10 minutes)

**Issue**: Alerts not being received
- **Cause**: Email blocked by spam filter
- **Fix**: Whitelist noreply@uptimerobot.com

**Issue**: Status page not updating
- **Cause**: Cache issue
- **Fix**: Clear browser cache or add cache-busting parameter

## Next Steps

1. ✅ Review this configuration with team
2. ✅ Create UptimeRobot account
3. ✅ Add alert contacts
4. ✅ Create all 10 monitors
5. ✅ Configure status page
6. ✅ Test alerts (all contacts)
7. ✅ Add monitors to PagerDuty escalation policy
8. ✅ Share status page URL with team
9. ✅ Schedule monthly uptime review meetings
10. ✅ Document any custom monitors for your specific use case

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**Owner**: DevOps Team
**Review Cycle**: Quarterly
