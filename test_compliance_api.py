"""
Test compliance API endpoints
Tests PIPEDA, Law 25, and SOC 2 compliance ViewSets
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from accounts.compliance_models import (
    DataBreachLog, ConsentHistory,
    DataRetentionPolicy, PrivacyImpactAssessment
)

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Create admin user for testing"""
    return User.objects.create_user(
        username='admin_test',
        email='admin@nzila.ca',
        password='testpass123',
        role='admin'
    )


@pytest.fixture
def regular_user(db):
    """Create regular user for testing"""
    return User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='testpass123',
        role='buyer'
    )


@pytest.fixture
def api_client():
    """Create API client"""
    return APIClient()


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated as admin"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user_client(api_client, regular_user):
    """API client authenticated as regular user"""
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def sample_breach(admin_user):
    """Create sample data breach"""
    return DataBreachLog.objects.create(
        breach_date=timezone.now().date() - timedelta(days=5),
        discovery_date=timezone.now() - timedelta(days=4),
        severity='medium',
        status='investigating',
        affected_users_count=100,
        data_types_compromised='Email addresses, names',
        description='Test breach for compliance testing',
        attack_vector='API vulnerability',
        reported_by=admin_user
    )


@pytest.fixture
def sample_consent(regular_user):
    """Create sample consent history"""
    return ConsentHistory.objects.create(
        user=regular_user,
        consent_type='marketing',
        action='granted',
        consent_given=True,
        privacy_policy_version='v2.1',
        consent_method='web_form',
        ip_address='192.168.1.1'
    )


@pytest.fixture
def sample_retention_policy():
    """Create sample retention policy"""
    return DataRetentionPolicy.objects.create(
        data_category='user_profiles',
        retention_days=730,
        legal_basis='PIPEDA Principle 5',
        auto_delete_enabled=True,
        description='User profile data retention'
    )


@pytest.fixture
def sample_pia(admin_user):
    """Create sample PIA"""
    return PrivacyImpactAssessment.objects.create(
        title='Test PIA',
        description='Privacy assessment for testing',
        project_name='Test Project',
        risk_level='medium',
        data_types_processed=['user_data', 'payment_info'],
        cross_border_transfer=False,
        identified_risks='Test risks',
        mitigation_measures='Test mitigations',
        status='in_progress',
        assessed_by=admin_user
    )


# ==================== DATA BREACH TESTS ====================

@pytest.mark.django_db
class TestDataBreachLogViewSet:
    """Test data breach tracking endpoints"""
    
    def test_list_breaches_admin(self, admin_client, sample_breach):
        """Admin can list all breaches"""
        response = admin_client.get('/api/accounts/compliance/breaches/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        assert response.data['results'][0]['id'] == sample_breach.id
    
    def test_list_breaches_non_admin(self, user_client, sample_breach):
        """Non-admin cannot list breaches"""
        response = user_client.get('/api/accounts/compliance/breaches/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_breach_admin(self, admin_client, admin_user):
        """Admin can create breach log"""
        data = {
            'breach_date': timezone.now().date().isoformat(),
            'discovery_date': timezone.now().isoformat(),
            'severity': 'high',
            'status': 'discovered',
            'affected_users_count': 500,
            'data_types_compromised': 'Passwords, payment tokens',
            'description': 'Critical security breach',
            'attack_vector': 'SQL injection'
        }
        response = admin_client.post('/api/accounts/compliance/breaches/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['severity'] == 'high'
        assert response.data['reported_by_name'] == admin_user.get_full_name()
    
    def test_export_breaches_csv(self, admin_client, sample_breach):
        """Admin can export breaches to CSV"""
        response = admin_client.get('/api/accounts/compliance/breaches/export_csv/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment' in response['Content-Disposition']
    
    def test_active_breaches(self, admin_client, sample_breach):
        """Get active/unresolved breaches"""
        response = admin_client.get('/api/accounts/compliance/breaches/active_breaches/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        # sample_breach has status='investigating' so should be in active list
        breach_ids = [b['id'] for b in response.data]
        assert sample_breach.id in breach_ids
    
    def test_overdue_notifications(self, admin_client):
        """Get breaches with overdue 72-hour notification"""
        # Create breach older than 72 hours without CAI notification
        old_breach = DataBreachLog.objects.create(
            breach_date=timezone.now().date() - timedelta(days=5),
            discovery_date=timezone.now() - timedelta(days=5),
            severity='medium',
            status='investigating',
            affected_users_count=50,
            data_types_compromised='Email addresses',
            description='Overdue breach',
            reported_by=admin_client.handler._force_user
        )
        
        response = admin_client.get('/api/accounts/compliance/breaches/overdue_notifications/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] > 0
        breach_ids = [b['id'] for b in response.data['breaches']]
        assert old_breach.id in breach_ids  # type: ignore[attr-defined]


# ==================== CONSENT HISTORY TESTS ====================

@pytest.mark.django_db
class TestConsentHistoryViewSet:
    """Test consent tracking endpoints"""
    
    def test_list_own_consent(self, user_client, sample_consent, regular_user):
        """User can list their own consent history"""
        response = user_client.get('/api/accounts/compliance/consent-history/')
        assert response.status_code == status.HTTP_200_OK
        # User should only see their own consents
        for consent in response.data['results']:
            assert consent['user'] == regular_user.id
    
    def test_admin_list_all_consents(self, admin_client, sample_consent):
        """Admin can list all consent history"""
        response = admin_client.get('/api/accounts/compliance/consent-history/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_my_consents_summary(self, user_client, regular_user):
        """User can get their consent summary"""
        # Create multiple consents for user
        for consent_type in ['marketing', 'analytics', 'data_sharing']:
            ConsentHistory.objects.create(
                user=regular_user,
                consent_type=consent_type,
                action='granted',
                consent_given=True,
                privacy_policy_version='v2.1',
                consent_method='web_form'
            )
        
        response = user_client.get('/api/accounts/compliance/consent-history/my_consents/')
        assert response.status_code == status.HTTP_200_OK
        assert 'marketing' in response.data
        assert response.data['marketing']['granted'] is True
    
    def test_export_consent_csv(self, admin_client, sample_consent):
        """Admin can export consent history to CSV"""
        response = admin_client.get('/api/accounts/compliance/consent-history/export_csv/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'


# ==================== RETENTION POLICY TESTS ====================

@pytest.mark.django_db
class TestDataRetentionPolicyViewSet:
    """Test retention policy endpoints"""
    
    def test_list_policies_admin(self, admin_client, sample_retention_policy):
        """Admin can list retention policies"""
        response = admin_client.get('/api/accounts/compliance/retention-policies/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_list_policies_non_admin(self, user_client):
        """Non-admin cannot list retention policies"""
        response = user_client.get('/api/accounts/compliance/retention-policies/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_policy_admin(self, admin_client):
        """Admin can create retention policy"""
        data = {
            'data_category': 'financial_records',
            'retention_days': 2555,  # 7 years
            'legal_basis': 'CRA Income Tax Act',
            'auto_delete_enabled': False,
            'description': 'Financial records retention'
        }
        response = admin_client.post('/api/accounts/compliance/retention-policies/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['retention_years'] == 7.0
    
    def test_policy_summary(self, admin_client, sample_retention_policy):
        """Get retention policy summary"""
        response = admin_client.get('/api/accounts/compliance/retention-policies/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert 'user_profiles' in response.data
        assert response.data['user_profiles']['retention_days'] == 730
    
    def test_export_policies_csv(self, admin_client, sample_retention_policy):
        """Admin can export retention policies to CSV"""
        response = admin_client.get('/api/accounts/compliance/retention-policies/export_csv/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'


# ==================== PRIVACY IMPACT ASSESSMENT TESTS ====================

@pytest.mark.django_db
class TestPrivacyImpactAssessmentViewSet:
    """Test PIA endpoints"""
    
    def test_list_pias_admin(self, admin_client, sample_pia):
        """Admin can list PIAs"""
        response = admin_client.get('/api/accounts/compliance/privacy-assessments/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_list_pias_non_admin(self, user_client):
        """Non-admin cannot list PIAs"""
        response = user_client.get('/api/accounts/compliance/privacy-assessments/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_pia_admin(self, admin_client, admin_user):
        """Admin can create PIA"""
        data = {
            'title': 'New Feature PIA',
            'description': 'Privacy assessment for new feature',
            'project_name': 'Feature X',
            'risk_level': 'low',
            'data_types_processed': ['user_preferences'],
            'cross_border_transfer': False,
            'identified_risks': 'Minimal risks',
            'mitigation_measures': 'Data minimization',
            'status': 'draft'
        }
        response = admin_client.post('/api/accounts/compliance/privacy-assessments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['assessed_by_name'] == admin_user.get_full_name()
    
    def test_approve_pia(self, admin_client, sample_pia):
        """Admin can approve PIA"""
        response = admin_client.post(
            f'/api/accounts/compliance/privacy-assessments/{sample_pia.id}/approve/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['pia']['status'] == 'approved'
        assert response.data['message'] == 'PIA approved successfully'
    
    def test_approve_already_approved(self, admin_client, sample_pia):
        """Cannot approve already approved PIA"""
        sample_pia.status = 'approved'
        sample_pia.save()
        
        response = admin_client.post(
            f'/api/accounts/compliance/privacy-assessments/{sample_pia.id}/approve/'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already approved' in response.data['error']
    
    def test_request_changes(self, admin_client, sample_pia):
        """Admin can request changes to PIA"""
        response = admin_client.post(
            f'/api/accounts/compliance/privacy-assessments/{sample_pia.id}/request_changes/'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['pia']['status'] == 'needs_revision'
    
    def test_pending_review(self, admin_client, admin_user):
        """Get PIAs pending review"""
        # Create PIA with upcoming review due date
        pia = PrivacyImpactAssessment.objects.create(
            title='Due for Review',
            description='Test',
            risk_level='medium',
            status='approved',
            assessed_by=admin_user,
            approved_by=admin_user,
            approval_date=timezone.now() - timedelta(days=335),
            review_due_date=timezone.now().date() + timedelta(days=15)
        )
        
        response = admin_client.get('/api/accounts/compliance/privacy-assessments/pending_review/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] > 0
        pia_ids = [p['id'] for p in response.data['assessments']]
        assert pia.id in pia_ids  # type: ignore[attr-defined]
    
    def test_export_pias_csv(self, admin_client, sample_pia):
        """Admin can export PIAs to CSV"""
        response = admin_client.get('/api/accounts/compliance/privacy-assessments/export_csv/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'


# ==================== FILTERING & SEARCH TESTS ====================

@pytest.mark.django_db
class TestComplianceFiltering:
    """Test filtering and search on compliance endpoints"""
    
    def test_filter_breaches_by_severity(self, admin_client, admin_user):
        """Filter breaches by severity level"""
        # Create breaches with different severities
        DataBreachLog.objects.create(
            breach_date=timezone.now().date(),
            discovery_date=timezone.now(),
            severity='low',
            status='resolved',
            affected_users_count=5,
            data_types_compromised='Email',
            description='Low severity breach',
            reported_by=admin_user
        )
        DataBreachLog.objects.create(
            breach_date=timezone.now().date(),
            discovery_date=timezone.now(),
            severity='critical',
            status='containing',
            affected_users_count=10000,
            data_types_compromised='Payment data',
            description='Critical breach',
            reported_by=admin_user
        )
        
        response = admin_client.get('/api/accounts/compliance/breaches/?severity=critical')
        assert response.status_code == status.HTTP_200_OK
        for breach in response.data['results']:
            assert breach['severity'] == 'critical'
    
    def test_filter_consents_by_type(self, user_client, regular_user):
        """Filter consent history by consent type"""
        ConsentHistory.objects.create(
            user=regular_user,
            consent_type='marketing',
            action='granted',
            consent_given=True,
            privacy_policy_version='v2.1',
            consent_method='web_form'
        )
        
        response = user_client.get('/api/accounts/compliance/consent-history/?consent_type=marketing')
        assert response.status_code == status.HTTP_200_OK
        for consent in response.data['results']:
            assert consent['consent_type'] == 'marketing'
    
    def test_search_pias(self, admin_client, admin_user):
        """Search PIAs by title/description"""
        PrivacyImpactAssessment.objects.create(
            title='AI Machine Learning System',
            description='ML-powered vehicle valuation',
            risk_level='medium',
            status='draft',
            assessed_by=admin_user
        )
        
        response = admin_client.get('/api/accounts/compliance/privacy-assessments/?search=machine learning')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        assert 'Machine Learning' in response.data['results'][0]['title']


# ==================== PERMISSION TESTS ====================

@pytest.mark.django_db
class TestCompliancePermissions:
    """Test permission enforcement on compliance endpoints"""
    
    def test_unauthenticated_access(self, api_client, sample_breach):
        """Unauthenticated users cannot access compliance endpoints"""
        endpoints = [
            '/api/accounts/compliance/breaches/',
            '/api/accounts/compliance/retention-policies/',
            '/api/accounts/compliance/privacy-assessments/',
        ]
        
        for endpoint in endpoints:
            response = api_client.get(endpoint)
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_consent_history_user_isolation(self, user_client, regular_user):
        """Users can only see their own consent history"""
        # Create another user's consent
        other_user = User.objects.create_user(
            username='other_user',
            email='other@test.com',
            password='testpass123',
            role='dealer'
        )
        other_consent = ConsentHistory.objects.create(
            user=other_user,
            consent_type='analytics',
            action='granted',
            consent_given=True,
            privacy_policy_version='v2.1',
            consent_method='web_form'
        )
        
        response = user_client.get('/api/accounts/compliance/consent-history/')
        assert response.status_code == status.HTTP_200_OK
        
        # Should not see other user's consents
        consent_user_ids = [c['user'] for c in response.data['results']]
        assert other_user.id not in consent_user_ids  # type: ignore[attr-defined]
        assert all(user_id == regular_user.id for user_id in consent_user_ids)  # type: ignore[attr-defined]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
