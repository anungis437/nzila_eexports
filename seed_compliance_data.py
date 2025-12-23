"""
Seed compliance data for testing compliance ViewSets
Creates sample data for:
- DataBreachLog (Law 25, PIPEDA)
- ConsentHistory (PIPEDA Principle 8)
- DataRetentionPolicy (Law 25 Article 11)
- PrivacyImpactAssessment (Law 25 Article 3.3)
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.compliance_models import (
    DataBreachLog, ConsentHistory, 
    DataRetentionPolicy, PrivacyImpactAssessment
)

User = get_user_model()

def create_retention_policies():
    """Create standard data retention policies for Canadian compliance"""
    print("\n📋 Creating Data Retention Policies...")
    
    policies = [
        # Financial data (7 years - CRA requirement)
        {
            'data_category': 'financial_records',
            'retention_days': 2555,  # 7 years
            'legal_basis': 'Canada Revenue Agency - Income Tax Act requires 7 years retention',
            'auto_delete_enabled': False,
            'description': 'Financial transactions, invoices, tax documents'
        },
        {
            'data_category': 'deal_records',
            'retention_days': 2555,  # 7 years
            'legal_basis': 'Provincial consumer protection laws require 7 years retention',
            'auto_delete_enabled': False,
            'description': 'Vehicle sales, deals, commissions, contracts'
        },
        
        # User data (active + 2 years after account closure)
        {
            'data_category': 'user_profiles',
            'retention_days': 730,  # 2 years after closure
            'legal_basis': 'PIPEDA Principle 5 - reasonable purpose retention',
            'auto_delete_enabled': True,
            'description': 'User profile data, preferences, settings (after account closure)'
        },
        {
            'data_category': 'consent_records',
            'retention_days': 3650,  # 10 years
            'legal_basis': 'PIPEDA compliance audit trail',
            'auto_delete_enabled': False,
            'description': 'Consent audit trail for regulatory compliance'
        },
        
        # Security data
        {
            'data_category': 'audit_logs',
            'retention_days': 2555,  # 7 years
            'legal_basis': 'SOC 2 Type II compliance - 7 years audit trail',
            'auto_delete_enabled': False,
            'description': 'System audit logs, security events, admin actions'
        },
        {
            'data_category': 'session_logs',
            'retention_days': 90,
            'legal_basis': 'Security monitoring and fraud detection',
            'auto_delete_enabled': True,
            'description': 'Login sessions, IP addresses, user agents'
        },
        
        # Communication data
        {
            'data_category': 'messages',
            'retention_days': 365,  # 1 year
            'legal_basis': 'Customer support and dispute resolution',
            'auto_delete_enabled': True,
            'description': 'Platform messages between users and dealers'
        },
        {
            'data_category': 'email_logs',
            'retention_days': 730,  # 2 years
            'legal_basis': 'CASL compliance - proof of consent for commercial emails',
            'auto_delete_enabled': False,
            'description': 'Email delivery logs, unsubscribe records'
        },
        
        # Analytics & Marketing
        {
            'data_category': 'analytics_data',
            'retention_days': 730,  # 2 years
            'legal_basis': 'Business intelligence and service improvement',
            'auto_delete_enabled': True,
            'description': 'Aggregated usage statistics, performance metrics'
        },
        {
            'data_category': 'marketing_data',
            'retention_days': 365,  # 1 year
            'legal_basis': 'CASL express consent valid for 2 years',
            'auto_delete_enabled': True,
            'description': 'Marketing preferences, campaign data'
        },
        
        # Vehicle & Shipment data
        {
            'data_category': 'vehicle_listings',
            'retention_days': 1095,  # 3 years
            'legal_basis': 'Historical marketplace data',
            'auto_delete_enabled': False,
            'description': 'Vehicle listings, condition reports'
        },
        {
            'data_category': 'shipment_records',
            'retention_days': 2190,  # 6 years
            'legal_basis': 'Transport Canada - commercial vehicle records',
            'auto_delete_enabled': False,
            'description': 'Shipment tracking, customs documentation, carrier records'
        },
    ]
    
    created = 0
    for policy_data in policies:
        policy, created_flag = DataRetentionPolicy.objects.get_or_create(
            data_category=policy_data['data_category'],
            defaults=policy_data
        )
        if created_flag:
            created += 1
            print(f"  ✓ {policy.get_data_category_display()}: {policy.retention_years():.1f} years")  # type: ignore[attr-defined]
        else:
            print(f"  → {policy.get_data_category_display()}: Already exists")  # type: ignore[attr-defined]
    
    print(f"\n✅ Created {created} retention policies")
    return DataRetentionPolicy.objects.count()


def create_sample_consents():
    """Create sample consent history records"""
    print("\n✅ Creating Sample Consent History...")
    
    # Get first 5 users for demo
    users = User.objects.all()[:5]
    if not users:
        print("  ⚠️  No users found. Run seed_tier_data.py first.")
        return 0
    
    consent_types = ['marketing', 'data_sharing', 'analytics', 'third_party', 'cross_border']
    created = 0
    
    for user in users:
        for consent_type in consent_types:
            # Create initial grant
            ConsentHistory.objects.create(
                user=user,
                consent_type=consent_type,
                action='granted',
                consent_given=True,
                privacy_policy_version='v2.1',
                consent_method='web_form',
                ip_address='192.168.1.1',
                consent_text=f'User granted {consent_type} consent',
                notes='Initial registration consent'
            )
            created += 1
    
    print(f"✅ Created {created} consent records for {len(users)} users")
    return created


def create_sample_pias():
    """Create sample Privacy Impact Assessments"""
    print("\n🔒 Creating Sample Privacy Impact Assessments...")
    
    # Get admin user
    admin = User.objects.filter(role='admin').first()
    if not admin:
        print("  ⚠️  No admin user found. Cannot create PIAs.")
        return 0
    
    pias = [
        {
            'title': 'AI-Powered Vehicle Valuation System',
            'description': 'Machine learning system for automated vehicle pricing using historical sales data',
            'project_name': 'ML Pricing Engine',
            'risk_level': 'medium',
            'data_types_processed': ['vehicle_history', 'market_data', 'user_preferences'],
            'cross_border_transfer': False,
            'identified_risks': 'Potential bias in pricing algorithms, data accuracy concerns',
            'mitigation_measures': 'Regular model audits, human oversight, bias testing',
            'status': 'approved',
            'assessed_by': admin,
            'approved_by': admin,
            'approval_date': timezone.now() - timedelta(days=30),
            'review_due_date': timezone.now() + timedelta(days=335)  # Annual review
        },
        {
            'title': 'Cross-Border Shipment Tracking',
            'description': 'System for tracking vehicles shipped from Canada to international buyers',
            'project_name': 'International Shipping Module',
            'risk_level': 'high',
            'data_types_processed': ['buyer_identity', 'payment_info', 'customs_data', 'gps_tracking'],
            'cross_border_transfer': True,
            'identified_risks': 'Data transfer to countries without adequate protection, GPS privacy concerns',
            'mitigation_measures': 'Standard contractual clauses, encryption, data minimization',
            'status': 'in_progress',
            'assessed_by': admin,
        },
        {
            'title': 'Dealer Performance Analytics Dashboard',
            'description': 'Analytics system for tracking dealer sales performance and customer satisfaction',
            'project_name': 'Dealer Analytics',
            'risk_level': 'low',
            'data_types_processed': ['sales_metrics', 'customer_reviews', 'response_times'],
            'cross_border_transfer': False,
            'identified_risks': 'Aggregated data may reveal dealer identity in small markets',
            'mitigation_measures': 'Minimum threshold for aggregation (5+ dealers), anonymization',
            'status': 'approved',
            'assessed_by': admin,
            'approved_by': admin,
            'approval_date': timezone.now() - timedelta(days=60),
            'review_due_date': timezone.now() + timedelta(days=305)
        },
    ]
    
    created = 0
    for pia_data in pias:
        pia, created_flag = PrivacyImpactAssessment.objects.get_or_create(
            title=pia_data['title'],
            defaults=pia_data
        )
        if created_flag:
            created += 1
            status_emoji = '✓' if pia.status == 'approved' else '⏳'
            risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴', 'critical': '⚠️'}[pia.risk_level]
            print(f"  {status_emoji} {risk_emoji} {pia.title} - {pia.get_status_display()}")  # type: ignore[attr-defined]
        else:
            print(f"  → {pia.title}: Already exists")
    
    print(f"\n✅ Created {created} Privacy Impact Assessments")
    return created


def create_sample_breaches():
    """Create sample data breach logs (for testing, not real breaches!)"""
    print("\n🚨 Creating Sample Data Breach Logs (DEMO DATA ONLY)...")
    
    admin = User.objects.filter(role='admin').first()
    if not admin:
        print("  ⚠️  No admin user found. Cannot create breach logs.")
        return 0
    
    breaches = [
        {
            'breach_date': timezone.now().date() - timedelta(days=90),
            'discovery_date': timezone.now() - timedelta(days=89),
            'severity': 'low',
            'status': 'resolved',
            'affected_users_count': 3,
            'data_types_compromised': 'Email addresses',
            'description': 'Minor email exposure in automated notification system',
            'attack_vector': 'Configuration error in email BCC field',
            'mitigation_steps': 'Fixed email template, notified affected users, no sensitive data exposed',
            'resolution_date': timezone.now().date() - timedelta(days=85),
            'users_notified_date': timezone.now().date() - timedelta(days=88),
            'reported_by': admin
        },
        {
            'breach_date': timezone.now().date() - timedelta(days=45),
            'discovery_date': timezone.now() - timedelta(days=44),
            'severity': 'medium',
            'status': 'resolved',
            'affected_users_count': 127,
            'data_types_compromised': 'Names, email addresses, phone numbers',
            'description': 'Unauthorized access to dealer contact list via misconfigured API endpoint',
            'attack_vector': 'API authentication bypass',
            'mitigation_steps': 'Fixed API authentication, rotated API keys, enhanced rate limiting',
            'resolution_date': timezone.now().date() - timedelta(days=38),
            'users_notified_date': timezone.now().date() - timedelta(days=43),
            'cai_notified_date': timezone.now().date() - timedelta(days=42),
            'reported_by': admin
        },
        {
            'breach_date': timezone.now().date() - timedelta(days=2),
            'discovery_date': timezone.now() - timedelta(hours=36),
            'severity': 'high',
            'status': 'containing',
            'affected_users_count': 1523,
            'data_types_compromised': 'Names, email addresses, hashed passwords, encrypted payment tokens',
            'description': 'SQL injection vulnerability in legacy search endpoint',
            'attack_vector': 'SQL injection via unsanitized search parameter',
            'mitigation_steps': 'Endpoint disabled, forensic analysis in progress, password reset initiated',
            'reported_by': admin,
            'users_notified_date': timezone.now().date() - timedelta(days=1),
            'cai_notified_date': timezone.now().date() - timedelta(days=1),
        },
    ]
    
    created = 0
    for breach_data in breaches:
        breach, created_flag = DataBreachLog.objects.get_or_create(
            breach_date=breach_data['breach_date'],
            discovery_date=breach_data['discovery_date'],
            defaults=breach_data
        )
        if created_flag:
            created += 1
            severity_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴', 'critical': '⚠️'}[breach.severity]
            status_emoji = '✓' if breach.status == 'resolved' else '⏳'
            within_72h = '✓' if breach.is_within_72_hours() else '❌'
            print(f"  {status_emoji} {severity_emoji} {breach.get_severity_display()} breach: {breach.affected_users_count} users")  # type: ignore[attr-defined]
            print(f"      Status: {breach.get_status_display()}, Within 72h: {within_72h}")  # type: ignore[attr-defined]
        else:
            print(f"  → Breach on {breach.breach_date}: Already exists")
    
    print(f"\n✅ Created {created} sample breach logs")
    return created


def main():
    print("=" * 60)
    print("COMPLIANCE DATA SEEDING")
    print("PIPEDA | Law 25 | SOC 2 Compliance")
    print("=" * 60)
    
    # Create data
    policy_count = create_retention_policies()
    consent_count = create_sample_consents()
    pia_count = create_sample_pias()
    breach_count = create_sample_breaches()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLIANCE DATA SUMMARY")
    print("=" * 60)
    print(f"Data Retention Policies:    {policy_count} policies")
    print(f"Consent History Records:    {consent_count} records")
    print(f"Privacy Impact Assessments: {pia_count} PIAs")
    print(f"Data Breach Logs:           {breach_count} breaches (DEMO)")
    print("=" * 60)
    print("\n✅ Compliance data seeded successfully!")
    print("\n🔐 Compliance Endpoints Available:")
    print("   • /api/accounts/compliance/retention-policies/")
    print("   • /api/accounts/compliance/consent-history/")
    print("   • /api/accounts/compliance/privacy-assessments/")
    print("   • /api/accounts/compliance/breaches/")
    print("\n📋 All endpoints include CSV export via /export_csv/ action")
    print()


if __name__ == '__main__':
    main()
