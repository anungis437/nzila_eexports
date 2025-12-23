"""
Pytest configuration and shared fixtures for Nzila Exports test suite.

This file contains fixtures that are available to all tests without imports.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import os

User = get_user_model()


# ============================================================================
# Django Setup Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Customize Django database setup for tests.
    This runs once per test session.
    """
    with django_db_blocker.unblock():
        # Any custom database setup can go here
        pass


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def db_access(db):
    """
    Provides database access for tests.
    Automatically rolls back after each test.
    """
    return db


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def user_password():
    """Returns the default password for test users."""
    return "TestPassword123!"


@pytest.fixture
def create_user(db, user_password):
    """
    Factory fixture to create test users with custom attributes.
    
    Usage:
        user = create_user(email='test@example.com', role='customer')
    """
    def make_user(**kwargs):
        # Set default values
        defaults = {
            'email': f'user_{User.objects.count() + 1}@example.com',
            'username': kwargs.get('email', f'user_{User.objects.count() + 1}@example.com').split('@')[0],
            'role': 'customer',
            'is_active': True,
            'is_verified': True,
        }
        defaults.update(kwargs)
        
        # Extract password before creating user
        password = defaults.pop('password', user_password)
        
        # Create user
        user = User.objects.create(**defaults)
        user.set_password(password)
        user.save()
        
        return user
    
    return make_user


@pytest.fixture
def customer_user(create_user):
    """Creates a customer user for testing."""
    return create_user(
        email='customer@example.com',
        role='customer',
        first_name='Test',
        last_name='Customer'
    )


@pytest.fixture
def dealer_user(create_user):
    """Creates a dealer user for testing."""
    return create_user(
        email='dealer@example.com',
        role='dealer',
        first_name='Test',
        last_name='Dealer'
    )


@pytest.fixture
def inspector_user(create_user):
    """Creates an inspector user for testing."""
    return create_user(
        email='inspector@example.com',
        role='inspector',
        first_name='Test',
        last_name='Inspector'
    )


@pytest.fixture
def admin_user(create_user):
    """Creates an admin/staff user for testing."""
    return create_user(
        email='admin@example.com',
        role='admin',
        is_staff=True,
        is_superuser=True,
        first_name='Test',
        last_name='Admin'
    )


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def jwt_token(user_password):
    """
    Factory fixture to generate JWT tokens for users.
    
    Usage:
        access_token, refresh_token = jwt_token(user)
    """
    def make_token(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)
    
    return make_token


@pytest.fixture
def customer_token(customer_user, jwt_token):
    """JWT access token for customer user."""
    access, refresh = jwt_token(customer_user)
    return access


@pytest.fixture
def dealer_token(dealer_user, jwt_token):
    """JWT access token for dealer user."""
    access, refresh = jwt_token(dealer_user)
    return access


@pytest.fixture
def inspector_token(inspector_user, jwt_token):
    """JWT access token for inspector user."""
    access, refresh = jwt_token(inspector_user)
    return access


@pytest.fixture
def admin_token(admin_user, jwt_token):
    """JWT access token for admin user."""
    access, refresh = jwt_token(admin_user)
    return access


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture
def django_client():
    """Django test client for testing views."""
    return Client()


@pytest.fixture
def api_client():
    """DRF API client without authentication."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, customer_token):
    """
    DRF API client authenticated as customer.
    
    Usage:
        response = authenticated_api_client.get('/api/deals/')
    """
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
    return api_client


@pytest.fixture
def customer_api_client(api_client, customer_token):
    """DRF API client authenticated as customer."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
    return api_client


@pytest.fixture
def dealer_api_client(api_client, dealer_token):
    """DRF API client authenticated as dealer."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {dealer_token}')
    return api_client


@pytest.fixture
def inspector_api_client(api_client, inspector_token):
    """DRF API client authenticated as inspector."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {inspector_token}')
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_token):
    """DRF API client authenticated as admin."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    return api_client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def test_image_file():
    """
    Creates a simple test image file for upload testing.
    
    Returns:
        PIL.Image: In-memory image object
    """
    from PIL import Image
    from io import BytesIO
    
    # Create a simple 100x100 red image
    image = Image.new('RGB', (100, 100), color='red')
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    image_io.name = 'test_image.png'
    
    return image_io


@pytest.fixture
def test_pdf_file():
    """
    Creates a simple test PDF file for upload testing.
    
    Returns:
        BytesIO: In-memory PDF file
    """
    from io import BytesIO
    from reportlab.pdfgen import canvas
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Test PDF Document")
    pdf.save()
    
    buffer.seek(0)
    buffer.name = 'test_document.pdf'
    
    return buffer


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_variables(monkeypatch):
    """
    Factory fixture to set environment variables for testing.
    
    Usage:
        mock_env_variables({'STRIPE_SECRET_KEY': 'test_key'})
    """
    def set_env_vars(env_dict):
        for key, value in env_dict.items():
            monkeypatch.setenv(key, value)
    
    return set_env_vars


@pytest.fixture(autouse=True)
def test_media_root(settings, tmp_path):
    """
    Automatically use temporary directory for MEDIA_ROOT in all tests.
    This prevents test media files from polluting the actual media directory.
    """
    settings.MEDIA_ROOT = tmp_path / 'media'
    settings.MEDIA_ROOT.mkdir(exist_ok=True)
    return settings.MEDIA_ROOT


@pytest.fixture(autouse=True)
def test_email_backend(settings):
    """
    Automatically use in-memory email backend for all tests.
    This prevents actual emails from being sent during tests.
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture(autouse=True)
def test_celery_eager(settings):
    """
    Automatically run Celery tasks synchronously in tests.
    This makes tests faster and more predictable.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


# ============================================================================
# Cache Fixtures
# ============================================================================

@pytest.fixture
def clear_cache():
    """
    Clears Django cache before and after tests.
    
    Usage:
        @pytest.mark.usefixtures('clear_cache')
        def test_with_clean_cache():
            pass
    """
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


# ============================================================================
# Time Fixtures
# ============================================================================

@pytest.fixture
def freeze_time():
    """
    Factory fixture to freeze time for testing.
    
    Usage:
        with freeze_time('2024-01-01 12:00:00'):
            # Time is frozen at 2024-01-01 12:00:00
            pass
    """
    from freezegun import freeze_time as _freeze_time
    return _freeze_time


# ============================================================================
# Async Fixtures
# ============================================================================

@pytest.fixture
def async_client():
    """Async test client for async views."""
    from django.test import AsyncClient
    return AsyncClient()


# ============================================================================
# Playwright Fixtures (E2E Testing)
# ============================================================================

@pytest.fixture(scope='session')
def browser_type_launch_args():
    """Browser launch arguments for Playwright."""
    return {
        'headless': True,
        'args': ['--disable-dev-shm-usage']
    }


@pytest.fixture(scope='session')
def browser_context_args():
    """Browser context arguments for Playwright."""
    return {
        'viewport': {'width': 1920, 'height': 1080},
        'ignore_https_errors': True,
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def assert_num_queries(db):
    """
    Context manager to assert the number of database queries.
    
    Usage:
        with assert_num_queries(5):
            # Code that should make exactly 5 queries
            pass
    """
    from django.test.utils import CaptureQueriesContext
    from django.db import connection
    
    class AssertNumQueries:
        def __init__(self, expected_num):
            self.expected_num = expected_num
            self.context = None
        
        def __enter__(self):
            self.context = CaptureQueriesContext(connection)
            self.context.__enter__()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.context.__exit__(exc_type, exc_val, exc_tb)
            actual_num = len(self.context.captured_queries)
            assert actual_num == self.expected_num, (
                f"Expected {self.expected_num} queries, but {actual_num} were executed.\n"
                f"Queries:\n" + "\n".join(
                    f"{i+1}. {q['sql']}" for i, q in enumerate(self.context.captured_queries)
                )
            )
    
    return AssertNumQueries


@pytest.fixture
def capture_emails():
    """
    Context manager to capture emails sent during tests.
    
    Usage:
        from django.core import mail
        with capture_emails() as outbox:
            # Send emails
            send_mail(...)
        
        assert len(outbox) == 1
        assert outbox[0].subject == 'Test Subject'
    """
    from django.core import mail
    
    class EmailCapture:
        def __enter__(self):
            mail.outbox = []
            return mail.outbox
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            mail.outbox = []
    
    return EmailCapture()


# ============================================================================
# Marker Configurations
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )


# ============================================================================
# Currency Fixtures
# ============================================================================

@pytest.fixture
def cad_currency(db):
    """Create CAD currency required by Deal.create_financial_terms()."""
    from payments.models import Currency
    return Currency.objects.get_or_create(
        code='CAD',
        defaults={
            'name': 'Canadian Dollar',
            'symbol': '$',
            'is_active': True
        }
    )[0]


# ============================================================================
# Test Session Hooks
# ============================================================================

def pytest_sessionstart(session):
    """Called before test run starts."""
    print("\n" + "="*80)
    print("Starting Nzila Exports Test Suite")
    print("="*80 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """Called after all tests complete."""
    print("\n" + "="*80)
    print(f"Test Suite Complete - Exit Status: {exitstatus}")
    print("="*80 + "\n")
