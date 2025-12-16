# Nzila Export Hub - Login Credentials

## Development Login

### Admin Account
- **Email**: `info@nzilaventures.com`
- **Password**: `admin123`
- **Role**: Buyer (with superuser privileges)
- **Access**: Full system access, Django admin panel

## Service URLs

### Marketing Site (Next.js)
- **URL**: http://localhost:3000
- **Description**: Public-facing marketing website with company info and lead capture

### Frontend Application (React + Vite)
- **URL**: http://localhost:5173
- **Description**: Main application dashboard for dealers, brokers, and buyers

### Backend API (Django)
- **URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

## API Endpoints

### Authentication
- **Login**: `POST /api/accounts/login/`
  - Body: `{ "username": "email@example.com", "password": "password" }`
  - Returns: JWT tokens + user info

- **Token Refresh**: `POST /api/accounts/token/refresh/`
  - Body: `{ "refresh": "refresh_token" }`
  - Returns: New access token

- **Current User**: `GET /api/accounts/users/me/`
  - Headers: `Authorization: Bearer {access_token}`
  - Returns: Current user details

## Testing Login

### Via cURL:
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "info@nzilaventures.com", "password": "admin123"}'
```

### Via Frontend:
1. Navigate to http://localhost:5173/login
2. Enter email: `info@nzilaventures.com`
3. Enter password: `admin123`
4. Click "Sign In"

## Status
✅ Django backend running on port 8000
✅ React frontend running on port 5173
✅ Marketing site running on port 3000
✅ JWT authentication configured
✅ Login endpoint active and tested
✅ Credentials verified and working

## Third-Party Services

### Sentry (Error Tracking & Monitoring)
- **Sign up**: https://sentry.io/signup/
- **Setup Guide**: [docs/monitoring/SENTRY_SETUP.md](docs/monitoring/SENTRY_SETUP.md)
- **Quick Setup**: Run `./setup_sentry.sh`

**Required Environment Variables**:
```bash
# Backend (.env)
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
APP_VERSION=1.0.0

# Frontend (frontend/.env)
VITE_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
VITE_ENVIRONMENT=development
```

### Stripe (Payment Processing)
**Required Environment Variables**:
```bash
# Backend (.env)
STRIPE_PUBLIC_KEY=pk_test_your_public_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Frontend (frontend/.env)
VITE_STRIPE_PUBLIC_KEY=pk_test_your_stripe_publishable_key_here
```

### Twilio (SMS 2FA)
**Required Environment Variables**:
```bash
# Backend (.env)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### AWS S3 (File Storage - Production)
**Required Environment Variables**:
```bash
# Backend (.env)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1
```

## Notes
- All credentials above are for **development only**
- Production credentials should be stored securely in environment variables
- Never commit `.env` files to version control
- See `.env.example` files for complete configuration templates

