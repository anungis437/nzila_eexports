# Disaster Recovery Plan

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Owner:** DevOps Team  
**Review Frequency:** Quarterly  

---

## 🎯 Executive Summary

This Disaster Recovery (DR) Plan outlines the procedures, responsibilities, and recovery targets for the Nzila Export Hub platform in the event of a catastrophic failure. Our DR strategy ensures business continuity with **minimal data loss** and **rapid recovery**.

### Recovery Objectives

| Metric | Target | Definition |
|--------|--------|------------|
| **RTO (Recovery Time Objective)** | **1 hour** | Maximum acceptable downtime |
| **RPO (Recovery Point Objective)** | **15 minutes** | Maximum acceptable data loss |
| **Backup Frequency** | **Hourly** | Database backup every hour |
| **Backup Retention** | **Daily: 7 days<br>Weekly: 4 weeks<br>Monthly: 12 months** | Retention policy |
| **Annual Downtime Budget** | **8.76 hours** | Based on 99.9% uptime SLA |

---

## 📊 Disaster Scenarios & Impact

### Scenario 1: Database Corruption/Failure
**Probability:** Low (2-5% annually)  
**Impact:** CRITICAL - Complete data loss  
**Recovery:** Restore from latest hourly backup  
**RTO:** 45-60 minutes  
**RPO:** <15 minutes (last hourly backup)  

### Scenario 2: Application Server Failure
**Probability:** Medium (10-15% annually)  
**Impact:** HIGH - Service unavailable  
**Recovery:** Redeploy application, no data loss  
**RTO:** 15-30 minutes  
**RPO:** 0 (no data loss)  

### Scenario 3: AWS Region Outage
**Probability:** Very Low (<1% annually)  
**Impact:** CRITICAL - Complete service unavailable  
**Recovery:** Failover to secondary region (if configured)  
**RTO:** 2-4 hours  
**RPO:** <1 hour  

### Scenario 4: Ransomware/Cyber Attack
**Probability:** Low (3-7% annually)  
**Impact:** CRITICAL - Data encrypted/deleted  
**Recovery:** Restore from offsite S3 backup  
**RTO:** 1-2 hours  
**RPO:** <1 hour  

### Scenario 5: Accidental Data Deletion
**Probability:** Medium (15-20% annually)  
**Impact:** MEDIUM - Partial data loss  
**Recovery:** Point-in-time restore from backup  
**RTO:** 30-60 minutes  
**RPO:** <1 hour  

### Scenario 6: Complete Infrastructure Loss
**Probability:** Very Low (<0.5% annually)  
**Impact:** CATASTROPHIC - All systems down  
**Recovery:** Rebuild from infrastructure-as-code + restore data  
**RTO:** 4-8 hours  
**RPO:** <1 hour  

---

## 🔄 Backup Strategy

### Automated Backup System

**Script:** `scripts/backup_database.py`  
**Frequency:** Hourly (via cron job)  
**Storage:** AWS S3 (`s3://nzila-export-backups/`)  
**Encryption:** AES-256 server-side encryption  
**Compression:** gzip (9x compression level)  

### Backup Types & Schedule

```
┌─────────────────────────────────────────────────────┐
│ HOURLY BACKUPS (Daily Type)                        │
│ Schedule: 0 * * * * (every hour)                   │
│ Retention: 7 days (168 backups)                    │
│ Size: ~50-100 MB compressed                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ WEEKLY BACKUPS                                      │
│ Schedule: 0 2 * * 0 (Sunday 2 AM)                  │
│ Retention: 4 weeks (4 backups)                     │
│ Size: ~50-100 MB compressed                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ MONTHLY BACKUPS                                     │
│ Schedule: 0 3 1 * * (1st of month, 3 AM)          │
│ Retention: 12 months (12 backups)                  │
│ Size: ~50-100 MB compressed                        │
└─────────────────────────────────────────────────────┘
```

### Backup Verification

**Automated Checks:**
- ✅ Checksum validation (SHA-256)
- ✅ File size validation (>10 MB expected)
- ✅ S3 upload confirmation
- ✅ Backup metadata stored

**Monthly Manual Tests:**
- Test restore to staging environment
- Verify data integrity
- Document restore time
- Update runbook if needed

---

## 🛠️ Recovery Procedures

### Prerequisites

**Required Access:**
- AWS Console access (S3, EC2, RDS)
- Database credentials (PostgreSQL)
- SSH access to application servers
- PagerDuty on-call access

**Required Tools:**
- AWS CLI (`aws`)
- PostgreSQL client (`psql`, `pg_restore`)
- Python 3.13+ with Django
- `scripts/restore_database.py`

---

### Procedure 1: Database Restore (Most Common)

**When to Use:**
- Database corruption detected
- Data deletion/modification error
- Ransomware attack on database
- Migration rollback needed

**Steps:**

```bash
# 1. List available backups
python scripts/restore_database.py --list

# Output:
# ================================================================================
# Available Backups in s3://nzila-export-backups/
# ================================================================================
# Filename                                           Size        Date
# --------------------------------------------------------------------------------
# nzila_db_daily_20241220_140000.sql.gz             85.23 MB    2024-12-20 14:00:00
# nzila_db_daily_20241220_130000.sql.gz             84.98 MB    2024-12-20 13:00:00
# ...

# 2. Choose backup (latest or specific)
python scripts/restore_database.py --latest

# OR restore specific backup
python scripts/restore_database.py --backup nzila_db_daily_20241220_130000.sql.gz

# 3. Confirm restore (prompted)
# Type 'RESTORE' to continue: RESTORE

# 4. Monitor restore progress
# [2024-12-20 14:15:00] - INFO - Downloading backup from S3...
# [2024-12-20 14:16:00] - INFO - Download complete: 85.23 MB
# [2024-12-20 14:16:05] - INFO - Validating backup file integrity
# [2024-12-20 14:16:10] - INFO - ✅ Checksum validation passed
# [2024-12-20 14:16:15] - INFO - Starting database restore...
# [2024-12-20 14:17:00] - INFO - ✅ Database restore completed successfully
# [2024-12-20 14:17:05] - INFO - Verifying database restoration...
# [2024-12-20 14:17:10] - INFO - ✅ Tables found: 87
# [2024-12-20 14:17:15] - INFO - ✅ accounts_customuser: 245 rows
# [2024-12-20 14:17:20] - INFO - ✅ vehicles_vehicle: 1,234 rows
# [2024-12-20 14:17:25] - INFO - ✅ deals_deal: 567 rows
# [2024-12-20 14:17:30] - INFO - ✅ Database verification completed

# 5. Restart application services
sudo systemctl restart nzila-backend
sudo systemctl restart nzila-celery
sudo systemctl restart nzila-celerybeat

# 6. Verify application functionality
curl https://api.nzila-export.com/health/
# Expected: {"status": "healthy"}

# 7. Clear Redis cache
redis-cli FLUSHALL

# 8. Notify stakeholders
# - Email users about brief downtime
# - Post status update
# - Document incident
```

**Expected Duration:** 45-60 minutes  
**Estimated Downtime:** 30-45 minutes (during restore + restart)  

---

### Procedure 2: Application Server Failure

**When to Use:**
- EC2 instance failure
- Application crash/unresponsive
- Docker container issues
- Deployment failure

**Steps:**

```bash
# 1. Assess the situation
ssh user@server.nzila-export.com

# Check service status
sudo systemctl status nzila-backend
sudo systemctl status nzila-celery
sudo systemctl status nginx

# Check logs
sudo journalctl -u nzila-backend -n 100 --no-pager
tail -f /var/log/nzila/error.log

# 2. Attempt service restart
sudo systemctl restart nzila-backend
sudo systemctl restart nzila-celery
sudo systemctl restart nginx

# 3. If restart fails, redeploy application
cd /opt/nzila_eexports
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart nzila-backend

# 4. If server is completely unresponsive, launch new instance
# (Use AWS Console or Terraform)
terraform apply -target=aws_instance.app_server

# 5. Update DNS if needed
# Point domain to new server IP

# 6. Verify recovery
curl https://nzila-export.com/api/health/

# 7. Monitor for 30 minutes
# Check error rates, response times, user reports
```

**Expected Duration:** 15-30 minutes  
**Estimated Downtime:** 10-20 minutes  

---

### Procedure 3: AWS Region Outage

**When to Use:**
- AWS region completely unavailable
- Multi-AZ failure
- Extended AWS service disruption (>2 hours)

**Steps:**

```bash
# 1. Verify outage scope
# Check AWS Status: https://status.aws.amazon.com/
# Confirm it's region-wide, not just our account

# 2. Activate DR site (if configured)
# Switch DNS to secondary region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://failover-config.json

# 3. Restore database to secondary region
# Download latest backup from S3
aws s3 cp s3://nzila-export-backups/database/daily/latest.sql.gz . \
  --region us-west-2

# Restore to secondary RDS instance
python scripts/restore_database.py --backup latest.sql.gz

# 4. Update application configuration
# Point to secondary database, Redis, etc.

# 5. Deploy application to secondary region
# (Use pre-configured infrastructure)

# 6. Notify users
# - Email notification of temporary URL
# - Social media updates
# - Status page update

# 7. Monitor secondary region
# Watch for any issues in new region

# 8. Post-incident: Failback when primary region restored
# Replicate data back to primary
# Switch DNS back
# Verify everything works
```

**Expected Duration:** 2-4 hours  
**Estimated Downtime:** 1-3 hours (until secondary active)  

**Note:** Multi-region DR requires pre-configured infrastructure (not in current setup). This is a Phase 4 enhancement.

---

### Procedure 4: Ransomware/Cyber Attack

**When to Use:**
- Database encrypted by ransomware
- Unauthorized data deletion
- Malicious code injection
- Compromised credentials used

**Steps:**

```bash
# 1. IMMEDIATELY isolate systems
# Disconnect from internet, disable access

# 2. Notify security team
# Email: security@nzila-export.com
# PagerDuty: Trigger "Security Incident" alert

# 3. Preserve evidence
# Take snapshots of affected systems
# Capture logs before restoration
aws ec2 create-snapshot --volume-id vol-xxx --description "Ransomware incident"

# 4. Reset all credentials
# Database passwords
# API keys
# AWS access keys
# User passwords (force password reset)

# 5. Restore from clean backup
# Use backup BEFORE the attack (not latest)
python scripts/restore_database.py --list
# Choose backup from before attack time
python scripts/restore_database.py --backup nzila_db_daily_20241219_080000.sql.gz

# 6. Scan systems for malware
# Run security scans on all servers
sudo clamscan -r /opt/nzila_eexports/

# 7. Rebuild compromised servers
# Don't reuse infected instances
# Launch new instances from clean AMIs

# 8. Implement additional security
# Update firewall rules
# Enable MFA for all admin accounts
# Review access logs

# 9. Notify affected users
# Email disclosure (if PII compromised)
# Offer credit monitoring if needed

# 10. Post-incident review
# Document attack vector
# Implement preventive measures
# Update security policies
```

**Expected Duration:** 4-8 hours (full recovery)  
**Estimated Downtime:** 2-4 hours  

---

## 📋 Recovery Checklist

Use this checklist during any disaster recovery event:

### Pre-Recovery (5-10 minutes)

- [ ] **Assess the situation**
  - What failed? (database, server, network, etc.)
  - When did it fail? (check monitoring alerts)
  - What is the impact? (affected users, data loss)
  
- [ ] **Notify stakeholders**
  - [ ] Trigger PagerDuty alert
  - [ ] Post status page update (status.nzila-export.com)
  - [ ] Email notification to operations team
  - [ ] Slack alert in #incidents channel
  
- [ ] **Determine recovery strategy**
  - Which procedure to follow?
  - Estimated recovery time?
  - Need to notify users?

### During Recovery (30-60 minutes)

- [ ] **Execute recovery procedure**
  - [ ] Follow documented steps
  - [ ] Document actions taken
  - [ ] Screenshot evidence
  - [ ] Note start time
  
- [ ] **Monitor progress**
  - [ ] Check logs for errors
  - [ ] Verify each step completes
  - [ ] Update status page every 15 minutes
  
- [ ] **Test restored system**
  - [ ] Database connectivity
  - [ ] Application health check
  - [ ] Critical user flows (login, payment, etc.)
  - [ ] API endpoints responding

### Post-Recovery (15-30 minutes)

- [ ] **Verify full functionality**
  - [ ] Run smoke tests
  - [ ] Check monitoring dashboards
  - [ ] Confirm no data loss (or document loss)
  - [ ] Monitor error rates for 30 minutes
  
- [ ] **Notify stakeholders of resolution**
  - [ ] Update status page (resolved)
  - [ ] Email notification to users
  - [ ] PagerDuty incident resolved
  - [ ] Slack update
  
- [ ] **Document the incident**
  - [ ] Create incident report
  - [ ] Timeline of events
  - [ ] Root cause analysis
  - [ ] Lessons learned
  - [ ] Action items for prevention

### Post-Mortem (24-48 hours later)

- [ ] **Conduct post-mortem meeting**
  - What happened?
  - Why did it happen?
  - What went well?
  - What could be improved?
  
- [ ] **Update documentation**
  - [ ] Update this DR plan if needed
  - [ ] Update runbooks
  - [ ] Update monitoring alerts
  
- [ ] **Implement improvements**
  - [ ] Add missing monitoring
  - [ ] Automate manual steps
  - [ ] Fix root cause
  - [ ] Test improvements

---

## 🔐 Access & Credentials

### Required Credentials (Secure Storage: 1Password/Vault)

| System | Credential | Location | Notes |
|--------|-----------|----------|-------|
| **AWS Console** | Root account | 1Password | MFA required |
| **AWS CLI** | Access Key ID | .env / AWS credentials | Rotate every 90 days |
| **PostgreSQL** | Master password | 1Password | Encrypted |
| **S3 Backup Bucket** | Bucket access | AWS IAM | Read/write permissions |
| **Redis** | Password | .env | Used for cache |
| **Sentry** | API key | .env | Error monitoring |
| **PagerDuty** | API key | .env | Alerting |
| **Grafana** | Admin password | 1Password | Dashboards |

### Emergency Contacts

| Role | Name | Phone | Email | Backup |
|------|------|-------|-------|--------|
| **On-Call Engineer** | Primary | +1-XXX-XXX-XXXX | oncall@nzila-export.com | Secondary engineer |
| **DevOps Lead** | TBD | +1-XXX-XXX-XXXX | devops@nzila-export.com | CTO |
| **CTO** | TBD | +1-XXX-XXX-XXXX | cto@nzila-export.com | CEO |
| **AWS Support** | N/A | N/A | Via AWS Console | Enterprise support |
| **Database Admin** | TBD | +1-XXX-XXX-XXXX | dba@nzila-export.com | DevOps Lead |

**PagerDuty Escalation:**
1. On-call engineer (immediate)
2. DevOps Lead (after 15 minutes)
3. CTO (after 30 minutes)

---

## 🧪 Testing & Drills

### Quarterly DR Drill Schedule

**Q1 (January):** Database restore test  
**Q2 (April):** Application server failover  
**Q3 (July):** Full disaster simulation  
**Q4 (October):** Security incident response  

### Testing Checklist

**Before Each Test:**
- [ ] Schedule test during low-traffic period
- [ ] Notify team of upcoming test
- [ ] Prepare staging environment
- [ ] Document current state

**During Test:**
- [ ] Time each step
- [ ] Document issues encountered
- [ ] Screenshot key steps
- [ ] Test communication channels

**After Test:**
- [ ] Compare actual vs. target RTO/RPO
- [ ] Update procedures if needed
- [ ] Document lessons learned
- [ ] Share results with team

### Metrics to Track

| Metric | Target | Last Test | Status |
|--------|--------|-----------|--------|
| Database restore time | <60 min | TBD | ⏳ Not tested |
| Application restart time | <15 min | TBD | ⏳ Not tested |
| Backup file size | <100 MB | TBD | ⏳ Not tested |
| Restore success rate | 100% | TBD | ⏳ Not tested |
| Data loss (RPO) | <15 min | TBD | ⏳ Not tested |

---

## 📈 Continuous Improvement

### Monthly Review

- [ ] Review backup success rate (target: 100%)
- [ ] Check backup storage costs
- [ ] Verify backup retention compliance
- [ ] Test random restore (monthly)

### Quarterly Review

- [ ] Conduct DR drill
- [ ] Update emergency contacts
- [ ] Review and update procedures
- [ ] Rotate AWS credentials

### Annual Review

- [ ] Full DR plan audit
- [ ] Update RTO/RPO targets
- [ ] Evaluate multi-region DR (Phase 4)
- [ ] Security assessment

---

## 📞 Incident Response Workflow

```
┌─────────────────────────────────────────────────────┐
│ INCIDENT DETECTED                                   │
│ (Monitoring alert, user report, manual discovery)  │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STEP 1: ASSESS (5 min)                             │
│ - What failed?                                      │
│ - Impact scope?                                     │
│ - Data loss risk?                                   │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STEP 2: NOTIFY (2 min)                             │
│ - Trigger PagerDuty                                 │
│ - Update status page                                │
│ - Notify team                                       │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STEP 3: CONTAIN (10 min)                           │
│ - Stop the damage                                   │
│ - Isolate affected systems                          │
│ - Preserve evidence                                 │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STEP 4: RECOVER (30-60 min)                        │
│ - Follow DR procedure                               │
│ - Restore from backup                               │
│ - Verify functionality                              │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STEP 5: COMMUNICATE (5 min)                        │
│ - Notify users of resolution                        │
│ - Update status page                                │
│ - Close PagerDuty incident                          │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STEP 6: POST-MORTEM (24-48 hours)                  │
│ - Document incident                                 │
│ - Root cause analysis                               │
│ - Implement improvements                            │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Approval & Maintenance

**Document Status:** ✅ APPROVED  
**Approved By:** Development Team  
**Approval Date:** December 20, 2025  
**Next Review:** March 20, 2026 (Quarterly)  

**Change Log:**
| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-12-20 | 1.0 | Initial DR plan creation | DevOps Team |

---

## 📚 Related Documents

- [Incident Response Playbook](INCIDENT_RESPONSE_PLAYBOOK.md)
- [Backup Script Documentation](../scripts/backup_database.py)
- [Restore Script Documentation](../scripts/restore_database.py)
- [Monitoring Guide](MONITORING_GUIDE.md)
- [SLA Targets](SLA_TARGETS.md)
- [Security Audit Report](security/WORLD_CLASS_AUDIT.md)

---

**For questions or updates to this plan, contact:** devops@nzila-export.com
