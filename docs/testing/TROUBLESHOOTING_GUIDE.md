# Testing Troubleshooting Guide

Common testing issues, solutions, and debugging strategies for the Nzila Exports test suite.

---

## Table of Contents

1. [Test Database Issues](#test-database-issues)
2. [Factory and Fixture Issues](#factory-and-fixture-issues)
3. [API Test Issues](#api-test-issues)
4. [Performance Test Issues](#performance-test-issues)
5. [Debugging Strategies](#debugging-strategies)
6. [Common Error Messages](#common-error-messages)

---

## Test Database Issues

### Issue: Tests Creating Data in Production Database

**Symptoms:**
```bash
# Tests creating real data
# Database not being reset between tests
```

**Cause:** Not using Django's test database properly

**Solution:**
```python
# ✅ Use Django's TestCase base classes
from django.test import TestCase  # Creates test database
from rest_framework.test import APITestCase  # For API tests

class MyTest(TestCase):  # Automatically uses test database
    def test_something(self):
        pass

# ❌ DON'T use unittest.TestCase directly
import unittest
class MyTest(unittest.TestCase):  # Uses real database!
    pass
```

### Issue: Database Locked Errors

**Symptoms:**
```bash
django.db.utils.OperationalError: database is locked
```

**Cause:** SQLite database contention (common with SQLite in tests)

**Solution 1: Run tests serially**
```bash
# Run tests without parallel execution
python manage.py test --parallel=1
```

**Solution 2: Use PostgreSQL for tests**
```python
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_nzila_db',
        # ... other settings
    }
}
```

**Solution 3: Use in-memory SQLite**
```python
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database
    }
}
```

### Issue: Test Database Not Clearing Between Tests

**Symptoms:**
```python
# Second test fails because first test's data exists
# Unexpected data in database
```

**Cause:** Using transactions incorrectly or not inheriting from TestCase

**Solution:**
```python
# ✅ GOOD - Each test gets clean database
class MyTest(TestCase):
    def test_one(self):
        User.objects.create(email='test@example.com')
        self.assertEqual(User.objects.count(), 1)
    
    def test_two(self):
        # Database is clean - no user from test_one
        self.assertEqual(User.objects.count(), 0)

# ❌ BAD - Using setUpClass incorrectly
class MyTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Data created here persists across ALL tests
        cls.user = User.objects.create(email='test@example.com')
    
    def test_one(self):
        # User exists
        pass
    
    def test_two(self):
        # Same user still exists (might cause issues)
        pass

# ✅ BETTER - Use setUpTestData for immutable data
class MyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Data created once, shared (read-only) across tests
        cls.user = User.objects.create(email='test@example.com')
    
    def setUp(self):
        # Fresh mutable data for each test
        self.deal = DealFactory()
```

### Issue: Migrations Not Applied in Tests

**Symptoms:**
```bash
django.db.utils.OperationalError: no such table: deals_deal
```

**Cause:** Test database not created properly

**Solution:**
```bash
# Recreate test database
python manage.py test --keepdb=False

# Or delete test database manually
rm db_test.sqlite3  # SQLite
# OR drop test database in PostgreSQL
```

---

## Factory and Fixture Issues

### Issue: Factory Creating Invalid Data

**Symptoms:**
```python
ValidationError: Invalid data created by factory
IntegrityError: Foreign key constraint failed
```

**Cause:** Factory not creating required related objects

**Solution:**
```python
# ❌ BAD - Missing required relationships
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    deal_number = factory.Sequence(lambda n: f'DEAL-{n}')
    # Missing buyer, seller, vehicle (required fields)

# ✅ GOOD - Create all required relationships
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    deal_number = factory.Sequence(lambda n: f'DEAL-{n:05d}')
    buyer = factory.SubFactory(UserFactory, role='buyer')
    seller = factory.SubFactory(UserFactory, role='seller')
    vehicle = factory.SubFactory(VehicleFactory)
    status = 'pending'
    total_price = factory.LazyAttribute(lambda obj: obj.vehicle.price)
```

### Issue: Circular Factory Dependencies

**Symptoms:**
```python
RecursionError: maximum recursion depth exceeded
```

**Cause:** Two factories creating each other

**Solution:**
```python
# ❌ BAD - Circular dependency
class UserFactory(factory.django.DjangoModelFactory):
    profile = factory.SubFactory(ProfileFactory)  # Creates Profile

class ProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)  # Creates User (CIRCULAR!)

# ✅ GOOD - Use RelatedFactory for reverse relationship
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    
    # Create profile after user is created
    profile = factory.RelatedFactory(
        'tests.factories.ProfileFactory',
        factory_related_name='user'
    )

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    
    user = factory.SubFactory(UserFactory)
    country = 'US'
```

### Issue: Factory Data Doesn't Match Model Constraints

**Symptoms:**
```python
IntegrityError: CHECK constraint failed
ValidationError: Ensure this value is greater than 0
```

**Cause:** Factory generating data that violates model constraints

**Solution:**
```python
# Model with constraints
class Deal(models.Model):
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_paid__lte=models.F('total_price')),
                name='amount_paid_lte_total_price'
            )
        ]

# ✅ GOOD - Factory respects constraints
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    total_price = Decimal('45000.00')
    amount_paid = Decimal('0.00')  # Always <= total_price
    
    class Params:
        # Trait for partially paid deal
        partially_paid = factory.Trait(
            amount_paid=factory.LazyAttribute(
                lambda obj: obj.total_price * Decimal('0.33')
            )
        )

# Usage
deal = DealFactory(partially_paid=True)
# amount_paid will be 33% of total_price (valid)
```

### Issue: Sequence Collisions in Factories

**Symptoms:**
```python
IntegrityError: UNIQUE constraint failed
```

**Cause:** Factory sequence not truly unique

**Solution:**
```python
# ❌ BAD - Might collide with existing data
class DealFactory(factory.django.DjangoModelFactory):
    deal_number = factory.Sequence(lambda n: f'DEAL-{n}')  # DEAL-1, DEAL-2...

# ✅ GOOD - Use unique sequence with timestamp
import uuid

class DealFactory(factory.django.DjangoModelFactory):
    deal_number = factory.LazyFunction(
        lambda: f'DEAL-{uuid.uuid4().hex[:8].upper()}'
    )
    # Generates: DEAL-A3F7B2C1, DEAL-9E4D1F8A, etc.

# ✅ ALTERNATIVE - Use Faker for realistic data
import factory.faker

class DealFactory(factory.django.DjangoModelFactory):
    deal_number = factory.Faker('bothify', text='DEAL-########')
    # Generates: DEAL-12345678, DEAL-87654321, etc.
```

---

## API Test Issues

### Issue: Authentication Errors in API Tests

**Symptoms:**
```python
AssertionError: 401 != 200
# {"detail": "Authentication credentials were not provided."}
```

**Cause:** Not authenticating test client

**Solution:**
```python
from rest_framework.test import APIClient

# ❌ BAD - No authentication
def test_api_endpoint(self):
    client = APIClient()
    response = client.get('/api/deals/')  # Returns 401

# ✅ GOOD - Force authenticate
def test_api_endpoint(self):
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    response = client.get('/api/deals/')  # Returns 200

# ✅ BETTER - Authenticate in setUp
class DealAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(role='buyer')
        self.client.force_authenticate(user=self.user)
    
    def test_get_deals(self):
        response = self.client.get('/api/deals/')
        self.assertEqual(response.status_code, 200)
```

### Issue: Permission Denied (403) Errors

**Symptoms:**
```python
AssertionError: 403 != 200
# {"detail": "You do not have permission to perform this action."}
```

**Cause:** User doesn't have required permissions

**Solution:**
```python
# ❌ BAD - User doesn't have right role
def test_admin_endpoint(self):
    user = UserFactory(role='buyer')  # Not admin!
    self.client.force_authenticate(user=user)
    response = self.client.get('/api/admin/users/')  # Returns 403

# ✅ GOOD - Create user with correct role
def test_admin_endpoint(self):
    admin_user = UserFactory(role='admin')
    self.client.force_authenticate(user=admin_user)
    response = self.client.get('/api/admin/users/')  # Returns 200

# ✅ BETTER - Create user with specific permissions
from django.contrib.auth.models import Permission

def test_with_permissions(self):
    user = UserFactory()
    permission = Permission.objects.get(codename='view_deal')
    user.user_permissions.add(permission)
    
    self.client.force_authenticate(user=user)
    response = self.client.get('/api/deals/')
    self.assertEqual(response.status_code, 200)
```

### Issue: JSON Serialization Errors

**Symptoms:**
```python
TypeError: Object of type Decimal is not JSON serializable
TypeError: Object of type datetime is not JSON serializable
```

**Cause:** Sending Python objects that aren't JSON-serializable

**Solution:**
```python
from decimal import Decimal
from datetime import datetime

# ❌ BAD - Python objects in data
def test_create_deal(self):
    data = {
        'total_price': Decimal('45000.00'),  # Not JSON serializable
        'date': datetime.now()               # Not JSON serializable
    }
    response = self.client.post('/api/deals/', data)  # ERROR

# ✅ GOOD - Convert to strings
def test_create_deal(self):
    data = {
        'total_price': '45000.00',  # String
        'date': '2024-12-20'        # ISO format string
    }
    response = self.client.post('/api/deals/', data, format='json')
    self.assertEqual(response.status_code, 201)

# ✅ BETTER - Use DRF's format parameter
def test_create_deal(self):
    data = {
        'total_price': 45000.00,  # DRF handles conversion
        'date': '2024-12-20'
    }
    # format='json' tells DRF to serialize properly
    response = self.client.post('/api/deals/', data, format='json')
```

### Issue: URL Reversal Errors

**Symptoms:**
```python
NoReverseMatch: Reverse for 'deal-detail' with arguments '(1,)' not found
```

**Cause:** URL name doesn't exist or wrong arguments

**Solution:**
```python
from django.urls import reverse

# ❌ BAD - Wrong URL name or args
def test_deal_detail(self):
    url = reverse('deal-detail', args=[1])  # Wrong name
    response = self.client.get(url)

# ✅ GOOD - Check URL configuration first
# In urls.py:
# path('deals/<int:pk>/', views.DealDetailView.as_view(), name='deal-financial-terms')

def test_deal_detail(self):
    deal = DealFactory()
    url = reverse('deal-financial-terms', kwargs={'pk': deal.id})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

# ✅ TIP - List available URLs
# python manage.py show_urls | grep deal
```

---

## Performance Test Issues

### Issue: Performance Tests Timing Out

**Symptoms:**
```bash
TimeoutError: Test exceeded 60 second timeout
```

**Cause:** Performance test taking too long

**Solution:**
```python
# ❌ BAD - Creating too much data
def test_performance(self):
    DealFactory.create_batch(10000)  # Too many!
    # Test times out...

# ✅ GOOD - Use reasonable dataset size
def test_performance(self):
    DealFactory.create_batch(100)  # Reasonable size
    # Test completes quickly

# ✅ BETTER - Use fixtures that persist between tests
class PerformanceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Created once for all tests
        cls.deals = DealFactory.create_batch(100)
    
    def test_list_performance(self):
        # Uses existing deals
        start = time.time()
        list(Deal.objects.all())
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.1)
```

### Issue: Inconsistent Performance Results

**Symptoms:**
```python
# Test passes sometimes, fails other times
AssertionError: 0.25 not less than 0.2
```

**Cause:** System load, caching, or database state variability

**Solution:**
```python
# ❌ BAD - Single measurement
def test_response_time(self):
    start = time.time()
    get_financial_terms(self.deal)
    elapsed = time.time() - start
    self.assertLess(elapsed, 0.2)  # Flaky!

# ✅ GOOD - Multiple measurements with average
def test_response_time(self):
    times = []
    for _ in range(10):  # Run 10 times
        start = time.time()
        get_financial_terms(self.deal)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    self.assertLess(avg_time, 0.2, f"Average time: {avg_time:.3f}s")

# ✅ BETTER - Use percentiles
def test_response_time(self):
    times = [self._measure_time() for _ in range(100)]
    times.sort()
    
    p50 = times[50]   # Median
    p95 = times[95]   # 95th percentile
    p99 = times[99]   # 99th percentile
    
    self.assertLess(p50, 0.1, f"p50: {p50:.3f}s")
    self.assertLess(p95, 0.2, f"p95: {p95:.3f}s")
    self.assertLess(p99, 0.3, f"p99: {p99:.3f}s")
```

### Issue: Query Count Assertions Failing

**Symptoms:**
```python
AssertionError: 15 queries executed, 5 expected
```

**Cause:** N+1 query problem or missing select_related/prefetch_related

**Solution:**
```python
from django.test.utils import override_settings
from django.db import connection

# ❌ BAD - N+1 queries
def get_deals_with_buyers():
    deals = Deal.objects.all()
    for deal in deals:
        print(deal.buyer.email)  # New query for each deal!
    return deals

# ✅ GOOD - Use select_related
def get_deals_with_buyers():
    # Single query with JOIN
    deals = Deal.objects.select_related('buyer').all()
    for deal in deals:
        print(deal.buyer.email)  # No additional queries
    return deals

# Test it
def test_no_n_plus_one(self):
    DealFactory.create_batch(10)
    
    with self.assertNumQueries(1):  # Should be 1 query
        deals = Deal.objects.select_related('buyer').all()
        for deal in deals:
            _ = deal.buyer.email

# Debug query count
def test_query_debug(self):
    from django.conf import settings
    settings.DEBUG = True  # Enable query logging
    
    DealFactory.create_batch(10)
    
    connection.queries_log.clear()
    get_deals_with_buyers()
    
    print(f"\nExecuted {len(connection.queries)} queries:")
    for query in connection.queries:
        print(query['sql'])
    
    self.assertLess(len(connection.queries), 5)
```

---

## Debugging Strategies

### Strategy 1: Print Debugging

```python
def test_something(self):
    """Test with debugging output."""
    deal = DealFactory()
    
    # Print model state
    print(f"\nDeal ID: {deal.id}")
    print(f"Total Price: {deal.total_price}")
    print(f"Amount Paid: {deal.amount_paid}")
    
    result = calculate_balance(deal)
    
    # Print result
    print(f"Calculated Balance: {result}")
    
    self.assertEqual(result, Decimal('45000.00'))

# Run single test with output
# python manage.py test tests.unit.MyTest.test_something --verbosity=2
```

### Strategy 2: Use Python Debugger

```python
def test_something(self):
    """Test with debugger breakpoint."""
    deal = DealFactory()
    
    # Set breakpoint
    import pdb; pdb.set_trace()
    
    # Execution pauses here
    # Commands:
    # n - next line
    # s - step into function
    # c - continue
    # p variable - print variable
    # l - list code
    
    result = calculate_balance(deal)
    self.assertEqual(result, Decimal('45000.00'))
```

### Strategy 3: Use logging

```python
import logging

logger = logging.getLogger(__name__)

class MyTest(TestCase):
    def test_with_logging(self):
        """Test with logging output."""
        deal = DealFactory()
        
        logger.info(f"Created deal: {deal.id}")
        logger.debug(f"Deal details: total={deal.total_price}, paid={deal.amount_paid}")
        
        result = calculate_balance(deal)
        logger.info(f"Calculated balance: {result}")
        
        self.assertEqual(result, Decimal('45000.00'))

# Run with logging
# python manage.py test tests.unit.MyTest --verbosity=2 --debug-mode
```

### Strategy 4: Isolate the Problem

```python
# ❌ Complex test that fails
def test_complex_workflow(self):
    """Test fails somewhere in this complex workflow."""
    deal = DealFactory()
    process_payment(deal, Decimal('5000.00'))
    apply_financing(deal, Decimal('8.5'), 36)
    create_milestones(deal)
    send_notifications(deal)
    # Which part failed?
    self.assertEqual(deal.status, 'active')

# ✅ Break into smaller tests
def test_payment_processing(self):
    """Test payment processing alone."""
    deal = DealFactory()
    result = process_payment(deal, Decimal('5000.00'))
    self.assertEqual(result['amount_paid'], Decimal('5000.00'))

def test_financing_application(self):
    """Test financing application alone."""
    deal = DealFactory()
    result = apply_financing(deal, Decimal('8.5'), 36)
    self.assertTrue(result['success'])

def test_milestone_creation(self):
    """Test milestone creation alone."""
    deal = DealFactory()
    milestones = create_milestones(deal)
    self.assertEqual(len(milestones), 3)

def test_notification_sending(self):
    """Test notification sending alone."""
    deal = DealFactory()
    result = send_notifications(deal)
    self.assertTrue(result['sent'])
```

### Strategy 5: Check Test Database State

```python
def test_with_database_inspection(self):
    """Test with database state inspection."""
    # Create data
    deal = DealFactory()
    
    # Check database state before action
    print(f"\nBefore: Deal count = {Deal.objects.count()}")
    print(f"Deal amount_paid = {deal.amount_paid}")
    
    # Perform action
    process_payment(deal, Decimal('5000.00'))
    
    # Check database state after action
    deal.refresh_from_db()  # Reload from database
    print(f"\nAfter: Deal amount_paid = {deal.amount_paid}")
    
    # Verify
    self.assertEqual(deal.amount_paid, Decimal('5000.00'))
```

---

## Common Error Messages

### Error: "RuntimeWarning: DateTimeField received a naive datetime"

**Meaning:** DateTime without timezone information

**Solution:**
```python
from django.utils import timezone

# ❌ BAD
from datetime import datetime
deal.created_at = datetime.now()  # Naive datetime

# ✅ GOOD
from django.utils import timezone
deal.created_at = timezone.now()  # Timezone-aware
```

### Error: "TransactionManagementError: An error occurred in the current transaction"

**Meaning:** Database transaction error, usually in tests

**Solution:**
```python
from django.db import transaction

# ❌ BAD
def test_with_transaction_error(self):
    try:
        Deal.objects.create(invalid_data=True)
    except Exception:
        pass  # Transaction is broken now
    
    # This will fail
    DealFactory()  # TransactionManagementError

# ✅ GOOD - Use atomic
def test_with_transaction_error(self):
    with transaction.atomic():
        try:
            Deal.objects.create(invalid_data=True)
        except Exception:
            pass  # Transaction rolled back properly
    
    # This works
    DealFactory()
```

### Error: "AssertionError: [] != [<Deal...>]"

**Meaning:** Expected data not in QuerySet

**Solution:**
```python
# Debug the issue
def test_queryset_debug(self):
    # Create data
    deal = DealFactory()
    
    # Query
    results = Deal.objects.filter(status='active')
    
    # Debug
    print(f"\nCreated deal status: {deal.status}")
    print(f"Query results: {list(results)}")
    print(f"All deals: {list(Deal.objects.all())}")
    
    # Might reveal: deal.status = 'pending', not 'active'!
    self.assertEqual(len(results), 1)
```

### Error: "AttributeError: 'NoneType' object has no attribute"

**Meaning:** Object is None when it shouldn't be

**Solution:**
```python
def test_none_check(self):
    deal = Deal.objects.filter(id=999).first()
    
    # ❌ BAD - Crashes if None
    print(deal.total_price)  # AttributeError if deal is None
    
    # ✅ GOOD - Check first
    self.assertIsNotNone(deal, "Deal should exist")
    print(deal.total_price)  # Safe now
    
    # ✅ BETTER - Use get_or_create
    deal, created = Deal.objects.get_or_create(
        id=999,
        defaults={'total_price': Decimal('45000.00')}
    )
    print(deal.total_price)  # Always safe
```

---

## Quick Diagnosis Checklist

When a test fails, check:

- [ ] Is the test database clean? (Use `--keepdb=False`)
- [ ] Are factories creating valid data? (Check constraints)
- [ ] Is authentication set up? (Use `force_authenticate`)
- [ ] Are relationships loaded? (Use `select_related`/`prefetch_related`)
- [ ] Are you testing the right thing? (Check test logic)
- [ ] Is the error in test or actual code? (Isolate the problem)
- [ ] Are you using the right assertion? (Check assertion types)
- [ ] Is data being created in setUp or setUpTestData? (Check lifecycle)
- [ ] Are there print statements or debugger breakpoints? (Remove for final version)
- [ ] Have migrations been applied? (Run `migrate`)

---

## Getting Help

1. **Read the error message carefully** - It usually tells you what's wrong
2. **Check Django documentation** - Most issues are documented
3. **Search existing issues** - Someone likely had the same problem
4. **Ask the team** - Share error messages and context
5. **Create a minimal reproduction** - Simplify to smallest failing case

---

**Last Updated**: December 20, 2024  
**Version**: 1.0
