# Test Patterns and Conventions

Comprehensive guide to test patterns, conventions, and best practices used in the Nzila Exports testing infrastructure.

---

## Table of Contents

1. [Test Organization](#test-organization)
2. [Naming Conventions](#naming-conventions)
3. [Test Class Patterns](#test-class-patterns)
4. [Fixture Patterns](#fixture-patterns)
5. [Assertion Patterns](#assertion-patterns)
6. [Data Factory Patterns](#data-factory-patterns)
7. [API Testing Patterns](#api-testing-patterns)
8. [Performance Testing Patterns](#performance-testing-patterns)

---

## Test Organization

### Directory Structure

```
tests/
├── __init__.py
├── unit/                          # Unit tests
│   ├── __init__.py
│   ├── test_financial_logic.py   # Business logic tests
│   ├── test_financial_serializers.py
│   └── test_models.py
├── integration/                   # Integration tests
│   ├── __init__.py
│   ├── test_financial_api.py     # API endpoint tests
│   └── test_financial_api_errors.py
├── performance/                   # Performance tests
│   ├── __init__.py
│   └── test_financial_api_performance.py
└── factories/                     # Test data factories
    ├── __init__.py
    ├── deal_factories.py
    ├── vehicle_factories.py
    └── user_factories.py
```

### Test File Organization

Each test file should follow this structure:

```python
"""
Brief description of what this test file covers.

This module contains tests for [component/feature].
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from decimal import Decimal

# Standard library imports first
import json
from datetime import datetime

# Django imports
from django.contrib.auth import get_user_model
from django.db import transaction

# Third-party imports
from rest_framework import status

# Local imports
from deals.models import Deal, DealFinancialTerms
from vehicles.models import Vehicle

# Test factories
from tests.factories import (
    DealFactory,
    VehicleFactory,
    UserFactory,
)

User = get_user_model()


class TestClassName(TestCase):
    """
    Test suite for [component].
    
    Tests cover:
    - Expected behavior
    - Edge cases
    - Error handling
    """
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase."""
        # Data that doesn't change across tests
        pass
    
    def setUp(self):
        """Set up data before each test method."""
        # Fresh data for each test
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        # Usually not needed with Django's test database
        pass
    
    def test_expected_behavior(self):
        """Test that [feature] works as expected."""
        # Arrange
        # Act
        # Assert
        pass
```

---

## Naming Conventions

### Test File Naming

- **Unit tests**: `test_<module_name>.py`
  - Example: `test_financial_logic.py`
  - Example: `test_models.py`

- **Integration tests**: `test_<feature>_<component>.py`
  - Example: `test_financial_api.py`
  - Example: `test_payment_integration.py`

- **Performance tests**: `test_<feature>_performance.py`
  - Example: `test_financial_api_performance.py`

### Test Class Naming

- **Pattern**: `<Component><Aspect>Test`
- **Examples**:
  - `FinancialLogicCalculationTest`
  - `DealSerializerValidationTest`
  - `PaymentAPIPermissionsTest`

### Test Method Naming

Use descriptive names that explain the scenario and expected outcome:

```python
# ✅ GOOD - Clear, descriptive names
def test_calculate_financing_returns_correct_monthly_payment(self):
    """Test that financing calculation returns accurate monthly payment."""
    pass

def test_process_payment_fails_when_amount_exceeds_balance(self):
    """Test that payment processing fails when amount exceeds remaining balance."""
    pass

def test_apply_financing_requires_positive_interest_rate(self):
    """Test that financing application requires interest rate > 0."""
    pass

# ❌ BAD - Vague, unclear names
def test_financing(self):
    pass

def test_payment_error(self):
    pass

def test_validation(self):
    pass
```

### Naming Pattern Template

```python
def test_<action>_<condition>_<expected_result>(self):
    """
    Test that <action> <expected_result> when <condition>.
    
    Additional context or business rule explanation.
    """
    pass
```

---

## Test Class Patterns

### Pattern 1: Single Responsibility Tests

Each test class should focus on one aspect of functionality:

```python
class FinancingCalculationTest(TestCase):
    """Tests for financing calculation logic only."""
    
    def test_monthly_payment_calculation_standard_terms(self):
        """Test monthly payment with standard 36-month term."""
        pass
    
    def test_monthly_payment_calculation_zero_interest(self):
        """Test monthly payment with 0% interest rate."""
        pass


class FinancingValidationTest(TestCase):
    """Tests for financing validation rules only."""
    
    def test_rejects_negative_interest_rate(self):
        """Test that negative interest rates are rejected."""
        pass
    
    def test_rejects_term_under_12_months(self):
        """Test that terms under 12 months are rejected."""
        pass
```

### Pattern 2: Arrange-Act-Assert (AAA)

Structure every test using the AAA pattern:

```python
def test_process_payment_updates_balance(self):
    """Test that processing payment updates the deal balance."""
    # Arrange - Set up test data
    deal = DealFactory(
        total_price=Decimal('45000.00'),
        amount_paid=Decimal('15000.00')
    )
    payment_amount = Decimal('5000.00')
    
    # Act - Perform the action
    result = process_payment(deal, payment_amount)
    
    # Assert - Verify the outcome
    self.assertEqual(result['amount_paid'], Decimal('20000.00'))
    self.assertEqual(result['amount_remaining'], Decimal('25000.00'))
    self.assertEqual(result['payment_progress'], Decimal('44.44'))
```

### Pattern 3: Test Data Isolation

Each test should be independent:

```python
class PaymentProcessingTest(TestCase):
    """Tests for payment processing."""
    
    def setUp(self):
        """Create fresh test data for each test."""
        # Each test gets its own deal
        self.deal = DealFactory(
            total_price=Decimal('45000.00'),
            amount_paid=Decimal('0.00')
        )
    
    def test_first_payment(self):
        """Test processing first payment."""
        # This test doesn't affect other tests
        process_payment(self.deal, Decimal('15000.00'))
        self.assertEqual(self.deal.amount_paid, Decimal('15000.00'))
    
    def test_second_payment(self):
        """Test processing second payment."""
        # Starts with fresh deal from setUp
        process_payment(self.deal, Decimal('10000.00'))
        self.assertEqual(self.deal.amount_paid, Decimal('10000.00'))
```

### Pattern 4: Parametric Testing

Use subTest for testing multiple inputs:

```python
def test_financing_calculation_various_terms(self):
    """Test financing calculation with various term lengths."""
    test_cases = [
        (12, Decimal('3830.25')),   # 12 months
        (24, Decimal('1970.46')),   # 24 months
        (36, Decimal('1345.57')),   # 36 months
        (48, Decimal('1034.27')),   # 48 months
    ]
    
    for term_months, expected_payment in test_cases:
        with self.subTest(term_months=term_months):
            result = calculate_monthly_payment(
                principal=Decimal('45000.00'),
                interest_rate=Decimal('8.5'),
                term_months=term_months
            )
            self.assertAlmostEqual(
                result,
                expected_payment,
                places=2,
                msg=f"Failed for {term_months} months"
            )
```

---

## Fixture Patterns

### Pattern 1: Class-Level Fixtures

Use `setUpTestData` for data that doesn't change:

```python
class DealFinancialTermsTest(TestCase):
    """Tests for deal financial terms."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class."""
        # Created once, shared across all tests (read-only)
        cls.buyer = UserFactory(role='buyer')
        cls.seller = UserFactory(role='seller')
        cls.vehicle = VehicleFactory(price=Decimal('45000.00'))
        cls.currency = CurrencyFactory(code='USD')
    
    def setUp(self):
        """Set up mutable data before each test."""
        # Created fresh for each test
        self.deal = DealFactory(
            buyer=self.buyer,
            seller=self.seller,
            vehicle=self.vehicle,
            total_price=self.vehicle.price
        )
```

### Pattern 2: Factory Fixtures

Use factories for test data creation:

```python
class PaymentMilestoneTest(TestCase):
    """Tests for payment milestones."""
    
    def setUp(self):
        """Create test data using factories."""
        # Factories handle complex object creation
        self.deal = DealFactory(
            status='active',
            total_price=Decimal('45000.00')
        )
        
        # Create related objects easily
        self.milestone = PaymentMilestoneFactory(
            deal=self.deal,
            amount_due=Decimal('15000.00'),
            status='pending'
        )
```

### Pattern 3: Fixture Methods

Create reusable fixture methods:

```python
class FinancingTest(TestCase):
    """Tests for financing functionality."""
    
    def create_deal_with_payment_history(self, payments_count=3):
        """Helper method to create deal with payment history."""
        deal = DealFactory()
        for i in range(payments_count):
            PaymentFactory(
                deal=deal,
                amount=Decimal('5000.00')
            )
        return deal
    
    def test_financing_with_existing_payments(self):
        """Test applying financing to deal with payments."""
        deal = self.create_deal_with_payment_history(payments_count=2)
        # Test continues...
```

---

## Assertion Patterns

### Pattern 1: Specific Assertions

Use the most specific assertion available:

```python
# ✅ GOOD - Specific assertions
self.assertEqual(result, expected_value)
self.assertIsNone(value)
self.assertTrue(condition)
self.assertIn(item, collection)
self.assertGreater(value, minimum)

# ❌ BAD - Generic assertions
self.assertTrue(result == expected_value)  # Use assertEqual
self.assertTrue(value is None)             # Use assertIsNone
self.assertEqual(True, condition)          # Use assertTrue
```

### Pattern 2: Decimal Comparison

For financial calculations, use appropriate decimal comparison:

```python
# ✅ GOOD - Proper decimal comparison
self.assertEqual(
    result,
    Decimal('15000.00'),
    "Payment amount should be exactly $15,000.00"
)

# For calculated values with rounding
self.assertAlmostEqual(
    monthly_payment,
    Decimal('1345.57'),
    places=2,
    msg="Monthly payment calculation incorrect"
)

# ❌ BAD - Float comparison
self.assertEqual(result, 15000.0)  # Avoid floats for money
```

### Pattern 3: Exception Assertions

Test exception raising properly:

```python
# ✅ GOOD - Proper exception testing
def test_negative_payment_raises_validation_error(self):
    """Test that negative payment amounts raise ValidationError."""
    deal = DealFactory()
    
    with self.assertRaises(ValidationError) as context:
        process_payment(deal, Decimal('-100.00'))
    
    self.assertIn('must be positive', str(context.exception))

# ✅ GOOD - Multiple exception scenarios
def test_invalid_financing_parameters(self):
    """Test various invalid financing parameters."""
    deal = DealFactory()
    
    # Test negative interest rate
    with self.assertRaises(ValidationError):
        apply_financing(deal, interest_rate=Decimal('-5.0'))
    
    # Test invalid term
    with self.assertRaises(ValidationError):
        apply_financing(deal, term_months=6)
```

### Pattern 4: Collection Assertions

Properly test collections:

```python
# ✅ GOOD - Comprehensive collection testing
def test_payment_schedule_milestones(self):
    """Test that payment schedule contains expected milestones."""
    schedule = get_payment_schedule(self.deal)
    
    # Test count
    self.assertEqual(len(schedule['milestones']), 3)
    
    # Test presence
    milestone_names = [m['name'] for m in schedule['milestones']]
    self.assertIn('Initial Deposit', milestone_names)
    
    # Test order
    self.assertEqual(schedule['milestones'][0]['name'], 'Initial Deposit')
    
    # Test all items
    for milestone in schedule['milestones']:
        self.assertIsInstance(milestone['amount_due'], Decimal)
        self.assertIn(milestone['status'], ['paid', 'pending', 'overdue'])
```

---

## Data Factory Patterns

### Pattern 1: Basic Factory Usage

```python
# Simple creation
deal = DealFactory()

# Override specific fields
deal = DealFactory(
    status='active',
    total_price=Decimal('50000.00')
)

# Create multiple instances
deals = DealFactory.create_batch(5)

# Create with related objects
deal = DealFactory(
    buyer=UserFactory(email='buyer@example.com'),
    vehicle=VehicleFactory(make='Toyota')
)
```

### Pattern 2: Factory Traits

Use factory traits for common configurations:

```python
class DealFactory(factory.django.DjangoModelFactory):
    """Factory for Deal model."""
    
    class Meta:
        model = Deal
    
    # Base fields
    deal_number = factory.Sequence(lambda n: f'DEAL-{n:05d}')
    status = 'pending'
    
    class Params:
        # Trait for active deal
        active = factory.Trait(
            status='active',
            amount_paid=Decimal('15000.00')
        )
        
        # Trait for completed deal
        completed = factory.Trait(
            status='completed',
            amount_paid=factory.SelfAttribute('total_price')
        )

# Usage
active_deal = DealFactory(active=True)
completed_deal = DealFactory(completed=True)
```

### Pattern 3: Factory Relationships

Handle complex relationships:

```python
def test_deal_with_full_relationship_tree(self):
    """Test creating deal with all related objects."""
    deal = DealFactory(
        # Create buyer with profile
        buyer=UserFactory(
            profile__country='US',
            profile__verified=True
        ),
        # Create vehicle with full details
        vehicle=VehicleFactory(
            make='Toyota',
            model='Land Cruiser',
            condition__name='Excellent'
        ),
        # Create financial terms
        financial_terms__total_price=Decimal('45000.00'),
        financial_terms__amount_paid=Decimal('15000.00')
    )
    
    self.assertEqual(deal.buyer.profile.country, 'US')
    self.assertEqual(deal.vehicle.make, 'Toyota')
```

---

## API Testing Patterns

### Pattern 1: REST API Test Structure

```python
class FinancialTermsAPITest(APITestCase):
    """Tests for financial terms API endpoint."""
    
    def setUp(self):
        """Set up test data and authenticate."""
        self.client = APIClient()
        self.user = UserFactory(role='buyer')
        self.client.force_authenticate(user=self.user)
        
        self.deal = DealFactory(buyer=self.user)
        self.url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
    
    def test_get_financial_terms_success(self):
        """Test successful retrieval of financial terms."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.deal.id)
        self.assertIn('total_price', response.data)
    
    def test_get_financial_terms_unauthorized(self):
        """Test that unauthorized requests are rejected."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### Pattern 2: POST Request Testing

```python
def test_process_payment_success(self):
    """Test successful payment processing."""
    url = reverse('deal-process-payment', kwargs={'pk': self.deal.id})
    data = {
        'amount': '5000.00'
    }
    
    response = self.client.post(url, data, format='json')
    
    # Assert response
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['amount_paid'], '5000.00')
    
    # Assert database changes
    self.deal.refresh_from_db()
    self.assertEqual(self.deal.amount_paid, Decimal('5000.00'))

def test_process_payment_validation_error(self):
    """Test payment validation errors."""
    url = reverse('deal-process-payment', kwargs={'pk': self.deal.id})
    data = {
        'amount': '-100.00'  # Invalid amount
    }
    
    response = self.client.post(url, data, format='json')
    
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn('error', response.data)
```

### Pattern 3: Permission Testing

```python
def test_permissions_buyer_can_view_own_deal(self):
    """Test that buyer can view their own deal."""
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_permissions_buyer_cannot_view_other_deal(self):
    """Test that buyer cannot view another buyer's deal."""
    other_deal = DealFactory()  # Different buyer
    url = reverse('deal-financial-terms', kwargs={'pk': other_deal.id})
    
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

def test_permissions_seller_can_view_their_deal(self):
    """Test that seller can view deals they are selling."""
    self.client.force_authenticate(user=self.deal.seller)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
```

---

## Performance Testing Patterns

### Pattern 1: Response Time Testing

```python
from django.test.utils import override_settings
import time

class APIResponseTimeTest(APITestCase):
    """Tests for API response times."""
    
    def setUp(self):
        """Set up test data."""
        self.client.force_authenticate(user=UserFactory())
        self.deal = DealFactory()
        self.url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
    
    def test_financial_terms_response_time(self):
        """Test that financial terms endpoint responds within target time."""
        start_time = time.time()
        response = self.client.get(self.url)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(
            response_time_ms,
            200,  # 200ms target
            f"Response time {response_time_ms:.2f}ms exceeds 200ms target"
        )
```

### Pattern 2: Query Count Testing

```python
from django.test.utils import override_settings
from django.db import connection
from django.test import TestCase

class QueryEfficiencyTest(TestCase):
    """Tests for database query efficiency."""
    
    def test_financial_terms_query_count(self):
        """Test that financial terms uses efficient queries."""
        deal = DealFactory()
        
        with self.assertNumQueries(5):  # Expected query count
            # Action that should use exactly 5 queries
            get_financial_terms(deal)
    
    def test_no_n_plus_one_queries(self):
        """Test that list endpoint doesn't have N+1 queries."""
        # Create test data
        DealFactory.create_batch(10)
        
        with self.assertNumQueries(3):  # Should be constant
            # Fetch deals with related data
            deals = Deal.objects.select_related('buyer', 'vehicle').all()
            for deal in deals:
                _ = deal.buyer.email
                _ = deal.vehicle.make
```

### Pattern 3: Load Testing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class LoadHandlingTest(APITestCase):
    """Tests for concurrent load handling."""
    
    def test_concurrent_payment_processing(self):
        """Test that API handles concurrent requests correctly."""
        deal = DealFactory(total_price=Decimal('100000.00'))
        url = reverse('deal-process-payment', kwargs={'pk': deal.id})
        
        def make_payment():
            """Make a payment request."""
            client = APIClient()
            client.force_authenticate(user=deal.buyer)
            return client.post(url, {'amount': '1000.00'}, format='json')
        
        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_payment) for _ in range(20)]
            responses = [f.result() for f in as_completed(futures)]
        
        # Verify all succeeded
        success_count = sum(1 for r in responses if r.status_code == 200)
        self.assertGreater(success_count, 15, "Too many concurrent failures")
```

---

## Best Practices Summary

### ✅ DO

1. **Use descriptive test names** that explain the scenario
2. **Follow AAA pattern** (Arrange, Act, Assert)
3. **Test one thing per test** (single responsibility)
4. **Use appropriate assertions** (assertEqual, assertIn, etc.)
5. **Use factories** for test data creation
6. **Test edge cases** and error conditions
7. **Add docstrings** to test methods
8. **Keep tests independent** (no test order dependencies)
9. **Use setUp and tearDown** appropriately
10. **Mock external dependencies** (APIs, services)

### ❌ DON'T

1. **Don't test Django/library code** (assume it works)
2. **Don't use sleep()** in tests (use proper synchronization)
3. **Don't hardcode IDs** (use factories and variables)
4. **Don't share mutable state** between tests
5. **Don't test implementation details** (test behavior)
6. **Don't ignore test failures** (fix or document)
7. **Don't write long tests** (split into multiple tests)
8. **Don't use print()** for debugging (use logging or debugger)
9. **Don't skip tests** without good reason and documentation
10. **Don't duplicate test code** (use helper methods/fixtures)

---

## Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)

---

**Last Updated**: December 20, 2024  
**Version**: 1.0
