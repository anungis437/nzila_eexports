# Nzila Export Hub

A comprehensive vehicle export platform connecting Canadian dealers with West African buyers.

## Overview

Nzila Export Hub is a Django-based platform that manages the complete vehicle export pipeline, from lead generation to delivery. The system handles:

- **Lead-to-Deal Pipeline Management**: Track potential buyers from initial interest to completed sale
- **Shipment Tracking**: Real-time tracking of vehicle shipments
- **Document Verification**: Automated workflow for verifying export documents
- **Commission Automation**: Automatic commission calculation and tracking for dealers and brokers
- **Multi-Role System**: Separate portals for admins, dealers, brokers, and buyers
- **Bilingual Support**: Full English/French (EN/FR) interface for international trade

## Key Features

### Automated Workflows

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

### User Roles

- **Admin**: Full system access, document verification, user management
- **Dealer**: Manage vehicle inventory, view their deals and commissions
- **Broker**: Facilitate deals between dealers and buyers, earn commissions
- **Buyer**: Browse vehicles, create leads, track orders and shipments

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
