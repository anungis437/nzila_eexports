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
