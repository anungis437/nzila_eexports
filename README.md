# Nzila Export Hub

A comprehensive, enterprise-grade vehicle export platform connecting Canadian dealers with West African buyers. Built with Django REST Framework, React, and TypeScript.

## Overview

Nzila Export Hub is a full-stack platform that manages the complete vehicle export pipeline with advanced payment processing, security features, and audit capabilities. The system handles:

- **Multi-Currency Payment System**: 33 currencies supported with Stripe integration
- **Two-Factor Authentication**: TOTP and SMS-based 2FA for enhanced security
- **Comprehensive Audit Trail**: Complete activity logging and security monitoring
- **PDF Report Generation**: Professional invoices, receipts, and reports
- **Lead-to-Deal Pipeline Management**: Track buyers from interest to completed sale
- **Shipment Tracking**: Real-time tracking of vehicle shipments
- **Document Verification**: Automated workflow for verifying export documents
- **Commission Automation**: Automatic commission calculation and tracking
- **Multi-Role System**: Separate portals for admins, dealers, brokers, and buyers
- **Bilingual Support**: Full English/French (EN/FR) interface

## 🚀 Key Features

### Phase 1: Payments & Security (Complete)

#### Multi-Currency Payment System
- **33 Currencies Supported**: USD, EUR, GBP, CAD + 29 African currencies
- **Stripe Integration**: Secure payment processing with Stripe PaymentIntents
- **Payment Methods**: Credit cards, bank transfers, mobile money
- **Payment Tracking**: Complete history and status monitoring
- **Refund Support**: Full and partial refunds with audit trail
- **Currency Conversion**: Real-time currency conversion with exchange rates
- **Invoice Generation**: Professional invoices with company branding

#### Two-Factor Authentication (2FA)
- **TOTP Support**: Time-based one-time passwords (Google Authenticator, Authy)
- **SMS Backup**: SMS-based 2FA as fallback option
- **Email Backup**: Email-based verification codes
- **QR Code Setup**: Easy setup with QR code scanning
- **Backup Codes**: Recovery codes for account access
- **Enforce 2FA**: Admin can require 2FA for all users
- **Session Management**: Secure session handling with 2FA

### Phase 2: Audit Trail & Reports (Complete)

#### Comprehensive Audit Trail
- **5 Audit Models**: AuditLog, LoginHistory, DataChangeLog, SecurityEvent, APIAccessLog
- **34 Action Types**: Track all user actions across the platform
- **Automatic Logging**: Middleware-based automatic API request logging
- **Security Monitoring**: Real-time detection of SQL injection, XSS, rate limits
- **Login Tracking**: Complete login/logout history with session duration
- **Data Change Tracking**: Field-level changes with before/after values
- **Performance Monitoring**: API response times and slow endpoint detection
- **Compliance Ready**: SOC 2, ISO 27001, GDPR compliance support

#### Security Features
- **Threat Detection**: Automatic detection of security threats
- **Failed Login Tracking**: Monitor failed login attempts by IP
- **Rate Limit Monitoring**: Track and block rate limit violations
- **Security Events**: Log and resolve security incidents
- **Risk Levels**: Low, medium, high, and critical risk classification
- **IP Blocking**: Automatic blocking of suspicious IPs
- **Resolution Workflow**: Track and resolve security events

#### PDF Report Generation
- **Professional Invoices**: Branded PDF invoices for payments
- **Payment Receipts**: Receipts for completed transactions
- **Deal Reports**: Comprehensive deal reports with vehicle and financial details
- **Custom Branding**: Company logo and branding on all documents
- **Download & Email**: Download PDFs or send via email
- **Multiple Formats**: A4 and Letter size support

### Core Features

#### Automated Workflows

1. **Document Verification Workflow**
   - Documents are uploaded by buyers/dealers
   - Admins verify documents
   - Deal status automatically advances when required documents are verified

2. **Commission Automation**
   - Commissions are automatically created when deals are completed
   - Separate tracking for dealer and broker commissions
   - Configurable commission percentages

3. **Stalled Deal Follow-ups**
   - Automatic detection of stalled leads (7+ days without update)
   - Automatic detection of stalled deals (14+ days without update)
   - Management command for sending follow-up notifications

#### User Roles

- **Admin**: Full system access, document verification, user management, audit trail access
- **Dealer**: Manage vehicle inventory, view their deals and commissions
- **Broker**: Facilitate deals between dealers and buyers, earn commissions
- **Buyer**: Browse vehicles, create leads, track orders and shipments

## 📊 Technical Stack

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT tokens with djangorestframework-simplejwt
- **Payment Processing**: Stripe Python SDK
- **2FA**: pyotp, qrcode
- **PDF Generation**: ReportLab
- **Task Queue**: Celery with Redis
- **File Storage**: AWS S3 / Azure Blob Storage

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **UI Components**: Headless UI, Lucide Icons
- **Date Handling**: date-fns

## Installation

### Prerequisites

- Python 3.12+
- pip
- virtualenv (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/anungis437/nzila_eexports.git
   cd nzila_eexports
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Admin interface: http://localhost:8000/admin/
   - API endpoints: http://localhost:8000/api/

## API Endpoints

### Authentication
- `POST /api-auth/login/` - Login
- `POST /api-auth/logout/` - Logout

### Accounts
- `GET /api/accounts/users/` - List users
- `GET /api/accounts/users/me/` - Get current user profile
- `PUT /api/accounts/users/me/` - Update current user profile

### Payments (Phase 1)
- `GET /api/v1/payments/currencies/` - List supported currencies
- `GET /api/v1/payments/currencies/african/` - List African currencies
- `GET /api/v1/payments/payment-methods/` - List payment methods
- `POST /api/v1/payments/payment-methods/` - Add payment method
- `POST /api/v1/payments/payments/create-intent/` - Create payment intent
- `POST /api/v1/payments/payments/confirm/` - Confirm payment
- `POST /api/v1/payments/payments/{id}/refund/` - Refund payment
- `GET /api/v1/payments/payments/{id}/invoice-pdf/` - Download invoice PDF
- `GET /api/v1/payments/payments/{id}/receipt-pdf/` - Download receipt PDF

### Two-Factor Authentication (Phase 1)
- `POST /api/v1/accounts/2fa/setup/totp/` - Setup TOTP 2FA
- `POST /api/v1/accounts/2fa/verify/totp/` - Verify TOTP code
- `POST /api/v1/accounts/2fa/disable/` - Disable 2FA
- `GET /api/v1/accounts/2fa/backup-codes/` - Get backup codes
- `POST /api/v1/accounts/2fa/regenerate-backup-codes/` - Regenerate backup codes

### Audit Trail (Phase 2)
- `GET /api/v1/audit/logs/` - List audit logs
- `GET /api/v1/audit/logs/stats/` - Get audit statistics
- `GET /api/v1/audit/logs/my_activity/` - Get user activity
- `GET /api/v1/audit/login-history/` - List login history
- `GET /api/v1/audit/login-history/failed_attempts/` - Failed login attempts
- `GET /api/v1/audit/data-changes/` - List data changes
- `GET /api/v1/audit/security-events/` - List security events
- `POST /api/v1/audit/security-events/{id}/resolve/` - Resolve security event
- `GET /api/v1/audit/api-access/` - List API access logs
- `GET /api/v1/audit/api-access/slowest_endpoints/` - Performance analysis

### Vehicles
- `GET /api/vehicles/vehicles/` - List vehicles (filtered by role)
- `POST /api/vehicles/vehicles/` - Create vehicle (dealers only)
- `GET /api/vehicles/vehicles/{id}/` - Get vehicle details
- `PUT /api/vehicles/vehicles/{id}/` - Update vehicle
- `DELETE /api/vehicles/vehicles/{id}/` - Delete vehicle

### Leads
- `GET /api/deals/leads/` - List leads
- `POST /api/deals/leads/` - Create lead
- `GET /api/deals/leads/{id}/` - Get lead details
- `PUT /api/deals/leads/{id}/` - Update lead

### Deals
- `GET /api/deals/deals/` - List deals
- `POST /api/deals/deals/` - Create deal
- `GET /api/deals/deals/{id}/` - Get deal details
- `PUT /api/deals/deals/{id}/` - Update deal status
- `GET /api/v1/payments/deals/{id}/report-pdf/` - Download deal report PDF

### Documents
- `GET /api/deals/documents/` - List documents
- `POST /api/deals/documents/` - Upload document
- `GET /api/deals/documents/{id}/` - Get document details
- `PUT /api/deals/documents/{id}/` - Update document (verify/reject)

### Shipments
- `GET /api/shipments/shipments/` - List shipments
- `POST /api/shipments/shipments/` - Create shipment
- `GET /api/shipments/shipments/{id}/` - Get shipment details
- `GET /api/shipments/shipments/{id}/track/` - Public tracking endpoint

### Commissions
- `GET /api/commissions/commissions/` - List commissions (user's own)
- `GET /api/commissions/commissions/{id}/` - Get commission details

## Testing

The platform includes comprehensive test suites for all major features.

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Suites
```bash
# Audit trail tests
python manage.py test audit.tests

# PDF generation tests
python manage.py test payments.test_pdf

# Payment system tests
python manage.py test payments.tests

# With verbose output
python manage.py test --verbosity=2
```

### Coverage Report
```bash
pip install coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Documentation
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing documentation.

## Documentation

### Guides
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide for development
- **[API_DOCS.md](API_DOCS.md)** - Complete API reference documentation
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing suite documentation (41 tests)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide (NEW)
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)** - Production best practices

### Implementation Summaries
- **[PHASE_1_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Multi-Currency Payments + 2FA
- **[PHASE_2_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Audit Trail + PDF Generation
- **[PHASE_3_SUMMARY.md](PHASE_3_SUMMARY.md)** - Testing Suite + Documentation (NEW)

### Development Status
- ✅ **Phase 1 Complete**: Multi-Currency Payments + Two-Factor Authentication
- ✅ **Phase 2 Complete**: Audit Trail System + PDF Report Generation
- ✅ **Phase 3 Complete**: Comprehensive Testing Suite (41 tests) + Full Documentation

## Management Commands

### Check for Stalled Deals
```bash
python manage.py check_stalled
```
This command should be run periodically (e.g., via cron or Celery) to:
- Identify stalled leads (>7 days without update)
- Identify stalled deals (>14 days without update)
- Send follow-up notifications

## Workflow Examples

### Complete Deal Flow

1. **Buyer creates lead** for a vehicle they're interested in
2. **Dealer/Broker contacts buyer** and negotiates
3. **Lead is converted to Deal** with agreed price
4. **Buyer uploads required documents** (ID, payment proof)
5. **Dealer uploads vehicle title** and export documents
6. **Admin verifies documents** → Deal status automatically advances
7. **Deal reaches "completed" status** → Commissions are automatically created
8. **Shipment is created** with tracking information
9. **Buyer tracks shipment** in real-time via buyer portal

### Document Verification Workflow

1. Document uploaded with status "pending"
2. Admin reviews document in admin panel
3. Admin changes status to "verified" or "rejected"
4. If verified and all required docs are verified:
   - Deal status automatically advances
   - Email notifications sent (if configured)

## Technology Stack

- **Backend**: Django 4.2+
- **API**: Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production recommended)
- **File Storage**: Local filesystem (development), S3 (production recommended)
- **Internationalization**: Django i18n with English and French support

## Project Structure

```
nzila_eexports/
├── accounts/           # User management and authentication
├── vehicles/           # Vehicle inventory management
├── deals/             # Leads, deals, and documents
├── shipments/         # Shipment tracking
├── commissions/       # Commission tracking and automation
├── nzila_export/      # Project settings and configuration
├── media/             # Uploaded files (gitignored)
├── staticfiles/       # Collected static files (gitignored)
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Security Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` properly
- Use HTTPS in production
- Implement proper file upload validation
- Regular security audits for document access

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Support

For support, please contact the development team or create an issue in the repository.
