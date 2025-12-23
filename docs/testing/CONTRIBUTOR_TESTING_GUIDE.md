# Contributor Testing Guide

Guide for contributors on running tests, writing new tests, and contributing to the Nzila Exports test suite.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Running Tests](#running-tests)
3. [Writing New Tests](#writing-new-tests)
4. [Test Coverage](#test-coverage)
5. [Contributing Guidelines](#contributing-guidelines)
6. [Pull Request Checklist](#pull-request-checklist)

---

## Getting Started

### Prerequisites

Before running tests, ensure you have:

1. **Python Environment Set Up**
   ```bash
   # Activate virtual environment
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Dependencies Installed**
   ```bash
   # Install test dependencies
   pip install -r requirements.txt
   ```

3. **Database Configured**
   ```bash
   # Run migrations
   python manage.py migrate
   ```

### Test Directory Structure

```
tests/
├── __init__.py
├── factories/                 # Test data factories
│   ├── __init__.py
│   ├── deal_factories.py
│   ├── vehicle_factories.py
│   └── user_factories.py
├── unit/                      # Unit tests
│   ├── __init__.py
│   ├── test_financial_logic.py
│   ├── test_financial_serializers.py
│   └── test_models.py
├── integration/               # Integration tests
│   ├── __init__.py
│   ├── test_financial_api.py
│   └── test_financial_api_errors.py
└── performance/               # Performance tests
    ├── __init__.py
    └── test_financial_api_performance.py
```

---

## Running Tests

### Run All Tests

```bash
# Run entire test suite
python manage.py test

# With verbose output
python manage.py test --verbosity=2
```

### Run Specific Test Modules

```bash
# Run unit tests only
python manage.py test tests.unit

# Run integration tests only
python manage.py test tests.integration

# Run performance tests only
python manage.py test tests.performance

# Run specific test file
python manage.py test tests.unit.test_financial_logic
```

### Run Specific Test Classes

```bash
# Run specific test class
python manage.py test tests.unit.test_financial_logic.FinancingCalculationTest

# Run specific test method
python manage.py test tests.unit.test_financial_logic.FinancingCalculationTest.test_calculate_monthly_payment_standard_terms
```

### Running Tests in Parallel

```bash
# Run tests in parallel (faster)
python manage.py test --parallel

# Specify number of parallel processes
python manage.py test --parallel=4
```

### Other Useful Options

```bash
# Keep test database (faster for repeated runs)
python manage.py test --keepdb

# Show timing for slowest tests
python manage.py test --timing

# Stop on first failure
python manage.py test --failfast

# Run with debug mode
python manage.py test --debug-mode
```

### Running Tests with Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# View coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

---

## Writing New Tests

### Step 1: Choose Test Location

Decide where your test belongs:

- **Unit tests** (`tests/unit/`): Test individual functions, methods, or classes
  - Example: Testing `calculate_monthly_payment()` function
  - Example: Testing `DealSerializer.validate()` method

- **Integration tests** (`tests/integration/`): Test multiple components working together
  - Example: Testing API endpoints with database interactions
  - Example: Testing payment processing workflow

- **Performance tests** (`tests/performance/`): Test speed and efficiency
  - Example: Testing API response times
  - Example: Testing database query counts

### Step 2: Create Test File

```python
"""
tests/unit/test_my_feature.py

Tests for my feature functionality.
"""
from django.test import TestCase
from decimal import Decimal

from myapp.models import MyModel
from myapp.logic import my_function
from tests.factories import MyModelFactory


class MyFeatureTest(TestCase):
    """Tests for my feature."""
    
    def setUp(self):
        """Set up test data before each test."""
        self.obj = MyModelFactory()
    
    def test_my_feature_works(self):
        """Test that my feature works as expected."""
        # Arrange
        input_value = 'test'
        
        # Act
        result = my_function(input_value)
        
        # Assert
        self.assertEqual(result, 'expected_output')
```

### Step 3: Write Unit Tests

**Template for Unit Tests:**

```python
from django.test import TestCase
from decimal import Decimal

from deals.logic.financial_calculations import calculate_balance
from tests.factories import DealFactory


class CalculateBalanceTest(TestCase):
    """Tests for calculate_balance function."""
    
    def test_calculate_balance_no_payments(self):
        """Test balance calculation with no payments made."""
        # Arrange
        deal = DealFactory(
            total_price=Decimal('45000.00'),
            amount_paid=Decimal('0.00')
        )
        
        # Act
        result = calculate_balance(deal)
        
        # Assert
        self.assertEqual(result['balance'], Decimal('45000.00'))
        self.assertEqual(result['percentage_paid'], Decimal('0.00'))
    
    def test_calculate_balance_partial_payment(self):
        """Test balance calculation with partial payment."""
        # Arrange
        deal = DealFactory(
            total_price=Decimal('45000.00'),
            amount_paid=Decimal('15000.00')
        )
        
        # Act
        result = calculate_balance(deal)
        
        # Assert
        self.assertEqual(result['balance'], Decimal('30000.00'))
        self.assertEqual(result['percentage_paid'], Decimal('33.33'))
    
    def test_calculate_balance_fully_paid(self):
        """Test balance calculation when fully paid."""
        # Arrange
        deal = DealFactory(
            total_price=Decimal('45000.00'),
            amount_paid=Decimal('45000.00')
        )
        
        # Act
        result = calculate_balance(deal)
        
        # Assert
        self.assertEqual(result['balance'], Decimal('0.00'))
        self.assertEqual(result['percentage_paid'], Decimal('100.00'))
```

### Step 4: Write Integration Tests

**Template for API Integration Tests:**

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal

from tests.factories import DealFactory, UserFactory


class DealAPITest(APITestCase):
    """Integration tests for Deal API endpoints."""
    
    def setUp(self):
        """Set up test client and authenticate."""
        self.client = self.client_class()
        self.user = UserFactory(role='buyer')
        self.client.force_authenticate(user=self.user)
        
        self.deal = DealFactory(buyer=self.user)
        self.url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
    
    def test_get_financial_terms_success(self):
        """Test successful retrieval of financial terms."""
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.deal.id)
        self.assertIn('total_price', response.data)
        self.assertIn('amount_paid', response.data)
    
    def test_get_financial_terms_unauthorized(self):
        """Test that unauthorized requests are rejected."""
        # Arrange
        self.client.force_authenticate(user=None)
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_financial_terms_wrong_user(self):
        """Test that users cannot access other users' deals."""
        # Arrange
        other_user = UserFactory(role='buyer')
        self.client.force_authenticate(user=other_user)
        
        # Act
        response = self.client.get(self.url)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

### Step 5: Write Performance Tests

**Template for Performance Tests:**

```python
import time
from django.test import TestCase
from rest_framework.test import APIClient

from tests.factories import DealFactory, UserFactory


class APIPerformanceTest(TestCase):
    """Performance tests for API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.deal = DealFactory()
    
    def test_financial_terms_response_time(self):
        """Test that financial terms endpoint responds quickly."""
        # Warm up
        self.client.get(f'/api/deals/{self.deal.id}/financial-terms/')
        
        # Measure
        start_time = time.time()
        response = self.client.get(f'/api/deals/{self.deal.id}/financial-terms/')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertLess(
            response_time_ms,
            200,  # Target: 200ms
            f"Response time {response_time_ms:.2f}ms exceeds target"
        )
    
    def test_no_n_plus_one_queries(self):
        """Test that endpoint doesn't have N+1 query problems."""
        # Create test data
        DealFactory.create_batch(10)
        
        # Measure query count
        with self.assertNumQueries(5):  # Expected: 5 queries
            response = self.client.get('/api/deals/')
            self.assertEqual(response.status_code, 200)
```

---

## Test Coverage

### Checking Coverage

```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# View coverage report
coverage report

# Generate HTML report
coverage html

# Open in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Overall coverage**: 80% minimum
- **New code**: 100% coverage for new features
- **Critical paths**: 100% coverage for financial logic, payment processing

### What to Test

#### ✅ DO Test

- Business logic and calculations
- API endpoints (success and error cases)
- Model methods and properties
- Serializer validation
- Permissions and authentication
- Error handling
- Edge cases

#### ❌ DON'T Test

- Django framework code (it's already tested)
- Third-party libraries (assume they work)
- Database migrations
- Static settings
- Simple getters/setters without logic

---

## Contributing Guidelines

### Before Writing Tests

1. **Check existing tests** - Don't duplicate existing tests
2. **Read the code** - Understand what you're testing
3. **Follow patterns** - Use existing test patterns
4. **Use factories** - Don't create test data manually

### Test Quality Standards

#### 1. Clear Test Names

```python
# ✅ GOOD - Descriptive name
def test_calculate_financing_returns_correct_monthly_payment(self):
    """Test that financing calculation returns accurate monthly payment."""
    pass

# ❌ BAD - Vague name
def test_financing(self):
    pass
```

#### 2. Arrange-Act-Assert Pattern

```python
def test_example(self):
    """Test description."""
    # Arrange - Set up test data
    deal = DealFactory(total_price=Decimal('45000.00'))
    
    # Act - Perform the action
    result = calculate_balance(deal)
    
    # Assert - Verify the outcome
    self.assertEqual(result['balance'], Decimal('45000.00'))
```

#### 3. Test One Thing

```python
# ✅ GOOD - Tests one specific thing
def test_payment_updates_amount_paid(self):
    """Test that processing payment updates amount_paid field."""
    pass

def test_payment_updates_balance(self):
    """Test that processing payment updates balance."""
    pass

# ❌ BAD - Tests multiple things
def test_payment_processing(self):
    """Test payment processing (does too much)."""
    # Tests amount_paid, balance, status, notifications...
    pass
```

#### 4. Independent Tests

```python
# ✅ GOOD - Tests are independent
class MyTest(TestCase):
    def setUp(self):
        # Fresh data for each test
        self.deal = DealFactory()
    
    def test_one(self):
        # Uses fresh deal
        pass
    
    def test_two(self):
        # Uses different fresh deal
        pass

# ❌ BAD - Tests depend on each other
class MyTest(TestCase):
    def test_one(self):
        self.deal = DealFactory()
    
    def test_two(self):
        # Assumes test_one ran first!
        self.deal.status = 'active'
```

#### 5. Meaningful Assertions

```python
# ✅ GOOD - Clear assertion with message
self.assertEqual(
    result['balance'],
    Decimal('45000.00'),
    "Balance calculation incorrect"
)

# ✅ GOOD - Multiple specific assertions
self.assertEqual(response.status_code, status.HTTP_200_OK)
self.assertIn('total_price', response.data)
self.assertEqual(response.data['status'], 'active')

# ❌ BAD - Generic assertion
self.assertTrue(result)
```

### Code Review Standards

Tests must pass code review before merging. Reviewers check for:

- [ ] Tests follow naming conventions
- [ ] Tests use factories (not manual object creation)
- [ ] Tests are independent
- [ ] Tests use AAA pattern
- [ ] Tests have clear docstrings
- [ ] Tests cover success and error cases
- [ ] Tests have meaningful assertions
- [ ] Tests run quickly (< 1s per test for unit tests)
- [ ] No commented-out code
- [ ] No print statements (use logging if needed)

---

## Pull Request Checklist

Before submitting a PR with tests:

### Required Checks

- [ ] All tests pass locally
  ```bash
  python manage.py test
  ```

- [ ] New code has test coverage
  ```bash
  coverage run --source='.' manage.py test
  coverage report
  ```

- [ ] Tests follow project conventions
  - [ ] Located in correct directory
  - [ ] Follow naming conventions
  - [ ] Use factories for test data
  - [ ] Include docstrings

- [ ] No test warnings or deprecation messages

- [ ] Tests run in reasonable time
  - [ ] Unit tests: < 1s each
  - [ ] Integration tests: < 5s each
  - [ ] Performance tests: < 10s each

### Recommended Checks

- [ ] Tests cover edge cases
- [ ] Tests cover error conditions
- [ ] Added tests for bug fixes (regression tests)
- [ ] Updated existing tests if behavior changed
- [ ] Removed or updated obsolete tests

### Documentation

- [ ] Updated relevant documentation
- [ ] Added docstrings to test classes and methods
- [ ] Explained complex test setup if needed

### Performance

- [ ] No N+1 query problems
- [ ] Efficient test data creation
- [ ] No unnecessary database queries

---

## Common Patterns

### Testing Business Logic

```python
from django.test import TestCase
from deals.logic import calculate_financing
from tests.factories import DealFactory

class FinancingLogicTest(TestCase):
    """Tests for financing calculation logic."""
    
    def test_financing_calculation(self):
        """Test financing calculation with standard terms."""
        deal = DealFactory(total_price=Decimal('45000.00'))
        
        result = calculate_financing(
            principal=deal.total_price,
            interest_rate=Decimal('8.5'),
            term_months=36
        )
        
        self.assertAlmostEqual(
            result['monthly_payment'],
            Decimal('1424.84'),
            places=2
        )
```

### Testing API Endpoints

```python
from rest_framework.test import APITestCase
from rest_framework import status
from tests.factories import DealFactory, UserFactory

class DealAPITest(APITestCase):
    """Tests for Deal API."""
    
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_list_deals(self):
        """Test listing deals."""
        DealFactory.create_batch(3, buyer=self.user)
        
        response = self.client.get('/api/deals/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
```

### Testing Permissions

```python
def test_buyer_can_view_own_deal(self):
    """Test that buyer can view their own deal."""
    deal = DealFactory(buyer=self.user)
    url = f'/api/deals/{deal.id}/'
    
    response = self.client.get(url)
    
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_buyer_cannot_view_other_deal(self):
    """Test that buyer cannot view another buyer's deal."""
    other_deal = DealFactory()  # Different buyer
    url = f'/api/deals/{other_deal.id}/'
    
    response = self.client.get(url)
    
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

### Testing Serializers

```python
from django.test import TestCase
from deals.api.serializers import DealSerializer
from tests.factories import DealFactory

class DealSerializerTest(TestCase):
    """Tests for Deal serializer."""
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer includes all expected fields."""
        deal = DealFactory()
        serializer = DealSerializer(deal)
        
        expected_fields = ['id', 'deal_number', 'total_price', 'status']
        for field in expected_fields:
            self.assertIn(field, serializer.data)
    
    def test_serializer_validation(self):
        """Test serializer validation."""
        invalid_data = {
            'total_price': '-100.00'  # Invalid
        }
        
        serializer = DealSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('total_price', serializer.errors)
```

---

## Getting Help

### Resources

- **Internal Documentation**:
  - [Test Patterns and Conventions](TEST_PATTERNS_AND_CONVENTIONS.md)
  - [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
  - [Factory Usage Guide](FACTORY_USAGE_GUIDE.md)

- **External Documentation**:
  - [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
  - [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
  - [Factory Boy Documentation](https://factoryboy.readthedocs.io/)

### Getting Help from Team

1. **Check existing tests** - Look for similar tests
2. **Read documentation** - Check internal docs first
3. **Ask in team chat** - Quick questions
4. **Schedule pairing session** - Complex issues
5. **Create discussion thread** - For architectural decisions

### Reporting Issues

If you find issues with tests:

1. **Check if it's a known issue**
2. **Try to reproduce** the issue
3. **Create minimal test case**
4. **Report with**:
   - Test command used
   - Error message
   - Expected vs actual behavior
   - Environment details

---

## Examples

### Complete Test Example

```python
"""
tests/unit/test_payment_processing.py

Tests for payment processing functionality.
"""
from django.test import TestCase
from decimal import Decimal
from django.core.exceptions import ValidationError

from deals.logic.payment_processing import process_payment
from tests.factories import DealFactory, PaymentFactory


class ProcessPaymentTest(TestCase):
    """Tests for process_payment function."""
    
    def setUp(self):
        """Set up test data before each test."""
        self.deal = DealFactory(
            total_price=Decimal('45000.00'),
            amount_paid=Decimal('0.00')
        )
    
    def test_process_payment_updates_amount_paid(self):
        """Test that processing payment updates amount_paid."""
        # Arrange
        payment_amount = Decimal('15000.00')
        
        # Act
        result = process_payment(self.deal, payment_amount)
        
        # Assert
        self.assertEqual(result['amount_paid'], Decimal('15000.00'))
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.amount_paid, Decimal('15000.00'))
    
    def test_process_payment_calculates_balance(self):
        """Test that processing payment calculates remaining balance."""
        # Arrange
        payment_amount = Decimal('15000.00')
        
        # Act
        result = process_payment(self.deal, payment_amount)
        
        # Assert
        self.assertEqual(result['balance'], Decimal('30000.00'))
    
    def test_process_payment_rejects_negative_amount(self):
        """Test that negative payment amounts are rejected."""
        # Arrange
        payment_amount = Decimal('-100.00')
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            process_payment(self.deal, payment_amount)
        
        self.assertIn('must be positive', str(context.exception))
    
    def test_process_payment_rejects_overpayment(self):
        """Test that overpayments are rejected."""
        # Arrange
        payment_amount = Decimal('50000.00')  # More than total_price
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            process_payment(self.deal, payment_amount)
        
        self.assertIn('exceeds remaining balance', str(context.exception))
    
    def test_process_multiple_payments(self):
        """Test processing multiple payments."""
        # Act
        process_payment(self.deal, Decimal('15000.00'))
        process_payment(self.deal, Decimal('10000.00'))
        process_payment(self.deal, Decimal('20000.00'))
        
        # Assert
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.amount_paid, Decimal('45000.00'))
```

---

**Last Updated**: December 20, 2024  
**Version**: 1.0

**Questions?** Contact the development team or check our internal documentation.
