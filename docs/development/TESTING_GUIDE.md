# Testing Guide - Nzila Exports Platform

## Overview
This guide covers testing practices, test suites, and how to run tests for the Nzila Exports platform. The platform uses Django's built-in testing framework with unittest for backend tests and Jest/React Testing Library for frontend tests.

---

## Backend Testing

### Test Structure

```
nzila_eexports/
├── audit/
│   └── tests.py           # Audit trail system tests
├── payments/
│   ├── tests.py           # Payment system tests
│   └── test_pdf.py        # PDF generation tests
├── accounts/
│   └── tests.py           # Authentication & 2FA tests
├── deals/
│   └── tests.py           # Deal management tests
└── ...
```

### Running Tests

#### Run All Tests
```bash
python manage.py test
```

#### Run Specific App Tests
```bash
python manage.py test audit
python manage.py test payments
python manage.py test accounts
```

#### Run Specific Test Class
```bash
python manage.py test audit.tests.AuditLogModelTest
python manage.py test payments.test_pdf.PDFGeneratorTest
```

#### Run Single Test Method
```bash
python manage.py test audit.tests.AuditLogModelTest.test_create_audit_log
python manage.py test payments.test_pdf.PDFGeneratorTest.test_generate_invoice_pdf
```

#### Run with Verbose Output
```bash
python manage.py test --verbosity=2
python manage.py test --verbosity=3  # Maximum verbosity
```

#### Run Tests in Parallel
```bash
python manage.py test --parallel
```

#### Run with Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Database
Tests use an in-memory SQLite database by default for speed. It's created and destroyed automatically for each test run.

---

## Test Suites

### 1. Audit Trail Tests (`audit/tests.py`)

**Purpose:** Test audit logging, security events, login history, and middleware

#### Test Classes:

**AuditLogModelTest** - Test AuditLog model
- `test_create_audit_log()` - Create basic audit log
- `test_audit_log_with_content_object()` - Test generic foreign key
- `test_audit_log_changes_field()` - Test JSON changes field
- `test_audit_log_severity_levels()` - Test all severity levels
- `test_audit_log_ordering()` - Test timestamp ordering

**LoginHistoryModelTest** - Test LoginHistory model
- `test_successful_login()` - Test successful login tracking
- `test_failed_login()` - Test failed login tracking
- `test_session_duration_calculation()` - Test session duration

**SecurityEventModelTest** - Test SecurityEvent model
- `test_create_security_event()` - Create security event
- `test_resolve_security_event()` - Test resolution workflow
- `test_blocked_security_event()` - Test blocking

**AuditServiceTest** - Test AuditService helper class
- `test_log_action()` - Test general action logging
- `test_log_login()` - Test login logging
- `test_log_logout()` - Test logout with session duration
- `test_log_data_change()` - Test field-level change tracking
- `test_log_security_event()` - Test security event logging
- `test_get_client_ip()` - Test IP extraction
- `test_get_client_ip_with_proxy()` - Test proxy IP extraction

**AuditMiddlewareTest** - Test automatic logging middleware
- `test_middleware_logs_api_request()` - Test API request logging
- `test_middleware_ignores_static_files()` - Test static file filtering
- `test_middleware_tracks_response_time()` - Test performance tracking

**AuditAPITest** - Test REST API endpoints
- `test_list_audit_logs_as_admin()` - Admin can see all logs
- `test_list_audit_logs_as_user()` - Users see own logs only
- `test_get_audit_stats()` - Test statistics endpoint
- `test_unauthorized_access()` - Test authentication required

#### Run Audit Tests:
```bash
python manage.py test audit.tests --verbosity=2
```

---

### 2. PDF Generation Tests (`payments/test_pdf.py`)

**Purpose:** Test PDF generation service and API endpoints

#### Test Classes:

**PDFGeneratorTest** - Test PDF generation service
- `test_generator_initialization()` - Test generator setup
- `test_generate_invoice_pdf()` - Test invoice PDF creation
- `test_generate_receipt_pdf()` - Test receipt PDF creation
- `test_generate_deal_report_pdf()` - Test deal report PDF
- `test_invoice_pdf_content()` - Test PDF contains expected text
- `test_pdf_with_missing_optional_data()` - Test with missing fields

**PDFAPIEndpointsTest** - Test PDF REST API endpoints
- `test_generate_invoice_pdf_authenticated()` - Test invoice download
- `test_generate_receipt_pdf_succeeded_payment()` - Test receipt for completed payment
- `test_generate_receipt_pdf_pending_payment()` - Test receipt requires succeeded payment
- `test_generate_pdf_permission_denied()` - Test permission checks
- `test_admin_can_generate_any_pdf()` - Admin can access all PDFs
- `test_generate_deal_report_pdf()` - Test deal report generation
- `test_unauthenticated_pdf_request()` - Test auth required
- `test_pdf_filename_generation()` - Test correct filenames
- `test_pdf_content_type_header()` - Test content type

**PDFIntegrationTest** - Integration tests with real data
- `test_full_invoice_generation_workflow()` - End-to-end invoice generation
- `test_receipt_generation_with_confirmed_payment()` - Receipt workflow

#### Run PDF Tests:
```bash
python manage.py test payments.test_pdf --verbosity=2
```

---

## Writing New Tests

### Test Template

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class MyModelTest(TestCase):
    """Test MyModel functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_model_creation(self):
        """Test creating a model instance"""
        # Your test code here
        self.assertEqual(expected, actual)


class MyAPITest(APITestCase):
    """Test API endpoints"""

    def setUp(self):
        """Set up API client and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_list_endpoint(self):
        """Test listing resources"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/resource/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
```

### Best Practices

1. **Isolation:** Each test should be independent
2. **setUp/tearDown:** Use setUp for common test data
3. **Descriptive Names:** Use clear test method names
4. **One Assert Per Test:** Focus on testing one thing
5. **Test Edge Cases:** Test boundary conditions and errors
6. **Mock External Services:** Don't rely on external APIs
7. **Fast Tests:** Keep tests fast (avoid sleep, unnecessary DB queries)

### Common Assertions

```python
# Equality
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# Truth
self.assertTrue(x)
self.assertFalse(x)

# Membership
self.assertIn(item, list)
self.assertNotIn(item, list)

# Exceptions
with self.assertRaises(ValueError):
    function_that_raises()

# Greater/Less Than
self.assertGreater(a, b)
self.assertGreaterEqual(a, b)
self.assertLess(a, b)

# None
self.assertIsNone(value)
self.assertIsNotNone(value)

# Instance
self.assertIsInstance(obj, ClassName)

# Dictionary/Keys
self.assertIn('key', dict)
self.assertEqual(dict['key'], value)
```

---

## API Testing

### Testing REST API Endpoints

```python
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

class MyAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(...)
        
    def test_get_request(self):
        """Test GET request"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/endpoint/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
    def test_post_request(self):
        """Test POST request"""
        self.client.force_authenticate(user=self.user)
        data = {'field': 'value'}
        response = self.client.post('/api/v1/endpoint/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_authentication_required(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/api/v1/endpoint/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

---

## Mocking and Fixtures

### Using Fixtures

```python
from django.test import TestCase

class MyTest(TestCase):
    fixtures = ['users.json', 'deals.json']
    
    def test_with_fixture_data(self):
        # Data from fixtures is available
        user = User.objects.get(email='fixture@example.com')
        self.assertIsNotNone(user)
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

class PaymentTest(TestCase):
    @patch('payments.stripe_service.stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_stripe):
        """Test payment intent creation with mocked Stripe"""
        mock_stripe.return_value = Mock(id='pi_123', status='succeeded')
        
        result = create_payment_intent(amount=1000)
        
        self.assertEqual(result.id, 'pi_123')
        mock_stripe.assert_called_once()
```

---

## Test Coverage

### Measuring Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# View coverage report
coverage report

# Generate HTML report
coverage html
open htmlcov/index.html
```

### Coverage Goals
- **Overall:** Aim for 80%+ code coverage
- **Critical Paths:** 100% coverage for payment/security code
- **Models:** 90%+ coverage
- **Views/APIs:** 85%+ coverage
- **Utilities:** 75%+ coverage

### Viewing Coverage Report
```bash
coverage report --skip-covered  # Hide 100% covered files
coverage report -m              # Show missing lines
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python manage.py test --verbosity=2
        
    - name: Check coverage
      run: |
        coverage run manage.py test
        coverage report --fail-under=80
```

---

## Performance Testing

### Testing Response Times

```python
import time
from django.test import TestCase

class PerformanceTest(TestCase):
    def test_query_performance(self):
        """Test query completes within acceptable time"""
        start = time.time()
        
        # Run your query
        results = MyModel.objects.filter(status='active')
        list(results)  # Force evaluation
        
        duration = time.time() - start
        self.assertLess(duration, 1.0, "Query took too long")
```

### Database Query Optimization

```python
from django.test import TestCase
from django.test.utils import override_settings

class QueryOptimizationTest(TestCase):
    def test_query_count(self):
        """Test number of database queries"""
        with self.assertNumQueries(3):
            # Code that should make exactly 3 queries
            users = list(User.objects.select_related('profile').all())
```

---

## Security Testing

### Testing Authentication

```python
class SecurityTest(APITestCase):
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access protected endpoints"""
        response = self.client.get('/api/v1/protected/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_unauthorized_access_denied(self):
        """Test users cannot access other users' data"""
        user1 = User.objects.create_user(username='user1', ...)
        user2 = User.objects.create_user(username='user2', ...)
        
        self.client.force_authenticate(user=user2)
        response = self.client.get(f'/api/v1/users/{user1.id}/private/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

### Testing Input Validation

```python
class ValidationTest(TestCase):
    def test_invalid_email(self):
        """Test invalid email is rejected"""
        with self.assertRaises(ValidationError):
            user = User(email='invalid-email')
            user.full_clean()
            
    def test_sql_injection_protection(self):
        """Test SQL injection is prevented"""
        malicious_input = "'; DROP TABLE users; --"
        users = User.objects.filter(email=malicious_input)
        # Django ORM should protect against SQL injection
        self.assertEqual(users.count(), 0)
```

---

## Debugging Tests

### Verbose Output

```bash
python manage.py test --verbosity=3
```

### Print Debugging

```python
def test_something(self):
    result = my_function()
    print(f"Result: {result}")  # Will show in test output
    self.assertEqual(result, expected)
```

### PDB Debugging

```python
def test_something(self):
    result = my_function()
    import pdb; pdb.set_trace()  # Breakpoint
    self.assertEqual(result, expected)
```

### Run Single Test with PDB

```bash
python manage.py test path.to.test --pdb
```

---

## Test Data Management

### Creating Test Data

```python
class MyTest(TestCase):
    def setUp(self):
        # Create reusable test data
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
```

### Factory Pattern

```python
class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
        
class MyTest(TestCase):
    def test_something(self):
        user = UserFactory.create(email='custom@example.com')
        # Use user in test
```

---

## Common Test Scenarios

### Test Payment Flow

```python
class PaymentFlowTest(APITestCase):
    def test_complete_payment_flow(self):
        """Test end-to-end payment process"""
        # 1. Create payment intent
        response = self.client.post('/api/v1/payments/create-intent/', {
            'amount': 1000,
            'currency': 'USD'
        })
        self.assertEqual(response.status_code, 201)
        intent_id = response.data['payment_intent_id']
        
        # 2. Confirm payment
        response = self.client.post('/api/v1/payments/confirm/', {
            'payment_intent_id': intent_id
        })
        self.assertEqual(response.status_code, 200)
        
        # 3. Verify payment status
        payment = Payment.objects.get(payment_intent_id=intent_id)
        self.assertEqual(payment.status, 'succeeded')
```

### Test Audit Logging

```python
class AuditLoggingTest(TestCase):
    def test_action_is_logged(self):
        """Test that actions are automatically logged"""
        initial_count = AuditLog.objects.count()
        
        # Perform action
        deal = Deal.objects.create(status='pending')
        
        # Verify log was created
        self.assertGreater(AuditLog.objects.count(), initial_count)
        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, 'deal_created')
```

---

## Test Checklist

### Before Committing
- [ ] All tests pass locally
- [ ] New code has tests
- [ ] Coverage is maintained or improved
- [ ] No debug prints left in code
- [ ] Tests are well-documented

### Test Categories to Cover
- [ ] Model creation and validation
- [ ] Business logic
- [ ] API endpoints (GET, POST, PUT, DELETE)
- [ ] Authentication and permissions
- [ ] Error handling
- [ ] Edge cases and boundary conditions
- [ ] Integration between components

---

## Troubleshooting

### Tests Failing Randomly
- Check for race conditions
- Ensure proper test isolation
- Reset state in setUp/tearDown
- Use atomic transactions

### Slow Tests
- Use in-memory database
- Minimize database queries
- Mock external services
- Run tests in parallel

### Import Errors
- Check PYTHONPATH
- Verify app is in INSTALLED_APPS
- Run `python manage.py check`

---

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

*Last Updated: December 2025*  
*Platform: Nzila Exports Vehicle Export Management System*
