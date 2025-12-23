# Incident Response Playbook

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Owner:** Operations Team  
**Review Frequency:** Quarterly  

---

## 🚨 Quick Reference Card

**Print this page and keep near your desk during on-call rotation**

### Emergency Contacts
- **PagerDuty:** https://nzila-export.pagerduty.com/
- **Status Page:** https://status.nzila-export.com/
- **Slack Channel:** #incidents
- **AWS Console:** https://console.aws.amazon.com/
- **Sentry:** https://sentry.io/organizations/nzila-export/

### Severity Levels

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| **P0 - Critical** | Complete outage, data loss | Immediate | Page CTO after 30 min |
| **P1 - High** | Major feature down, degraded | 15 minutes | Page DevOps Lead after 1 hour |
| **P2 - Medium** | Minor feature impacted | 1 hour | Email team |
| **P3 - Low** | Cosmetic issue, no impact | 24 hours | Normal ticket |

### Quick Commands

```bash
# Check service health
curl https://api.nzila-export.com/health/

# Check database
python manage.py dbshell

# View recent errors
tail -f /var/log/nzila/error.log

# Restart services
sudo systemctl restart nzila-backend nzila-celery

# Check Celery queue
python manage.py shell -c "from celery import current_app; print(current_app.control.inspect().active())"

# Clear Redis cache
redis-cli FLUSHALL
```

---

## 📋 Incident Response Framework

### Phase 1: Detection & Assessment (0-5 minutes)

**Incident Sources:**
- Monitoring alerts (Sentry, UptimeRobot, Grafana)
- User reports (email, social media, support tickets)
- Manual discovery (team member notice)
- Security alerts (AWS GuardDuty, failed login attempts)

**Initial Assessment Questions:**
1. **What is broken?** (Database, API, frontend, payment system, etc.)
2. **When did it start?** (Check monitoring dashboards for exact time)
3. **Who is affected?** (All users, specific region, specific feature)
4. **Is data at risk?** (Data loss, corruption, security breach)
5. **What is the business impact?** (Revenue loss, reputation damage, legal)

**Severity Classification:**

**P0 - Critical (Page immediately, 24/7 response)**
- Complete site outage (>90% of users affected)
- Database unavailable or corrupted
- Payment processing completely down
- Security breach with data exposure
- Data loss or corruption

**P1 - High (Page during business hours, 15-min response)**
- Major feature unavailable (payments, deals, shipments)
- API errors >20% for >15 minutes
- Degraded performance affecting >50% of users
- Single-region outage
- Critical integration failure (Stripe, WhatsApp)

**P2 - Medium (Email alert, 1-hour response)**
- Minor feature unavailable (analytics, reports)
- Performance degradation affecting <50% users
- Non-critical integration failure
- Elevated error rates (<20%)
- UI/UX bugs affecting workflow

**P3 - Low (Ticket only, 24-hour response)**
- Cosmetic issues (styling, layout)
- Minor bugs with workarounds
- Documentation errors
- Non-urgent feature requests

---

### Phase 2: Notification & Communication (5-7 minutes)

**Step-by-Step Communication Protocol:**

1. **Create PagerDuty Incident** (1 minute)
   ```
   - Go to https://nzila-export.pagerduty.com/
   - Click "New Incident"
   - Title: "[P0/P1/P2/P3] Brief description"
   - Assign to: On-call engineer
   - Urgency: High (P0/P1) or Low (P2/P3)
   - Add incident channel: #incident-YYYY-MM-DD
   ```

2. **Update Status Page** (1 minute)
   ```
   - Go to https://status.nzila-export.com/admin
   - Create new incident
   - Status: "Investigating" → "Identified" → "Monitoring" → "Resolved"
   - Affected components: Select impacted services
   - Message template:
     
     "We are currently investigating reports of [issue].
     Our team is actively working on a resolution.
     We will provide updates every 15 minutes.
     Affected services: [list services]
     Started at: [time] UTC"
   ```

3. **Post to Slack #incidents** (1 minute)
   ```
   @here [P0] Database connection failures detected
   
   Status: Investigating
   Started: 14:30 UTC
   Impact: All users unable to log in
   Assigned: @oncall-engineer
   PagerDuty: https://...
   Status Page: Updated
   ```

4. **Email Stakeholders** (2 minutes - for P0/P1 only)
   ```
   To: operations@nzila-export.com, cto@nzila-export.com
   Subject: [P0 INCIDENT] Brief description
   
   An incident has been detected and is being investigated.
   
   Severity: P0 (Critical)
   Started: [time] UTC
   Impact: [description]
   Status: Investigating
   Assigned: [engineer name]
   
   We will send updates every 15 minutes.
   
   PagerDuty: [link]
   Status Page: [link]
   ```

5. **Create Incident Channel** (2 minutes - for P0/P1)
   ```
   - Slack: Create #incident-2024-12-20
   - Invite: @oncall-engineer, @devops-lead, @cto
   - Pin: PagerDuty link, status page link, runbook link
   - Purpose: Coordinate response, share updates
   ```

---

### Phase 3: Containment & Mitigation (7-20 minutes)

**Goal:** Stop the damage, prevent it from getting worse

**Actions by Incident Type:**

#### Database Issues
```bash
# 1. Check database connectivity
python manage.py dbshell
# If fails: Database is unreachable

# 2. Check database size and connections
SELECT pg_database_size('nzila_db');
SELECT count(*) FROM pg_stat_activity;

# 3. Check slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;

# 4. Kill long-running queries if needed
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <pid>;

# 5. If database is corrupted:
# - STOP all writes immediately (maintenance mode)
# - Proceed to disaster recovery (restore from backup)
```

#### Application Server Issues
```bash
# 1. Check service status
sudo systemctl status nzila-backend nzila-celery nginx redis

# 2. Check recent logs
sudo journalctl -u nzila-backend -n 100 --no-pager
tail -f /var/log/nzila/error.log

# 3. Check resource usage
top
df -h  # Disk space
free -h  # Memory

# 4. Restart services (if safe)
sudo systemctl restart nzila-backend
sudo systemctl restart nzila-celery

# 5. If server is unresponsive:
# - Launch new instance
# - Update load balancer
# - Investigate old instance offline
```

#### Payment System Issues
```bash
# 1. Check Stripe dashboard
# - Go to https://dashboard.stripe.com/
# - Check for API errors, declined payments

# 2. Check Stripe webhook status
python manage.py shell
>>> from payments.models import Payment
>>> Payment.objects.filter(created_at__gte='2024-12-20 14:00').count()

# 3. Check Celery tasks for payment processing
# Look for failed payment_processing tasks

# 4. If payments are failing:
# - Enable maintenance mode for payment page
# - Queue payments for retry
# - Contact Stripe support if their issue
```

#### Security Incidents
```bash
# 1. IMMEDIATELY isolate affected systems
# - Disable external access (security groups)
# - Disconnect from internet if severe

# 2. Preserve evidence
# - Take snapshots of affected instances
# - Save logs before any changes
aws ec2 create-snapshot --volume-id vol-xxx

# 3. Reset compromised credentials
# - Rotate AWS keys
# - Reset database passwords
# - Force user password reset if needed

# 4. Contact security team
# - Email: security@nzila-export.com
# - Follow security incident protocol

# 5. DO NOT RESTORE from backup yet
# - Backup might be compromised
# - Forensics needed first
```

---

### Phase 4: Recovery & Resolution (20-60 minutes)

**Follow appropriate disaster recovery procedure:**

See [Disaster Recovery Plan](DISASTER_RECOVERY_PLAN.md) for detailed procedures:
- Procedure 1: Database Restore
- Procedure 2: Application Server Failure
- Procedure 3: AWS Region Outage
- Procedure 4: Ransomware/Cyber Attack

**Standard Recovery Steps:**

1. **Execute recovery procedure** (30-45 min)
   - Follow documented runbook
   - Document every action taken
   - Update incident channel every 10 minutes

2. **Verify recovery** (10-15 min)
   ```bash
   # Health check
   curl https://api.nzila-export.com/health/
   
   # Test critical paths
   # - User login
   # - View vehicles
   # - Create deal
   # - Process payment
   # - Upload document
   
   # Check monitoring dashboards
   # - Sentry: Error rate back to normal?
   # - Grafana: Response times back to normal?
   # - UptimeRobot: All endpoints green?
   ```

3. **Monitor for regressions** (15-30 min)
   - Watch error rates closely
   - Check for cascading failures
   - Monitor user feedback
   - Keep incident channel active

---

### Phase 5: Communication Updates

**During Incident (Every 15 minutes):**

```
Status Page Update:
"Update [time] UTC: We have identified the root cause as [description].
Our team is actively working on restoring service.
Current status: [X% of functionality restored]
Estimated resolution: [time] UTC"
```

```
Slack Update:
🔄 Update #3 (15:00 UTC)
- Root cause: Database connection pool exhausted
- Action: Restarted database, increased pool size
- Status: 80% of users can now access site
- ETA: Full resolution by 15:30 UTC
```

**Resolution Notification:**

```
Status Page:
"Resolved [time] UTC: The incident has been resolved.
All services are now operating normally.
Root cause: [brief description]
Resolution: [brief description]
We apologize for any inconvenience caused.
Total duration: [X] minutes"
```

```
Slack:
✅ RESOLVED (15:30 UTC)
Duration: 60 minutes
Root cause: Database connection pool exhaustion
Fix: Increased pool size from 20 to 50, restarted services
Impact: ~1,000 users affected (login failures)
Post-mortem: Will be scheduled for Friday
```

---

### Phase 6: Post-Incident Review (24-48 hours later)

**Post-Mortem Meeting Agenda:**

1. **Timeline Review** (10 min)
   - When did it start?
   - When was it detected?
   - When was it resolved?
   - Downtime duration

2. **Root Cause Analysis** (15 min)
   - What was the immediate cause?
   - What was the underlying cause?
   - Why wasn't it detected earlier?
   - Could it have been prevented?

3. **Response Effectiveness** (10 min)
   - What went well?
   - What could be improved?
   - Were RTO/RPO targets met?
   - Communication effectiveness

4. **Action Items** (15 min)
   - Technical improvements
   - Process improvements
   - Documentation updates
   - Monitoring additions

5. **Prevention** (10 min)
   - How do we prevent this from happening again?
   - Early warning signs to watch for
   - Proactive monitoring changes

**Post-Mortem Template:**

```markdown
# Incident Post-Mortem: [Title]

**Date:** [Date]
**Duration:** [X] minutes
**Severity:** P0/P1/P2/P3
**Impact:** [Number] users affected
**Authors:** [Names]

## Summary
Brief 2-3 sentence summary of what happened.

## Timeline
| Time (UTC) | Event |
|------------|-------|
| 14:30 | Incident started (database connection failures) |
| 14:35 | First monitoring alert triggered |
| 14:37 | PagerDuty incident created |
| 14:40 | On-call engineer began investigation |
| 14:50 | Root cause identified (pool exhaustion) |
| 15:00 | Fix deployed (increased pool size) |
| 15:15 | Services restored |
| 15:30 | Incident resolved |

## Root Cause
Detailed explanation of what caused the incident.

## Detection
How was the incident detected? Could it have been detected earlier?

## Resolution
What was done to resolve the incident?

## Impact
- Users affected: ~1,000
- Revenue impact: ~$X
- SLA impact: 60 minutes downtime (99.9% → 99.8% for the day)
- Reputation impact: [assessment]

## What Went Well
- Quick detection (5 minutes)
- Clear communication
- Effective teamwork

## What Could Be Improved
- Monitoring should have alerted earlier
- Runbook was incomplete
- Recovery took longer than RTO target

## Action Items
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| Add connection pool monitoring | @devops | 2024-12-27 | High |
| Update runbook with pool tuning | @oncall | 2024-12-21 | Medium |
| Increase connection pool to 100 | @devops | 2024-12-20 | High |
| Test load under high traffic | @qa | 2024-12-30 | Medium |

## Lessons Learned
- Database connection pool was undersized for traffic
- Need better capacity planning
- Monitoring gaps existed for connection metrics
```

---

## 📞 Escalation Matrix

### Escalation Triggers

**Escalate to DevOps Lead when:**
- P0 incident lasts >30 minutes
- P1 incident lasts >1 hour
- On-call engineer needs assistance
- Root cause is unclear

**Escalate to CTO when:**
- P0 incident lasts >1 hour
- Data loss occurred
- Security breach suspected
- Multiple failures cascading
- Media/PR attention likely

**Escalate to CEO when:**
- Catastrophic data loss
- Major security breach with data exposure
- Legal implications
- Regulatory compliance violation

### Contact Information

| Role | Primary | Phone | Backup | Phone |
|------|---------|-------|--------|-------|
| On-Call Engineer | TBD | +1-XXX-XXX-XXXX | TBD | +1-XXX-XXX-XXXX |
| DevOps Lead | TBD | +1-XXX-XXX-XXXX | TBD | +1-XXX-XXX-XXXX |
| CTO | TBD | +1-XXX-XXX-XXXX | CEO | +1-XXX-XXX-XXXX |
| CEO | TBD | +1-XXX-XXX-XXXX | Board Member | +1-XXX-XXX-XXXX |
| AWS Support | N/A | Via Console | N/A | N/A |
| Stripe Support | N/A | dashboard.stripe.com | N/A | N/A |

---

## 🛠️ Common Incident Scenarios

### Scenario 1: "Site is Slow"

**Symptoms:** Users report slow page loads, API timeouts

**Quick Diagnosis:**
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.nzila-export.com/api/vehicles/

# Check database query performance
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)

# Check Celery queue backlog
python manage.py shell
>>> from celery import current_app
>>> inspect = current_app.control.inspect()
>>> print(inspect.reserved())

# Check Redis
redis-cli INFO stats
```

**Common Causes:**
1. Database slow queries (missing indexes)
2. Celery queue backlog
3. Redis cache full
4. High CPU/memory usage
5. Network issues

**Quick Fixes:**
```bash
# Restart services
sudo systemctl restart nzila-backend nzila-celery

# Clear Redis cache
redis-cli FLUSHALL

# Kill slow queries
# (Use database management tool)

# Scale up if resource-constrained
# (Launch additional application servers)
```

---

### Scenario 2: "Payments Are Failing"

**Symptoms:** Users cannot complete payments, Stripe errors

**Quick Diagnosis:**
```bash
# Check Stripe dashboard
# https://dashboard.stripe.com/

# Check recent payment attempts
python manage.py shell
>>> from payments.models import Payment
>>> recent_payments = Payment.objects.filter(created_at__gte='now-1hour')
>>> failed = recent_payments.filter(status='failed')
>>> print(f"Success rate: {100 - (failed.count() / recent_payments.count() * 100)}%")

# Check Celery payment tasks
# Look for stuck/failed tasks

# Check webhook logs
tail -f /var/log/nzila/stripe_webhooks.log
```

**Common Causes:**
1. Stripe API outage
2. Invalid API keys
3. Card declines (normal)
4. Webhook failures
5. Database issues

**Quick Fixes:**
```bash
# Verify Stripe API status
curl https://status.stripe.com/

# Check API keys are valid
python manage.py shell
>>> import stripe
>>> stripe.api_key = settings.STRIPE_SECRET_KEY
>>> stripe.Account.retrieve()

# Retry failed webhooks manually
python manage.py retry_stripe_webhooks --since="1 hour ago"

# Enable payment queue for retry
# (Payments will be queued if Stripe is down)
```

---

### Scenario 3: "Users Cannot Login"

**Symptoms:** Login attempts fail, "Invalid credentials" errors

**Quick Diagnosis:**
```bash
# Check authentication service
curl -X POST https://api.nzila-export.com/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Check database user table
python manage.py shell
>>> from accounts.models import CustomUser
>>> CustomUser.objects.count()

# Check JWT token generation
# Look for expired keys, configuration issues

# Check Redis (session storage)
redis-cli PING
```

**Common Causes:**
1. Database connection issues
2. Redis unavailable (sessions)
3. JWT secret key changed
4. Password hash algorithm changed
5. Database migration missing

**Quick Fixes:**
```bash
# Restart authentication services
sudo systemctl restart nzila-backend redis

# Regenerate JWT tokens (extreme case)
# Users will need to re-login

# Check migrations
python manage.py showmigrations
python manage.py migrate

# Clear broken sessions
redis-cli FLUSHDB
```

---

## ✅ Incident Checklist

Print this and keep next to your desk:

### Detection (0-5 min)
- [ ] Confirm the incident is real (not false alarm)
- [ ] Determine severity (P0/P1/P2/P3)
- [ ] Note exact start time (UTC)
- [ ] Identify affected systems/users

### Notification (5-10 min)
- [ ] Create PagerDuty incident
- [ ] Update status page ("Investigating")
- [ ] Post to Slack #incidents
- [ ] Email stakeholders (P0/P1 only)
- [ ] Create incident channel (P0/P1 only)

### Containment (10-20 min)
- [ ] Stop the damage from spreading
- [ ] Preserve evidence (logs, snapshots)
- [ ] Isolate affected systems if needed
- [ ] Update status page ("Identified")

### Recovery (20-60 min)
- [ ] Execute appropriate recovery procedure
- [ ] Document all actions taken
- [ ] Update incident channel every 10 min
- [ ] Update status page ("Monitoring")

### Verification (60-75 min)
- [ ] Test critical user flows
- [ ] Check monitoring dashboards
- [ ] Monitor for regressions (30 min)
- [ ] Update status page ("Resolved")

### Communication (75-90 min)
- [ ] Notify users of resolution
- [ ] Close PagerDuty incident
- [ ] Post resolution to Slack
- [ ] Thank team members

### Post-Mortem (24-48 hours)
- [ ] Schedule post-mortem meeting
- [ ] Write incident report
- [ ] Identify action items
- [ ] Update documentation
- [ ] Implement improvements

---

## 📚 Related Documents

- [Disaster Recovery Plan](DISASTER_RECOVERY_PLAN.md)
- [Monitoring Guide](MONITORING_GUIDE.md)
- [SLA Targets](SLA_TARGETS.md)
- [Security Incident Response](security/SECURITY_INCIDENT_RESPONSE.md)
- [On-Call Guide](ON_CALL_GUIDE.md)

---

**For questions or updates, contact:** operations@nzila-export.com

**Document Status:** ✅ APPROVED  
**Next Review:** March 20, 2026
