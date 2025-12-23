# API Error Reference

Complete guide to understanding and resolving API errors.

---

## Table of Contents

1. [Error Response Format](#error-response-format)
2. [HTTP Status Codes](#http-status-codes)
3. [Error Categories](#error-categories)
4. [Common Errors](#common-errors)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Error Prevention](#error-prevention)

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional context",
    "value": "Related information"
  }
}
```

### Example Error Response

```json
{
  "error": "Payment amount must be positive",
  "code": "INVALID_AMOUNT",
  "details": {
    "amount": "-100.00",
    "minimum": "0.01"
  }
}
```

---

## HTTP Status Codes

### 2xx Success

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |

### 4xx Client Errors

| Code | Status | Description | Common Causes |
|------|--------|-------------|---------------|
| 400 | Bad Request | Invalid request data | Validation errors, invalid format, missing fields |
| 401 | Unauthorized | Authentication required | Missing token, expired token, invalid credentials |
| 403 | Forbidden | Access denied | Insufficient permissions, wrong role |
| 404 | Not Found | Resource not found | Invalid deal ID, deleted resource |
| 409 | Conflict | Resource conflict | Duplicate transaction, concurrent update |
| 422 | Unprocessable Entity | Validation failed | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded | Too many requests in time window |

### 5xx Server Errors

| Code | Status | Description | Action |
|------|--------|-------------|--------|
| 500 | Internal Server Error | Server error | Contact support with request ID |
| 502 | Bad Gateway | Gateway error | Retry after a short delay |
| 503 | Service Unavailable | Service down | Check status page, retry later |
| 504 | Gateway Timeout | Request timeout | Retry with shorter timeout |

---

## Error Categories

### Authentication Errors (401)

**Error Codes**:
- `AUTH_REQUIRED`: Authentication credentials missing
- `TOKEN_EXPIRED`: Access token has expired
- `TOKEN_INVALID`: Access token is invalid
- `CREDENTIALS_INVALID`: Login credentials are incorrect

### Permission Errors (403)

**Error Codes**:
- `PERMISSION_DENIED`: User lacks required permission
- `ROLE_REQUIRED`: Specific role required
- `DEAL_ACCESS_DENIED`: Cannot access this deal
- `SELLER_ONLY`: Action restricted to sellers
- `BUYER_ONLY`: Action restricted to buyers

### Validation Errors (400)

**Error Codes**:
- `INVALID_AMOUNT`: Payment amount is invalid
- `INVALID_DATE`: Date format is incorrect
- `REQUIRED_FIELD`: Required field is missing
- `INVALID_FORMAT`: Data format is incorrect
- `VALUE_OUT_OF_RANGE`: Value exceeds allowed range

### Business Logic Errors (422)

**Error Codes**:
- `DEAL_NOT_ACTIVE`: Deal must be in active status
- `INSUFFICIENT_BALANCE`: Payment exceeds remaining balance
- `FINANCING_EXISTS`: Financing already applied
- `MILESTONE_NOT_DUE`: Milestone payment not yet due
- `PAYMENT_ALREADY_PROCESSED`: Payment already recorded

### Resource Errors (404)

**Error Codes**:
- `DEAL_NOT_FOUND`: Deal does not exist
- `PAYMENT_NOT_FOUND`: Payment record not found
- `MILESTONE_NOT_FOUND`: Milestone does not exist
- `FINANCING_NOT_FOUND`: Financing option not found

### Rate Limit Errors (429)

**Error Codes**:
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

## Common Errors

### 1. Authentication Credentials Not Provided

**Status Code**: 401  
**Error Code**: `AUTH_REQUIRED`

**Error Response**:
```json
{
  "error": "Authentication credentials were not provided",
  "code": "AUTH_REQUIRED"
}
```

**Cause**: Missing `Authorization` header

**Solution**:
```javascript
// ❌ Wrong
fetch('https://api.nzila.com/api/deals/123/financial-terms/')

// ✅ Correct
fetch('https://api.nzila.com/api/deals/123/financial-terms/', {
  headers: {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
  }
})
```

---

### 2. Token Has Expired

**Status Code**: 401  
**Error Code**: `TOKEN_EXPIRED`

**Error Response**:
```json
{
  "error": "Token has expired",
  "code": "TOKEN_EXPIRED",
  "details": {
    "expired_at": "2024-12-20T10:00:00Z"
  }
}
```

**Cause**: Access token is older than 1 hour

**Solution**: Refresh your access token

```javascript
async function refreshToken(refreshToken) {
  const response = await fetch('https://api.nzila.com/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });
  
  const data = await response.json();
  return data.access; // New access token
}
```

---

### 3. Permission Denied

**Status Code**: 403  
**Error Code**: `PERMISSION_DENIED`

**Error Response**:
```json
{
  "error": "You do not have permission to perform this action",
  "code": "PERMISSION_DENIED",
  "details": {
    "required_role": "seller",
    "user_role": "buyer"
  }
}
```

**Cause**: Insufficient permissions for the action

**Common Scenarios**:
- Buyer trying to access seller-only features
- Accessing another user's deal
- Admin-only action attempted by regular user

**Solution**: Ensure you're:
1. Accessing only your own deals (as buyer or seller)
2. Using the correct account role
3. Not trying to modify deals you don't own

```python
# Check deal ownership before accessing
def get_deal_safely(deal_id, user_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f'https://api.nzila.com/api/deals/{deal_id}/financial-terms/',
        headers=headers
    )
    
    if response.status_code == 403:
        raise PermissionError(f"You don't have access to deal {deal_id}")
    
    return response.json()
```

---

### 4. Deal Not Found

**Status Code**: 404  
**Error Code**: `DEAL_NOT_FOUND`

**Error Response**:
```json
{
  "error": "Deal not found",
  "code": "DEAL_NOT_FOUND",
  "details": {
    "deal_id": 999999
  }
}
```

**Cause**: Deal ID doesn't exist or has been deleted

**Solution**: Verify the deal ID

```javascript
async function getDealSafely(dealId, accessToken) {
  try {
    const response = await fetch(
      `https://api.nzila.com/api/deals/${dealId}/financial-terms/`,
      { headers: { 'Authorization': `Bearer ${accessToken}` }}
    );
    
    if (response.status === 404) {
      throw new Error(`Deal ${dealId} not found. Please check the deal ID.`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching deal:', error.message);
    throw error;
  }
}
```

---

### 5. Invalid Payment Amount

**Status Code**: 400  
**Error Code**: `INVALID_AMOUNT`

**Error Response**:
```json
{
  "error": "Payment amount must be positive",
  "code": "INVALID_AMOUNT",
  "details": {
    "amount": "-100.00",
    "minimum": "0.01"
  }
}
```

**Cause**: Payment amount is negative or zero

**Solution**: Validate amount before sending

```python
def validate_payment_amount(amount):
    """Validate payment amount."""
    try:
        amount_decimal = Decimal(str(amount))
    except (ValueError, decimal.InvalidOperation):
        raise ValueError("Amount must be a valid number")
    
    if amount_decimal <= 0:
        raise ValueError("Amount must be positive")
    
    return str(amount_decimal.quantize(Decimal('0.01')))

# Usage
try:
    validated_amount = validate_payment_amount('100.00')
    process_payment(deal_id, validated_amount, access_token)
except ValueError as e:
    print(f"Invalid amount: {e}")
```

---

### 6. Payment Exceeds Remaining Balance

**Status Code**: 422  
**Error Code**: `INSUFFICIENT_BALANCE`

**Error Response**:
```json
{
  "error": "Payment amount exceeds remaining balance",
  "code": "INSUFFICIENT_BALANCE",
  "details": {
    "amount": "50000.00",
    "remaining_balance": "30000.00"
  }
}
```

**Cause**: Trying to pay more than what's owed

**Solution**: Check balance before payment

```javascript
async function processPaymentSafely(dealId, amount, accessToken) {
  // Get current balance
  const terms = await fetch(
    `https://api.nzila.com/api/deals/${dealId}/financial-terms/`,
    { headers: { 'Authorization': `Bearer ${accessToken}` }}
  ).then(r => r.json());
  
  const requestedAmount = parseFloat(amount);
  const remainingBalance = parseFloat(terms.amount_remaining);
  
  if (requestedAmount > remainingBalance) {
    throw new Error(
      `Payment amount $${requestedAmount} exceeds remaining balance $${remainingBalance}. ` +
      `Maximum payment: $${remainingBalance}`
    );
  }
  
  // Process payment
  return await fetch(
    `https://api.nzila.com/api/deals/${dealId}/process-payment/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ amount })
    }
  ).then(r => r.json());
}
```

---

### 7. Deal Not in Active Status

**Status Code**: 422  
**Error Code**: `DEAL_NOT_ACTIVE`

**Error Response**:
```json
{
  "error": "Deal is not in active status",
  "code": "DEAL_NOT_ACTIVE",
  "details": {
    "current_status": "completed",
    "required_status": "active"
  }
}
```

**Cause**: Trying to process payment on non-active deal

**Valid Deal Statuses**: `draft`, `active`, `completed`, `cancelled`

**Solution**: Check status before operation

```python
def process_payment_if_active(deal_id, amount, access_token):
    """Process payment only if deal is active."""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Get deal status
    terms_response = requests.get(
        f'https://api.nzila.com/api/deals/{deal_id}/financial-terms/',
        headers=headers
    )
    terms = terms_response.json()
    
    # Check status
    if terms['status'] != 'active':
        raise ValueError(
            f"Cannot process payment. Deal status is '{terms['status']}', "
            f"must be 'active'"
        )
    
    # Process payment
    payment_response = requests.post(
        f'https://api.nzila.com/api/deals/{deal_id}/process-payment/',
        headers=headers,
        json={'amount': amount}
    )
    
    return payment_response.json()
```

---

### 8. Financing Already Exists

**Status Code**: 422  
**Error Code**: `FINANCING_EXISTS`

**Error Response**:
```json
{
  "error": "Financing already exists for this deal",
  "code": "FINANCING_EXISTS",
  "details": {
    "existing_financing_id": 456
  }
}
```

**Cause**: Attempting to apply financing when it already exists

**Solution**: Check if financing exists first

```javascript
async function applyFinancingIfNotExists(dealId, financingParams, accessToken) {
  const headers = { 'Authorization': `Bearer ${accessToken}` };
  
  // Check if financing already exists
  const financingResponse = await fetch(
    `https://api.nzila.com/api/deals/${dealId}/financing/`,
    { headers }
  );
  const financing = await financingResponse.json();
  
  if (financing.has_financing) {
    throw new Error(
      `Financing already exists for this deal. ` +
      `Monthly payment: $${financing.monthly_payment}, ` +
      `Term: ${financing.term_months} months`
    );
  }
  
  // Apply financing
  return await fetch(
    `https://api.nzila.com/api/deals/${dealId}/apply-financing/`,
    {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(financingParams)
    }
  ).then(r => r.json());
}
```

---

### 9. Invalid Interest Rate

**Status Code**: 400  
**Error Code**: `VALUE_OUT_OF_RANGE`

**Error Response**:
```json
{
  "error": "Interest rate must be between 0.1% and 30%",
  "code": "VALUE_OUT_OF_RANGE",
  "details": {
    "field": "interest_rate",
    "value": "35.0",
    "min": "0.1",
    "max": "30.0"
  }
}
```

**Cause**: Interest rate outside valid range (0.1% - 30%)

**Solution**: Validate parameters before submission

```python
def validate_financing_params(interest_rate, term_months, down_payment, total_price):
    """Validate financing parameters."""
    errors = []
    
    # Validate interest rate
    if not (0.1 <= float(interest_rate) <= 30.0):
        errors.append("Interest rate must be between 0.1% and 30%")
    
    # Validate term
    if not (12 <= int(term_months) <= 84):
        errors.append("Term must be between 12 and 84 months")
    
    # Validate down payment
    down_payment_decimal = Decimal(str(down_payment))
    total_price_decimal = Decimal(str(total_price))
    
    if down_payment_decimal < 0:
        errors.append("Down payment cannot be negative")
    
    if down_payment_decimal >= total_price_decimal:
        errors.append("Down payment must be less than total price")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return True

# Usage
try:
    validate_financing_params('8.5', 36, '10000.00', '45000.00')
    apply_financing(deal_id, params, access_token)
except ValueError as e:
    print(f"Invalid financing parameters: {e}")
```

---

### 10. Rate Limit Exceeded

**Status Code**: 429  
**Error Code**: `RATE_LIMIT_EXCEEDED`

**Error Response**:
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": 100,
    "window": "60 seconds",
    "retry_after": 45
  }
}
```

**Rate Limits**:
- **Authenticated**: 100 requests per minute
- **Unauthenticated**: 20 requests per minute

**Solution**: Implement rate limiting and retry logic

```javascript
async function apiRequestWithRateLimit(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch(url, options);
    
    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
      console.log(`Rate limited. Retrying after ${retryAfter} seconds...`);
      
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      continue;
    }
    
    return response;
  }
  
  throw new Error('Rate limit exceeded. Max retries reached.');
}
```

---

## Troubleshooting Guide

### Quick Diagnosis

When you encounter an error, follow this checklist:

1. **Check the HTTP status code**: Identifies the error category
2. **Read the error message**: Provides human-readable description
3. **Check the error code**: Identifies specific error type
4. **Review details object**: Contains context-specific information
5. **Verify your request**: Ensure all required fields are present
6. **Check authentication**: Verify token is valid and not expired
7. **Review permissions**: Ensure you have access to the resource
8. **Validate input data**: Check data types and formats
9. **Check API status**: Visit [https://status.nzila.com](https://status.nzila.com)
10. **Contact support**: If issue persists, email api-support@nzila.com

### Debugging Tips

#### 1. Log Full Error Response

```python
import requests
import json

def debug_api_request(url, method='GET', **kwargs):
    """Make API request with detailed logging."""
    print(f"\n--- API Request ---")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(kwargs.get('headers', {}), indent=2)}")
    
    if 'json' in kwargs:
        print(f"Body: {json.dumps(kwargs['json'], indent=2)}")
    
    response = requests.request(method, url, **kwargs)
    
    print(f"\n--- API Response ---")
    print(f"Status: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    print(f"Body: {response.text}")
    
    return response
```

#### 2. Validate Before Sending

```javascript
function validateBeforeSend(data, schema) {
  const errors = [];
  
  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    
    if (rules.required && !value) {
      errors.push(`${field} is required`);
    }
    
    if (rules.type && typeof value !== rules.type) {
      errors.push(`${field} must be ${rules.type}`);
    }
    
    if (rules.min && value < rules.min) {
      errors.push(`${field} must be at least ${rules.min}`);
    }
    
    if (rules.max && value > rules.max) {
      errors.push(`${field} must be at most ${rules.max}`);
    }
  }
  
  if (errors.length > 0) {
    throw new Error(`Validation failed:\n- ${errors.join('\n- ')}`);
  }
}

// Usage
const schema = {
  amount: { required: true, type: 'string', min: 0.01 },
  deal_id: { required: true, type: 'number' }
};

try {
  validateBeforeSend({ amount: '100.00', deal_id: 123 }, schema);
} catch (error) {
  console.error(error.message);
}
```

#### 3. Test in Stages

```python
def test_api_flow():
    """Test complete API flow step by step."""
    
    # Stage 1: Authentication
    print("Stage 1: Authenticating...")
    tokens = authenticate('user@example.com', 'password')
    print(f"✓ Access token obtained: {tokens['access'][:20]}...")
    
    # Stage 2: Get deal
    print("\nStage 2: Fetching deal...")
    deal = get_deal(123, tokens['access'])
    print(f"✓ Deal fetched: #{deal['deal_number']}")
    
    # Stage 3: Check balance
    print("\nStage 3: Checking balance...")
    terms = get_financial_terms(123, tokens['access'])
    print(f"✓ Balance: ${terms['amount_remaining']}")
    
    # Stage 4: Process payment
    print("\nStage 4: Processing payment...")
    result = process_payment(123, '100.00', tokens['access'])
    print(f"✓ Payment processed: ${result['amount_paid']}")
    
    print("\n✓ All stages completed successfully!")
```

---

## Error Prevention

### Best Practices

#### 1. Validate Input Early

```javascript
function validatePaymentInput(amount, dealId) {
  if (!dealId || typeof dealId !== 'number') {
    throw new Error('Valid deal ID is required');
  }
  
  const numAmount = parseFloat(amount);
  if (isNaN(numAmount) || numAmount <= 0) {
    throw new Error('Amount must be a positive number');
  }
  
  return { amount: numAmount.toFixed(2), dealId };
}
```

#### 2. Check Preconditions

```python
async def process_payment_with_checks(deal_id, amount, access_token):
    """Process payment with all precondition checks."""
    
    # Check 1: Deal exists
    terms = await get_financial_terms(deal_id, access_token)
    if not terms:
        raise ValueError(f"Deal {deal_id} not found")
    
    # Check 2: Deal is active
    if terms['status'] != 'active':
        raise ValueError(f"Deal must be active (current: {terms['status']})")
    
    # Check 3: Amount is valid
    amount_decimal = Decimal(amount)
    if amount_decimal <= 0:
        raise ValueError("Amount must be positive")
    
    # Check 4: Amount doesn't exceed balance
    remaining = Decimal(terms['amount_remaining'])
    if amount_decimal > remaining:
        raise ValueError(f"Amount ${amount} exceeds balance ${remaining}")
    
    # All checks passed - process payment
    return await process_payment(deal_id, amount, access_token)
```

#### 3. Handle Token Expiration Automatically

```javascript
class APIClient {
  constructor(credentials) {
    this.credentials = credentials;
    this.accessToken = null;
    this.refreshToken = null;
  }
  
  async ensureAuthenticated() {
    if (!this.accessToken) {
      await this.authenticate();
    }
  }
  
  async authenticate() {
    const response = await fetch('https://api.nzila.com/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(this.credentials)
    });
    
    const data = await response.json();
    this.accessToken = data.access;
    this.refreshToken = data.refresh;
  }
  
  async request(url, options = {}) {
    await this.ensureAuthenticated();
    
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${this.accessToken}`
    };
    
    let response = await fetch(url, options);
    
    // Auto-refresh on 401
    if (response.status === 401) {
      await this.refreshAccessToken();
      options.headers['Authorization'] = `Bearer ${this.accessToken}`;
      response = await fetch(url, options);
    }
    
    return response;
  }
  
  async refreshAccessToken() {
    const response = await fetch('https://api.nzila.com/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: this.refreshToken })
    });
    
    const data = await response.json();
    this.accessToken = data.access;
  }
}
```

---

## Getting Help

If you continue to experience issues:

1. **Check API Status**: [https://status.nzila.com](https://status.nzila.com)
2. **Search Documentation**: [https://docs.nzila.com](https://docs.nzila.com)
3. **Community Forum**: [https://community.nzila.com](https://community.nzila.com)
4. **Contact Support**: api-support@nzila.com

When contacting support, include:
- Request ID (from `X-Request-ID` response header)
- Error message and code
- Request details (URL, method, timestamp)
- Steps to reproduce

---

**Last Updated**: December 20, 2024  
**Version**: 1.0
