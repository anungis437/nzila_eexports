# API Best Practices Guide

Comprehensive guide to using the Nzila Financial API effectively, securely, and efficiently.

---

## Table of Contents

1. [Security Best Practices](#security-best-practices)
2. [Performance Optimization](#performance-optimization)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [Data Validation](#data-validation)
6. [Testing](#testing)
7. [Production Deployment](#production-deployment)
8. [Monitoring and Logging](#monitoring-and-logging)

---

## Security Best Practices

### 1. Protect Your Credentials

#### ✅ DO

**Use Environment Variables**:
```bash
# .env file
NZILA_API_KEY=your-api-key
NZILA_API_SECRET=your-api-secret
NZILA_ACCESS_TOKEN=your-access-token
```

```javascript
// Load from environment
const accessToken = process.env.NZILA_ACCESS_TOKEN;
```

**Use Secrets Management**:
```python
# AWS Secrets Manager
import boto3
import json

def get_api_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='nzila/api/credentials')
    return json.loads(response['SecretString'])

credentials = get_api_credentials()
access_token = credentials['access_token']
```

#### ❌ DON'T

**Never Hardcode Credentials**:
```javascript
// ❌ Bad - Hardcoded
const accessToken = 'eyJ0eXAiOiJKV1QiLCJhbGc...';

// ❌ Bad - Committed to git
const API_KEY = 'sk_live_abc123xyz';
```

### 2. Use HTTPS Only

#### ✅ DO

```python
# Always use HTTPS in production
API_BASE_URL = 'https://api.nzila.com'

# Verify SSL certificates
response = requests.get(url, verify=True)
```

#### ❌ DON'T

```python
# ❌ Never use HTTP for sensitive data
API_BASE_URL = 'http://api.nzila.com'

# ❌ Never disable SSL verification
response = requests.get(url, verify=False)
```

### 3. Implement Token Rotation

```javascript
class SecureAPIClient {
  constructor() {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiresAt = null;
  }
  
  async getValidToken() {
    const now = Date.now();
    
    // Refresh if token expires in < 5 minutes
    if (!this.tokenExpiresAt || this.tokenExpiresAt - now < 5 * 60 * 1000) {
      await this.refreshAccessToken();
    }
    
    return this.accessToken;
  }
  
  async refreshAccessToken() {
    const response = await fetch('https://api.nzila.com/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: this.refreshToken })
    });
    
    const data = await response.json();
    this.accessToken = data.access;
    this.tokenExpiresAt = Date.now() + (60 * 60 * 1000); // 1 hour
  }
  
  async request(url, options = {}) {
    const token = await this.getValidToken();
    
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }
}
```

### 4. Validate Input to Prevent Injection

```python
from decimal import Decimal, InvalidOperation
import re

def sanitize_and_validate_input(data):
    """Sanitize and validate all input data."""
    
    # Validate deal ID (must be positive integer)
    deal_id = data.get('deal_id')
    if not isinstance(deal_id, int) or deal_id <= 0:
        raise ValueError("Invalid deal ID")
    
    # Validate amount (must be valid decimal)
    amount = data.get('amount')
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid amount format")
    
    # Sanitize strings (remove special characters)
    description = data.get('description', '')
    description = re.sub(r'[^\w\s-]', '', description)[:500]
    
    return {
        'deal_id': deal_id,
        'amount': str(amount_decimal.quantize(Decimal('0.01'))),
        'description': description
    }
```

### 5. Implement Request Signing (Advanced)

```javascript
const crypto = require('crypto');

function signRequest(method, path, timestamp, body, apiSecret) {
  const message = `${method}\n${path}\n${timestamp}\n${body}`;
  const signature = crypto
    .createHmac('sha256', apiSecret)
    .update(message)
    .digest('hex');
  
  return signature;
}

async function makeSignedRequest(url, options, apiSecret) {
  const timestamp = Date.now();
  const body = options.body || '';
  const signature = signRequest(
    options.method || 'GET',
    new URL(url).pathname,
    timestamp,
    body,
    apiSecret
  );
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'X-Timestamp': timestamp,
      'X-Signature': signature
    }
  });
}
```

---

## Performance Optimization

### 1. Implement Caching

```javascript
class CachedAPIClient {
  constructor(accessToken, cacheDuration = 5 * 60 * 1000) {
    this.accessToken = accessToken;
    this.cache = new Map();
    this.cacheDuration = cacheDuration;
  }
  
  getCacheKey(url, options) {
    return `${options.method || 'GET'}:${url}`;
  }
  
  async get(url, options = {}) {
    const cacheKey = this.getCacheKey(url, options);
    const cached = this.cache.get(cacheKey);
    
    // Return cached if valid
    if (cached && Date.now() - cached.timestamp < this.cacheDuration) {
      console.log(`Cache hit: ${cacheKey}`);
      return cached.data;
    }
    
    // Fetch fresh data
    console.log(`Cache miss: ${cacheKey}`);
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.accessToken}`
      }
    });
    
    const data = await response.json();
    
    // Cache only successful responses
    if (response.ok) {
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });
    }
    
    return data;
  }
  
  invalidate(url) {
    const keysToDelete = [];
    for (const key of this.cache.keys()) {
      if (key.includes(url)) {
        keysToDelete.push(key);
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key));
  }
}

// Usage
const client = new CachedAPIClient('your-access-token');

// First call - hits API
const data1 = await client.get('https://api.nzila.com/api/deals/123/financial-terms/');

// Second call within 5 minutes - returns cached data
const data2 = await client.get('https://api.nzila.com/api/deals/123/financial-terms/');

// Invalidate cache after update
await processPayment(123, '100.00', 'token');
client.invalidate('/api/deals/123/');
```

### 2. Batch Requests When Possible

```python
import asyncio
import aiohttp

async def fetch_multiple_deals(deal_ids, access_token):
    """Fetch multiple deals concurrently."""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_deal(session, deal_id, headers)
            for deal_id in deal_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

async def fetch_deal(session, deal_id, headers):
    """Fetch single deal."""
    url = f'https://api.nzila.com/api/deals/{deal_id}/financial-terms/'
    async with session.get(url, headers=headers) as response:
        return await response.json()

# Usage
deal_ids = [123, 124, 125, 126, 127]
results = asyncio.run(fetch_multiple_deals(deal_ids, 'your-access-token'))
```

### 3. Use Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_pooling():
    """Create session with connection pooling and retries."""
    session = requests.Session()
    
    # Configure retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET", "POST"]
    )
    
    # Configure connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

# Usage
session = create_session_with_pooling()
headers = {'Authorization': 'Bearer your-access-token'}

# Reuse session for multiple requests
for deal_id in range(100, 200):
    response = session.get(
        f'https://api.nzila.com/api/deals/{deal_id}/financial-terms/',
        headers=headers
    )
    print(f"Deal {deal_id}: {response.status_code}")
```

### 4. Optimize Payload Size

```javascript
// Request only needed fields
async function getEssentialDealInfo(dealId, accessToken) {
  const response = await fetch(
    `https://api.nzila.com/api/deals/${dealId}/financial-terms/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        // Request minimal response
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate'
      }
    }
  );
  
  const data = await response.json();
  
  // Extract only what you need
  return {
    dealId: data.deal_id,
    balance: data.amount_remaining,
    status: data.status
  };
}
```

### 5. Implement Request Debouncing

```javascript
function debounce(func, wait) {
  let timeout;
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Usage: Debounce search requests
const searchDeals = debounce(async (query, accessToken) => {
  const response = await fetch(
    `https://api.nzila.com/api/deals/?search=${query}`,
    { headers: { 'Authorization': `Bearer ${accessToken}` }}
  );
  return response.json();
}, 300); // Wait 300ms after user stops typing

// User types quickly - only last search is executed
searchInput.addEventListener('input', (e) => {
  searchDeals(e.target.value, accessToken);
});
```

---

## Rate Limiting

### Rate Limits

- **Authenticated**: 100 requests per minute
- **Unauthenticated**: 20 requests per minute

### 1. Check Rate Limit Headers

```python
def check_rate_limit(response):
    """Check and log rate limit status."""
    limit = response.headers.get('X-RateLimit-Limit')
    remaining = response.headers.get('X-RateLimit-Remaining')
    reset = response.headers.get('X-RateLimit-Reset')
    
    print(f"Rate Limit: {remaining}/{limit} remaining")
    print(f"Resets at: {reset}")
    
    if int(remaining) < 10:
        print("⚠️  Warning: Approaching rate limit!")
```

### 2. Implement Client-Side Rate Limiting

```javascript
class RateLimitedClient {
  constructor(accessToken, maxRequests = 100, timeWindow = 60000) {
    this.accessToken = accessToken;
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow;
    this.requests = [];
  }
  
  async waitIfNeeded() {
    const now = Date.now();
    
    // Remove old requests outside time window
    this.requests = this.requests.filter(
      time => now - time < this.timeWindow
    );
    
    // Check if at limit
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = this.timeWindow - (now - oldestRequest);
      
      console.log(`Rate limit reached. Waiting ${waitTime}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      
      // Recursive call to check again
      return this.waitIfNeeded();
    }
    
    this.requests.push(now);
  }
  
  async request(url, options = {}) {
    await this.waitIfNeeded();
    
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.accessToken}`
      }
    });
  }
}

// Usage
const client = new RateLimitedClient('your-access-token');

// Make many requests - automatically rate limited
for (let i = 0; i < 150; i++) {
  await client.request(`https://api.nzila.com/api/deals/${i}/financial-terms/`);
}
```

### 3. Implement Exponential Backoff

```python
import time
import random

def api_request_with_backoff(url, headers, max_retries=5):
    """Make API request with exponential backoff on rate limit."""
    
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:  # Rate limited
            if attempt == max_retries - 1:
                raise Exception("Max retries reached")
            
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Retrying in {wait_time:.2f}s...")
            time.sleep(wait_time)
            continue
        
        response.raise_for_status()
        return response.json()
    
    raise Exception("Failed after all retries")
```

---

## Error Handling

### 1. Implement Comprehensive Error Handling

```javascript
class APIError extends Error {
  constructor(message, statusCode, errorCode, details) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.details = details;
  }
}

async function apiRequest(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new APIError(
        error.error || `HTTP ${response.status}`,
        response.status,
        error.code,
        error.details
      );
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      // Handle API errors
      console.error(`API Error [${error.errorCode}]: ${error.message}`);
      if (error.details) {
        console.error('Details:', error.details);
      }
    } else if (error instanceof TypeError) {
      // Handle network errors
      console.error('Network error:', error.message);
    } else {
      // Handle other errors
      console.error('Unexpected error:', error);
    }
    
    throw error;
  }
}
```

### 2. Implement Retry Logic

```python
from functools import wraps
import time

def retry_on_error(max_retries=3, delay=1, backoff=2):
    """Decorator to retry function on error."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    
                    if retries == max_retries:
                        raise
                    
                    print(f"Attempt {retries} failed: {e}")
                    print(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage
@retry_on_error(max_retries=3, delay=1, backoff=2)
def get_deal_financial_terms(deal_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f'https://api.nzila.com/api/deals/{deal_id}/financial-terms/',
        headers=headers
    )
    response.raise_for_status()
    return response.json()
```

### 3. Implement Circuit Breaker Pattern

```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.threshold = threshold;
    this.timeout = timeout;
    this.failures = 0;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
  }
  
  async execute(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }
  
  onFailure() {
    this.failures++;
    
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
      console.log(`Circuit breaker OPEN. Will retry after ${this.timeout}ms`);
    }
  }
}

// Usage
const breaker = new CircuitBreaker(5, 60000);

async function makeAPICall(dealId, accessToken) {
  return breaker.execute(async () => {
    const response = await fetch(
      `https://api.nzila.com/api/deals/${dealId}/financial-terms/`,
      { headers: { 'Authorization': `Bearer ${accessToken}` }}
    );
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  });
}
```

---

## Data Validation

### 1. Validate Before Sending

```typescript
interface PaymentRequest {
  deal_id: number;
  amount: string;
}

function validatePaymentRequest(data: PaymentRequest): void {
  // Validate deal ID
  if (!Number.isInteger(data.deal_id) || data.deal_id <= 0) {
    throw new Error('Invalid deal ID: must be a positive integer');
  }
  
  // Validate amount
  const amount = parseFloat(data.amount);
  if (isNaN(amount)) {
    throw new Error('Invalid amount: must be a number');
  }
  if (amount <= 0) {
    throw new Error('Invalid amount: must be positive');
  }
  if (amount > 1000000) {
    throw new Error('Invalid amount: exceeds maximum of $1,000,000');
  }
  
  // Validate decimal places
  const decimalPlaces = (data.amount.split('.')[1] || '').length;
  if (decimalPlaces > 2) {
    throw new Error('Invalid amount: maximum 2 decimal places');
  }
}

// Usage
try {
  validatePaymentRequest({ deal_id: 123, amount: '100.50' });
  await processPayment(123, '100.50', accessToken);
} catch (error) {
  console.error('Validation error:', error.message);
}
```

### 2. Sanitize User Input

```python
import re
from decimal import Decimal

def sanitize_payment_data(data):
    """Sanitize payment data before sending to API."""
    
    # Sanitize deal ID (remove non-numeric characters)
    deal_id = int(re.sub(r'\D', '', str(data['deal_id'])))
    
    # Sanitize amount (remove non-numeric except decimal point)
    amount_str = re.sub(r'[^\d.]', '', str(data['amount']))
    amount = Decimal(amount_str).quantize(Decimal('0.01'))
    
    # Sanitize description (remove special characters, limit length)
    description = data.get('description', '')
    description = re.sub(r'[^\w\s-]', '', description)[:500]
    
    return {
        'deal_id': deal_id,
        'amount': str(amount),
        'description': description.strip()
    }
```

---

## Testing

### 1. Test in Staging First

```javascript
const environments = {
  development: 'http://localhost:8000',
  staging: 'https://staging-api.nzila.com',
  production: 'https://api.nzila.com'
};

const API_BASE_URL = environments[process.env.NODE_ENV || 'development'];

// Test in staging before production
if (process.env.NODE_ENV === 'production') {
  console.warn('⚠️  Running in PRODUCTION environment');
}
```

### 2. Write Integration Tests

```python
import unittest
import os

class APIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.access_token = os.getenv('TEST_ACCESS_TOKEN')
    
    def test_get_financial_terms(self):
        """Test getting financial terms for a deal."""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f'{self.api_base_url}/api/deals/1/financial-terms/',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_price', data)
        self.assertIn('amount_remaining', data)
    
    def test_process_payment(self):
        """Test processing a payment."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(
            f'{self.api_base_url}/api/deals/1/process-payment/',
            headers=headers,
            json={'amount': '100.00'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('amount_paid', data)

if __name__ == '__main__':
    unittest.main()
```

---

## Production Deployment

### 1. Use Configuration Management

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    api_base_url: str
    access_token: str
    rate_limit: int
    cache_ttl: int
    retry_max_attempts: int
    timeout: int

def load_config():
    """Load configuration from environment."""
    return Config(
        api_base_url=os.getenv('NZILA_API_BASE_URL', 'https://api.nzila.com'),
        access_token=os.getenv('NZILA_ACCESS_TOKEN'),
        rate_limit=int(os.getenv('NZILA_RATE_LIMIT', '100')),
        cache_ttl=int(os.getenv('NZILA_CACHE_TTL', '300')),
        retry_max_attempts=int(os.getenv('NZILA_RETRY_ATTEMPTS', '3')),
        timeout=int(os.getenv('NZILA_TIMEOUT', '30'))
    )

# Usage
config = load_config()
```

### 2. Implement Health Checks

```javascript
async function healthCheck() {
  try {
    const response = await fetch(
      'https://api.nzila.com/health/',
      { timeout: 5000 }
    );
    
    if (response.ok) {
      console.log('✓ API is healthy');
      return true;
    }
    
    console.error('✗ API is unhealthy');
    return false;
  } catch (error) {
    console.error('✗ API is unreachable:', error.message);
    return false;
  }
}

// Run health check on startup
healthCheck().then(healthy => {
  if (!healthy) {
    console.error('Cannot start: API is not available');
    process.exit(1);
  }
});
```

---

## Monitoring and Logging

### 1. Implement Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_api_request(self, method, url, status_code, duration_ms):
        """Log API request with structured data."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'api_request',
            'method': method,
            'url': url,
            'status_code': status_code,
            'duration_ms': duration_ms
        }
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error_message, context):
        """Log error with context."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'error',
            'message': error_message,
            'context': context
        }
        self.logger.error(json.dumps(log_data))

# Usage
logger = StructuredLogger('nzila-api')
logger.log_api_request('GET', '/api/deals/123/financial-terms/', 200, 45)
```

### 2. Track API Metrics

```javascript
class APIMetrics {
  constructor() {
    this.requests = 0;
    this.errors = 0;
    this.totalDuration = 0;
  }
  
  recordRequest(duration, error = null) {
    this.requests++;
    this.totalDuration += duration;
    
    if (error) {
      this.errors++;
    }
  }
  
  getStats() {
    return {
      total_requests: this.requests,
      total_errors: this.errors,
      error_rate: this.errors / this.requests,
      avg_duration_ms: this.totalDuration / this.requests
    };
  }
  
  reset() {
    this.requests = 0;
    this.errors = 0;
    this.totalDuration = 0;
  }
}

// Usage
const metrics = new APIMetrics();

async function makeAPICall(url, options) {
  const start = Date.now();
  let error = null;
  
  try {
    const response = await fetch(url, options);
    return await response.json();
  } catch (e) {
    error = e;
    throw e;
  } finally {
    const duration = Date.now() - start;
    metrics.recordRequest(duration, error);
  }
}

// Log metrics every minute
setInterval(() => {
  console.log('API Metrics:', metrics.getStats());
  metrics.reset();
}, 60000);
```

---

## Summary Checklist

### Security
- ✓ Store credentials in environment variables
- ✓ Use HTTPS only
- ✓ Implement token rotation
- ✓ Validate and sanitize all input
- ✓ Never log sensitive data

### Performance
- ✓ Implement caching for read operations
- ✓ Use connection pooling
- ✓ Batch requests when possible
- ✓ Minimize payload size
- ✓ Debounce frequent requests

### Reliability
- ✓ Implement comprehensive error handling
- ✓ Add retry logic with exponential backoff
- ✓ Use circuit breaker pattern
- ✓ Respect rate limits
- ✓ Monitor API health

### Quality
- ✓ Validate data before sending
- ✓ Write integration tests
- ✓ Test in staging first
- ✓ Implement structured logging
- ✓ Track metrics

---

## Additional Resources

- **API Documentation**: [https://docs.nzila.com/api](../api/financial-api.md)
- **Getting Started Guide**: [GETTING_STARTED_API.md](GETTING_STARTED_API.md)
- **Error Reference**: [API_ERROR_REFERENCE.md](API_ERROR_REFERENCE.md)
- **API Status**: [https://status.nzila.com](https://status.nzila.com)
- **Support**: api-support@nzila.com

---

**Last Updated**: December 20, 2024  
**Version**: 1.0
