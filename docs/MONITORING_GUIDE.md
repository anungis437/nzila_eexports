# Production Monitoring Guide

## Overview
Complete monitoring strategy for Nzila Export Hub ensuring 99.9% uptime, rapid incident detection, and proactive issue resolution.

## Table of Contents
1. [Monitoring Stack](#monitoring-stack)
2. [Observability Layers](#observability-layers)
3. [Alert Configuration](#alert-configuration)
4. [Dashboard Access](#dashboard-access)
5. [Daily Operations](#daily-operations)
6. [Troubleshooting Guides](#troubleshooting-guides)
7. [Maintenance Procedures](#maintenance-procedures)

---

## Monitoring Stack

### 1. Sentry (Application Performance Monitoring)
**Purpose**: Error tracking, performance monitoring, slow query detection
**URL**: https://sentry.io/organizations/nzila-export
**Cost**: $26/month (Team plan, 50K events)
**Key Features**:
- Real-time error tracking with stack traces
- Transaction performance monitoring (p50, p95, p99)
- Slow database query detection (<100ms threshold)
- Breadcrumb tracking (user actions leading to errors)
- Release tracking (correlate errors with deployments)

**Configuration**: [nzila_export/settings.py](nzila_export/settings.py#L347-L410)

### 2. UptimeRobot (Uptime Monitoring)
**Purpose**: External availability monitoring for critical endpoints
**URL**: https://uptimerobot.com/dashboard
**Public Status**: https://status.nzila-export.com
**Cost**: $7/month (Pro plan, 50 monitors, 5-min intervals)
**Monitors**: 10 critical endpoints
- API Health Check (5min)
- Authentication Service (5min)
- Deals API (5min)
- Vehicles API (5min)
- Payments API (5min)
- Database Health (5min)
- Redis Cache (5min)
- Celery Workers (5min)
- WebSocket Server (5min)
- Admin Portal (10min)

**Configuration**: [monitoring/uptimerobot_setup.md](monitoring/uptimerobot_setup.md)

### 3. Grafana (Business & Infrastructure Metrics)
**Purpose**: Business metrics, infrastructure monitoring, custom dashboards
**URL**: https://grafana.nzila-export.com
**Cost**: $0 (self-hosted)
**Dashboards**:
- Production Overview (main dashboard)
- API Performance (response times, error rates)
- Database Performance (query times, connection pool)
- Business Metrics (DAU, deals/day, revenue/day)
- Infrastructure Health (CPU, memory, disk, network)

**Configuration**: [monitoring/grafana_dashboard.json](monitoring/grafana_dashboard.json)

### 4. PagerDuty (Incident Management)
**Purpose**: 24/7 alerting, escalation, on-call management
**URL**: https://nzila-export.pagerduty.com
**Cost**: $168/month (8 users × $21/user)
**Services**: 6 services with escalation policies
- API Platform (Critical)
- Database & Cache (Critical)
- Payment Processing (Critical)
- Background Jobs (High)
- Authentication (Critical)
- Infrastructure (Critical)

**Configuration**: [monitoring/pagerduty_setup.md](monitoring/pagerduty_setup.md)

### 5. AWS CloudWatch (Infrastructure Monitoring)
**Purpose**: AWS resource monitoring, log aggregation
**URL**: https://console.aws.amazon.com/cloudwatch
**Cost**: ~$20/month (logs + metrics)
**Metrics**:
- EC2: CPU, memory, disk, network
- RDS: Database connections, queries/sec, storage
- S3: Bucket size, request count, data transfer
- Lambda: Invocations, duration, errors (if used)

---

## Observability Layers

### Layer 1: External Availability (UptimeRobot)
**Question**: Is the site up?
**Check Frequency**: Every 5 minutes
**Alert Threshold**: 1 down check (5 minutes)
**Response Time**: < 5 minutes
**Owner**: On-call engineer

**What It Monitors**:
- HTTP status codes (200, 302, 401 expected)
- Response time (< 2000ms expected)
- Keyword presence (`"status":"healthy"`)
- SSL certificate validity

**When It Alerts**:
- HTTP 5xx errors
- Timeout (> 30 seconds)
- Connection refused
- SSL certificate expired

### Layer 2: Application Errors (Sentry)
**Question**: Are there errors in the code?
**Check Frequency**: Real-time
**Alert Threshold**: Error rate > 5% (P0), > 2% (P1), > 0.5% (P2)
**Response Time**: < 5 minutes (P0), < 30 minutes (P1)
**Owner**: On-call engineer + dev who deployed recent release

**What It Monitors**:
- Unhandled exceptions
- API errors (4xx, 5xx)
- Database errors (connection, query, transaction)
- Payment processing errors
- Authentication/authorization errors
- Background job failures

**When It Alerts**:
- New error type introduced (regression)
- Error rate spikes suddenly
- Critical error (DatabaseError, StripeAPIError)
- Error affects > 10 users in 5 minutes

### Layer 3: Performance (Sentry APM)
**Question**: Is the site fast?
**Check Frequency**: Every request (10% sample rate)
**Alert Threshold**: p95 > 1000ms (Warning), p95 > 2000ms (Critical)
**Response Time**: < 1 hour (investigate if sustained)
**Owner**: On-call engineer

**What It Monitors**:
- API response time (p50, p95, p99)
- Database query time (<100ms target)
- External API calls (Stripe, exchange rates)
- Middleware execution time
- Cache hit rate

**When It Alerts**:
- Response time spike (>2x baseline)
- Slow queries increasing (>100ms)
- Cache hit rate drops (<80%)
- Database connection pool saturated

### Layer 4: Business Metrics (Grafana)
**Question**: Is the business healthy?
**Check Frequency**: Every 5 minutes
**Alert Threshold**: Varies by metric
**Response Time**: < 4 hours (investigate if anomaly)
**Owner**: Product/Business team + engineering

**What It Monitors**:
- Daily Active Users (DAU)
- Deals created per day
- Payment success rate (>95% expected)
- Revenue per day (CAD)
- Conversion rates
- Feature adoption rates

**When It Alerts**:
- DAU drops >20% from baseline
- Payment success rate <90%
- Zero deals created in 2 hours (during business hours)
- Revenue drops >50% from baseline

### Layer 5: Infrastructure (AWS CloudWatch)
**Question**: Are resources healthy?
**Check Frequency**: Every 5 minutes
**Alert Threshold**: CPU >90%, Disk >85%, Memory >90%
**Response Time**: < 1 hour
**Owner**: DevOps/Infrastructure team

**What It Monitors**:
- EC2 instance health (CPU, memory, disk, network)
- RDS database health (connections, queries, storage)
- S3 bucket usage and costs
- Lambda errors (if used)
- Network throughput

**When It Alerts**:
- EC2 instance down
- CPU sustained >90% for 10 minutes
- Disk >85% (risk of out-of-space)
- Database connections >80% of max
- Network errors increasing

---

## Alert Configuration

### Alert Severity Levels

#### P0: Critical (Complete Outage)
**Definition**: Complete platform down, data loss risk, revenue impact

**Examples**:
- Database server down
- All API endpoints returning 500
- Payment processing completely failed
- Security breach detected

**SLA**:
- Detection: < 5 minutes
- Response: < 5 minutes
- Resolution: < 1 hour
- Communication: Immediate (executives, customers)

**Escalation**:
1. Primary on-call (SMS + Phone) → 0 min
2. Secondary on-call (SMS + Phone) → 5 min
3. Engineering Manager (Phone) → 10 min
4. CTO/VP Engineering (Phone) → 15 min

**Compensation**: 3x hourly rate + $500 resolution bonus

#### P1: Critical Service Degradation
**Definition**: Single critical service down, elevated errors, payment issues

**Examples**:
- Payments processing slow (>30s)
- Authentication service down
- API error rate >5%
- Database connection pool saturated

**SLA**:
- Detection: < 5 minutes
- Response: < 30 minutes
- Resolution: < 4 hours
- Communication: Dev team, stakeholders

**Escalation**:
1. Primary on-call (SMS + Phone) → 0 min
2. Secondary on-call (SMS + Phone) → 15 min
3. Engineering Manager (Phone) → 30 min

**Compensation**: 2x hourly rate

#### P2: High Priority (Service Degradation)
**Definition**: Non-critical service degradation, elevated warnings

**Examples**:
- API response time >2000ms (p95)
- Redis cache down (API still works, slower)
- Celery queue backed up (>1000 tasks)
- Single worker down (others operational)

**SLA**:
- Detection: < 10 minutes
- Response: < 1 hour
- Resolution: < 8 hours (or next business day)
- Communication: Dev team

**Escalation**:
1. Primary on-call (SMS + Email) → 0 min
2. Secondary on-call (SMS) → 1 hour
3. Engineering Manager (Email) → 4 hours

**Compensation**: 1.5x hourly rate

#### P3: Medium Priority (Warnings)
**Definition**: Capacity warnings, minor issues, preventive alerts

**Examples**:
- Disk usage >70%
- Error rate >0.5% but <2%
- Slow queries increasing
- Unusual user behavior patterns

**SLA**:
- Detection: < 30 minutes
- Response: < 4 hours (business hours)
- Resolution: Best effort (create ticket)
- Communication: Engineering team (Slack)

**Escalation**:
1. Primary on-call (Email) → 0 min
2. Auto-escalate to P2 if unresolved after 8 hours

**Compensation**: Regular hourly rate (during on-call shift)

### Alert Routing Matrix

| Source | Event Type | Severity | Route To | Escalation Policy |
|--------|-----------|----------|----------|-------------------|
| UptimeRobot | API Down | P0 | PagerDuty (API Service) | Critical Infrastructure |
| UptimeRobot | Database Down | P0 | PagerDuty (Database Service) | Critical Infrastructure |
| UptimeRobot | Payment Down | P0 | PagerDuty (Payments Service) | Critical Infrastructure |
| Sentry | DatabaseError | P0 | PagerDuty (Database Service) | Critical Infrastructure |
| Sentry | StripeAPIError | P0 | PagerDuty (Payments Service) | Critical Infrastructure |
| Sentry | Error rate >5% | P0 | PagerDuty (API Service) | Critical Infrastructure |
| Sentry | Error rate >2% | P1 | PagerDuty (API Service) | High Priority |
| Sentry | p95 >2000ms | P2 | PagerDuty (API Service) | Medium Priority |
| Grafana | Payment success <90% | P1 | PagerDuty (Payments Service) | Critical Infrastructure |
| Grafana | DAU drops >20% | P2 | Email (Product Team) | No escalation |
| AWS CloudWatch | EC2 down | P0 | PagerDuty (Infrastructure) | Critical Infrastructure |
| AWS CloudWatch | CPU >90% | P2 | PagerDuty (Infrastructure) | High Priority |
| AWS CloudWatch | Disk >85% | P2 | PagerDuty (Infrastructure) | High Priority |

### Alert Tuning Guidelines

**Reduce False Positives**:
1. Use 2-check threshold for non-critical services (10 minutes instead of 5)
2. Allow expected HTTP codes (401 for auth endpoints = service is up)
3. Keyword monitoring to verify actual functionality
4. Exclude maintenance windows from alerts

**Prevent Alert Fatigue**:
1. Max 10 alerts/week per engineer (if exceeded, tune thresholds)
2. Group related alerts (if DB is down, suppress dependent service alerts)
3. Use alert aggregation in PagerDuty (5-minute window)
4. Weekly alert review meetings (disable noisy alerts)

**Ensure Critical Alerts Work**:
1. Test each alert type monthly
2. Verify escalation works (let it escalate to Level 2)
3. Check notification delivery (SMS, email, phone, push)
4. Update contact information quarterly

---

## Dashboard Access

### Sentry Dashboard
**URL**: https://sentry.io/organizations/nzila-export/issues/
**Login**: SSO with GitHub or email

**Key Views**:
- **Issues Dashboard**: All unresolved errors
- **Performance**: Transaction performance (API endpoints)
- **Releases**: Errors by release version
- **Alerts**: Configured alert rules

**Daily Checks**:
- [ ] Review new issues (unresolved errors)
- [ ] Check error trends (increasing or decreasing?)
- [ ] Review slow transactions (>1000ms)
- [ ] Verify no database performance regressions

### UptimeRobot Dashboard
**URL**: https://uptimerobot.com/dashboard
**Public Status Page**: https://status.nzila-export.com

**Key Views**:
- **Monitors**: Current status of all endpoints
- **Uptime**: 30-day uptime percentage
- **Response Times**: Avg/min/max response times
- **Alert Contacts**: Verify contacts are active

**Daily Checks**:
- [ ] Verify all monitors green (100% uptime)
- [ ] Review response time trends
- [ ] Check for any overnight alerts
- [ ] Verify status page is accessible

### Grafana Dashboard
**URL**: https://grafana.nzila-export.com
**Login**: Admin credentials (see CREDENTIALS.md)

**Key Views**:
- **Production Overview**: Main dashboard (all metrics)
- **API Performance**: Response times, error rates
- **Database Performance**: Query times, connection pool
- **Business Metrics**: DAU, deals, revenue

**Daily Checks**:
- [ ] Review API response times (p50, p95, p99)
- [ ] Check error rate (<0.5% target)
- [ ] Verify business metrics (DAU, deals, revenue)
- [ ] Review database query performance

### PagerDuty Dashboard
**URL**: https://nzila-export.pagerduty.com
**Mobile App**: iOS/Android available

**Key Views**:
- **Incidents**: Open incidents requiring attention
- **On-Call**: Current on-call schedule
- **Analytics**: MTTA, MTTR, escalation rate
- **Services**: Status of all monitored services

**Daily Checks**:
- [ ] Review open incidents (should be 0)
- [ ] Verify on-call schedule is correct
- [ ] Check for any overnight pages
- [ ] Review MTTA (should be <5 minutes)

### AWS CloudWatch Dashboard
**URL**: https://console.aws.amazon.com/cloudwatch
**Login**: AWS IAM credentials

**Key Views**:
- **EC2 Metrics**: CPU, memory, disk, network
- **RDS Metrics**: Database performance
- **S3 Metrics**: Bucket usage and costs
- **Logs**: Application and system logs

**Weekly Checks**:
- [ ] Review resource utilization trends
- [ ] Check for any capacity warnings
- [ ] Verify backup jobs completed successfully
- [ ] Review log insights for errors

---

## Daily Operations

### Morning Routine (9:00 AM)
**Duration**: 15 minutes
**Owner**: On-call engineer

1. **Check PagerDuty**:
   - Any overnight incidents?
   - Review incident status (all resolved?)
   - Check MTTA/MTTR from last 24 hours

2. **Review Sentry**:
   - New errors introduced?
   - Error trends (up or down?)
   - Any slow transactions?

3. **Check UptimeRobot**:
   - All monitors green?
   - Any response time spikes?
   - Review overnight alerts

4. **Grafana Overview**:
   - Business metrics (DAU, deals, revenue)
   - API performance (response times, errors)
   - Database performance (query times)

5. **Slack Update**:
   - Post daily status to #engineering
   - Format: "🟢 All systems operational" or "🟡 Investigating [issue]"

### Afternoon Check (2:00 PM)
**Duration**: 10 minutes
**Owner**: On-call engineer

1. **Mid-day Status**:
   - Sentry: New issues since morning?
   - Grafana: Business metrics on track?
   - PagerDuty: Any new incidents?

2. **Capacity Check**:
   - AWS CloudWatch: Resource utilization
   - Database: Connection pool usage
   - Redis: Memory usage

### Evening Wrap-Up (5:00 PM)
**Duration**: 10 minutes
**Owner**: On-call engineer

1. **Daily Summary**:
   - Total incidents: X
   - Major issues resolved: Y
   - Outstanding issues: Z

2. **Handoff to Night Shift** (if applicable):
   - Document any ongoing issues
   - Share context in #engineering
   - Update incident notes in PagerDuty

3. **Next Day Prep**:
   - Review on-call schedule (who's on tomorrow?)
   - Check for any planned maintenance
   - Verify backups completed successfully

---

## Troubleshooting Guides

### Issue: High API Response Time

**Symptoms**:
- Sentry: p95 >1000ms
- Grafana: Response time spike
- Users: Reporting slow page loads

**Diagnosis Commands**:
```bash
# 1. Check database query performance
python manage.py shell
from django.db import connection
print(connection.queries)

# 2. Check Celery queue length
celery -A nzila_export inspect active_queues

# 3. Check Redis memory usage
redis-cli INFO memory

# 4. Check database connection pool
SELECT count(*) FROM pg_stat_activity;

# 5. Check for slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**Resolution Steps**:
1. Identify bottleneck (database, external API, cache miss)
2. If database: Add index, optimize query
3. If external API: Add caching, increase timeout
4. If cache miss: Warm up cache, increase cache TTL
5. Monitor for improvement

### Issue: Payment Processing Failed

**Symptoms**:
- UptimeRobot: Payment health check failed
- Sentry: StripeAPIError
- PagerDuty: P0 alert

**Diagnosis Commands**:
```bash
# 1. Check Stripe API status
curl https://status.stripe.com/api/v2/status.json

# 2. Check Stripe webhooks
python manage.py shell
from deals.models import PaymentIntent
recent_payments = PaymentIntent.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
)
print(f"Recent payments: {recent_payments.count()}")

# 3. Check webhook delivery
# Go to Stripe Dashboard → Developers → Webhooks
# Review failed webhook deliveries

# 4. Test payment endpoint
curl -X POST https://nzila-export.com/api/payments/health/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Resolution Steps**:
1. If Stripe is down: Wait for Stripe recovery, communicate to users
2. If webhook issue: Manually retry failed webhooks in Stripe dashboard
3. If API error: Check Sentry for stack trace, deploy hotfix
4. If network issue: Check firewall rules, restart application
5. Verify payment processing resumed

### Issue: Database Connection Pool Exhausted

**Symptoms**:
- Sentry: `Too many connections` error
- Grafana: Database connections >80% of max
- Users: `500 Internal Server Error`

**Diagnosis Commands**:
```bash
# 1. Check active connections
psql -h localhost -U nzila_user -d nzila_db -c \
  "SELECT count(*) FROM pg_stat_activity;"

# 2. Identify long-running queries
psql -h localhost -U nzila_user -d nzila_db -c \
  "SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
   FROM pg_stat_activity 
   WHERE state != 'idle' 
   ORDER BY duration DESC;"

# 3. Check connection pool settings
grep -i "conn_max_age\|max_connections" nzila_export/settings.py

# 4. Kill long-running queries (if safe)
psql -h localhost -U nzila_user -d nzila_db -c \
  "SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state != 'idle' AND query_start < now() - interval '5 minutes';"
```

**Resolution Steps**:
1. Identify and kill long-running queries
2. Increase `CONN_MAX_AGE` (currently 600s)
3. Increase `max_connections` in PostgreSQL config
4. Review code for unclosed database connections
5. Add connection pooling (PgBouncer) if needed

### Issue: Redis Cache Down

**Symptoms**:
- UptimeRobot: Redis health check failed
- Sentry: `ConnectionError: Error connecting to Redis`
- Grafana: Cache hit rate = 0%

**Diagnosis Commands**:
```bash
# 1. Check Redis process
ps aux | grep redis

# 2. Check Redis port
netstat -an | grep 6379

# 3. Test Redis connection
redis-cli ping
# Expected: PONG

# 4. Check Redis logs
tail -n 100 /var/log/redis/redis-server.log

# 5. Check Redis memory usage
redis-cli INFO memory
```

**Resolution Steps**:
1. If Redis stopped: `sudo systemctl restart redis`
2. If memory full: Increase `maxmemory` or flush old keys
3. If network issue: Check firewall, restart networking
4. If corrupted: Restore from Redis persistence file
5. Verify cache operations resumed

### Issue: Celery Workers Not Processing Tasks

**Symptoms**:
- Grafana: Celery queue >1000 tasks
- Sentry: Celery task timeout errors
- Users: Background jobs not completing

**Diagnosis Commands**:
```bash
# 1. Check Celery workers
celery -A nzila_export inspect active

# 2. Check queue length
celery -A nzila_export inspect reserved

# 3. Check for stuck tasks
celery -A nzila_export inspect active_queues

# 4. Restart Celery workers
sudo systemctl restart celery
sudo systemctl restart celerybeat

# 5. Purge queue (if needed)
celery -A nzila_export purge
```

**Resolution Steps**:
1. Restart Celery workers
2. Check for memory leaks (workers consuming too much RAM)
3. Increase worker count (`--concurrency=8`)
4. Review task code for infinite loops
5. Monitor queue length for normalization

---

## Maintenance Procedures

### Weekly Maintenance (Sunday 2:00-4:00 AM)

**Pre-Maintenance Checklist**:
- [ ] Announce maintenance window (48 hours notice)
- [ ] Update status page (scheduled maintenance)
- [ ] Notify on-call engineer
- [ ] Verify backup completed successfully
- [ ] Test rollback procedure

**Maintenance Tasks**:
1. **Database Maintenance** (30 min):
   ```sql
   VACUUM ANALYZE;
   REINDEX DATABASE nzila_db;
   ```

2. **Log Rotation** (10 min):
   ```bash
   logrotate -f /etc/logrotate.d/nzila_export
   ```

3. **Dependency Updates** (30 min):
   ```bash
   pip install -U -r requirements.txt
   npm update
   ```

4. **Security Patches** (30 min):
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

5. **Cache Warm-Up** (10 min):
   ```bash
   python manage.py warm_cache
   ```

6. **Restart Services** (10 min):
   ```bash
   sudo systemctl restart nginx
   sudo systemctl restart gunicorn
   sudo systemctl restart celery
   sudo systemctl restart redis
   ```

**Post-Maintenance Checklist**:
- [ ] Verify all services started successfully
- [ ] Check Sentry for new errors
- [ ] Run smoke tests (critical user flows)
- [ ] Update status page (all operational)
- [ ] Monitor for 1 hour post-maintenance

### Monthly Maintenance (First Sunday)

**Additional Tasks**:
1. **SSL Certificate Renewal** (10 min):
   ```bash
   sudo certbot renew
   sudo systemctl reload nginx
   ```

2. **Backup Verification** (30 min):
   - Restore latest backup to staging environment
   - Verify data integrity
   - Document restore time (RTO validation)

3. **Security Audit** (1 hour):
   - Review user permissions
   - Audit access logs
   - Check for suspicious activity
   - Update security documentation

4. **Performance Review** (1 hour):
   - Analyze Sentry APM data
   - Identify performance regressions
   - Plan optimization tasks
   - Update performance baselines

### Quarterly Maintenance (First Sunday of Quarter)

**Additional Tasks**:
1. **Disaster Recovery Drill** (4 hours):
   - Simulate complete outage
   - Execute recovery procedures
   - Measure RTO/RPO
   - Document lessons learned

2. **Capacity Planning** (2 hours):
   - Review resource utilization trends
   - Forecast capacity needs (3-6 months)
   - Plan infrastructure upgrades
   - Update budget estimates

3. **Monitoring Review** (2 hours):
   - Audit all alert rules
   - Disable noisy alerts
   - Add missing alerts
   - Update escalation policies

4. **Documentation Update** (2 hours):
   - Review all monitoring docs
   - Update contact information
   - Add new troubleshooting guides
   - Archive obsolete procedures

---

## Performance Baselines

### API Response Times
| Metric | Baseline (Dec 2024) | Target | Alert Threshold |
|--------|-------------------|--------|----------------|
| p50 | 150ms | <200ms | >300ms |
| p95 | 450ms | <500ms | >1000ms |
| p99 | 850ms | <1000ms | >2000ms |

### Database Query Times
| Query Type | Baseline | Target | Alert Threshold |
|-----------|----------|--------|----------------|
| Simple SELECT | 5ms | <10ms | >50ms |
| JOIN (2-3 tables) | 25ms | <50ms | >100ms |
| Complex aggregation | 150ms | <200ms | >500ms |

### Error Rates
| Error Type | Baseline | Target | Alert Threshold |
|-----------|----------|--------|----------------|
| 4xx (Client) | 2% | <5% | >10% |
| 5xx (Server) | 0.1% | <0.5% | >2% |
| Database errors | 0.01% | <0.1% | >1% |

### Cache Performance
| Metric | Baseline | Target | Alert Threshold |
|--------|----------|--------|----------------|
| Hit rate | 92% | >90% | <80% |
| Avg latency | 1ms | <5ms | >10ms |

### Business Metrics
| Metric | Baseline (Dec 2024) | Target (Q1 2025) | Alert Threshold |
|--------|-------------------|-----------------|----------------|
| DAU | 500 | 750 (+50%) | <400 (-20%) |
| Deals/day | 50 | 75 (+50%) | <40 (-20%) |
| Payment success | 96% | >95% | <90% |
| Revenue/day (CAD) | $15,000 | $22,500 (+50%) | <$12,000 (-20%) |

---

## Support & Resources

### Internal Documentation
- [Disaster Recovery Plan](DISASTER_RECOVERY_PLAN.md)
- [Incident Response Playbook](INCIDENT_RESPONSE_PLAYBOOK.md)
- [UptimeRobot Setup](../monitoring/uptimerobot_setup.md)
- [PagerDuty Setup](../monitoring/pagerduty_setup.md)
- [Grafana Dashboard](../monitoring/grafana_dashboard.json)

### External Resources
- **Sentry Docs**: https://docs.sentry.io
- **UptimeRobot Docs**: https://uptimerobot.com/api
- **Grafana Docs**: https://grafana.com/docs
- **PagerDuty Docs**: https://support.pagerduty.com
- **AWS CloudWatch Docs**: https://docs.aws.amazon.com/cloudwatch

### Emergency Contacts
- **On-Call Engineer**: Check PagerDuty schedule
- **Engineering Manager**: manager@nzila-export.com
- **CTO**: cto@nzila-export.com
- **DevOps Team**: devops@nzila-export.com

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**Owner**: DevOps Team
**Review Cycle**: Monthly
