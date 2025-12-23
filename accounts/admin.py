from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User
from .compliance_models import DataBreachLog, ConsentHistory, DataRetentionPolicy, PrivacyImpactAssessment

# Import dealer verification admin (will self-register)
from .dealer_verification_admin import DealerLicenseAdmin, DealerVerificationAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'company_name', 'country', 'is_diaspora_buyer', 'is_active', 'consent_status']
    list_filter = ['role', 'is_active', 'country', 'is_diaspora_buyer', 'canadian_province', 
                   'data_processing_consent', 'marketing_consent']
    search_fields = ['username', 'email', 'company_name', 'canadian_city', 'destination_country']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Role & Company'), {
            'fields': ('role', 'company_name', 'phone', 'address', 'country', 'preferred_language')
        }),
        (_('Canadian Diaspora Buyer Profile (Phase 1)'), {
            'fields': (
                'is_diaspora_buyer', 'canadian_city', 'canadian_province', 'canadian_postal_code',
                'destination_country', 'destination_city', 'buyer_type', 'residency_status',
                'prefers_in_person_inspection'
            ),
            'classes': ('collapse',)
        }),
        (_('Dealer Showroom Information (Phase 1)'), {
            'fields': (
                'showroom_address', 'showroom_city', 'showroom_province', 'showroom_postal_code',
                'showroom_phone', 'business_hours', 'allows_test_drives', 'requires_appointment'
            ),
            'classes': ('collapse',)
        }),
        (_('Canadian Phone Support (Phase 1)'), {
            'fields': (
                'toll_free_number', 'local_phone_number', 'phone_support_hours', 
                'preferred_contact_method'
            ),
            'classes': ('collapse',)
        }),
        (_('PIPEDA & Law 25 Compliance'), {
            'fields': (
                'data_processing_consent', 'marketing_consent', 'third_party_sharing_consent',
                'data_transfer_consent_africa', 'consent_date', 'consent_ip_address', 'consent_version',
                'data_export_requested_date', 'data_deletion_requested_date', 'data_rectification_requested_date'
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Role & Company'), {
            'fields': ('role', 'company_name', 'phone', 'address', 'country', 'preferred_language')
        }),
    )
    
    def consent_status(self, obj):
        """Display consent status with color coding"""
        if obj.data_processing_consent and obj.data_transfer_consent_africa:
            return format_html('<span style="color: green;">✓ Full Consent</span>')
        elif obj.data_processing_consent:
            return format_html('<span style="color: orange;">⚠ Partial</span>')
        else:
            return format_html('<span style="color: red;">✗ No Consent</span>')
    consent_status.short_description = 'Consent Status'


@admin.register(DataBreachLog)
class DataBreachLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'breach_date', 'discovery_date', 'severity', 'status', 'affected_users_count', 'compliance_status']
    list_filter = ['severity', 'status', 'discovery_date']
    search_fields = ['description', 'attack_vector']
    date_hierarchy = 'discovery_date'
    readonly_fields = ['created_at', 'updated_at', 'days_since_discovery']
    filter_horizontal = ['affected_users']
    
    fieldsets = (
        ('Breach Details', {
            'fields': ('breach_date', 'discovery_date', 'severity', 'status', 'description', 'attack_vector')
        }),
        ('Affected Data', {
            'fields': ('affected_users_count', 'affected_users', 'data_types_compromised')
        }),
        ('Notifications', {
            'fields': ('users_notified_date', 'cai_notified_date', 'opc_notified_date')
        }),
        ('Mitigation', {
            'fields': ('mitigation_steps', 'resolution_date')
        }),
        ('Audit Trail', {
            'fields': ('reported_by', 'created_at', 'updated_at', 'days_since_discovery'),
            'classes': ('collapse',)
        }),
    )
    
    def compliance_status(self, obj):
        """Display Law 25 72-hour compliance status"""
        if obj.is_within_72_hours():
            return format_html('<span style="color: green;">✓ Within 72h</span>')
        else:
            return format_html('<span style="color: red;">✗ Overdue</span>')
    compliance_status.short_description = 'Law 25 Compliance'
    
    def days_since_discovery(self, obj):
        return obj.days_since_discovery()
    days_since_discovery.short_description = 'Days Since Discovery'


@admin.register(ConsentHistory)
class ConsentHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'consent_type', 'action', 'consent_given', 'privacy_policy_version', 'timestamp']
    list_filter = ['consent_type', 'action', 'consent_given', 'timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'consent_type', 'action', 'consent_given', 'privacy_policy_version', 
                       'consent_method', 'ip_address', 'user_agent', 'consent_text', 'timestamp', 'notes']
    
    def has_add_permission(self, request):
        """Consent history is created automatically via API - no manual additions"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Consent history is immutable - never delete"""
        return False


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['data_category', 'retention_years_display', 'legal_basis', 'auto_delete_enabled', 'last_cleanup_date']
    list_filter = ['data_category', 'auto_delete_enabled']
    search_fields = ['data_category', 'legal_basis', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Policy Details', {
            'fields': ('data_category', 'retention_days', 'legal_basis', 'description')
        }),
        ('Automation', {
            'fields': ('auto_delete_enabled', 'last_cleanup_date')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def retention_years_display(self, obj):
        return f"{obj.retention_years()} years ({obj.retention_days} days)"
    retention_years_display.short_description = 'Retention Period'


@admin.register(PrivacyImpactAssessment)
class PrivacyImpactAssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_name', 'risk_level', 'status', 'cross_border_transfer', 'assessed_by', 'approval_date']
    list_filter = ['risk_level', 'status', 'cross_border_transfer']
    search_fields = ['title', 'project_name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Assessment Details', {
            'fields': ('title', 'description', 'project_name', 'risk_level')
        }),
        ('Data Processing', {
            'fields': ('data_types_processed', 'cross_border_transfer')
        }),
        ('Risk Analysis', {
            'fields': ('identified_risks', 'mitigation_measures')
        }),
        ('Approval Workflow', {
            'fields': ('status', 'assessed_by', 'approved_by', 'approval_date', 'review_due_date')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
