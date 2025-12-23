# P2 Features Quick Reference Guide

## 🔒 Shipment Security (ISO 28000)

### SecurityRisk Model
Track and mitigate supply chain security risks.

**Fields**:
- `risk_id`: Unique identifier (e.g., "RISK-2024-001")
- `category`: theft, smuggling, terrorism, fraud, customs, cyber, personnel, facility
- `risk_level`: low, medium, high, critical
- `likelihood`: 1-5 (rare to certain)
- `impact`: 1-5 (negligible to catastrophic)
- `status`: open, mitigating, mitigated, accepted, closed
- `mitigation_strategy`: Plan to reduce risk
- `target_resolution_date`: When to resolve by

**Computed Properties**:
- `risk_score`: likelihood × impact (1-25)
- `is_overdue`: Past target resolution date

**API Endpoints**:
- `GET /api/shipments/security/risks/` - List all
- `GET /api/shipments/security/risks/high_priority/` - High/critical + open
- `GET /api/shipments/security/risks/overdue/` - Past target date
- `POST /api/shipments/security/risks/{id}/mitigate/` - Mark mitigated
- `POST /api/shipments/security/risks/{id}/accept/` - Accept risk
- `GET /api/shipments/security/risks/export_csv/` - Download report

### SecurityIncident Model
Log and track actual security events.

**Fields**:
- `incident_id`: Unique identifier (e.g., "INC-2024-001")
- `incident_type`: theft, damage, tampering, unauthorized_access, hijacking, fraud, cyber_attack, personnel, natural_disaster, other
- `severity`: low, medium, high, critical
- `occurred_at`: When incident happened
- `location`: Where it happened
- `status`: reported, investigating, contained, resolved, escalated
- `financial_loss`: CAD amount
- `authorities_notified`: Boolean
- `insurance_claimed`: Boolean
- `root_cause`: Analysis
- `corrective_actions`: Prevention measures

**API Endpoints**:
- `GET /api/shipments/security/incidents/` - List all
- `GET /api/shipments/security/incidents/critical/` - High/critical + active
- `GET /api/shipments/security/incidents/recent/` - Last 30 days
- `GET /api/shipments/security/incidents/statistics/` - Summary stats
- `POST /api/shipments/security/incidents/{id}/escalate/` - Escalate
- `POST /api/shipments/security/incidents/{id}/resolve/` - Mark resolved
- `GET /api/shipments/security/incidents/export_csv/` - Download log

### PortVerification Model
Track port security certifications.

**Fields**:
- `port_name`: Human-readable name
- `port_code`: UN/LOCODE (e.g., "CAVAN" for Vancouver)
- `certification_type`: isps, c-tpat, aeo, iso_28000, customs, other
- `certification_number`: Cert ID
- `certifying_authority`: Who issued cert
- `issue_date`: When issued
- `expiry_date`: When expires
- `status`: active, expired, pending_renewal, revoked
- `security_level`: 1-3 (ISPS: 1=normal, 2=heightened, 3=exceptional)

**Computed Properties**:
- `is_expired`: Past expiry date
- `days_until_expiry`: Days remaining

**API Endpoints**:
- `GET /api/shipments/security/port-verifications/` - List all
- `GET /api/shipments/security/port-verifications/expiring_soon/` - Within 90 days
- `GET /api/shipments/security/port-verifications/expired/` - Past expiry
- `GET /api/shipments/security/port-verifications/by_port/?port_code=CAVAN` - By port
- `GET /api/shipments/security/port-verifications/summary/` - Statistics
- `POST /api/shipments/security/port-verifications/{id}/renew/` - Renew cert
- `GET /api/shipments/security/port-verifications/export_csv/` - Download report

---

## 📧 Email Service

### EmailService Class (`utils/email_service.py`)

All methods use HTML templates with company branding.

#### send_invoice_reminder(invoice, recipient_email)
Payment reminder for overdue/upcoming invoices.

**Template**: `email_templates/invoice_reminder.html`
**Includes**:
- Invoice number and amount
- Due date
- Payment instructions (wire, credit card, e-Transfer)
- "View Invoice" button

**Usage**:
```python
from utils.email_service import EmailService
from payments.models import Invoice

invoice = Invoice.objects.get(id=123)
EmailService.send_invoice_reminder(invoice, 'buyer@example.com')
```

#### send_breach_notification(breach, recipient_email)
PIPEDA/Law 25 data breach notification.

**Template**: `email_templates/breach_notification.html`
**Includes**:
- Severity and discovery date
- Data types compromised
- Steps company is taking
- User action checklist
- Privacy office contact

**Usage**:
```python
from accounts.compliance_models import DataBreachLog

breach = DataBreachLog.objects.get(breach_id='BREACH-2024-001')
EmailService.send_breach_notification(breach, 'affected@example.com')
```

#### send_consent_confirmation(consent_record, recipient_email)
Confirm consent granted or withdrawn.

**Template**: `email_templates/consent_confirmation.html`
**Includes**:
- Consent type and action
- Timestamp
- Privacy rights summary
- "View Privacy Policy" and "Manage Preferences" buttons

**Usage**:
```python
from accounts.compliance_models import ConsentHistory

consent = ConsentHistory.objects.latest('timestamp')
EmailService.send_consent_confirmation(consent, 'user@example.com')
```

#### send_deal_notification(deal, recipient_email, notification_type)
Deal status updates.

**Notification Types**: 'approved', 'rejected', 'pending', 'shipped'

**Usage**:
```python
from deals.models import Deal

deal = Deal.objects.get(id=456)
EmailService.send_deal_notification(deal, 'buyer@example.com', 'approved')
```

#### send_shipment_update(shipment, recipient_email, update_type)
Shipment tracking updates.

**Update Types**: 'in_transit', 'customs', 'delivered', 'delayed'

**Usage**:
```python
from shipments.models import Shipment

shipment = Shipment.objects.get(tracking_number='SHIP-001')
EmailService.send_shipment_update(shipment, 'customer@example.com', 'in_transit')
```

### Email Configuration

**Development** (console output):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Production** (SendGrid):
```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Production** (AWS SES):
```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<ses-smtp-username>
EMAIL_HOST_PASSWORD=<ses-smtp-password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

## 📄 PDF Generation

### InvoicePDFGenerator (`utils/pdf_generator.py`)

Generate professional invoice PDFs with company branding.

**Features**:
- Company header on every page
- Invoice number and dates
- Bill To section with customer details
- Vehicle details (year, make, model, VIN)
- Line items table with alternating row colors
- Subtotal, tax, and total
- Payment instructions (3 methods)
- Terms & conditions
- Page numbers in footer

**Usage (Programmatic)**:
```python
from utils.pdf_generator import generate_invoice_pdf
from payments.models import Invoice

invoice = Invoice.objects.get(id=123)
pdf_buffer = generate_invoice_pdf(invoice)

# Save to file
with open('invoice.pdf', 'wb') as f:
    f.write(pdf_buffer.read())
```

**Usage (API Endpoint)**:
```bash
# Download invoice PDF
GET /api/payments/invoices/{id}/generate_pdf/
# Returns: PDF file with filename "invoice_INV-2024-12345678.pdf"
```

**Integration in InvoiceViewSet**:
```python
@action(detail=True, methods=['get'])
def generate_pdf(self, request, pk=None):
    """Generate and download invoice PDF"""
    invoice = self.get_object()
    pdf_buffer = generate_invoice_pdf(invoice)
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    return response
```

### ComplianceReportPDFGenerator

Generate data breach incident reports.

**Usage**:
```python
from utils.pdf_generator import generate_breach_report_pdf
from accounts.compliance_models import DataBreachLog

breach = DataBreachLog.objects.get(breach_id='BREACH-2024-001')
pdf_buffer = generate_breach_report_pdf(breach)
```

---

## 🚀 Quick Start Commands

### Create Security Records

```bash
python manage.py shell

from shipments.security_models import SecurityRisk, SecurityIncident, PortVerification
from shipments.models import Shipment
from accounts.models import User
from django.utils import timezone
from datetime import timedelta

admin = User.objects.filter(role='admin').first()
shipment = Shipment.objects.first()

# Create security risk
risk = SecurityRisk.objects.create(
    shipment=shipment,
    risk_id='RISK-2024-001',
    category='theft',
    risk_level='high',
    description='High-value vehicle in transit',
    likelihood=4,
    impact=5,
    mitigation_strategy='GPS tracking + armed escort',
    identified_by=admin,
    target_resolution_date=timezone.now().date() + timedelta(days=30)
)

# Create security incident
incident = SecurityIncident.objects.create(
    shipment=shipment,
    incident_id='INC-2024-001',
    incident_type='tampering',
    severity='medium',
    occurred_at=timezone.now(),
    location='Port of Vancouver',
    description='Tamper seal broken on container',
    reported_by=admin,
    authorities_notified=False
)

# Create port verification
port = PortVerification.objects.create(
    port_name='Port of Vancouver',
    port_code='CAVAN',
    country='Canada',
    certification_type='isps',
    certification_number='ISPS-CAVAN-2024-001',
    certifying_authority='Transport Canada',
    issue_date=timezone.now().date() - timedelta(days=180),
    expiry_date=timezone.now().date() + timedelta(days=545),
    status='active',
    security_level=1,
    security_measures='ISPS Code compliant, 24/7 patrol, CCTV',
    verified_by=admin
)

print("✅ Security records created!")
```

### Test Email Service

```bash
python manage.py shell

from utils.email_service import EmailService
from payments.models import Invoice
from accounts.compliance_models import DataBreachLog, ConsentHistory

# Test invoice reminder
invoice = Invoice.objects.first()
EmailService.send_invoice_reminder(invoice, 'test@example.com')

# Test breach notification
breach = DataBreachLog.objects.first()
EmailService.send_breach_notification(breach, 'test@example.com')

# Test consent confirmation
consent = ConsentHistory.objects.first()
EmailService.send_consent_confirmation(consent, 'test@example.com')

print("✅ Emails sent! Check console output (development) or SendGrid dashboard (production)")
```

### Test PDF Generation

```bash
python manage.py shell

from utils.pdf_generator import generate_invoice_pdf
from payments.models import Invoice

invoice = Invoice.objects.first()
pdf_buffer = generate_invoice_pdf(invoice)

# Save test PDF
with open('test_invoice.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

print("✅ PDF generated: test_invoice.pdf")
```

---

## 📊 CSV Export Formats

All security ViewSets support CSV export.

### SecurityRisk CSV Columns
```
Risk ID, Shipment, Category, Risk Level, Likelihood, Impact,
Risk Score, Status, Description, Mitigation Strategy,
Identified By, Assigned To, Identified Date,
Target Resolution, Resolution Date, Is Overdue
```

### SecurityIncident CSV Columns
```
Incident ID, Shipment, Type, Severity, Occurred At,
Location, Description, Financial Loss, Status,
Reported By, Assigned To, Reported Date, Resolution Date,
Authorities Notified, Insurance Claimed
```

### PortVerification CSV Columns
```
Port Name, Port Code, Country, Certification Type,
Certification Number, Certifying Authority,
Issue Date, Expiry Date, Days Until Expiry, Status,
Security Level, Last Inspection, Next Inspection,
Verified By, Verification Date
```

---

## 🔍 Filtering Examples

### Security Risks
```bash
# High and critical risks
GET /api/shipments/security/risks/?risk_level=high&risk_level=critical

# Open theft risks
GET /api/shipments/security/risks/?category=theft&status=open

# Risks for specific shipment
GET /api/shipments/security/risks/?shipment=1

# Search in description
GET /api/shipments/security/risks/?search=GPS+tracking
```

### Security Incidents
```bash
# Critical severity
GET /api/shipments/security/incidents/?severity=critical

# Investigating status
GET /api/shipments/security/incidents/?status=investigating

# Theft incidents
GET /api/shipments/security/incidents/?incident_type=theft

# Search by location
GET /api/shipments/security/incidents/?search=Vancouver
```

### Port Verifications
```bash
# Active certifications
GET /api/shipments/security/port-verifications/?status=active

# ISPS certifications
GET /api/shipments/security/port-verifications/?certification_type=isps

# Canadian ports
GET /api/shipments/security/port-verifications/?country=Canada

# Search by port name
GET /api/shipments/security/port-verifications/?search=Vancouver
```

---

## 🎯 Common Use Cases

### Use Case 1: Invoice Payment Reminder
```python
# 1. Get overdue invoices
from payments.models import Invoice
from django.utils import timezone

overdue = Invoice.objects.filter(
    due_date__lt=timezone.now().date(),
    status='unpaid'
)

# 2. Send reminders
from utils.email_service import EmailService

for invoice in overdue:
    recipient = invoice.deal.buyer.email if invoice.deal else invoice.user.email
    EmailService.send_invoice_reminder(invoice, recipient)
    print(f"✉️ Reminder sent for invoice {invoice.invoice_number}")
```

### Use Case 2: Data Breach Notification
```python
# 1. Create breach record
from accounts.compliance_models import DataBreachLog
from django.utils import timezone

breach = DataBreachLog.objects.create(
    breach_id='BREACH-2024-001',
    severity='high',
    status='discovered',
    breach_date=timezone.now(),
    data_types_compromised='email, phone',
    users_affected=1200,
    description='Unauthorized database access',
    reported_by=admin_user
)

# 2. Notify affected users
from utils.email_service import EmailService

affected_users = User.objects.filter(
    # Filter logic for affected users
)

for user in affected_users:
    EmailService.send_breach_notification(breach, user.email)
    print(f"✉️ Breach notification sent to {user.email}")
```

### Use Case 3: High-Risk Shipment Alert
```python
# Monitor high-risk shipments
from shipments.security_models import SecurityRisk

high_risks = SecurityRisk.objects.filter(
    risk_level__in=['high', 'critical'],
    status__in=['open', 'mitigating']
).select_related('shipment', 'identified_by')

for risk in high_risks:
    print(f"⚠️ {risk.risk_id}: {risk.description}")
    print(f"   Shipment: {risk.shipment.tracking_number}")
    print(f"   Risk Score: {risk.risk_score}/25")
    if risk.is_overdue:
        print(f"   🚨 OVERDUE!")
```

---

## 📚 Related Documentation

- [BACKEND_100_PERCENT_COMPLETE.md](BACKEND_100_PERCENT_COMPLETE.md) - Full implementation guide
- [BACKEND_IMPLEMENTATION_FINAL.md](BACKEND_IMPLEMENTATION_FINAL.md) - P0/P1 features
- [SESSION_SUMMARY_COMPLIANCE_COMPLETE.md](SESSION_SUMMARY_COMPLIANCE_COMPLETE.md) - Compliance details

---

**All P2 features are production-ready and fully documented!** 🎉
