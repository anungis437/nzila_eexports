# Getting Started with Nzila Financial API

Complete guide for end users to get started with the Nzila Financial API.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Authentication Setup](#authentication-setup)
4. [Making Your First Request](#making-your-first-request)
5. [Common Workflows](#common-workflows)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

---

## Overview

The Nzila Financial API allows you to programmatically access financial information for vehicle deals, including:

- **Financial Terms**: View deal pricing, payments, and balances
- **Payment Schedules**: Access payment milestones and due dates
- **Financing Options**: View and apply for financing
- **Payment Processing**: Process payments programmatically
- **Financing Applications**: Submit financing applications

### API Base URL

```
Production: https://api.nzila.com
Staging: https://staging-api.nzila.com
Development: http://localhost:8000
```

---

## Prerequisites

Before you begin, you'll need:

1. **Nzila Account**: Sign up at [https://nzila.com/signup](https://nzila.com/signup)
2. **API Credentials**: Obtain from your account dashboard
3. **HTTP Client**: Any HTTP client (curl, Postman, or programming language library)

### Supported Languages

Our API can be used with any language that supports HTTP requests. Popular choices include:

- **JavaScript/TypeScript**: Using `fetch`, `axios`, or `node-fetch`
- **Python**: Using `requests` or `aiohttp`
- **PHP**: Using `cURL` or `Guzzle`
- **Ruby**: Using `net/http` or `httparty`
- **Java**: Using `HttpClient` or `OkHttp`
- **C#**: Using `HttpClient`

---

## Authentication Setup

### Step 1: Create an Account

1. Visit [https://nzila.com/signup](https://nzila.com/signup)
2. Fill in your registration details
3. Verify your email address
4. Complete your profile

### Step 2: Obtain API Credentials

1. Log in to your Nzila account
2. Navigate to **Settings** → **API Credentials**
3. Click **Generate API Key**
4. Save your credentials securely:
   - **API Key**: Your unique identifier
   - **API Secret**: Your authentication secret (keep this secure!)

⚠️ **Important**: Never share your API secret or commit it to version control.

### Step 3: Get Access Token

Use your credentials to obtain an access token:

**Request:**

```bash
curl -X POST https://api.nzila.com/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 123,
    "email": "your-email@example.com",
    "role": "buyer"
  }
}
```

**Save the tokens:**
- `access`: Use this token in your API requests (valid for 1 hour)
- `refresh`: Use this to get a new access token (valid for 24 hours)

### Step 4: Refresh Your Token

When your access token expires, use the refresh token:

**Request:**

```bash
curl -X POST https://api.nzila.com/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your-refresh-token"
  }'
```

**Response:**

```json
{
  "access": "new-access-token"
}
```

---

## Making Your First Request

### Using cURL

```bash
# Get financial terms for a deal
curl https://api.nzila.com/api/deals/123/financial-terms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using JavaScript (fetch)

```javascript
const accessToken = 'YOUR_ACCESS_TOKEN';
const dealId = 123;

fetch(`https://api.nzila.com/api/deals/${dealId}/financial-terms/`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Using Python (requests)

```python
import requests

access_token = 'YOUR_ACCESS_TOKEN'
deal_id = 123

headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(
    f'https://api.nzila.com/api/deals/{deal_id}/financial-terms/',
    headers=headers
)

data = response.json()
print(data)
```

---

## Common Workflows

### Workflow 1: View Deal Financial Summary

**Scenario**: You want to see the complete financial picture of a deal.

```javascript
async function getDealFinancials(dealId, accessToken) {
  const baseUrl = 'https://api.nzila.com/api';
  const headers = {
    'Authorization': `Bearer ${accessToken}`
  };
  
  // Get financial terms
  const termsResponse = await fetch(
    `${baseUrl}/deals/${dealId}/financial-terms/`,
    { headers }
  );
  const terms = await termsResponse.json();
  
  console.log('Deal Summary:');
  console.log(`Total Price: $${terms.total_price}`);
  console.log(`Amount Paid: $${terms.amount_paid}`);
  console.log(`Balance: $${terms.amount_remaining}`);
  console.log(`Payment Progress: ${terms.payment_progress}%`);
  
  return terms;
}

// Usage
getDealFinancials(123, 'your-access-token');
```

### Workflow 2: View Payment Schedule

**Scenario**: You want to see all payment milestones and their status.

```python
import requests

def get_payment_schedule(deal_id, access_token):
    """Get payment schedule for a deal."""
    url = f'https://api.nzila.com/api/deals/{deal_id}/payment-schedule/'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    schedule = response.json()
    
    print(f"\nPayment Schedule for Deal #{deal_id}")
    print(f"Total Milestones: {schedule['total_milestones']}")
    print(f"Completed: {schedule['completed_milestones']}")
    print(f"Pending: {schedule['pending_milestones']}")
    print(f"\nMilestones:")
    
    for milestone in schedule['milestones']:
        status_emoji = '✓' if milestone['status'] == 'paid' else '○'
        print(f"{status_emoji} {milestone['name']}: ${milestone['amount_due']} - Due: {milestone['due_date']}")
    
    return schedule

# Usage
get_payment_schedule(123, 'your-access-token')
```

**Output:**
```
Payment Schedule for Deal #123
Total Milestones: 3
Completed: 1
Pending: 2

Milestones:
✓ Initial Deposit: $15000.00 - Due: 2024-12-01
○ Shipping Payment: $15000.00 - Due: 2024-12-15
○ Final Payment: $15000.00 - Due: 2024-12-30
```

### Workflow 3: Process a Payment

**Scenario**: You want to record a payment for a deal.

```javascript
async function processPayment(dealId, amount, accessToken) {
  const url = `https://api.nzila.com/api/deals/${dealId}/process-payment/`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ amount: amount })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Payment processing failed');
  }
  
  const result = await response.json();
  
  console.log('Payment Successful!');
  console.log(`Amount Paid: $${result.amount_paid}`);
  console.log(`New Balance: $${result.amount_remaining}`);
  console.log(`Progress: ${result.payment_progress}%`);
  
  return result;
}

// Usage
try {
  await processPayment(123, '5000.00', 'your-access-token');
} catch (error) {
  console.error('Payment failed:', error.message);
}
```

### Workflow 4: View Financing Options

**Scenario**: You want to see available financing options for a deal.

```python
import requests

def get_financing_options(deal_id, access_token):
    """Get financing details for a deal."""
    url = f'https://api.nzila.com/api/deals/{deal_id}/financing/'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    financing = response.json()
    
    if financing.get('has_financing'):
        print(f"\nFinancing Available for Deal #{deal_id}")
        print(f"Interest Rate: {financing['interest_rate']}%")
        print(f"Term: {financing['term_months']} months")
        print(f"Monthly Payment: ${financing['monthly_payment']}")
        print(f"Total Interest: ${financing['total_interest']}")
        
        print(f"\nInstallment Schedule:")
        for installment in financing['installments'][:3]:  # Show first 3
            print(f"Payment {installment['installment_number']}: ${installment['amount']} - Due: {installment['due_date']}")
    else:
        print(f"No financing available for deal #{deal_id}")
    
    return financing

# Usage
get_financing_options(123, 'your-access-token')
```

### Workflow 5: Apply for Financing

**Scenario**: You want to apply for financing on a deal.

```javascript
async function applyForFinancing(dealId, interestRate, termMonths, downPayment, accessToken) {
  const url = `https://api.nzila.com/api/deals/${dealId}/apply-financing/`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      interest_rate: interestRate,
      term_months: termMonths,
      down_payment: downPayment
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Financing application failed');
  }
  
  const result = await response.json();
  
  console.log('Financing Application Successful!');
  console.log(`Monthly Payment: $${result.monthly_payment}`);
  console.log(`Total Amount: $${result.total_amount}`);
  console.log(`Total Interest: $${result.total_interest}`);
  
  return result;
}

// Usage
try {
  await applyForFinancing(
    123,           // dealId
    '8.5',        // 8.5% interest rate
    36,           // 36 months
    '10000.00',   // $10,000 down payment
    'your-access-token'
  );
} catch (error) {
  console.error('Financing application failed:', error.message);
}
```

---

## Error Handling

### Understanding Error Responses

When an error occurs, the API returns a JSON response with error details:

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

### HTTP Status Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 200 | Success | Request completed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input data, validation errors |
| 401 | Unauthorized | Missing or invalid access token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Deal or resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

### Common Errors and Solutions

#### Error: "Authentication credentials were not provided"

**Status Code**: 401

**Cause**: Missing or invalid Authorization header

**Solution**:
```javascript
// ❌ Wrong - No authorization
fetch('https://api.nzila.com/api/deals/123/financial-terms/')

// ✅ Correct - Include Authorization header
fetch('https://api.nzila.com/api/deals/123/financial-terms/', {
  headers: {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
  }
})
```

#### Error: "You do not have permission to perform this action"

**Status Code**: 403

**Cause**: Trying to access a deal you don't own

**Solution**: Ensure you're accessing only your own deals (as buyer or seller).

#### Error: "Payment amount exceeds remaining balance"

**Status Code**: 400

**Cause**: Trying to pay more than the remaining balance

**Solution**: Check the remaining balance first:
```javascript
async function safeProcessPayment(dealId, amount, accessToken) {
  // Get current balance
  const terms = await fetch(
    `https://api.nzila.com/api/deals/${dealId}/financial-terms/`,
    { headers: { 'Authorization': `Bearer ${accessToken}` }}
  ).then(r => r.json());
  
  // Check if amount is valid
  if (parseFloat(amount) > parseFloat(terms.amount_remaining)) {
    throw new Error(`Payment amount $${amount} exceeds remaining balance $${terms.amount_remaining}`);
  }
  
  // Process payment
  return processPayment(dealId, amount, accessToken);
}
```

#### Error: "Deal is not in active status"

**Status Code**: 400

**Cause**: Trying to process payment on a non-active deal

**Solution**: Check deal status before processing:
```python
def process_payment_safe(deal_id, amount, access_token):
    # Get deal status
    terms = get_financial_terms(deal_id, access_token)
    
    if terms['status'] != 'active':
        raise ValueError(f"Deal must be active. Current status: {terms['status']}")
    
    # Process payment
    return process_payment(deal_id, amount, access_token)
```

#### Error: "Invalid interest rate"

**Status Code**: 400

**Cause**: Interest rate outside allowed range

**Solution**: Use valid interest rate (0.1% - 30%):
```javascript
function validateFinancingParams(interestRate, termMonths) {
  if (interestRate < 0.1 || interestRate > 30) {
    throw new Error('Interest rate must be between 0.1% and 30%');
  }
  
  if (termMonths < 12 || termMonths > 84) {
    throw new Error('Term must be between 12 and 84 months');
  }
  
  return true;
}
```

### Error Handling Best Practices

#### 1. Always Check Response Status

```javascript
async function apiRequest(url, options) {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `HTTP ${response.status}`);
  }
  
  return response.json();
}
```

#### 2. Implement Retry Logic for Transient Errors

```python
import time
import requests

def api_request_with_retry(url, headers, max_retries=3):
    """Make API request with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:  # Server error
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
            else:
                raise  # Client error - don't retry
```

#### 3. Handle Token Expiration

```javascript
class NzilaAPIClient {
  constructor(accessToken, refreshToken) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }
  
  async request(url, options = {}) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${this.accessToken}`
    };
    
    let response = await fetch(url, options);
    
    // If unauthorized, try refreshing token
    if (response.status === 401) {
      await this.refreshAccessToken();
      
      // Retry with new token
      options.headers['Authorization'] = `Bearer ${this.accessToken}`;
      response = await fetch(url, options);
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    return response.json();
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

## Best Practices

### 1. Secure Your Credentials

```bash
# ❌ Bad - Hardcoded credentials
const API_KEY = 'my-secret-key';

# ✅ Good - Use environment variables
const API_KEY = process.env.NZILA_API_KEY;
```

### 2. Respect Rate Limits

**Rate Limits**:
- **Authenticated requests**: 100 requests per minute
- **Unauthenticated requests**: 20 requests per minute

**Check rate limit headers**:
```javascript
const response = await fetch(url, options);

console.log('Rate Limit:', response.headers.get('X-RateLimit-Limit'));
console.log('Remaining:', response.headers.get('X-RateLimit-Remaining'));
console.log('Reset:', response.headers.get('X-RateLimit-Reset'));
```

**Implement rate limiting**:
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests=100, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def wait_if_needed(self):
        now = time.time()
        
        # Remove old requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(time.time())

# Usage
limiter = RateLimiter()

def make_api_request(url, headers):
    limiter.wait_if_needed()
    return requests.get(url, headers=headers)
```

### 3. Cache Responses When Appropriate

```javascript
class CachedAPIClient {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.cache = new Map();
    this.cacheDuration = 5 * 60 * 1000; // 5 minutes
  }
  
  async get(url) {
    const cached = this.cache.get(url);
    
    if (cached && Date.now() - cached.timestamp < this.cacheDuration) {
      return cached.data;
    }
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${this.accessToken}` }
    });
    
    const data = await response.json();
    
    this.cache.set(url, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  }
}
```

### 4. Use HTTPS in Production

```python
# ✅ Good - Always use HTTPS in production
API_BASE_URL = 'https://api.nzila.com'

# ❌ Bad - Never use HTTP for sensitive data
API_BASE_URL = 'http://api.nzila.com'
```

### 5. Validate Input Before Sending

```javascript
function validatePaymentAmount(amount, maxAmount) {
  const numAmount = parseFloat(amount);
  
  if (isNaN(numAmount)) {
    throw new Error('Amount must be a valid number');
  }
  
  if (numAmount <= 0) {
    throw new Error('Amount must be positive');
  }
  
  if (numAmount > maxAmount) {
    throw new Error(`Amount cannot exceed $${maxAmount}`);
  }
  
  return numAmount.toFixed(2);
}
```

### 6. Log API Requests for Debugging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def api_request(url, method='GET', **kwargs):
    logger.info(f"API Request: {method} {url}")
    
    try:
        response = requests.request(method, url, **kwargs)
        logger.info(f"API Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise
```

---

## Next Steps

Now that you're familiar with the basics:

1. **Explore the API**: Try the common workflows with your own deals
2. **Read the API Reference**: See [API Documentation](../api/financial-api.md) for complete endpoint details
3. **Check Integration Examples**: See [Integration Guide](../api/integration-guide.md) for production-ready code
4. **Join the Community**: Get help at [https://community.nzila.com](https://community.nzila.com)

---

## Support

Need help?

- **Documentation**: [https://docs.nzila.com](https://docs.nzila.com)
- **API Status**: [https://status.nzila.com](https://status.nzila.com)
- **Support Email**: api-support@nzila.com
- **Community Forum**: [https://community.nzila.com](https://community.nzila.com)

---

**Last Updated**: December 20, 2024  
**Version**: 1.0
