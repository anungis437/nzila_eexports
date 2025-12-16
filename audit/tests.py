from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import Mock, patch
from datetime import timedelta

from .models import AuditLog, LoginHistory, DataChangeLog, SecurityEvent, APIAccessLog
from .services import AuditService, get_client_ip, serialize_changes
from .middleware import AuditMiddleware, SecurityAuditMiddleware
from deals.models import Deal

User = get_user_model()


class AuditLogModelTest(TestCase):
    """Test AuditLog model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_audit_log(self):
        """Test creating an audit log entry"""
        log = AuditLog.objects.create(
            user=self.user,
            action='login',
            description='User logged in',
            ip_address='192.168.1.1',
            severity='info'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'login')
        self.assertEqual(log.severity, 'info')
        self.assertIsNotNone(log.timestamp)

    def test_audit_log_with_content_object(self):
        """Test audit log with generic foreign key"""
        # Create required users and vehicle first
        from django.contrib.auth import get_user_model
        from vehicles.models import Vehicle
        User = get_user_model()
        buyer = User.objects.create_user(username='buyer', email='buyer@test.com', role='buyer')
        dealer = User.objects.create_user(username='dealer', email='dealer@test.com', role='dealer')
        vehicle = Vehicle.objects.create(
            dealer=dealer,
            make='Toyota',
            model='Camry',
            year=2020,
            price_cad=25000,
            status='available',
            mileage=50000,
            color='Silver',
            vin='1HGBH41JXMN109186'
        )
        deal = Deal.objects.create(
            vehicle=vehicle,
            buyer=buyer,
            dealer=dealer,
            status='pending_docs',
            agreed_price_cad=25000
        )
        log = AuditLog.objects.create(
            user=self.user,
            action='deal_created',
            content_object=deal,
            description='New deal created',
            severity='info'
        )
        self.assertEqual(log.content_object, deal)
        self.assertEqual(log.object_id, deal.id)

    def test_audit_log_changes_field(self):
        """Test storing changes in JSON field"""
        changes = {
            'status': {'old': 'pending', 'new': 'approved'},
            'amount': {'old': 1000, 'new': 1500}
        }
        log = AuditLog.objects.create(
            user=self.user,
            action='deal_updated',
            changes=changes,
            severity='info'
        )
        self.assertEqual(log.changes['status']['old'], 'pending')
        self.assertEqual(log.changes['amount']['new'], 1500)

    def test_audit_log_severity_levels(self):
        """Test all severity levels"""
        for severity in ['info', 'warning', 'error', 'critical']:
            log = AuditLog.objects.create(
                user=self.user,
                action='test_action',
                severity=severity
            )
            self.assertEqual(log.severity, severity)

    def test_audit_log_ordering(self):
        """Test audit logs are ordered by timestamp descending"""
        log1 = AuditLog.objects.create(user=self.user, action='action1')
        log2 = AuditLog.objects.create(user=self.user, action='action2')
        logs = AuditLog.objects.all()
        self.assertEqual(logs[0], log2)  # Most recent first


class LoginHistoryModelTest(TestCase):
    """Test LoginHistory model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_successful_login(self):
        """Test recording successful login"""
        login = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            status='success',
            two_factor_used=True,
            two_factor_method='totp'
        )
        self.assertEqual(login.status, 'success')
        self.assertTrue(login.two_factor_used)
        self.assertEqual(login.two_factor_method, 'totp')

    def test_failed_login(self):
        """Test recording failed login"""
        login = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            status='failed',
            failure_reason='Invalid password'
        )
        self.assertEqual(login.status, 'failed')
        self.assertEqual(login.failure_reason, 'Invalid password')

    def test_session_duration_calculation(self):
        """Test session duration is calculated correctly"""
        login = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            status='success'
        )
        # Simulate logout after 1 hour
        login.logout_timestamp = login.login_timestamp + timedelta(hours=1)
        login.save()
        
        # Session duration should be approximately 1 hour
        self.assertIsNotNone(login.session_duration)
        self.assertEqual(login.session_duration, timedelta(hours=1))


class SecurityEventModelTest(TestCase):
    """Test SecurityEvent model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_security_event(self):
        """Test creating a security event"""
        event = SecurityEvent.objects.create(
            event_type='suspicious_login',
            description='Login from unusual location',
            ip_address='192.168.1.1',
            risk_level='high',
            user=self.user
        )
        self.assertEqual(event.event_type, 'suspicious_login')
        self.assertEqual(event.risk_level, 'high')
        self.assertFalse(event.resolved)
        self.assertFalse(event.blocked)

    def test_resolve_security_event(self):
        """Test resolving a security event"""
        event = SecurityEvent.objects.create(
            event_type='failed_login_attempt',
            ip_address='192.168.1.1',
            risk_level='medium'
        )
        event.resolved = True
        event.resolved_at = timezone.now()
        event.resolved_by = self.user
        event.save()
        
        self.assertTrue(event.resolved)
        self.assertIsNotNone(event.resolved_at)
        self.assertEqual(event.resolved_by, self.user)

    def test_blocked_security_event(self):
        """Test marking security event as blocked"""
        event = SecurityEvent.objects.create(
            event_type='sql_injection',
            ip_address='192.168.1.1',
            risk_level='critical',
            blocked=True,
            action_taken='IP address blocked'
        )
        self.assertTrue(event.blocked)
        self.assertEqual(event.action_taken, 'IP address blocked')


class AuditServiceTest(TestCase):
    """Test AuditService helper class"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()

    def test_log_action(self):
        """Test AuditService.log_action"""
        request = self.factory.get('/api/test/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        log = AuditService.log_action(
            user=self.user,
            action='test_action',
            description='Test description',
            request=request
        )
        
        self.assertIsInstance(log, AuditLog)
        self.assertEqual(log.action, 'test_action')
        self.assertEqual(log.ip_address, '192.168.1.1')

    def test_log_login(self):
        """Test AuditService.log_login"""
        request = self.factory.post('/api/auth/login/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'
        
        history = AuditService.log_login(
            user=self.user,
            status='success',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            two_factor_used=True
        )
        
        self.assertIsInstance(history, LoginHistory)
        self.assertEqual(history.status, 'success')
        self.assertTrue(history.two_factor_used)

    def test_log_logout(self):
        """Test AuditService.log_logout"""
        # First create a login
        login = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            status='success',
            session_key='test_session_key'
        )
        
        # Then log logout
        AuditService.log_logout(user=self.user, session_key='test_session_key')
        
        # Refresh from database
        login.refresh_from_db()
        self.assertIsNotNone(login.logout_timestamp)
        self.assertIsNotNone(login.session_duration)

    def test_log_data_change(self):
        """Test AuditService.log_data_change"""
        change = AuditService.log_data_change(
            user=self.user,
            model_name='Deal',
            object_id=123,
            object_repr='Deal #123',
            action='update',
            field_name='status',
            old_value='pending',
            new_value='approved'
        )
        
        self.assertIsInstance(change, DataChangeLog)
        self.assertEqual(change.model_name, 'Deal')
        self.assertEqual(change.field_name, 'status')
        self.assertEqual(change.old_value, 'pending')
        self.assertEqual(change.new_value, 'approved')

    def test_log_security_event(self):
        """Test AuditService.log_security_event"""
        event = AuditService.log_security_event(
            event_type='sql_injection',
            description='SQL injection attempt detected',
            ip_address='192.168.1.1',
            risk_level='critical'
        )
        
        self.assertIsInstance(event, SecurityEvent)
        self.assertEqual(event.event_type, 'sql_injection')
        self.assertEqual(event.risk_level, 'critical')

    def test_get_client_ip(self):
        """Test get_client_ip helper function"""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_with_proxy(self):
        """Test get_client_ip with X-Forwarded-For header"""
        request = self.factory.get('/api/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')


class AuditMiddlewareTest(TestCase):
    """Test AuditMiddleware"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.factory = RequestFactory()
        # Create a proper mock response with content attribute
        mock_response = Mock(status_code=200, content=b'{"result": "success"}')
        self.middleware = AuditMiddleware(get_response=lambda r: mock_response)

    def test_middleware_logs_api_request(self):
        """Test middleware logs API requests"""
        request = self.factory.get('/api/deals/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        initial_count = APIAccessLog.objects.count()
        self.middleware(request)
        
        self.assertEqual(APIAccessLog.objects.count(), initial_count + 1)
        log = APIAccessLog.objects.latest('timestamp')
        self.assertEqual(log.path, '/api/deals/')
        self.assertEqual(log.user, self.user)

    def test_middleware_ignores_static_files(self):
        """Test middleware ignores static file requests"""
        request = self.factory.get('/static/admin/css/base.css')
        request.user = self.user
        
        initial_count = APIAccessLog.objects.count()
        self.middleware(request)
        
        self.assertEqual(APIAccessLog.objects.count(), initial_count)

    def test_middleware_tracks_response_time(self):
        """Test middleware tracks response time"""
        request = self.factory.get('/api/test/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        self.middleware(request)
        
        log = APIAccessLog.objects.latest('timestamp')
        self.assertIsNotNone(log.response_time_ms)
        self.assertGreaterEqual(log.response_time_ms, 0)


class AuditAPITest(APITestCase):
    """Test Audit REST API endpoints"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='userpass123'
        )
        self.client = APIClient()

    def test_list_audit_logs_as_admin(self):
        """Test admin can list all audit logs"""
        # Create some logs
        AuditLog.objects.create(user=self.admin_user, action='test1')
        AuditLog.objects.create(user=self.regular_user, action='test2')
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/audit/logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_list_audit_logs_as_user(self):
        """Test regular user can only see their own logs"""
        AuditLog.objects.create(user=self.admin_user, action='admin_action')
        AuditLog.objects.create(user=self.regular_user, action='user_action')
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/audit/logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see their own log
        for log in response.data['results']:
            self.assertEqual(log['user_display']['email'], self.regular_user.email)

    def test_get_audit_stats(self):
        """Test getting audit statistics"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/audit/logs/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_actions', response.data)

    def test_unauthorized_access(self):
        """Test unauthenticated users cannot access audit endpoints"""
        response = self.client.get('/api/v1/audit/logs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
