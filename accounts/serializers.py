from rest_framework import serializers
from .models import User
from .compliance_models import (
    DataBreachLog, ConsentHistory, 
    DataRetentionPolicy, PrivacyImpactAssessment
)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'company_name', 'phone', 'country', 'preferred_language',
                  'is_staff', 'is_superuser', 'is_active',
                  # Phase 1: Diaspora buyer fields
                  'is_diaspora_buyer', 'canadian_city', 'canadian_province', 
                  'canadian_postal_code', 'destination_country', 'destination_city',
                  'buyer_type', 'residency_status', 'prefers_in_person_inspection',
                  # Phase 1: Dealer showroom fields
                  'showroom_address', 'showroom_city', 'showroom_province',
                  'showroom_postal_code', 'showroom_phone', 'business_hours',
                  'allows_test_drives', 'requires_appointment',
                  # Phase 1: Canadian phone support
                  'toll_free_number', 'local_phone_number', 'phone_support_hours',
                  'preferred_contact_method']
        read_only_fields = ['id', 'is_staff', 'is_superuser']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'company_name', 'phone', 'address', 'country', 
                  'preferred_language', 'is_staff', 'is_superuser', 'is_active',
                  # Phase 1: Diaspora buyer fields
                  'is_diaspora_buyer', 'canadian_city', 'canadian_province', 
                  'canadian_postal_code', 'destination_country', 'destination_city',
                  'buyer_type', 'residency_status', 'prefers_in_person_inspection',
                  # Phase 1: Dealer showroom fields
                  'showroom_address', 'showroom_city', 'showroom_province',
                  'showroom_postal_code', 'showroom_phone', 'business_hours',
                  'allows_test_drives', 'requires_appointment',
                  # Phase 1: Canadian phone support
                  'toll_free_number', 'local_phone_number', 'phone_support_hours',
                  'preferred_contact_method']
        read_only_fields = ['id', 'username', 'role', 'is_staff', 'is_superuser']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


# ==================== COMPLIANCE SERIALIZERS ====================

class DataBreachLogSerializer(serializers.ModelSerializer):
    """Serializer for data breach tracking (Law 25, PIPEDA)"""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    days_since_discovery = serializers.IntegerField(read_only=True)
    is_within_72_hours = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DataBreachLog
        fields = [
            'id', 'breach_date', 'discovery_date', 'severity', 'severity_display',
            'status', 'status_display', 'affected_users_count', 'data_types_compromised',
            'description', 'attack_vector', 'users_notified_date', 'cai_notified_date',
            'opc_notified_date', 'mitigation_steps', 'resolution_date', 'reported_by',
            'reported_by_name', 'days_since_discovery', 'is_within_72_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'days_since_discovery', 
                           'is_within_72_hours', 'reported_by_name']
    
    def create(self, validated_data):
        # Automatically set reported_by to current user
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)


class ConsentHistorySerializer(serializers.ModelSerializer):
    """Serializer for consent tracking (PIPEDA Principle 8)"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    consent_type_display = serializers.CharField(source='get_consent_type_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ConsentHistory
        fields = [
            'id', 'user', 'user_name', 'user_email', 'consent_type', 'consent_type_display',
            'action', 'action_display', 'consent_given', 'privacy_policy_version',
            'consent_method', 'ip_address', 'user_agent', 'consent_text', 'timestamp',
            'notes'
        ]
        read_only_fields = ['id', 'timestamp', 'user_name', 'user_email']


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    """Serializer for data retention policies (Law 25 Article 11)"""
    data_category_display = serializers.CharField(source='get_data_category_display', read_only=True)
    retention_years = serializers.FloatField(read_only=True)
    
    class Meta:
        model = DataRetentionPolicy
        fields = [
            'id', 'data_category', 'data_category_display', 'retention_days',
            'retention_years', 'legal_basis', 'auto_delete_enabled', 'last_cleanup_date',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'retention_years']


class PrivacyImpactAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Privacy Impact Assessments (Law 25 Article 3.3)"""
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assessed_by_name = serializers.CharField(source='assessed_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = PrivacyImpactAssessment
        fields = [
            'id', 'title', 'description', 'project_name', 'risk_level', 'risk_level_display',
            'data_types_processed', 'cross_border_transfer', 'identified_risks',
            'mitigation_measures', 'status', 'status_display', 'assessed_by',
            'assessed_by_name', 'approved_by', 'approved_by_name', 'approval_date',
            'review_due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'assessed_by_name', 
                           'approved_by_name']
    
    def create(self, validated_data):
        # Automatically set assessed_by to current user
        validated_data['assessed_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
