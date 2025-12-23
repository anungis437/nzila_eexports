# API Testing Guide

Comprehensive guide for testing applications that integrate with the Nzila Exports Financial API.

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [Test Data Management](#test-data-management)
6. [Mocking Strategies](#mocking-strategies)
7. [Performance Testing](#performance-testing)
8. [CI/CD Integration](#cicd-integration)

---

## Testing Strategy

### Test Pyramid

```
       /\
      /  \     E2E Tests (10%)
     /----\    - Complete workflows
    /      \   - Browser automation
   /--------\  
  / Integration\ (30%)
 /--------------\  - API testing
/    Unit Tests  \ (60%)
------------------  - Business logic
                    - Utilities
```

### What to Test

**DO Test**:
- ✅ Request validation logic
- ✅ Response data transformation
- ✅ Error handling flows
- ✅ Business logic calculations
- ✅ State management
- ✅ Component rendering
- ✅ User interactions

**DON'T Test**:
- ❌ API implementation details
- ❌ Server-side business rules
- ❌ Database operations
- ❌ Third-party library internals

---

## Unit Testing

### Testing Utilities

#### JavaScript/Jest

```javascript
// utils/financial.js
export function calculatePaymentProgress(amountPaid, totalPrice) {
  if (totalPrice === 0) return 0;
  return Math.round((amountPaid / totalPrice) * 100 * 100) / 100;
}

export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function validatePaymentAmount(amount, maxAmount) {
  const numAmount = parseFloat(amount);
  
  if (isNaN(numAmount)) {
    return { valid: false, error: 'Amount must be a number' };
  }
  
  if (numAmount <= 0) {
    return { valid: false, error: 'Amount must be greater than zero' };
  }
  
  if (numAmount > maxAmount) {
    return { valid: false, error: `Amount cannot exceed $${maxAmount}` };
  }
  
  return { valid: true };
}
```

```javascript
// __tests__/utils/financial.test.js
import {
  calculatePaymentProgress,
  formatCurrency,
  validatePaymentAmount,
} from '../utils/financial';

describe('Financial Utilities', () => {
  describe('calculatePaymentProgress', () => {
    test('calculates percentage correctly', () => {
      expect(calculatePaymentProgress(15000, 45000)).toBe(33.33);
      expect(calculatePaymentProgress(45000, 45000)).toBe(100);
      expect(calculatePaymentProgress(0, 45000)).toBe(0);
    });
    
    test('handles zero total price', () => {
      expect(calculatePaymentProgress(1000, 0)).toBe(0);
    });
  });
  
  describe('formatCurrency', () => {
    test('formats USD correctly', () => {
      expect(formatCurrency(45000)).toBe('$45,000.00');
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });
    
    test('formats other currencies', () => {
      expect(formatCurrency(45000, 'EUR')).toBe('€45,000.00');
    });
  });
  
  describe('validatePaymentAmount', () => {
    test('validates correct amounts', () => {
      expect(validatePaymentAmount(5000, 10000)).toEqual({ valid: true });
      expect(validatePaymentAmount('5000', 10000)).toEqual({ valid: true });
    });
    
    test('rejects invalid amounts', () => {
      expect(validatePaymentAmount(-100, 10000).valid).toBe(false);
      expect(validatePaymentAmount(0, 10000).valid).toBe(false);
      expect(validatePaymentAmount('invalid', 10000).valid).toBe(false);
      expect(validatePaymentAmount(15000, 10000).valid).toBe(false);
    });
  });
});
```

#### Python/pytest

```python
# utils/financial.py
from decimal import Decimal
from typing import Dict, Any

def calculate_payment_progress(amount_paid: Decimal, total_price: Decimal) -> Decimal:
    """Calculate payment progress percentage."""
    if total_price == 0:
        return Decimal('0')
    return round((amount_paid / total_price) * 100, 2)

def validate_payment_amount(amount: str, max_amount: Decimal) -> Dict[str, Any]:
    """Validate payment amount."""
    try:
        amount_decimal = Decimal(amount)
    except (ValueError, TypeError):
        return {'valid': False, 'error': 'Amount must be a valid number'}
    
    if amount_decimal <= 0:
        return {'valid': False, 'error': 'Amount must be greater than zero'}
    
    if amount_decimal > max_amount:
        return {'valid': False, 'error': f'Amount cannot exceed {max_amount}'}
    
    return {'valid': True}
```

```python
# tests/test_financial_utils.py
import pytest
from decimal import Decimal
from utils.financial import calculate_payment_progress, validate_payment_amount

class TestFinancialUtils:
    def test_calculate_payment_progress(self):
        assert calculate_payment_progress(Decimal('15000'), Decimal('45000')) == Decimal('33.33')
        assert calculate_payment_progress(Decimal('45000'), Decimal('45000')) == Decimal('100')
        assert calculate_payment_progress(Decimal('0'), Decimal('45000')) == Decimal('0')
    
    def test_calculate_payment_progress_zero_total(self):
        assert calculate_payment_progress(Decimal('1000'), Decimal('0')) == Decimal('0')
    
    def test_validate_payment_amount_valid(self):
        result = validate_payment_amount('5000', Decimal('10000'))
        assert result['valid'] is True
    
    def test_validate_payment_amount_invalid(self):
        # Negative amount
        result = validate_payment_amount('-100', Decimal('10000'))
        assert result['valid'] is False
        
        # Zero amount
        result = validate_payment_amount('0', Decimal('10000'))
        assert result['valid'] is False
        
        # Invalid string
        result = validate_payment_amount('invalid', Decimal('10000'))
        assert result['valid'] is False
        
        # Exceeds max
        result = validate_payment_amount('15000', Decimal('10000'))
        assert result['valid'] is False
```

### Testing React Components

```javascript
// __tests__/components/PaymentForm.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PaymentForm } from '../components/PaymentForm';

// Mock the custom hook
jest.mock('../hooks/useFinancialData', () => ({
  useProcessPayment: () => ({
    mutate: jest.fn(),
    isPending: false,
    error: null,
  }),
}));

describe('PaymentForm', () => {
  test('renders form elements', () => {
    render(<PaymentForm dealId={123} maxAmount={10000} />);
    
    expect(screen.getByText('Make a Payment')).toBeInTheDocument();
    expect(screen.getByLabelText('Payment Amount')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Process Payment' })).toBeInTheDocument();
  });
  
  test('validates minimum amount', async () => {
    render(<PaymentForm dealId={123} maxAmount={10000} />);
    
    const input = screen.getByLabelText('Payment Amount');
    const button = screen.getByRole('button', { name: 'Process Payment' });
    
    // Enter invalid amount
    fireEvent.change(input, { target: { value: '0' } });
    fireEvent.click(button);
    
    // Check for validation alert (you might want to use a better UI feedback)
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Please enter a valid amount');
    });
  });
  
  test('disables form during submission', () => {
    // Mock pending state
    jest.mock('../hooks/useFinancialData', () => ({
      useProcessPayment: () => ({
        mutate: jest.fn(),
        isPending: true,
        error: null,
      }),
    }));
    
    render(<PaymentForm dealId={123} maxAmount={10000} />);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent('Processing...');
  });
});
```

---

## Integration Testing

### Testing API Client

```javascript
// __tests__/api/financialAPI.integration.test.js
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { financialAPI } from '../api/financial';

describe('Financial API Integration', () => {
  let mock;
  
  beforeEach(() => {
    mock = new MockAdapter(axios);
  });
  
  afterEach(() => {
    mock.restore();
  });
  
  test('getFinancialTerms returns formatted data', async () => {
    const mockData = {
      id: 1,
      deal: {
        id: 123,
        deal_number: 'DEAL-123',
      },
      total_price: '45000.00',
      amount_paid: '15000.00',
      amount_remaining: '30000.00',
      payment_progress_percentage: 33.33,
      currency: {
        code: 'USD',
        symbol: '$',
      },
    };
    
    mock.onGet('/api/deals/123/financial-terms/').reply(200, mockData);
    
    const result = await financialAPI.getFinancialTerms(123);
    
    expect(result).toEqual(mockData);
    expect(result.total_price).toBe('45000.00');
  });
  
  test('processPayment handles errors', async () => {
    mock.onPost('/api/deals/123/process-payment/').reply(400, {
      error: 'Payment amount exceeds remaining balance',
    });
    
    await expect(
      financialAPI.processPayment(123, '50000')
    ).rejects.toThrow();
  });
  
  test('handles authentication errors', async () => {
    mock.onGet('/api/deals/123/financial-terms/').reply(401, {
      detail: 'Authentication credentials were not provided.',
    });
    
    await expect(
      financialAPI.getFinancialTerms(123)
    ).rejects.toThrow();
  });
});
```

### Python Integration Tests

```python
# tests/integration/test_api_client.py
import pytest
import responses
from api.client import NzilaAPIClient

@pytest.fixture
def mock_client():
    """Create client with mocked authentication."""
    with responses.RequestsMock() as rsps:
        # Mock login
        rsps.add(
            responses.POST,
            'http://localhost:8000/api/auth/login/',
            json={'access': 'test_token', 'refresh': 'refresh_token'},
            status=200
        )
        
        client = NzilaAPIClient(
            base_url='http://localhost:8000/api',
            username='test@example.com',
            password='password'
        )
        
        yield client, rsps

def test_get_financial_terms(mock_client):
    """Test getting financial terms."""
    client, rsps = mock_client
    
    # Mock API response
    rsps.add(
        responses.GET,
        'http://localhost:8000/api/deals/123/financial-terms/',
        json={
            'id': 1,
            'total_price': '45000.00',
            'amount_remaining': '30000.00',
        },
        status=200
    )
    
    result = client.get('/deals/123/financial-terms/')
    
    assert result['id'] == 1
    assert result['total_price'] == '45000.00'

def test_process_payment_error(mock_client):
    """Test payment processing error handling."""
    client, rsps = mock_client
    
    # Mock error response
    rsps.add(
        responses.POST,
        'http://localhost:8000/api/deals/123/process-payment/',
        json={'error': 'Payment amount exceeds remaining balance'},
        status=400
    )
    
    with pytest.raises(Exception) as exc_info:
        client.post('/deals/123/process-payment/', json={'amount': '50000'})
    
    assert 'exceeds remaining balance' in str(exc_info.value)
```

---

## End-to-End Testing

### Cypress Tests

```javascript
// cypress/e2e/payment-workflow.cy.js
describe('Payment Workflow', () => {
  beforeEach(() => {
    // Login
    cy.login('buyer@example.com', 'password');
    
    // Navigate to deal
    cy.visit('/deals/123');
  });
  
  it('displays financial terms correctly', () => {
    cy.get('[data-testid="total-price"]').should('contain', '$45,000.00');
    cy.get('[data-testid="amount-paid"]').should('contain', '$15,000.00');
    cy.get('[data-testid="amount-remaining"]').should('contain', '$30,000.00');
    cy.get('[data-testid="payment-progress"]').should('contain', '33.33%');
  });
  
  it('processes payment successfully', () => {
    // Enter payment amount
    cy.get('[data-testid="payment-amount"]').type('5000');
    
    // Submit payment
    cy.get('[data-testid="submit-payment"]').click();
    
    // Wait for success message
    cy.get('[data-testid="success-message"]')
      .should('be.visible')
      .and('contain', 'Payment processed successfully');
    
    // Verify updated balance
    cy.get('[data-testid="amount-paid"]').should('contain', '$20,000.00');
    cy.get('[data-testid="amount-remaining"]').should('contain', '$25,000.00');
  });
  
  it('validates payment amount', () => {
    // Try to pay more than remaining
    cy.get('[data-testid="payment-amount"]').type('50000');
    cy.get('[data-testid="submit-payment"]').click();
    
    // Check error message
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'exceeds remaining balance');
  });
  
  it('applies financing correctly', () => {
    // Open financing form
    cy.get('[data-testid="apply-financing-button"]').click();
    
    // Fill form
    cy.get('[data-testid="financed-amount"]').clear().type('30000');
    cy.get('[data-testid="interest-rate"]').clear().type('8.5');
    cy.get('[data-testid="term-months"]').select('36');
    
    // Submit
    cy.get('[data-testid="submit-financing"]').click();
    
    // Verify success
    cy.get('[data-testid="success-message"]')
      .should('contain', 'Financing applied successfully');
    
    // Check financing details displayed
    cy.get('[data-testid="monthly-payment"]').should('be.visible');
  });
});
```

### Playwright Tests

```javascript
// tests/e2e/payment.spec.js
import { test, expect } from '@playwright/test';

test.describe('Payment Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'buyer@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Wait for navigation
    await page.waitForURL('/dashboard');
    
    // Go to deal
    await page.goto('/deals/123');
  });
  
  test('displays financial information', async ({ page }) => {
    await expect(page.locator('[data-testid="total-price"]')).toContainText('$45,000.00');
    await expect(page.locator('[data-testid="amount-remaining"]')).toContainText('$30,000.00');
  });
  
  test('processes payment', async ({ page }) => {
    await page.fill('[data-testid="payment-amount"]', '5000');
    await page.click('[data-testid="submit-payment"]');
    
    // Wait for success
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="amount-paid"]')).toContainText('$20,000.00');
  });
});
```

---

## Test Data Management

### Test Fixtures

```javascript
// fixtures/financial.js
export const mockFinancialTerms = {
  id: 1,
  deal: {
    id: 123,
    deal_number: 'DEAL-123',
    status: 'active',
  },
  vehicle: {
    id: 456,
    make: 'Toyota',
    model: 'Land Cruiser',
    year: 2023,
  },
  total_price: '45000.00',
  amount_paid: '15000.00',
  amount_remaining: '30000.00',
  payment_progress_percentage: 33.33,
  currency: {
    code: 'USD',
    symbol: '$',
    name: 'US Dollar',
  },
  payment_milestones: [
    {
      id: 1,
      name: 'Initial Deposit',
      amount_due: '15000.00',
      status: 'paid',
      due_date: '2024-01-15',
      paid_date: '2024-01-14',
    },
    {
      id: 2,
      name: 'Pre-Shipment Payment',
      amount_due: '20000.00',
      status: 'pending',
      due_date: '2024-02-15',
      paid_date: null,
    },
  ],
};

export const mockPaymentSchedule = {
  deal_id: 123,
  total_amount: '45000.00',
  amount_paid: '15000.00',
  amount_remaining: '30000.00',
  currency: {
    code: 'USD',
    symbol: '$',
  },
  milestones: [
    {
      id: 1,
      name: 'Initial Deposit',
      amount_due: '15000.00',
      percentage: 33.33,
      status: 'paid',
      due_date: '2024-01-15',
    },
  ],
};
```

### Factory Functions

```python
# tests/factories.py
from decimal import Decimal
from datetime import date, timedelta

def create_financial_terms(**overrides):
    """Create test financial terms data."""
    defaults = {
        'id': 1,
        'deal': {
            'id': 123,
            'deal_number': 'DEAL-123',
            'status': 'active',
        },
        'vehicle': {
            'id': 456,
            'make': 'Toyota',
            'model': 'Land Cruiser',
            'year': 2023,
        },
        'total_price': '45000.00',
        'amount_paid': '15000.00',
        'amount_remaining': '30000.00',
        'payment_progress_percentage': Decimal('33.33'),
        'currency': {
            'code': 'USD',
            'symbol': '$',
            'name': 'US Dollar',
        },
    }
    
    return {**defaults, **overrides}

def create_payment_milestone(**overrides):
    """Create test payment milestone."""
    defaults = {
        'id': 1,
        'name': 'Initial Deposit',
        'amount_due': '15000.00',
        'status': 'pending',
        'due_date': (date.today() + timedelta(days=30)).isoformat(),
        'paid_date': None,
    }
    
    return {**defaults, **overrides}
```

---

## Mocking Strategies

### Mock Service Worker (MSW)

```javascript
// mocks/handlers.js
import { http, HttpResponse } from 'msw';
import { mockFinancialTerms, mockPaymentSchedule } from '../fixtures/financial';

export const handlers = [
  // Get financial terms
  http.get('/api/deals/:id/financial-terms/', ({ params }) => {
    return HttpResponse.json({
      ...mockFinancialTerms,
      deal: {
        ...mockFinancialTerms.deal,
        id: parseInt(params.id),
      },
    });
  }),
  
  // Get payment schedule
  http.get('/api/deals/:id/payment-schedule/', ({ params }) => {
    return HttpResponse.json({
      ...mockPaymentSchedule,
      deal_id: parseInt(params.id),
    });
  }),
  
  // Process payment
  http.post('/api/deals/:id/process-payment/', async ({ request, params }) => {
    const body = await request.json();
    
    return HttpResponse.json({
      payment_id: 789,
      deal_id: parseInt(params.id),
      amount_paid: body.amount,
      new_balance: '25000.00',
      payment_progress: 44.44,
      next_milestone: {
        name: 'Pre-Shipment Payment',
        amount_due: '20000.00',
      },
    });
  }),
  
  // Error cases
  http.post('/api/deals/999/process-payment/', () => {
    return HttpResponse.json(
      { error: 'Deal not found' },
      { status: 404 }
    );
  }),
];
```

```javascript
// mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

```javascript
// setupTests.js
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

## Performance Testing

### Load Testing with k6

```javascript
// k6-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% failures
  },
};

const BASE_URL = 'http://localhost:8000/api';
let authToken;

export function setup() {
  // Login once
  const loginRes = http.post(`${BASE_URL}/auth/login/`, JSON.stringify({
    username: 'test@example.com',
    password: 'password',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  authToken = loginRes.json('access');
  return { token: authToken };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };
  
  // Get financial terms
  let res = http.get(`${BASE_URL}/deals/123/financial-terms/`, { headers });
  check(res, {
    'financial terms status is 200': (r) => r.status === 200,
    'has total_price': (r) => r.json('total_price') !== undefined,
  });
  
  sleep(1);
  
  // Get payment schedule
  res = http.get(`${BASE_URL}/deals/123/payment-schedule/`, { headers });
  check(res, {
    'payment schedule status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
}
```

Run test:
```bash
k6 run k6-load-test.js
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: API Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Start API server
        run: |
          npm run build
          npm start &
          sleep 10
      
      - name: Run integration tests
        run: npm run test:integration
        env:
          API_URL: http://localhost:8000
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Additional Resources

- [Financial API Reference](financial-api.md)
- [Integration Guide](integration-guide.md)
- [OpenAPI Specification](openapi.yaml)

---

**Last Updated**: December 20, 2024
