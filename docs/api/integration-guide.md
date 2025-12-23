# Financial API Integration Guide

Complete guide for integrating the Nzila Exports Financial API into your application.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication Setup](#authentication-setup)
3. [React Integration](#react-integration)
4. [Python Integration](#python-integration)
5. [Common Workflows](#common-workflows)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Testing Strategies](#testing-strategies)

---

## Quick Start

### Prerequisites

- Node.js 16+ or Python 3.8+
- JWT authentication token
- API base URL

### Installation

**JavaScript/Node.js**:
```bash
npm install axios
# or
npm install @tanstack/react-query axios
```

**Python**:
```bash
pip install requests
```

---

## Authentication Setup

### JavaScript Client

```javascript
// api/client.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        
        localStorage.setItem('access_token', data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Python Client

```python
# api/client.py
import requests
from typing import Optional, Dict, Any
import time

class NzilaAPIClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: float = 0
        
        # Authenticate
        self.login(username, password)
    
    def login(self, username: str, password: str) -> None:
        """Authenticate and store tokens."""
        response = self.session.post(
            f'{self.base_url}/auth/login/',
            json={'username': username, 'password': password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data['access']
        self.refresh_token = data['refresh']
        self.token_expires_at = time.time() + 3600  # 1 hour
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })
    
    def refresh_access_token(self) -> None:
        """Refresh the access token."""
        response = self.session.post(
            f'{self.base_url}/auth/token/refresh/',
            json={'refresh': self.refresh_token}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data['access']
        self.token_expires_at = time.time() + 3600
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })
    
    def _ensure_authenticated(self) -> None:
        """Ensure token is valid, refresh if needed."""
        if time.time() >= self.token_expires_at - 300:  # Refresh 5 min before expiry
            self.refresh_access_token()
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make authenticated request."""
        self._ensure_authenticated()
        
        url = f'{self.base_url}{endpoint}'
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        
        return response.json()
    
    def get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """GET request."""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """POST request."""
        return self.request('POST', endpoint, **kwargs)


# Usage
client = NzilaAPIClient(
    base_url='http://localhost:8000/api',
    username='buyer@example.com',
    password='your_password'
)
```

---

## React Integration

### Using React Query

```javascript
// api/financial.js
import apiClient from './client';

export const financialAPI = {
  getFinancialTerms: (dealId) =>
    apiClient.get(`/deals/${dealId}/financial-terms/`).then(res => res.data),
  
  getPaymentSchedule: (dealId) =>
    apiClient.get(`/deals/${dealId}/payment-schedule/`).then(res => res.data),
  
  getFinancing: (dealId) =>
    apiClient.get(`/deals/${dealId}/financing/`).then(res => res.data),
  
  processPayment: (dealId, amount) =>
    apiClient.post(`/deals/${dealId}/process-payment/`, { amount }).then(res => res.data),
  
  applyFinancing: (dealId, data) =>
    apiClient.post(`/deals/${dealId}/apply-financing/`, data).then(res => res.data),
};
```

```javascript
// hooks/useFinancialData.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { financialAPI } from '../api/financial';

export function useFinancialTerms(dealId) {
  return useQuery({
    queryKey: ['financial-terms', dealId],
    queryFn: () => financialAPI.getFinancialTerms(dealId),
    enabled: !!dealId,
  });
}

export function usePaymentSchedule(dealId) {
  return useQuery({
    queryKey: ['payment-schedule', dealId],
    queryFn: () => financialAPI.getPaymentSchedule(dealId),
    enabled: !!dealId,
  });
}

export function useFinancing(dealId) {
  return useQuery({
    queryKey: ['financing', dealId],
    queryFn: () => financialAPI.getFinancing(dealId),
    enabled: !!dealId,
  });
}

export function useProcessPayment(dealId) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (amount) => financialAPI.processPayment(dealId, amount),
    onSuccess: () => {
      // Invalidate and refetch related queries
      queryClient.invalidateQueries({ queryKey: ['financial-terms', dealId] });
      queryClient.invalidateQueries({ queryKey: ['payment-schedule', dealId] });
    },
  });
}

export function useApplyFinancing(dealId) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => financialAPI.applyFinancing(dealId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['financial-terms', dealId] });
      queryClient.invalidateQueries({ queryKey: ['financing', dealId] });
    },
  });
}
```

### React Components

```javascript
// components/FinancialTerms.jsx
import React from 'react';
import { useFinancialTerms } from '../hooks/useFinancialData';

export function FinancialTerms({ dealId }) {
  const { data, isLoading, error } = useFinancialTerms(dealId);
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div className="financial-terms">
      <h2>Financial Terms</h2>
      
      <div className="summary">
        <div className="item">
          <span>Total Price:</span>
          <span>{data.currency.symbol}{data.total_price}</span>
        </div>
        <div className="item">
          <span>Amount Paid:</span>
          <span>{data.currency.symbol}{data.amount_paid}</span>
        </div>
        <div className="item">
          <span>Remaining:</span>
          <span>{data.currency.symbol}{data.amount_remaining}</span>
        </div>
        <div className="item">
          <span>Progress:</span>
          <span>{data.payment_progress_percentage}%</span>
        </div>
      </div>
      
      <div className="milestones">
        <h3>Payment Milestones</h3>
        {data.payment_milestones.map((milestone) => (
          <div key={milestone.id} className={`milestone ${milestone.status}`}>
            <div className="name">{milestone.name}</div>
            <div className="amount">
              {data.currency.symbol}{milestone.amount_due}
            </div>
            <div className="status">{milestone.status}</div>
            <div className="due-date">Due: {milestone.due_date}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

```javascript
// components/PaymentForm.jsx
import React, { useState } from 'react';
import { useProcessPayment } from '../hooks/useFinancialData';

export function PaymentForm({ dealId, maxAmount }) {
  const [amount, setAmount] = useState('');
  const { mutate: processPayment, isPending, error } = useProcessPayment(dealId);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!amount || parseFloat(amount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }
    
    processPayment(amount, {
      onSuccess: (data) => {
        alert(`Payment of $${amount} processed successfully!`);
        setAmount('');
      },
      onError: (error) => {
        alert(`Payment failed: ${error.response?.data?.error || error.message}`);
      },
    });
  };
  
  return (
    <form onSubmit={handleSubmit} className="payment-form">
      <h3>Make a Payment</h3>
      
      <div className="form-group">
        <label htmlFor="amount">Payment Amount</label>
        <input
          type="number"
          id="amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.00"
          step="0.01"
          min="0.01"
          max={maxAmount}
          disabled={isPending}
        />
        <small>Maximum: ${maxAmount}</small>
      </div>
      
      {error && (
        <div className="error">
          {error.response?.data?.error || error.message}
        </div>
      )}
      
      <button type="submit" disabled={isPending}>
        {isPending ? 'Processing...' : 'Process Payment'}
      </button>
    </form>
  );
}
```

```javascript
// components/FinancingApplication.jsx
import React, { useState } from 'react';
import { useApplyFinancing } from '../hooks/useFinancialData';

export function FinancingApplication({ dealId, remainingBalance }) {
  const [formData, setFormData] = useState({
    financed_amount: remainingBalance,
    interest_rate: '8.50',
    term_months: 36,
  });
  
  const { mutate: applyFinancing, isPending, error } = useApplyFinancing(dealId);
  
  const calculateMonthlyPayment = () => {
    const principal = parseFloat(formData.financed_amount);
    const rate = parseFloat(formData.interest_rate) / 100 / 12;
    const months = parseInt(formData.term_months);
    
    if (rate === 0) {
      return (principal / months).toFixed(2);
    }
    
    const monthly = (principal * rate * Math.pow(1 + rate, months)) / 
                   (Math.pow(1 + rate, months) - 1);
    return monthly.toFixed(2);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    applyFinancing(formData, {
      onSuccess: (data) => {
        alert(`Financing applied! Monthly payment: $${data.monthly_payment}`);
      },
      onError: (error) => {
        alert(`Financing failed: ${error.response?.data?.error || error.message}`);
      },
    });
  };
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };
  
  return (
    <form onSubmit={handleSubmit} className="financing-form">
      <h3>Apply for Financing</h3>
      
      <div className="form-group">
        <label>Financed Amount</label>
        <input
          type="number"
          name="financed_amount"
          value={formData.financed_amount}
          onChange={handleChange}
          step="0.01"
          min="0.01"
          max={remainingBalance}
          disabled={isPending}
        />
      </div>
      
      <div className="form-group">
        <label>Interest Rate (%)</label>
        <input
          type="number"
          name="interest_rate"
          value={formData.interest_rate}
          onChange={handleChange}
          step="0.01"
          min="0"
          max="25"
          disabled={isPending}
        />
      </div>
      
      <div className="form-group">
        <label>Term (months)</label>
        <select
          name="term_months"
          value={formData.term_months}
          onChange={handleChange}
          disabled={isPending}
        >
          <option value="12">12 months</option>
          <option value="24">24 months</option>
          <option value="36">36 months</option>
          <option value="48">48 months</option>
          <option value="60">60 months</option>
          <option value="72">72 months</option>
          <option value="84">84 months</option>
        </select>
      </div>
      
      <div className="summary">
        <div>Estimated Monthly Payment: ${calculateMonthlyPayment()}</div>
      </div>
      
      {error && (
        <div className="error">
          {error.response?.data?.error || error.message}
        </div>
      )}
      
      <button type="submit" disabled={isPending}>
        {isPending ? 'Applying...' : 'Apply Financing'}
      </button>
    </form>
  );
}
```

---

## Python Integration

### Using the Client

```python
# examples/financial_operations.py
from api.client import NzilaAPIClient

# Initialize client
client = NzilaAPIClient(
    base_url='http://localhost:8000/api',
    username='buyer@example.com',
    password='your_password'
)

# Get financial terms
def get_deal_financial_status(deal_id: int):
    """Get complete financial status for a deal."""
    terms = client.get(f'/deals/{deal_id}/financial-terms/')
    schedule = client.get(f'/deals/{deal_id}/payment-schedule/')
    
    print(f"Deal #{deal_id} Financial Status:")
    print(f"  Total Price: ${terms['total_price']}")
    print(f"  Amount Paid: ${terms['amount_paid']}")
    print(f"  Remaining: ${terms['amount_remaining']}")
    print(f"  Progress: {terms['payment_progress_percentage']}%")
    print(f"\nPayment Milestones:")
    for milestone in schedule['milestones']:
        print(f"  - {milestone['name']}: ${milestone['amount_due']} ({milestone['status']})")
    
    return terms, schedule

# Process payment
def make_payment(deal_id: int, amount: float):
    """Process a payment for a deal."""
    try:
        result = client.post(
            f'/deals/{deal_id}/process-payment/',
            json={'amount': str(amount)}
        )
        
        print(f"Payment Processed Successfully:")
        print(f"  Payment ID: {result['payment_id']}")
        print(f"  Amount Paid: ${result['amount_paid']}")
        print(f"  New Balance: ${result['new_balance']}")
        print(f"  Progress: {result['payment_progress']}%")
        
        return result
    except requests.HTTPError as e:
        error_data = e.response.json()
        print(f"Payment Failed: {error_data.get('error', str(e))}")
        raise

# Apply financing
def apply_financing(deal_id: int, financed_amount: float, 
                   interest_rate: float, term_months: int):
    """Apply financing to a deal."""
    try:
        result = client.post(
            f'/deals/{deal_id}/apply-financing/',
            json={
                'financed_amount': str(financed_amount),
                'interest_rate': str(interest_rate),
                'term_months': term_months
            }
        )
        
        print(f"Financing Applied Successfully:")
        print(f"  Financing ID: {result['financing_id']}")
        print(f"  Financed Amount: ${result['financed_amount']}")
        print(f"  Interest Rate: {result['interest_rate']}%")
        print(f"  Term: {result['term_months']} months")
        print(f"  Monthly Payment: ${result['monthly_payment']}")
        print(f"  Total Interest: ${result['total_interest']}")
        print(f"  Total Repayment: ${result['total_repayment']}")
        
        return result
    except requests.HTTPError as e:
        error_data = e.response.json()
        print(f"Financing Failed: {error_data.get('error', str(e))}")
        raise

# Example usage
if __name__ == '__main__':
    DEAL_ID = 123
    
    # Check financial status
    terms, schedule = get_deal_financial_status(DEAL_ID)
    
    # Make a payment
    make_payment(DEAL_ID, 5000.00)
    
    # Apply financing for remaining balance
    remaining = float(terms['amount_remaining'])
    apply_financing(DEAL_ID, remaining, 8.50, 36)
```

### Async Python Client

```python
# api/async_client.py
import aiohttp
import asyncio
from typing import Dict, Any

class AsyncNzilaAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.access_token: str = None
        self.session: aiohttp.ClientSession = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def login(self, username: str, password: str):
        """Authenticate and store token."""
        async with self.session.post(
            f'{self.base_url}/auth/login/',
            json={'username': username, 'password': password}
        ) as response:
            data = await response.json()
            self.access_token = data['access']
    
    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make authenticated request."""
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        kwargs['headers'] = headers
        
        url = f'{self.base_url}{endpoint}'
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """GET request."""
        return await self.request('GET', endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """POST request."""
        return await self.request('POST', endpoint, **kwargs)


# Usage
async def main():
    async with AsyncNzilaAPIClient('http://localhost:8000/api') as client:
        await client.login('buyer@example.com', 'password')
        
        # Fetch multiple endpoints concurrently
        deal_id = 123
        terms, schedule, financing = await asyncio.gather(
            client.get(f'/deals/{deal_id}/financial-terms/'),
            client.get(f'/deals/{deal_id}/payment-schedule/'),
            client.get(f'/deals/{deal_id}/financing/'),
        )
        
        print('Financial Terms:', terms)
        print('Payment Schedule:', schedule)
        print('Financing:', financing)

if __name__ == '__main__':
    asyncio.run(main())
```

---

## Common Workflows

### Workflow 1: Check Deal Status and Make Payment

```javascript
// React Component
import React, { useState } from 'react';
import { useFinancialTerms, useProcessPayment } from '../hooks/useFinancialData';

export function DealPaymentWorkflow({ dealId }) {
  const { data: terms, isLoading } = useFinancialTerms(dealId);
  const { mutate: processPayment } = useProcessPayment(dealId);
  const [paymentAmount, setPaymentAmount] = useState('');
  
  if (isLoading) return <div>Loading...</div>;
  
  const handlePayment = () => {
    processPayment(paymentAmount, {
      onSuccess: () => {
        alert('Payment successful!');
        setPaymentAmount('');
      },
    });
  };
  
  return (
    <div>
      <h2>Deal Payment Status</h2>
      <p>Remaining Balance: ${terms.amount_remaining}</p>
      <p>Progress: {terms.payment_progress_percentage}%</p>
      
      <input
        type="number"
        value={paymentAmount}
        onChange={(e) => setPaymentAmount(e.target.value)}
        placeholder="Enter amount"
      />
      <button onClick={handlePayment}>Make Payment</button>
    </div>
  );
}
```

### Workflow 2: Apply Financing with Validation

```python
# Python function
def apply_financing_with_validation(client, deal_id: int, 
                                   financed_amount: float,
                                   interest_rate: float,
                                   term_months: int):
    """Apply financing with business validation."""
    
    # Get current financial status
    terms = client.get(f'/deals/{deal_id}/financial-terms/')
    remaining = float(terms['amount_remaining'])
    
    # Validate financed amount
    if financed_amount > remaining:
        raise ValueError(f"Financed amount ${financed_amount} exceeds remaining balance ${remaining}")
    
    # Validate interest rate
    if not 0 <= interest_rate <= 25:
        raise ValueError(f"Interest rate {interest_rate}% must be between 0% and 25%")
    
    # Validate term
    if not 12 <= term_months <= 84:
        raise ValueError(f"Term {term_months} months must be between 12 and 84")
    
    # Apply financing
    result = client.post(
        f'/deals/{deal_id}/apply-financing/',
        json={
            'financed_amount': str(financed_amount),
            'interest_rate': str(interest_rate),
            'term_months': term_months
        }
    )
    
    return result
```

### Workflow 3: Payment Plan Calculator

```javascript
// React hook
export function usePaymentCalculator() {
  const calculatePaymentPlan = (principal, rate, months) => {
    const monthlyRate = rate / 100 / 12;
    
    if (rate === 0) {
      return {
        monthlyPayment: (principal / months).toFixed(2),
        totalInterest: '0.00',
        totalRepayment: principal.toFixed(2),
      };
    }
    
    const monthly = (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) / 
                   (Math.pow(1 + monthlyRate, months) - 1);
    
    const totalRepayment = monthly * months;
    const totalInterest = totalRepayment - principal;
    
    return {
      monthlyPayment: monthly.toFixed(2),
      totalInterest: totalInterest.toFixed(2),
      totalRepayment: totalRepayment.toFixed(2),
    };
  };
  
  return { calculatePaymentPlan };
}
```

---

## Error Handling Patterns

### JavaScript Error Handling

```javascript
// Comprehensive error handler
export function handleAPIError(error) {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return {
          title: 'Validation Error',
          message: data.detail || data.error || 'Invalid request data',
        };
      case 401:
        return {
          title: 'Authentication Required',
          message: 'Please log in to continue',
          action: 'redirect_login',
        };
      case 403:
        return {
          title: 'Permission Denied',
          message: 'You do not have permission to perform this action',
        };
      case 404:
        return {
          title: 'Not Found',
          message: 'The requested resource was not found',
        };
      case 429:
        return {
          title: 'Rate Limit Exceeded',
          message: 'Too many requests. Please try again later.',
        };
      case 500:
        return {
          title: 'Server Error',
          message: 'An unexpected error occurred. Please try again.',
        };
      default:
        return {
          title: 'Error',
          message: data.error || 'An error occurred',
        };
    }
  } else if (error.request) {
    // No response received
    return {
      title: 'Network Error',
      message: 'Unable to connect to server. Please check your connection.',
    };
  } else {
    // Request setup error
    return {
      title: 'Error',
      message: error.message || 'An unexpected error occurred',
    };
  }
}
```

### Python Error Handling

```python
# Custom exception classes
class NzilaAPIError(Exception):
    """Base exception for API errors."""
    pass

class ValidationError(NzilaAPIError):
    """Validation error (400)."""
    pass

class AuthenticationError(NzilaAPIError):
    """Authentication error (401)."""
    pass

class PermissionError(NzilaAPIError):
    """Permission error (403)."""
    pass

class NotFoundError(NzilaAPIError):
    """Resource not found (404)."""
    pass

class RateLimitError(NzilaAPIError):
    """Rate limit exceeded (429)."""
    pass

class ServerError(NzilaAPIError):
    """Server error (500)."""
    pass


def handle_api_error(response):
    """Convert HTTP error to custom exception."""
    status = response.status_code
    try:
        data = response.json()
        message = data.get('detail') or data.get('error') or response.text
    except ValueError:
        message = response.text
    
    error_map = {
        400: ValidationError,
        401: AuthenticationError,
        403: PermissionError,
        404: NotFoundError,
        429: RateLimitError,
        500: ServerError,
    }
    
    error_class = error_map.get(status, NzilaAPIError)
    raise error_class(message)


# Usage in client
def safe_request(self, method: str, endpoint: str, **kwargs):
    """Make request with error handling."""
    try:
        response = self.session.request(method, f'{self.base_url}{endpoint}', **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError:
        handle_api_error(response)
```

---

## Testing Strategies

### JavaScript Unit Tests

```javascript
// __tests__/financialAPI.test.js
import { financialAPI } from '../api/financial';
import apiClient from '../api/client';

jest.mock('../api/client');

describe('Financial API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('getFinancialTerms returns data', async () => {
    const mockData = {
      id: 1,
      total_price: '45000.00',
      amount_remaining: '30000.00',
    };
    
    apiClient.get.mockResolvedValue({ data: mockData });
    
    const result = await financialAPI.getFinancialTerms(123);
    
    expect(apiClient.get).toHaveBeenCalledWith('/deals/123/financial-terms/');
    expect(result).toEqual(mockData);
  });
  
  test('processPayment sends correct data', async () => {
    const mockResponse = {
      payment_id: 456,
      amount_paid: '5000.00',
    };
    
    apiClient.post.mockResolvedValue({ data: mockResponse });
    
    const result = await financialAPI.processPayment(123, '5000.00');
    
    expect(apiClient.post).toHaveBeenCalledWith(
      '/deals/123/process-payment/',
      { amount: '5000.00' }
    );
    expect(result).toEqual(mockResponse);
  });
});
```

### Python Unit Tests

```python
# tests/test_financial_client.py
import unittest
from unittest.mock import Mock, patch
from api.client import NzilaAPIClient

class TestFinancialAPI(unittest.TestCase):
    def setUp(self):
        with patch.object(NzilaAPIClient, 'login'):
            self.client = NzilaAPIClient(
                base_url='http://localhost:8000/api',
                username='test@example.com',
                password='password'
            )
    
    @patch('requests.Session.get')
    def test_get_financial_terms(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 1,
            'total_price': '45000.00',
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.client.get('/deals/123/financial-terms/')
        
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['total_price'], '45000.00')
    
    @patch('requests.Session.post')
    def test_process_payment(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            'payment_id': 456,
            'amount_paid': '5000.00',
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.client.post(
            '/deals/123/process-payment/',
            json={'amount': '5000.00'}
        )
        
        self.assertEqual(result['payment_id'], 456)

if __name__ == '__main__':
    unittest.main()
```

---

## Additional Resources

- [Financial API Reference](financial-api.md)
- [OpenAPI Specification](openapi.yaml)
- [Authentication Guide](../auth/authentication.md)
- [Error Codes Reference](../errors/error-codes.md)

---

**Last Updated**: December 20, 2024
