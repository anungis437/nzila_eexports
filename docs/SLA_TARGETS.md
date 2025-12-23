# Service Level Agreement (SLA) Targets

## Overview
This document defines the Service Level Agreements (SLAs) for Nzila Export Hub production environment, including uptime targets, response time goals, and incident management commitments.

## Table of Contents
1. [Uptime SLA](#uptime-sla)
2. [Performance SLA](#performance-sla)
3. [Incident Response SLA](#incident-response-sla)
4. [Data Protection SLA](#data-protection-sla)
5. [Support SLA](#support-sla)
6. [Monitoring & Reporting](#monitoring--reporting)
7. [SLA Violations & Credits](#sla-violations--credits)

---

## Uptime SLA

### Overall Platform Uptime
**Target**: 99.9% monthly uptime
**Calculation**: `(Total Minutes - Downtime Minutes) / Total Minutes × 100`
**Allowed Downtime**: 43.8 minutes per month (8.76 hours per year)

**Excluded from SLA**:
- Scheduled maintenance (announced 48 hours in advance)
- Third-party service outages (Stripe, AWS, etc.)
- User-caused issues (invalid API requests, DDoS attacks)
- Force majeure events (natural disasters, pandemics, etc.)

### Service-Level Uptime Targets

| Service | Target Uptime | Allowed Downtime/Month | Severity When Down |
|---------|--------------|----------------------|-------------------|
| API Platform | 99.95% | 21.9 minutes | P0 (Critical) |
| Payment Processing | 99.95% | 21.9 minutes | P0 (Critical) |
| Authentication | 99.95% | 21.9 minutes | P0 (Critical) |
| Database | 99.99% | 4.4 minutes | P0 (Critical) |
| Admin Portal | 99.9% | 43.8 minutes | P1 (High) |
| WebSocket Notifications | 99.5% | 3.6 hours | P2 (Medium) |
| Background Jobs | 99.0% | 7.2 hours | P2 (Medium) |

### Uptime Measurement

**Monitoring Method**: UptimeRobot with 5-minute check intervals
**Calculation Period**: Calendar month (1st 00:00 to last day 23:59)
**Reporting**: Published monthly on public status page

**Example Calculation** (January 2024):
```
Total minutes in January: 31 days × 24 hours × 60 minutes = 44,640 minutes
Actual downtime: 35 minutes (15 min planned maintenance + 20 min unplanned)
Effective downtime: 20 minutes (exclude planned maintenance)
Uptime: (44,640 - 20) / 44,640 = 99.955% ✅ (Target: 99.9%)
```

---

## Performance SLA

### API Response Time
**Target**: p95 response time < 500ms
**Measurement**: Sentry APM (10% sample rate)
**Calculation Period**: Monthly average

| Percentile | Target | Warning Threshold | Critical Threshold |
|-----------|--------|------------------|-------------------|
| p50 (Median) | <200ms | >300ms | >500ms |
| p75 | <350ms | >500ms | >800ms |
| p95 | <500ms | >1000ms | >2000ms |
| p99 | <1000ms | >2000ms | >5000ms |

### Database Query Performance
**Target**: p95 query time < 100ms
**Measurement**: Sentry APM + PostgreSQL slow query log
**Calculation Period**: Monthly average

| Query Type | Target (p95) | Warning | Critical |
|-----------|-------------|---------|----------|
| Simple SELECT | <10ms | >50ms | >100ms |
| JOIN (2-3 tables) | <50ms | >100ms | >200ms |
| Complex aggregation | <200ms | >500ms | >1000ms |
| INSERT/UPDATE | <20ms | >100ms | >200ms |

### Page Load Time (Frontend)
**Target**: p95 page load < 2 seconds
**Measurement**: Google Lighthouse + Real User Monitoring
**Calculation Period**: Monthly average

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| First Contentful Paint (FCP) | <1.0s | >1.8s | >3.0s |
| Largest Contentful Paint (LCP) | <2.5s | >4.0s | >6.0s |
| Cumulative Layout Shift (CLS) | <0.1 | >0.25 | >0.5 |
| Time to Interactive (TTI) | <3.0s | >5.0s | >7.0s |

### Error Rate
**Target**: <0.5% of all requests result in errors
**Measurement**: Sentry error tracking
**Calculation Period**: Monthly average

| Error Type | Target | Warning | Critical |
|-----------|--------|---------|----------|
| 4xx (Client errors) | <5% | >10% | >20% |
| 5xx (Server errors) | <0.5% | >2% | >5% |
| Database errors | <0.1% | >1% | >5% |
| Payment errors | <1% | >5% | >10% |

---

## Incident Response SLA

### Incident Severity Definitions

#### P0: Critical (Complete Outage)
**Definition**: Complete platform down, data loss risk, security breach

**Examples**:
- All API endpoints returning 500
- Database server down
- Payment processing completely failed
- Data breach or security incident

**SLA Commitments**:
- Detection Time: <5 minutes
- Acknowledgement Time: <5 minutes
- Initial Response: <5 minutes
- Resolution Time: <1 hour
- Communication: Immediate (public status page + email)
- Post-Mortem: Within 24 hours

**Escalation**:
1. Primary on-call engineer (0 min)
2. Secondary on-call engineer (5 min)
3. Engineering Manager (10 min)
4. CTO/VP Engineering (15 min)

#### P1: High (Critical Service Degradation)
**Definition**: Single critical service down, elevated errors

**Examples**:
- Authentication service down
- Payment processing slow (>30s)
- API error rate >5%
- Database connection pool saturated

**SLA Commitments**:
- Detection Time: <5 minutes
- Acknowledgement Time: <30 minutes
- Initial Response: <30 minutes
- Resolution Time: <4 hours
- Communication: Dev team + stakeholders
- Post-Mortem: Within 48 hours (if major impact)

**Escalation**:
1. Primary on-call engineer (0 min)
2. Secondary on-call engineer (30 min)
3. Engineering Manager (1 hour)

#### P2: Medium (Service Degradation)
**Definition**: Non-critical service degradation, elevated warnings

**Examples**:
- API response time >2000ms (p95)
- Redis cache down (API still works, slower)
- Celery queue backed up (>1000 tasks)
- Single worker down

**SLA Commitments**:
- Detection Time: <10 minutes
- Acknowledgement Time: <1 hour
- Initial Response: <1 hour
- Resolution Time: <8 hours (or next business day)
- Communication: Dev team (Slack)
- Post-Mortem: Optional (if recurring)

**Escalation**:
1. Primary on-call engineer (0 min)
2. Secondary on-call engineer (2 hours)
3. Engineering Manager (4 hours)

#### P3: Low (Minor Issues)
**Definition**: Capacity warnings, minor issues, preventive alerts

**Examples**:
- Disk usage >70%
- Error rate >0.5% but <2%
- Slow queries increasing
- Unusual user behavior

**SLA Commitments**:
- Detection Time: <30 minutes
- Acknowledgement Time: <4 hours (business hours)
- Initial Response: <4 hours (business hours)
- Resolution Time: Best effort (create ticket)
- Communication: Engineering team (Slack)
- Post-Mortem: Not required

**Escalation**:
- Auto-escalate to P2 if unresolved after 8 hours

### Response Time Metrics (MTTA/MTTR)

**MTTA (Mean Time To Acknowledge)**:
- P0: <5 minutes (target), <10 minutes (max)
- P1: <30 minutes (target), <1 hour (max)
- P2: <1 hour (target), <2 hours (max)
- P3: <4 hours (target), <8 hours (max)

**MTTR (Mean Time To Resolve)**:
- P0: <1 hour (target), <2 hours (max)
- P1: <4 hours (target), <8 hours (max)
- P2: <8 hours (target), <24 hours (max)
- P3: Best effort (no SLA)

**Measurement**: PagerDuty analytics dashboard
**Reporting**: Monthly performance review

---

## Data Protection SLA

### Backup Frequency
**Target**: Automated backups every hour
**Retention Policy**: 
- 7 daily backups (last 7 days, kept for 7 days)
- 4 weekly backups (last 4 weeks, kept for 4 weeks)
- 12 monthly backups (last 12 months, kept for 12 months)

**Backup Locations**:
- Primary: AWS S3 (US-East-1)
- Secondary: AWS S3 (US-West-2) - Cross-region replication
- Tertiary: AWS Glacier (long-term archival, >6 months old)

**Backup Verification**: Daily automated restore test to staging environment

### Recovery Time Objective (RTO)
**Target**: <1 hour for complete database restoration
**Measurement**: Quarterly DR drills + monthly backup restore tests

**RTO by Scenario**:
| Disaster Scenario | RTO Target | RTO Maximum | Last Tested |
|------------------|-----------|------------|-------------|
| Database corruption | 45 minutes | 1 hour | TBD |
| Application server failure | 15 minutes | 30 minutes | TBD |
| AWS region outage | 2 hours | 4 hours | TBD |
| Ransomware attack | 4 hours | 8 hours | TBD |

### Recovery Point Objective (RPO)
**Target**: <15 minutes of data loss maximum
**Measurement**: Time between last successful backup and disaster event

**RPO by Scenario**:
| Disaster Scenario | RPO Target | RPO Maximum | Data Loss Risk |
|------------------|-----------|------------|----------------|
| Database corruption | 15 minutes | 1 hour | Minimal |
| Hardware failure | 15 minutes | 1 hour | Minimal |
| Cyber attack | 1 hour | 4 hours | Low |
| Natural disaster | 4 hours | 24 hours | Medium |

### Backup Success Rate
**Target**: >99.5% of backups complete successfully
**Measurement**: Daily backup monitoring + email notifications
**Alert Threshold**: 2 consecutive backup failures = P1 incident

**Monthly Backup Report**:
```
January 2024 Backup Report:
- Total backup attempts: 744 (31 days × 24 hours)
- Successful backups: 742 (99.73%)
- Failed backups: 2 (0.27%)
- Average backup size: 2.3 GB
- Average backup duration: 8 minutes
- Total S3 storage used: 156 GB
- Estimated monthly S3 cost: $3.60
✅ SLA Met (>99.5%)
```

---

## Support SLA

### Business Hours Support
**Hours**: Monday-Friday, 9:00 AM - 5:00 PM ET
**Channels**: Email, Slack, Phone
**Response Times**:
- Critical (P0): <15 minutes
- High (P1): <1 hour
- Medium (P2): <4 hours
- Low (P3): <8 hours

### After-Hours Support
**Hours**: Weekends, holidays, 5:00 PM - 9:00 AM ET
**Channels**: PagerDuty, Phone (emergencies only)
**Response Times**:
- Critical (P0): <15 minutes
- High (P1): <2 hours
- Medium (P2): Next business day
- Low (P3): Next business day

### Support Channels

#### Email Support
- **Address**: support@nzila-export.com
- **Response Time**: Within 4 hours (business hours)
- **Use For**: Non-urgent issues, feature requests, general inquiries

#### Slack Support
- **Channel**: #engineering (internal), #support (customer-facing)
- **Response Time**: Within 1 hour (business hours)
- **Use For**: Quick questions, status updates, clarifications

#### Phone Support
- **Number**: +1-XXX-XXX-XXXX
- **Response Time**: Immediate (business hours)
- **Use For**: P0/P1 incidents, urgent issues only

#### PagerDuty
- **Use**: Critical incidents (P0/P1) after hours
- **Response Time**: <5 minutes (SMS + Phone call)
- **Escalation**: Automatic after 5 minutes

---

## Monitoring & Reporting

### Real-Time Monitoring

**Uptime Monitoring** (UptimeRobot):
- Check Frequency: Every 5 minutes
- Public Status Page: https://status.nzila-export.com
- Historical Data: 30 days visible to public

**Performance Monitoring** (Sentry APM):
- Sample Rate: 10% of all requests
- Retention: 90 days of transaction data
- Slow Query Detection: Queries >100ms logged

**Error Tracking** (Sentry):
- Real-time error capture and grouping
- Retention: 90 days of error data
- Alert on new error types or spikes

**Business Metrics** (Grafana):
- Refresh: Every 5 minutes
- Retention: 1 year of metric data
- Custom dashboards for stakeholders

### SLA Reporting

**Daily Reports** (Automated):
- Uptime: Last 24 hours
- Error Count: Last 24 hours
- Incident Summary: Open/closed incidents
- Distribution: #engineering Slack channel (9:00 AM ET)

**Weekly Reports** (Automated):
- Uptime: Last 7 days
- Performance: API response times (p50, p95, p99)
- Error Trends: Increasing/decreasing errors
- Incident Summary: All incidents + resolution times
- Distribution: Engineering leadership (Monday 9:00 AM ET)

**Monthly Reports** (Manual):
- Uptime: Calendar month percentage
- SLA Compliance: Met/missed targets
- Incident Analysis: Total incidents by severity
- MTTA/MTTR: Average response and resolution times
- Performance Trends: Month-over-month comparison
- Recommendations: Improvements for next month
- Distribution: Executives + stakeholders (5th of following month)

**Quarterly Reports** (Manual):
- Uptime: Quarterly average + trend analysis
- SLA Violations: Root causes + corrective actions
- Capacity Planning: Resource utilization trends
- DR Testing: Drill results + RTO/RPO validation
- Cost Analysis: Infrastructure costs vs. budget
- Roadmap: Infrastructure improvements for next quarter
- Distribution: Board of Directors (within 15 days of quarter end)

### Example Monthly SLA Report

```markdown
# Nzila Export Hub - January 2024 SLA Report

## Executive Summary
✅ All SLA targets met for January 2024
- Uptime: 99.96% (Target: 99.9%)
- P0 Incidents: 0 (Target: <2)
- MTTA: 4.2 minutes (Target: <5 minutes)
- MTTR: 32 minutes (Target: <60 minutes)

## Uptime Performance

### Overall Platform
- **Uptime**: 99.96% ✅
- **Allowed Downtime**: 43.8 minutes
- **Actual Downtime**: 17.8 minutes
- **Margin**: 26 minutes remaining

**Downtime Breakdown**:
1. Jan 15, 2:00-2:15 AM (15 min) - Planned maintenance ❌ Excluded
2. Jan 22, 10:23-10:40 AM (17 min) - Database query timeout (P1) ✅ Counted
3. Jan 22, 10:40-10:41 AM (1 min) - Service restart ✅ Counted

### Service-Level Uptime
| Service | Target | Actual | Status | Notes |
|---------|--------|--------|--------|-------|
| API Platform | 99.95% | 99.96% | ✅ Met | 17.8 min downtime |
| Payments | 99.95% | 100% | ✅ Met | 0 min downtime |
| Authentication | 99.95% | 100% | ✅ Met | 0 min downtime |
| Database | 99.99% | 99.96% | ✅ Met | 17.8 min downtime |
| Admin Portal | 99.9% | 100% | ✅ Met | 0 min downtime |

## Performance Metrics

### API Response Times
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| p50 | <200ms | 178ms | ✅ Met |
| p95 | <500ms | 423ms | ✅ Met |
| p99 | <1000ms | 867ms | ✅ Met |

### Database Query Times
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| p95 | <100ms | 87ms | ✅ Met |
| Slow Queries (>100ms) | <1% | 0.8% | ✅ Met |

### Error Rates
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| 4xx Rate | <5% | 2.1% | ✅ Met |
| 5xx Rate | <0.5% | 0.09% | ✅ Met |
| Database Errors | <0.1% | 0.02% | ✅ Met |

## Incident Management

### Incidents by Severity
- **P0 (Critical)**: 0 incidents ✅
- **P1 (High)**: 1 incident ⚠️
- **P2 (Medium)**: 3 incidents
- **P3 (Low)**: 12 incidents

### P1 Incident Details
**Date**: Jan 22, 10:23 AM
**Duration**: 17 minutes
**Root Cause**: Long-running database query (invoice generation) blocked connection pool
**Impact**: 500 errors on API for 17 minutes (~15 users affected)
**Resolution**: Killed blocking query, restarted application, added query timeout
**Prevention**: Added database query timeout (30s), optimized invoice query

### Response Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| MTTA (P0/P1) | <5 min | 4.2 min | ✅ Met |
| MTTR (P0/P1) | <1 hour | 32 min | ✅ Met |
| Escalation Rate | <10% | 7% | ✅ Met |

## Data Protection

### Backup Performance
- **Total Backups**: 744 (31 days × 24 hours)
- **Successful**: 742 (99.73%) ✅
- **Failed**: 2 (0.27%)
- **Average Duration**: 8 minutes
- **S3 Storage Used**: 156 GB

### DR Testing
- **Last Full DR Drill**: Dec 15, 2024
- **Next Scheduled Drill**: Mar 15, 2025
- **Last RTO Test**: Jan 28, 2024 (52 minutes) ✅
- **Last RPO Verification**: Jan 28, 2024 (12 minutes data loss) ✅

## Business Metrics

### User Activity
- **DAU (Avg)**: 523 (Target: 500) ✅ +4.6%
- **Peak DAU**: 687 (Jan 25)
- **Lowest DAU**: 412 (Jan 1 - New Year's Day)

### Deals & Revenue
- **Deals Created**: 1,547 (Avg 50/day) ✅
- **Payment Success Rate**: 96.2% (Target: >95%) ✅
- **Total Revenue**: $465,000 CAD (Avg $15,000/day) ✅

## Recommendations

### Short-Term (This Month)
1. ✅ Add query timeout for all database queries (30s)
2. ✅ Optimize invoice generation query (reduce from 18s to <5s)
3. ⏳ Increase database connection pool size (80 → 100)
4. ⏳ Add caching for frequently accessed invoices

### Medium-Term (Next Quarter)
1. ⏳ Implement database connection pooling (PgBouncer)
2. ⏳ Add read replica for reporting queries
3. ⏳ Migrate to managed Redis (AWS ElastiCache)
4. ⏳ Implement progressive caching strategy

### Long-Term (Next 6 Months)
1. ⏳ Multi-region deployment (US-East + US-West)
2. ⏳ CDN for static assets (CloudFlare or AWS CloudFront)
3. ⏳ Implement rate limiting per user (prevent abuse)
4. ⏳ Auto-scaling based on traffic patterns

## Conclusion

January 2024 was a successful month with all SLA targets met. The single P1 incident (database query timeout) was resolved quickly and preventive measures were implemented. Uptime exceeded target (99.96% vs. 99.9%), and performance metrics were within acceptable ranges.

**Key Achievements**:
- Zero P0 incidents
- 99.96% uptime (exceeded target)
- Fast incident response (4.2 min MTTA)
- 96.2% payment success rate

**Areas for Improvement**:
- Database query optimization (prevent future timeouts)
- Connection pool management (increase capacity)
- Proactive monitoring (detect slow queries before they cause incidents)

**Next Month Focus**:
- Implement database query timeout globally
- Optimize high-impact queries
- Increase monitoring coverage for database performance
```

---

## SLA Violations & Credits

### SLA Violation Definition

An SLA violation occurs when:
1. **Uptime**: Monthly uptime falls below 99.9%
2. **Performance**: Monthly p95 response time exceeds 500ms
3. **Incident Response**: MTTA exceeds 5 minutes for P0/P1
4. **Data Loss**: RPO exceeds 15 minutes (unplanned data loss)

### Service Credit Calculation

**Uptime-Based Credits**:
| Actual Uptime | Downtime | Service Credit |
|--------------|----------|----------------|
| 99.9% - 99.0% | 43.8 - 7.2 hours | 10% monthly fee |
| 99.0% - 95.0% | 7.2 - 36 hours | 25% monthly fee |
| < 95.0% | > 36 hours | 50% monthly fee |

**Example**:
```
Monthly subscription: $1,000
Actual uptime: 99.2% (downtime: 5.8 hours)
Service credit: 10% × $1,000 = $100 credit applied to next invoice
```

### SLA Violation Process

1. **Detection**: Automated monitoring detects SLA violation
2. **Notification**: Email sent to customer within 24 hours
3. **Investigation**: Root cause analysis conducted within 48 hours
4. **Credit Application**: Service credit automatically applied to next invoice
5. **Corrective Action**: Preventive measures implemented to avoid recurrence
6. **Follow-Up**: Post-mortem shared with customer within 7 days

### Credit Request Process

**Eligibility**: Customers can request service credit if SLA violation was not automatically detected

**Process**:
1. **Submit Request**: Email support@nzila-export.com within 30 days of violation
2. **Include Details**: Date, time, duration, impact, supporting evidence
3. **Review**: Support team reviews within 5 business days
4. **Decision**: Approve/deny credit based on SLA definitions
5. **Apply Credit**: Credit applied to next invoice if approved

**Not Eligible for Credit**:
- Scheduled maintenance (announced 48 hours in advance)
- Third-party service outages (Stripe, AWS, etc.)
- User-caused issues (invalid requests, abuse, DDoS)
- Force majeure events (natural disasters, pandemics)
- Beta features or services

---

## SLA Governance

### Review Cycle

**Monthly**: Performance review meeting
- Review uptime, performance, incident metrics
- Identify trends and anomalies
- Adjust alert thresholds if needed
- Plan improvements for next month

**Quarterly**: SLA adjustment review
- Evaluate if targets are too aggressive or too lenient
- Consider adjusting targets based on 3 months of data
- Update SLA document if changes approved
- Communicate changes to customers (30 days notice)

**Annually**: Comprehensive SLA audit
- Review all SLA targets and definitions
- Benchmark against industry standards
- Customer feedback survey on SLA expectations
- Major revisions to SLA document (if needed)

### Stakeholder Approval

**SLA Changes Require Approval From**:
1. VP Engineering (technical feasibility)
2. VP Product (customer expectations)
3. CFO (cost implications)
4. Legal (contractual obligations)

**Notice Period**: 30 days written notice to customers before changes take effect

### Documentation

- **Primary Document**: This SLA_TARGETS.md file
- **Supporting Docs**: Monitoring Guide, Incident Response Playbook, DR Plan
- **Change Log**: Maintained at bottom of this document
- **Version Control**: Git-tracked, reviewed with every change

---

## Appendix

### SLA Calculation Formulas

**Uptime Percentage**:
```
Uptime % = ((Total Minutes - Downtime Minutes) / Total Minutes) × 100
```

**Error Rate**:
```
Error Rate % = (Error Requests / Total Requests) × 100
```

**MTTA (Mean Time To Acknowledge)**:
```
MTTA = Sum(Acknowledgement Time - Alert Time) / Number of Incidents
```

**MTTR (Mean Time To Resolve)**:
```
MTTR = Sum(Resolution Time - Alert Time) / Number of Incidents
```

**Response Time Percentiles**:
```
p50 = 50th percentile of all response times (median)
p95 = 95th percentile of all response times
p99 = 99th percentile of all response times
```

### Industry Benchmarks

**Uptime Targets** (SaaS Industry):
- 99.9% ("three nines"): Standard for most SaaS (43.8 min downtime/month)
- 99.95% ("three nines five"): Premium SaaS ($77K-$300K contracts)
- 99.99% ("four nines"): Enterprise SaaS (>$1M contracts, mission-critical)

**Response Time Targets** (API Performance):
- Excellent: p95 <300ms
- Good: p95 <500ms
- Acceptable: p95 <1000ms
- Poor: p95 >1000ms

**Incident Response Targets**:
- MTTA: Industry average 15-30 minutes, best-in-class <5 minutes
- MTTR: Industry average 4-8 hours, best-in-class <1 hour

**Backup Targets** (Data Protection):
- RTO: Industry standard 4-8 hours, aggressive 1-4 hours
- RPO: Industry standard 1-4 hours, aggressive 15-60 minutes

### References

- **AWS SLA**: https://aws.amazon.com/legal/service-level-agreements/
- **Stripe SLA**: https://stripe.com/legal/sla
- **Google Cloud SLA**: https://cloud.google.com/terms/sla
- **Atlassian SLA**: https://www.atlassian.com/legal/sla
- **SLA Best Practices**: Site Reliability Engineering (Google, O'Reilly, 2016)

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | DevOps Team | Initial SLA document created |

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**Owner**: DevOps Team
**Approved By**: VP Engineering, VP Product, CFO
**Effective Date**: 2024-02-01
**Next Review**: 2024-04-15 (Quarterly)
