# PagerDuty Alerting Setup

## Overview
PagerDuty provides 24/7 incident management with automatic escalation, ensuring critical issues are addressed immediately.

## Table of Contents
1. [Escalation Policies](#escalation-policies)
2. [Services Configuration](#services-configuration)
3. [Integration Keys](#integration-keys)
4. [Alert Routing](#alert-routing)
5. [On-Call Schedules](#on-call-schedules)
6. [Response Workflows](#response-workflows)

---

## Escalation Policies

### Policy 1: Critical Infrastructure (P0/P1)
**Triggers**: Database down, complete outage, payment system failure

**Escalation Chain**:
1. **Level 1 (0 min)**: Primary On-Call Engineer
   - Notification: SMS, Phone Call, Push
   - Timeout: 5 minutes
   
2. **Level 2 (5 min)**: Secondary On-Call Engineer
   - Notification: SMS, Phone Call, Push
   - Timeout: 5 minutes
   
3. **Level 3 (10 min)**: Engineering Manager
   - Notification: SMS, Phone Call, Push
   - Timeout: 5 minutes
   
4. **Level 4 (15 min)**: CTO/VP Engineering
   - Notification: Phone Call
   - No timeout (escalate to executive team if needed)

### Policy 2: High Priority (P2)
**Triggers**: Single service degradation, slow response times, elevated error rates

**Escalation Chain**:
1. **Level 1 (0 min)**: Primary On-Call Engineer
   - Notification: SMS, Email, Push
   - Timeout: 15 minutes
   
2. **Level 2 (15 min)**: Secondary On-Call Engineer
   - Notification: SMS, Phone Call
   - Timeout: 15 minutes
   
3. **Level 3 (30 min)**: Engineering Manager
   - Notification: Phone Call
   - No further escalation

### Policy 3: Medium Priority (P3)
**Triggers**: Non-critical warnings, capacity alerts, minor bugs

**Escalation Chain**:
1. **Level 1 (0 min)**: Primary On-Call Engineer
   - Notification: Email, Push
   - Timeout: 1 hour
   
2. **Level 2 (1 hour)**: Engineering Team (group notification)
   - Notification: Email
   - No further escalation during business hours
   - Auto-escalate to P2 if unresolved after 4 hours

---

## Services Configuration

### Service 1: API Platform
**Integration**: Sentry (API errors)
**Escalation Policy**: Critical Infrastructure
**Alert Rules**:
- Error rate > 5% → P0
- Error rate > 2% → P1
- Error rate > 0.5% → P2
- Slow queries > 100ms (p95) → P3

**Integration Key**: `PAGERDUTY_API_PLATFORM_KEY`

### Service 2: Database & Cache
**Integration**: UptimeRobot, Sentry (database errors)
**Escalation Policy**: Critical Infrastructure
**Alert Rules**:
- Database down → P0
- Redis down → P1
- Connection pool > 90% → P2
- Slow queries increasing → P3

**Integration Key**: `PAGERDUTY_DATABASE_KEY`

### Service 3: Payment Processing
**Integration**: Stripe webhooks, Sentry (payment errors)
**Escalation Policy**: Critical Infrastructure
**Alert Rules**:
- Payment webhook failures → P0
- Stripe API errors > 5% → P0
- Payment processing time > 30s → P1
- Unusual refund rate → P2

**Integration Key**: `PAGERDUTY_PAYMENTS_KEY`

### Service 4: Background Jobs (Celery)
**Integration**: Celery monitoring, Sentry
**Escalation Policy**: High Priority
**Alert Rules**:
- All workers down → P1
- Task queue > 1000 → P2
- Task failures > 10% → P2
- Scheduled tasks missed → P3

**Integration Key**: `PAGERDUTY_CELERY_KEY`

### Service 5: Authentication & Sessions
**Integration**: UptimeRobot, Sentry (auth errors)
**Escalation Policy**: Critical Infrastructure
**Alert Rules**:
- Auth service down → P0
- Login failures > 20% → P1
- Session errors increasing → P2
- Redis session store issues → P2

**Integration Key**: `PAGERDUTY_AUTH_KEY`

### Service 6: Infrastructure & Hosting
**Integration**: AWS CloudWatch, UptimeRobot
**Escalation Policy**: Critical Infrastructure
**Alert Rules**:
- EC2 instance down → P0
- CPU > 90% for 10 min → P1
- Disk > 85% → P2
- Network errors increasing → P2

**Integration Key**: `PAGERDUTY_INFRA_KEY`

---

## Integration Keys

### Generating Integration Keys

1. **Log into PagerDuty**: https://nzila-export.pagerduty.com
2. **Navigate to**: Services → Service Directory
3. **For each service**: Click "Integrations" → "Add Integration"
4. **Select**: "Events API v2"
5. **Copy**: Integration Key (format: `R1234567890ABCDEF`)
6. **Add to environment variables**:

```bash
# .env.production
PAGERDUTY_API_PLATFORM_KEY=R1234567890ABCDEF
PAGERDUTY_DATABASE_KEY=R2345678901BCDEFG
PAGERDUTY_PAYMENTS_KEY=R3456789012CDEFGH
PAGERDUTY_CELERY_KEY=R4567890123DEFGHI
PAGERDUTY_AUTH_KEY=R5678901234EFGHIJ
PAGERDUTY_INFRA_KEY=R6789012345FGHIJK
```

### Testing Integration Keys

```python
import requests
import os

def test_pagerduty_integration(service_key, test_message):
    """Test PagerDuty integration by sending a test alert."""
    
    response = requests.post(
        'https://events.pagerduty.com/v2/enqueue',
        json={
            'routing_key': service_key,
            'event_action': 'trigger',
            'payload': {
                'summary': f'[TEST] {test_message}',
                'severity': 'info',
                'source': 'manual_test',
                'custom_details': {
                    'test': True,
                    'timestamp': '2024-01-15T10:00:00Z'
                }
            }
        }
    )
    
    return response.status_code == 202

# Test all services
services = {
    'API Platform': os.getenv('PAGERDUTY_API_PLATFORM_KEY'),
    'Database': os.getenv('PAGERDUTY_DATABASE_KEY'),
    'Payments': os.getenv('PAGERDUTY_PAYMENTS_KEY'),
    'Celery': os.getenv('PAGERDUTY_CELERY_KEY'),
    'Auth': os.getenv('PAGERDUTY_AUTH_KEY'),
    'Infrastructure': os.getenv('PAGERDUTY_INFRA_KEY'),
}

for name, key in services.items():
    result = test_pagerduty_integration(key, f'{name} service test')
    print(f"{name}: {'✅ Success' if result else '❌ Failed'}")
```

---

## Alert Routing

### Sentry Integration

Add to `nzila_export/settings.py`:

```python
# PagerDuty integration for critical errors
PAGERDUTY_ROUTING_KEYS = {
    'api': os.getenv('PAGERDUTY_API_PLATFORM_KEY'),
    'database': os.getenv('PAGERDUTY_DATABASE_KEY'),
    'payments': os.getenv('PAGERDUTY_PAYMENTS_KEY'),
    'celery': os.getenv('PAGERDUTY_CELERY_KEY'),
    'auth': os.getenv('PAGERDUTY_AUTH_KEY'),
}

def sentry_before_send(event, hint):
    """
    Route Sentry errors to PagerDuty based on severity and type.
    """
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Determine severity
        severity = determine_severity(exc_type, exc_value, event)
        
        # Route to PagerDuty if P0-P2
        if severity in ['critical', 'error', 'warning']:
            service_key = determine_service_key(event)
            send_to_pagerduty(event, service_key, severity)
    
    return event

def determine_severity(exc_type, exc_value, event):
    """Determine PagerDuty severity based on exception."""
    
    # P0 (Critical) - Complete outage
    if exc_type.__name__ in ['DatabaseError', 'ConnectionError', 'OSError']:
        return 'critical'
    
    # P1 (Error) - Service degradation
    if exc_type.__name__ in ['TimeoutError', 'HTTPError', 'StripeError']:
        return 'error'
    
    # P2 (Warning) - Minor issues
    if exc_type.__name__ in ['ValidationError', 'PermissionError']:
        return 'warning'
    
    return 'info'

def determine_service_key(event):
    """Route to appropriate PagerDuty service."""
    
    transaction = event.get('transaction', '')
    
    if 'payment' in transaction.lower():
        return PAGERDUTY_ROUTING_KEYS['payments']
    elif 'auth' in transaction.lower() or 'login' in transaction.lower():
        return PAGERDUTY_ROUTING_KEYS['auth']
    elif 'celery' in transaction.lower() or 'task' in transaction.lower():
        return PAGERDUTY_ROUTING_KEYS['celery']
    elif 'database' in event.get('tags', {}).get('logger', ''):
        return PAGERDUTY_ROUTING_KEYS['database']
    else:
        return PAGERDUTY_ROUTING_KEYS['api']

def send_to_pagerduty(event, routing_key, severity):
    """Send alert to PagerDuty."""
    
    import requests
    
    payload = {
        'routing_key': routing_key,
        'event_action': 'trigger',
        'payload': {
            'summary': event.get('message', 'Unknown error')[:1024],
            'severity': severity,
            'source': 'sentry',
            'timestamp': event.get('timestamp'),
            'custom_details': {
                'event_id': event.get('event_id'),
                'level': event.get('level'),
                'platform': event.get('platform'),
                'transaction': event.get('transaction'),
                'user': event.get('user', {}).get('email'),
                'environment': event.get('environment'),
                'release': event.get('release'),
            }
        },
        'links': [{
            'href': f"https://sentry.io/organizations/nzila-export/issues/?query={event.get('event_id')}",
            'text': 'View in Sentry'
        }]
    }
    
    try:
        requests.post(
            'https://events.pagerduty.com/v2/enqueue',
            json=payload,
            timeout=5
        )
    except Exception as e:
        # Don't let PagerDuty errors affect application
        pass

# Update Sentry configuration
sentry_sdk.init(
    # ... existing config ...
    before_send=sentry_before_send,
)
```

### UptimeRobot Integration

Configure webhook in UptimeRobot:

1. **Go to**: My Settings → Alert Contacts → Add Alert Contact
2. **Type**: Webhook
3. **URL**: `https://events.pagerduty.com/v2/enqueue`
4. **Method**: POST (Custom)
5. **Body**:

```json
{
  "routing_key": "YOUR_SERVICE_KEY",
  "event_action": "trigger",
  "payload": {
    "summary": "*monitorFriendlyName* is *alertTypeFriendlyName*",
    "severity": "error",
    "source": "uptimerobot",
    "custom_details": {
      "monitor_id": "*monitorID*",
      "monitor_url": "*monitorURL*",
      "alert_type": "*alertType*",
      "alert_datetime": "*alertDateTime*"
    }
  },
  "links": [{
    "href": "*monitorURL*",
    "text": "View Monitor"
  }]
}
```

6. **Test**: Send test notification

---

## On-Call Schedules

### Primary On-Call Schedule

**Rotation**: Weekly (Monday 9:00 AM → Monday 9:00 AM)

**Engineers**:
1. Week 1-2: Engineer A
2. Week 3-4: Engineer B
3. Week 5-6: Engineer C
4. Week 7-8: Engineer D

**Compensation**: $500/week on-call bonus + hourly rate for incidents

### Secondary On-Call Schedule

**Rotation**: Weekly (offset by 4 weeks from primary)

**Engineers**:
1. Week 1-2: Engineer C
2. Week 3-4: Engineer D
3. Week 5-6: Engineer A
4. Week 7-8: Engineer B

**Compensation**: $250/week on-call bonus + hourly rate for incidents

### Manager On-Call Schedule

**Rotation**: Monthly

**Managers**:
1. Month 1: Engineering Manager A
2. Month 2: Engineering Manager B
3. Month 3: Engineering Manager A
4. Month 4: Engineering Manager B

**Compensation**: Included in manager responsibilities

### Schedule Configuration

```python
# scripts/setup_pagerduty_schedules.py
from pdpyras import APISession

api_token = os.getenv('PAGERDUTY_API_TOKEN')
session = APISession(api_token)

# Create primary on-call schedule
primary_schedule = session.post('/schedules', json={
    'schedule': {
        'name': 'Primary On-Call',
        'time_zone': 'America/New_York',
        'schedule_layers': [{
            'name': 'Weekly Rotation',
            'start': '2024-01-15T09:00:00',
            'rotation_virtual_start': '2024-01-15T09:00:00',
            'rotation_turn_length_seconds': 604800,  # 1 week
            'users': [
                {'user': {'id': 'ENGINEER_A_ID', 'type': 'user_reference'}},
                {'user': {'id': 'ENGINEER_B_ID', 'type': 'user_reference'}},
                {'user': {'id': 'ENGINEER_C_ID', 'type': 'user_reference'}},
                {'user': {'id': 'ENGINEER_D_ID', 'type': 'user_reference'}},
            ],
            'restrictions': []  # 24/7 coverage
        }]
    }
})

print(f"Created primary schedule: {primary_schedule['schedule']['id']}")
```

---

## Response Workflows

### P0: Critical Outage

**Trigger**: Complete platform down, database failure, payment system failure

**Workflow**:
1. **0-1 min**: PagerDuty alert sent (SMS + Phone Call)
2. **1-3 min**: On-call engineer acknowledges
3. **3-5 min**: Initial assessment and war room creation
4. **5-10 min**: Incident communication sent to stakeholders
5. **10-30 min**: Mitigation steps executed
6. **30-60 min**: Service restoration
7. **24-48 hours**: Post-mortem

**Communication**:
- Slack: #incidents (immediate)
- Email: executives@nzila-export.com (within 5 min)
- Status Page: Public update (within 10 min)
- Customer Support: Alert support team (within 15 min)

### P1: Critical Service Degradation

**Trigger**: Single service down, payment processing slow, elevated errors

**Workflow**:
1. **0-2 min**: PagerDuty alert sent (SMS + Phone Call)
2. **2-5 min**: On-call engineer acknowledges
3. **5-15 min**: Investigation and diagnosis
4. **15-30 min**: Mitigation plan executed
5. **30-90 min**: Service restoration
6. **48 hours**: Post-mortem (optional)

**Communication**:
- Slack: #incidents (immediate)
- Email: dev-team@nzila-export.com (within 15 min)
- Status Page: Update if user-facing (within 30 min)

### P2: Service Degradation

**Trigger**: Slow response times, elevated warnings, capacity issues

**Workflow**:
1. **0-5 min**: PagerDuty alert sent (SMS + Email)
2. **5-15 min**: On-call engineer acknowledges
3. **15-60 min**: Investigation and diagnosis
4. **1-4 hours**: Resolution
5. **No post-mortem required** (unless recurring issue)

**Communication**:
- Slack: #engineering (within 30 min)
- Email: dev-team@nzila-export.com (if unresolved after 2 hours)

### P3: Minor Issues

**Trigger**: Warnings, capacity alerts, non-critical bugs

**Workflow**:
1. **0-15 min**: PagerDuty alert sent (Email only)
2. **15-60 min**: On-call engineer reviews
3. **During business hours**: Address if capacity available
4. **Create ticket**: For backlog if not immediately actionable

**Communication**:
- Slack: #engineering (optional)
- Email: None required

---

## PagerDuty Analytics

### Key Metrics to Track

1. **MTTA (Mean Time To Acknowledge)**
   - Target: < 5 minutes for P0/P1
   - Target: < 15 minutes for P2
   - Measure: Time from alert to acknowledgement

2. **MTTR (Mean Time To Resolve)**
   - Target: < 1 hour for P0
   - Target: < 4 hours for P1
   - Target: < 24 hours for P2
   - Measure: Time from alert to resolution

3. **Escalation Rate**
   - Target: < 10% of alerts escalate
   - High escalation rate indicates:
     - Incorrect primary on-call assignment
     - Alerts not clear enough
     - Training gaps

4. **Alert Volume**
   - Target: < 10 alerts/week
   - High volume indicates:
     - Alert fatigue risk
     - Need to tune alert thresholds
     - Potential systemic issues

5. **False Positive Rate**
   - Target: < 5%
   - High rate indicates:
     - Alert tuning needed
     - Monitoring configuration issues

### Monthly Review Process

1. **Generate PagerDuty Analytics Report**
   - Export incident data for last 30 days
   - Analyze MTTA, MTTR, escalation rate
   - Identify trends and patterns

2. **Team Retrospective**
   - Review major incidents
   - Discuss response effectiveness
   - Identify improvement opportunities

3. **Alert Tuning**
   - Disable noisy alerts
   - Adjust thresholds for false positives
   - Add missing alerts based on incidents

4. **On-Call Feedback**
   - Survey on-call engineers
   - Address pain points
   - Update runbooks and documentation

---

## Cost Analysis

### PagerDuty Pricing

**Professional Plan**: $21/user/month
- Unlimited schedules
- Unlimited escalation policies
- Advanced analytics
- Webhooks and API access
- 14-day incident history

**Team Composition**:
- 6 engineers (primary + secondary rotation)
- 2 managers
- Total: 8 users

**Monthly Cost**: $168/month
**Annual Cost**: $2,016/year

### ROI Calculation

**Value Delivered**:
- Faster incident response (MTTR reduced from 2 hours → 30 minutes)
- Revenue protected: 1.5 hours × $8,800/hour = $13,200 per incident
- Expected incidents prevented/mitigated: 12/year
- **Annual Value**: $158,400

**ROI**: 7,757% ($158,400 value / $2,016 cost)

**Additional Benefits**:
- Reduced stress on on-call engineers (clear escalation)
- Better stakeholder communication (automated updates)
- Improved SLA compliance (faster response)
- Enhanced team accountability (clear ownership)

---

## Implementation Checklist

### Phase 1: Setup (Week 1)
- [ ] Create PagerDuty account (Professional plan)
- [ ] Add all engineers and managers as users
- [ ] Configure notification methods (SMS, phone, email, push)
- [ ] Test notifications for all users

### Phase 2: Services (Week 1)
- [ ] Create 6 services (API, Database, Payments, Celery, Auth, Infrastructure)
- [ ] Generate integration keys for each service
- [ ] Add integration keys to environment variables
- [ ] Test each integration with test alert

### Phase 3: Escalation Policies (Week 1)
- [ ] Create "Critical Infrastructure" policy (3 levels)
- [ ] Create "High Priority" policy (2 levels)
- [ ] Create "Medium Priority" policy (1 level)
- [ ] Assign policies to services

### Phase 4: Schedules (Week 1)
- [ ] Create primary on-call schedule (weekly rotation)
- [ ] Create secondary on-call schedule (weekly rotation)
- [ ] Create manager on-call schedule (monthly rotation)
- [ ] Add schedules to escalation policies

### Phase 5: Integrations (Week 2)
- [ ] Integrate Sentry (API errors → PagerDuty)
- [ ] Integrate UptimeRobot (downtime → PagerDuty)
- [ ] Integrate AWS CloudWatch (infrastructure → PagerDuty)
- [ ] Integrate Slack (#incidents channel)

### Phase 6: Testing (Week 2)
- [ ] Test P0 alert (complete outage scenario)
- [ ] Test P1 alert (service degradation scenario)
- [ ] Test P2 alert (warning scenario)
- [ ] Test escalation (let alert escalate to level 2)
- [ ] Test acknowledgement and resolution workflow

### Phase 7: Documentation (Week 2)
- [ ] Document on-call responsibilities
- [ ] Document escalation procedures
- [ ] Document incident response workflows
- [ ] Train team on PagerDuty usage

### Phase 8: Monitoring (Ongoing)
- [ ] Weekly: Review open incidents
- [ ] Monthly: Analyze MTTA/MTTR metrics
- [ ] Quarterly: Survey on-call engineers
- [ ] Annually: Review and optimize alert policies

---

## Support & Resources

### PagerDuty Support
- **Email**: support@pagerduty.com
- **Phone**: 1-844-800-5790
- **Documentation**: https://support.pagerduty.com
- **Community**: https://community.pagerduty.com
- **Status Page**: https://status.pagerduty.com

### Internal Resources
- **On-Call Runbook**: `/docs/INCIDENT_RESPONSE_PLAYBOOK.md`
- **Disaster Recovery**: `/docs/DISASTER_RECOVERY_PLAN.md`
- **Sentry Dashboard**: https://sentry.io/organizations/nzila-export
- **Grafana Dashboard**: https://grafana.nzila-export.com
- **Status Page**: https://status.nzila-export.com

### Emergency Contacts
- **CTO**: cto@nzila-export.com | +1-XXX-XXX-XXXX
- **VP Engineering**: vp-eng@nzila-export.com | +1-XXX-XXX-XXXX
- **DevOps Lead**: devops@nzila-export.com | +1-XXX-XXX-XXXX

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**Owner**: DevOps Team
**Review Cycle**: Quarterly
