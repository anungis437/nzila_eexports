# Privacy & Compliance Documentation

This directory contains comprehensive privacy and compliance documentation for Nzila Exports.

## 📋 Available Documentation

### [PIPEDA & Law 25 Compliance Guide](./PIPEDA_LAW25_COMPLIANCE.md)
Complete implementation guide for Canadian privacy laws:
- **PIPEDA (Federal)**: Personal Information Protection and Electronic Documents Act
- **Law 25 (Quebec)**: Bill 64 - Modernization of privacy laws

**Key Features:**
- ✅ Explicit consent tracking (4 consent types)
- ✅ 72-hour breach notification (Law 25 requirement)
- ✅ Data subject rights (access, correction, deletion)
- ✅ Cross-border transfer consent (Canada → Africa)
- ✅ Data retention policies (category-specific)
- ✅ Privacy Impact Assessments (PIAs)

**Sections:**
1. Regulatory Framework (PIPEDA 10 Principles, Law 25 Articles)
2. Implementation Overview (Database schema, models)
3. User Consent Management (Workflows, API examples)
4. Data Breach Protocols (72-hour notification process)
5. Data Retention Policies (12 data categories, schedules)
6. Privacy Impact Assessments (PIA requirements, workflow)
7. API Endpoints (Complete reference)
8. Admin Management (Django admin features)
9. Audit & Reporting (SQL queries, compliance reports)
10. Legal References (OPC, CAI contact information)

---

## 🚀 Quick Start

### For Developers

**1. View Privacy Settings:**
```bash
GET /api/accounts/privacy/settings/
Authorization: Bearer <jwt_token>
```

**2. Update Consent:**
```bash
POST /api/accounts/privacy/settings/update/
{
  "marketing_consent": false,
  "data_transfer_consent_africa": true
}
```

**3. Export User Data:**
```bash
GET /api/accounts/privacy/export/
```

### For Administrators

**1. Access Compliance Admin:**
- Visit: `/admin/accounts/databreachlog/` - Data breach management
- Visit: `/admin/accounts/consenthistory/` - Consent audit trail (read-only)
- Visit: `/admin/accounts/dataretentionpolicy/` - Retention policies
- Visit: `/admin/accounts/privacyimpactassessment/` - PIAs

**2. Report Data Breach:**
```bash
POST /api/accounts/privacy/breach/report/
{
  "breach_date": "2024-01-18T08:00:00Z",
  "severity": "high",
  "affected_users_count": 250,
  "data_types_compromised": ["email", "phone"]
}
```

**3. Review Consent Status:**
- Django Admin → Users → List view shows consent status (✓ Full / ⚠ Partial / ✗ No Consent)

---

## 📊 Compliance Models

### User Model Extensions
- `data_processing_consent` - PIPEDA Principle 3
- `marketing_consent` - Law 25 Article 8
- `third_party_sharing_consent` - Broker data sharing
- `data_transfer_consent_africa` - Cross-border transfers (CRITICAL)
- `consent_date`, `consent_ip_address`, `consent_version` - Audit metadata

### DataBreachLog
Tracks data breaches with 72-hour notification compliance:
- Severity levels (low/medium/high/critical)
- Affected users tracking (Many-to-Many)
- Notification dates (users, CAI, OPC)
- Mitigation steps documentation
- `is_within_72_hours()` compliance checker

### ConsentHistory
Immutable audit trail of consent changes:
- 6 consent types (data_processing, marketing, third_party_sharing, cross_border_africa, cookies, analytics)
- 4 actions (granted, withdrawn, modified, renewed)
- IP address, user agent, exact consent text
- **Read-only** - never delete

### DataRetentionPolicy
Category-specific data retention periods:
- 12 data categories (financial, transactions, session_logs, etc.)
- Legal basis documentation (CRA, Tax Act)
- Auto-deletion capability
- `retention_years()` helper method

### PrivacyImpactAssessment
PIA tracking for high-risk systems:
- Risk levels (low/medium/high/very_high)
- Cross-border transfer flag
- Approval workflow (draft → under_review → approved)
- Annual review tracking

---

## 🔐 Critical Compliance Requirements

### 1. Cross-Border Data Transfers (PIPEDA Principle 4.1.3)
**Context:** Nzila Exports transfers Canadian dealer personal information to African brokers (Côte d'Ivoire, Senegal, Ghana, Kenya).

**Requirement:** Explicit consent required because:
- African countries lack GDPR-equivalent laws
- Personal data leaves Canadian jurisdiction
- Dealers must be informed of reduced protections

**Implementation:**
- `data_transfer_consent_africa` field on User model
- Consent text explains specific countries (Côte d'Ivoire, Senegal, etc.)
- ConsentHistory tracks when consent granted/withdrawn
- Broker matching disabled if consent withdrawn

### 2. 72-Hour Breach Notification (Law 25 Article 3.5)
**Requirement:** 
- Notify affected users within 72 hours of discovery
- Notify CAI (Commission d'accès à l'information du Québec) within 72 hours
- Notify OPC (Office of the Privacy Commissioner) for federal breaches

**Implementation:**
- `DataBreachLog` model with automatic compliance checking
- `is_within_72_hours()` method shows ✓ Within 72h / ✗ Overdue
- Admin interface tracks notification dates
- Email templates for user notification

### 3. Data Retention Limits (Law 25 Article 11)
**Requirement:** 
- Retain data only as long as necessary
- Document legal basis for retention
- Delete or anonymize when no longer needed

**Implementation:**
- Financial records: 7 years (CRA requirement)
- Session logs: 90 days (security monitoring)
- Analytics: 2 years (business intelligence)
- Auto-deletion Celery task (nightly)

---

## 📞 Contact Privacy Authorities

### Office of the Privacy Commissioner of Canada (OPC)
- **Email:** privacy@priv.gc.ca
- **Phone:** 1-800-282-1376
- **Website:** https://www.priv.gc.ca/
- **Use for:** Federal breaches, PIPEDA complaints

### Commission d'accès à l'information du Québec (CAI)
- **Email:** caiquebec@cai.gouv.qc.ca
- **Phone:** 1-888-528-7741
- **Website:** https://www.cai.gouv.qc.ca/
- **Use for:** Quebec breaches (Law 25), provincial complaints

---

## ✅ Implementation Checklist

### Phase 1: Database & Models ✅
- [x] User model consent fields (13 fields)
- [x] DataBreachLog model
- [x] ConsentHistory model
- [x] DataRetentionPolicy model
- [x] PrivacyImpactAssessment model
- [x] Migration applied

### Phase 2: API Endpoints ✅
- [x] Privacy settings (GET/POST)
- [x] Consent management (grant/history)
- [x] Data breach reporting (admin)
- [x] Data retention info
- [x] Data export/deletion

### Phase 3: Admin Interface ✅
- [x] DataBreachLog admin (compliance status)
- [x] ConsentHistory admin (read-only)
- [x] DataRetentionPolicy admin
- [x] PrivacyImpactAssessment admin
- [x] User admin consent status

### Phase 4: Initial Data ✅
- [x] 4 data retention policies created
- [x] Financial (7 years)
- [x] Transactions (7 years)
- [x] Session logs (90 days)
- [x] Analytics (2 years)

### Phase 5: Documentation ✅
- [x] PIPEDA_LAW25_COMPLIANCE.md (comprehensive guide)
- [x] README.md (this file)

### Phase 6: Frontend Integration 🔄
- [ ] Consent form on registration
- [ ] Privacy settings dashboard
- [ ] Consent history page
- [ ] Data export button
- [ ] Data deletion request button

### Phase 7: Automated Processes 🔄
- [ ] Celery task for data retention cleanup
- [ ] Breach notification email templates
- [ ] PIA review reminders
- [ ] Consent withdrawal workflow

---

## 📖 Additional Resources

### Internal Documentation
- [API Documentation](../api/) - REST API reference
- [Deployment Guide](../deployment/) - Production deployment
- [Security Guide](../security/) - Security best practices

### External Resources
- [PIPEDA Full Text](https://laws-lois.justice.gc.ca/eng/acts/P-8.6/)
- [Law 25 (Bill 64)](http://legisquebec.gouv.qc.ca/)
- [OPC Guidance](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/)
- [CAI Law 25 Resources](https://www.cai.gouv.qc.ca/loi-25/)

---

## 🆘 Support

**Privacy Officer:** [privacy@nzilaexports.com](mailto:privacy@nzilaexports.com)  
**Technical Support:** [support@nzilaexports.com](mailto:support@nzilaexports.com)  
**Security Issues:** [security@nzilaexports.com](mailto:security@nzilaexports.com)

---

**Last Updated:** January 20, 2024  
**Version:** 1.0  
**Review Date:** January 20, 2025
