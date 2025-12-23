# Financial API Documentation

## Overview

The Nzila Exports Financial API provides comprehensive endpoints for managing financial transactions, payment processing, and financing options in the vehicle trading platform.

**Base URL**: 
- Development: `http://localhost:8000/api`
- Production: `https://api.nzilaexports.com/api`

**OpenAPI Specification**: See [openapi.yaml](openapi.yaml) for the complete API specification.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Get Financial Terms](#get-financial-terms)
   - [Get Payment Schedule](#get-payment-schedule)
   - [Get Financing Details](#get-financing-details)
   - [Process Payment](#process-payment)
   - [Apply Financing](#apply-financing)
3. [Request/Response Examples](#requestresponse-examples)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Best Practices](#best-practices)

---

## Authentication

All API endpoints require JWT authentication. Include your JWT token in the `Authorization` header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Obtaining a Token

**Endpoint**: `POST /auth/login/`

**Request**:
```json
{
  "username": "buyer@example.com",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 123,
    "username": "buyer@example.com",
    "role": "buyer"
  }
}
```

### Token Refresh

**Endpoint**: `POST /auth/token/refresh/`

**Request**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Endpoints

### Get Financial Terms

Retrieves comprehensive financial terms for a specific deal.

**Endpoint**: `GET /deals/{deal_id}/financial-terms/`  
**Permissions**: Buyer, Dealer, or Admin

#### Request

**cURL**:
```bash
curl -X GET \
  'http://localhost:8000/api/deals/123/financial-terms/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

**JavaScript (fetch)**:
```javascript
const response = await fetch('http://localhost:8000/api/deals/123/financial-terms/', {
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
});
const data = await response.json();
```

**Python (requests)**:
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
}
response = requests.get(
    'http://localhost:8000/api/deals/123/financial-terms/',
    headers=headers
)
data = response.json()
```

#### Response

**Status**: `200 OK`

```json
{
  "id": 1,
  "deal": {
    "id": 123,
    "buyer_name": "John Doe",
    "dealer_name": "Global Motors",
    "vehicle": {
      "make": "Toyota",
      "model": "Land Cruiser",
      "year": 2022
    }
  },
  "total_price": "45000.00",
  "currency": {
    "code": "USD",
    "symbol": "$"
  },
  "deposit_amount": "10000.00",
  "deposit_percentage": "22.22",
  "balance_amount": "35000.00",
  "amount_paid": "15000.00",
  "amount_remaining": "30000.00",
  "payment_progress_percentage": "33.33",
  "payment_milestones": [
    {
      "id": 1,
      "milestone_type": "deposit",
      "name": "Initial Deposit",
      "amount_due": "10000.00",
      "due_date": "2024-01-15",
      "status": "paid",
      "amount_paid": "10000.00"
    },
    {
      "id": 2,
      "milestone_type": "progress",
      "name": "First Progress Payment",
      "amount_due": "15000.00",
      "due_date": "2024-02-15",
      "status": "partial",
      "amount_paid": "5000.00"
    },
    {
      "id": 3,
      "milestone_type": "final",
      "name": "Final Payment",
      "amount_due": "20000.00",
      "due_date": "2024-03-15",
      "status": "pending",
      "amount_paid": "0.00"
    }
  ]
}
```

---

### Get Payment Schedule

Retrieves the complete payment schedule for a deal.

**Endpoint**: `GET /deals/{deal_id}/payment-schedule/`  
**Permissions**: Buyer, Dealer, or Admin

#### Request

**cURL**:
```bash
curl -X GET \
  'http://localhost:8000/api/deals/123/payment-schedule/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### Response

**Status**: `200 OK`

```json
{
  "deal_id": 123,
  "total_amount": "45000.00",
  "amount_paid": "15000.00",
  "amount_remaining": "30000.00",
  "payment_progress": "33.33",
  "milestones": [
    {
      "id": 1,
      "milestone_type": "deposit",
      "name": "Initial Deposit",
      "amount_due": "10000.00",
      "amount_paid": "10000.00",
      "due_date": "2024-01-15",
      "status": "paid",
      "is_overdue": false
    },
    {
      "id": 2,
      "milestone_type": "progress",
      "name": "First Progress Payment",
      "amount_due": "15000.00",
      "amount_paid": "5000.00",
      "due_date": "2024-02-15",
      "status": "partial",
      "is_overdue": false
    },
    {
      "id": 3,
      "milestone_type": "final",
      "name": "Final Payment",
      "amount_due": "20000.00",
      "amount_paid": "0.00",
      "due_date": "2024-03-15",
      "status": "pending",
      "is_overdue": false
    }
  ]
}
```

---

### Get Financing Details

Retrieves financing information for a deal.

**Endpoint**: `GET /deals/{deal_id}/financing/`  
**Permissions**: Buyer, Dealer, or Admin

#### Request

**cURL**:
```bash
curl -X GET \
  'http://localhost:8000/api/deals/123/financing/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### Response

**Status**: `200 OK`

```json
{
  "id": 1,
  "deal_id": 123,
  "financed_amount": "35000.00",
  "interest_rate": "8.50",
  "term_months": 36,
  "monthly_payment": "1104.43",
  "total_interest": "4759.48",
  "total_repayment": "39759.48",
  "start_date": "2024-02-01",
  "end_date": "2027-02-01",
  "status": "active",
  "installments_count": 36,
  "installments_paid": 3,
  "installments_pending": 33,
  "installments_overdue": 0,
  "installments": [
    {
      "id": 1,
      "installment_number": 1,
      "due_date": "2024-03-01",
      "amount": "1104.43",
      "principal_amount": "833.33",
      "interest_amount": "271.10",
      "status": "paid",
      "paid_date": "2024-02-28"
    },
    {
      "id": 2,
      "installment_number": 2,
      "due_date": "2024-04-01",
      "amount": "1104.43",
      "principal_amount": "839.23",
      "interest_amount": "265.20",
      "status": "paid",
      "paid_date": "2024-03-29"
    },
    {
      "id": 3,
      "installment_number": 3,
      "due_date": "2024-05-01",
      "amount": "1104.43",
      "principal_amount": "845.17",
      "interest_amount": "259.26",
      "status": "pending",
      "paid_date": null
    }
  ]
}
```

---

### Process Payment

Processes a payment for a deal with automatic status updates.

**Endpoint**: `POST /deals/{deal_id}/process-payment/`  
**Permissions**: Buyer or Admin

#### Request

**cURL**:
```bash
curl -X POST \
  'http://localhost:8000/api/deals/123/process-payment/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "amount": "5000.00"
  }'
```

**JavaScript (fetch)**:
```javascript
const response = await fetch('http://localhost:8000/api/deals/123/process-payment/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    amount: '5000.00'
  })
});
const data = await response.json();
```

**Python (requests)**:
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}
payload = {
    'amount': '5000.00'
}
response = requests.post(
    'http://localhost:8000/api/deals/123/process-payment/',
    headers=headers,
    json=payload
)
data = response.json()
```

#### Request Body

```json
{
  "amount": "5000.00"
}
```

**Validation**:
- `amount`: Required, must be a positive decimal number

#### Response

**Status**: `200 OK`

```json
{
  "message": "Payment processed successfully",
  "payment_id": 456,
  "amount_paid": "5000.00",
  "new_balance": "30000.00",
  "payment_progress": "38.89",
  "milestone_updated": {
    "id": 2,
    "status": "partial",
    "amount_paid": "5000.00",
    "amount_remaining": "10000.00"
  }
}
```

#### Side Effects

- Creates `Payment` record in database
- Updates `PaymentMilestone` status (partial/paid)
- Updates `DealFinancialTerms` (amount_paid, amount_remaining)
- Updates `Deal` status to 'paid' if fully paid
- Sends notifications to buyer and dealer

---

### Apply Financing

Applies financing to a deal with custom terms.

**Endpoint**: `POST /deals/{deal_id}/apply-financing/`  
**Permissions**: Buyer or Admin

#### Request

**cURL**:
```bash
curl -X POST \
  'http://localhost:8000/api/deals/123/apply-financing/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "financed_amount": "30000.00",
    "interest_rate": "8.50",
    "term_months": 36
  }'
```

**JavaScript (fetch)**:
```javascript
const response = await fetch('http://localhost:8000/api/deals/123/apply-financing/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    financed_amount: '30000.00',
    interest_rate: '8.50',
    term_months: 36
  })
});
const data = await response.json();
```

#### Request Body

```json
{
  "financed_amount": "30000.00",
  "interest_rate": "8.50",
  "term_months": 36
}
```

**Validation**:
- `financed_amount`: Required, must be ≤ remaining balance
- `interest_rate`: Required, 0-25%
- `term_months`: Required, 12-84 months

#### Response

**Status**: `201 Created`

```json
{
  "message": "Financing applied successfully",
  "financing_id": 789,
  "financed_amount": "30000.00",
  "interest_rate": "8.50",
  "term_months": 36,
  "monthly_payment": "946.40",
  "total_interest": "4070.40",
  "total_repayment": "34070.40",
  "installments_created": 36,
  "first_payment_date": "2024-02-01",
  "last_payment_date": "2027-02-01"
}
```

#### Side Effects

- Creates `FinancingOption` record
- Generates `FinancingInstallment` records (monthly schedule)
- Updates `Deal` status to 'financing_applied'
- Sends notifications to buyer and dealer

#### Business Rules

- Cannot apply financing to fully paid deals
- Financed amount cannot exceed remaining balance
- Interest rate must be between 0% and 25%
- Term must be between 12 and 84 months
- Only one active financing option per deal

---

## Request/Response Examples

### Common Use Cases

#### 1. Check Deal Financial Status

```bash
# Get financial terms
curl -X GET \
  'http://localhost:8000/api/deals/123/financial-terms/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'

# Get payment schedule
curl -X GET \
  'http://localhost:8000/api/deals/123/payment-schedule/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### 2. Make a Payment

```bash
# Process payment
curl -X POST \
  'http://localhost:8000/api/deals/123/process-payment/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"amount": "10000.00"}'

# Verify updated status
curl -X GET \
  'http://localhost:8000/api/deals/123/financial-terms/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

#### 3. Apply Financing and Check Installments

```bash
# Apply financing
curl -X POST \
  'http://localhost:8000/api/deals/123/apply-financing/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "financed_amount": "25000.00",
    "interest_rate": "7.50",
    "term_months": 48
  }'

# Get financing details with installments
curl -X GET \
  'http://localhost:8000/api/deals/123/financing/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "error_code"
}
```

### Common Errors

#### 1. Authentication Errors

**Status**: `401 Unauthorized`

```json
{
  "error": "Authentication credentials were not provided",
  "code": "not_authenticated"
}
```

**Solution**: Include valid JWT token in Authorization header.

#### 2. Permission Errors

**Status**: `403 Forbidden`

```json
{
  "error": "You do not have permission to perform this action",
  "code": "permission_denied"
}
```

**Solution**: Ensure user role has required permissions.

#### 3. Validation Errors

**Status**: `400 Bad Request`

```json
{
  "error": "Validation error",
  "detail": "Amount must be a positive number",
  "code": "invalid"
}
```

**Solution**: Validate input data before sending request.

#### 4. Business Logic Errors

**Status**: `400 Bad Request`

```json
{
  "error": "Cannot apply financing to fully paid deal",
  "detail": "Deal has no remaining balance",
  "code": "invalid_state"
}
```

**Solution**: Check deal status and requirements before request.

#### 5. Not Found Errors

**Status**: `404 Not Found`

```json
{
  "error": "Deal not found",
  "code": "not_found"
}
```

**Solution**: Verify deal ID exists and user has access.

---

## Rate Limiting

### Limits

- **Authenticated requests**: 1000 requests/hour
- **Anonymous requests**: 100 requests/hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded

**Status**: `429 Too Many Requests`

```json
{
  "error": "Request was throttled",
  "detail": "Request limit exceeded. Try again in 3600 seconds.",
  "code": "throttled"
}
```

---

## Best Practices

### 1. Authentication

- **Store tokens securely**: Never expose tokens in client-side code
- **Refresh tokens before expiry**: Implement automatic token refresh
- **Use HTTPS**: Always use HTTPS in production

### 2. Error Handling

```javascript
async function processPayment(dealId, amount) {
  try {
    const response = await fetch(`/api/deals/${dealId}/process-payment/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ amount })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.error);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Payment processing failed:', error);
    throw error;
  }
}
```

### 3. Validation

```javascript
function validatePaymentAmount(amount) {
  const numAmount = parseFloat(amount);
  
  if (isNaN(numAmount) || numAmount <= 0) {
    throw new Error('Amount must be a positive number');
  }
  
  if (!/^\d+(\.\d{1,2})?$/.test(amount)) {
    throw new Error('Amount must have at most 2 decimal places');
  }
  
  return true;
}
```

### 4. Retry Logic

```javascript
async function retryRequest(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1 || error.status !== 500) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

### 5. Idempotency

For payment operations, implement idempotency to prevent duplicate transactions:

```javascript
async function processPaymentIdempotent(dealId, amount, idempotencyKey) {
  const response = await fetch(`/api/deals/${dealId}/process-payment/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey
    },
    body: JSON.stringify({ amount })
  });
  
  return await response.json();
}

// Usage
const idempotencyKey = generateUUID(); // Use same key for retries
await processPaymentIdempotent(123, '5000.00', idempotencyKey);
```

### 6. Testing

Always test with realistic data in development environment:

```bash
# Test authentication
curl -X POST \
  'http://localhost:8000/auth/login/' \
  -H 'Content-Type: application/json' \
  -d '{"username": "test@example.com", "password": "test123"}'

# Test payment processing
curl -X POST \
  'http://localhost:8000/api/deals/123/process-payment/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"amount": "100.00"}'
```

---

## Additional Resources

- **OpenAPI Specification**: [openapi.yaml](openapi.yaml)
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **API Testing**: [api-testing-guide.md](api-testing-guide.md)
- **Integration Examples**: [integration-examples.md](integration-examples.md)

---

## Support

For API support or questions:
- **Email**: api@nzilaexports.com
- **Documentation**: https://docs.nzilaexports.com
- **Issue Tracker**: https://github.com/nzilaexports/issues

---

**Last Updated**: December 20, 2024  
**API Version**: 1.0.0
