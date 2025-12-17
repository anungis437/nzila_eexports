# PIPEDA & Law 25 Quick Reference

## 🎯 TL;DR - What You Need to Know

Nzila Exports is now **fully compliant** with Canadian privacy laws (PIPEDA + Law 25) for:
- ✅ Explicit consent tracking (4 types)
- ✅ 72-hour breach notification (Law 25)
- ✅ Data subject rights (access, correction, deletion)
- ✅ Cross-border data transfers (Canada → Africa)
- ✅ Data retention limits (7 years financial, 90 days session logs)

---

## 🚨 Critical Scenarios

### Scenario 1: Data Breach Discovered

**Timeline:** Law 25 requires **72-hour notification**

**Steps:**
1. **Log breach immediately** via Django Admin → Data Breach Logs → Add
   - Or API: `POST /api/accounts/privacy/breach/report/`
2. **Notify affected users** within 72 hours (email template available)
3. **Notify CAI (Quebec)** within 72 hours: caiquebec@cai.gouv.qc.ca
4. **Notify OPC (Federal)** within 72 hours: privacy@priv.gc.ca
5. **Document mitigation** in DataBreachLog admin

**Admin Interface:**
- Shows **✓ Within 72h** / **✗ Overdue** status
- Tracks notification dates automatically

### Scenario 2: User Wants to Withdraw Consent

**User Action:** Visits Privacy Settings → Unchecks "Share data with brokers"

**System Behavior:**
1. **ConsentHistory** record created automatically (immutable audit trail)
2. User's `third_party_sharing_consent` = `False`
3. **Broker matching disabled** - no new matches sent
4. Existing deals continue (legitimate interest)
5. User can re-grant consent anytime

**API Endpoint:** `POST /api/accounts/privacy/settings/update/`

### Scenario 3: Dealer Without Africa Transfer Consent

**Issue:** Dealer has `data_transfer_consent_africa = False`

**Impact:**
- ❌ Cannot match with African brokers
- ❌ Broker recommendation algorithm excludes this dealer
- ❌ Cross-border features disabled

**Solution:**
- Show consent prompt: "To access African broker network, we need your consent to transfer your information to Côte d'Ivoire, Senegal, Ghana..."
- API: `POST /api/accounts/privacy/consent/grant/`

### Scenario 4: User Requests Data Export

**User Action:** Clicks "Download My Data"

**System Response:**
1. Calls `GET /api/accounts/privacy/export/`
2. Returns JSON file with:
   - User profile
   - All deals
   - All commissions
   - Vehicle listings
   - Consent history
   - Audit log
3. **Law 25 Article 8.5** - Right to data portability

**Timeline:** Immediate (real-time export)

### Scenario 5: User Requests Account Deletion

**User Action:** Clicks "Delete My Account"

**System Behavior:**
1. Calls `POST /api/accounts/privacy/delete/`
2. **Soft delete** (account marked inactive)
3. Personal data anonymized immediately:
   - Name → `Deleted User <id>`
   - Email → `deleted_<id>@example.com`
   - Phone/Address → Removed
4. **Financial records retained** 7 years (CRA requirement)
5. After 7 years → Permanent deletion

**Timeline:** Immediate anonymization, permanent deletion after 7 years

---

## 📋 Consent Types Explained

| Consent Type | Required For | Can Withdraw? | Impact if Withdrawn |
|--------------|--------------|---------------|---------------------|
| **Data Processing** | Basic account operations | ⚠️ Account closure | Cannot use platform |
| **Marketing** | Newsletters, promotions | ✅ Anytime | Still can use platform |
| **Third-Party Sharing** | Sharing with brokers/partners | ✅ Anytime | Broker features disabled |
| **Cross-Border Africa** | Transferring to African brokers | ✅ Anytime | African broker matching disabled |

### Example Consent Text

**Cross-Border Africa Consent:**
> "I consent to Nzila Exports transferring my personal information (name, email, company name, contact details, vehicle data) to brokers in African countries including Côte d'Ivoire, Senegal, Ghana, and Kenya. I understand these countries may not have equivalent data protection laws to Canada."

---

## 🔐 Admin Quick Actions

### View Consent Status
1. Django Admin → Users
2. See **Consent Status** column:
   - ✓ **Full Consent** (green) - All consents granted
   - ⚠️ **Partial** (orange) - Some consents missing
   - ✗ **No Consent** (red) - No consents granted

### Report Data Breach
1. Django Admin → Data Breach Logs → Add
2. Fill in:
   - **Breach Date** (when it happened)
   - **Severity** (low/medium/high/critical)
   - **Affected Users Count**
   - **Data Types** (email, phone, financial, etc.)
   - **Description** (what happened)
3. System calculates **72-hour deadline** automatically
4. Update notification dates as you notify users/authorities

### View Consent History (Audit Trail)
1. Django Admin → Consent History
2. Filter by user, consent type, date
3. **Read-only** - never delete (immutable audit trail)
4. Shows IP address, exact consent text, policy version

### Configure Data Retention
1. Django Admin → Data Retention Policies
2. Each data category has one policy
3. Examples:
   - **Financial:** 2555 days (7 years) - CRA requirement
   - **Session Logs:** 90 days - Auto-delete enabled
4. Auto-delete runs nightly via Celery

---

## 📞 Contact Information

### Internal
- **Privacy Officer:** privacy@nzilaexports.com
- **Technical Support:** support@nzilaexports.com
- **Security Issues:** security@nzilaexports.com

### External Authorities
- **OPC (Federal):** privacy@priv.gc.ca | 1-800-282-1376
- **CAI (Quebec):** caiquebec@cai.gouv.qc.ca | 1-888-528-7741

---

## 🛠️ API Endpoints Quick Reference

### Privacy Settings
```bash
# View current settings
GET /api/accounts/privacy/settings/
Authorization: Bearer <token>

# Update consent preferences
POST /api/accounts/privacy/settings/update/
{
  "marketing_consent": false,
  "data_transfer_consent_africa": true
}
```

### Consent Management
```bash
# Grant initial consent (registration)
POST /api/accounts/privacy/consent/grant/
{
  "data_processing_consent": true,
  "marketing_consent": false,
  "third_party_sharing_consent": true,
  "data_transfer_consent_africa": true,
  "privacy_policy_version": "1.0"
}

# View consent history
GET /api/accounts/privacy/consent/history/
```

### Data Subject Rights
```bash
# Export all personal data
GET /api/accounts/privacy/export/

# Request account deletion
POST /api/accounts/privacy/delete/

# View retention policies
GET /api/accounts/privacy/retention/
```

### Admin Only
```bash
# Report data breach
POST /api/accounts/privacy/breach/report/
{
  "breach_date": "2024-01-18T08:00:00Z",
  "severity": "high",
  "affected_users_count": 250,
  "data_types_compromised": ["email", "phone"]
}
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T: Delete ConsentHistory records
**Why:** Immutable audit trail required by PIPEDA Principle 8 (Accountability)
**What to do:** ConsentHistory is read-only - never delete

### ❌ DON'T: Share dealer data with African brokers without consent
**Why:** PIPEDA Principle 4.1.3 requires explicit consent for cross-border transfers
**What to do:** Check `user.data_transfer_consent_africa` before sharing

### ❌ DON'T: Miss 72-hour breach notification deadline
**Why:** Law 25 Article 3.5 - can result in fines up to $25M
**What to do:** Log breach immediately, system tracks deadline automatically

### ❌ DON'T: Keep data forever
**Why:** Law 25 Article 11 - data minimization required
**What to do:** Use DataRetentionPolicy - financial 7 years, session logs 90 days

### ❌ DON'T: Skip Privacy Impact Assessments for high-risk systems
**Why:** Law 25 Article 3.3 - mandatory for cross-border transfers
**What to do:** Create PIA in Django Admin before launching new features

---

## ✅ Best Practices

### ✅ DO: Check consent before matching dealers with brokers
```python
if dealer.data_transfer_consent_africa and dealer.third_party_sharing_consent:
    # Safe to share with African brokers
    match_with_broker(dealer, african_broker)
else:
    # Show consent prompt
    return "Need consent for cross-border transfer"
```

### ✅ DO: Log all data processing activities
```python
from nzila_export.models import AuditLog

AuditLog.objects.create(
    user=request.user,
    action='export',
    model_name='UserData',
    object_id=str(user.id),
    ip_address=request.META.get('REMOTE_ADDR')
)
```

### ✅ DO: Provide clear consent text
**Good:** "I consent to Nzila Exports transferring my information to brokers in Côte d'Ivoire, Senegal, Ghana..."
**Bad:** "I agree to Terms of Service" (not specific enough)

### ✅ DO: Review PIAs annually
- Django Admin → Privacy Impact Assessments
- Check `review_due_date` field
- Update if system changes

### ✅ DO: Test data export/deletion regularly
```bash
# Test data export
curl -H "Authorization: Bearer <token>" \
  https://api.nzilaexports.com/api/accounts/privacy/export/

# Verify all data included (user, deals, commissions, etc.)
```

---

## 📊 Compliance Dashboard (Coming Soon)

Future frontend features:
- [ ] User consent dashboard (view/update all consents)
- [ ] Consent history timeline (visual audit trail)
- [ ] Data retention calendar (when data will be deleted)
- [ ] Privacy policy version tracker
- [ ] One-click data export button
- [ ] Account deletion wizard

---

## 📚 Full Documentation

**Comprehensive Guide:** [PIPEDA_LAW25_COMPLIANCE.md](./PIPEDA_LAW25_COMPLIANCE.md)

Covers:
- PIPEDA 10 Fair Information Principles
- Law 25 key articles
- Implementation details
- API reference
- Admin procedures
- Legal references
- SQL queries for compliance reports

---

**Version:** 1.0  
**Last Updated:** January 20, 2024  
**For:** All developers, admins, privacy officers
