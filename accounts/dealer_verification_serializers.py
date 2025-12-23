"""
Dealer Verification Serializers
Phase 3 - Feature 9
"""

from rest_framework import serializers
from accounts.dealer_verification_models import DealerLicense, DealerVerification
from accounts.models import User


class DealerLicenseSerializer(serializers.ModelSerializer):
    """Serializer for dealer licenses"""
    
    dealer_username = serializers.CharField(source='dealer.username', read_only=True)
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    expires_soon = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    verified_by_username = serializers.CharField(source='verified_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = DealerLicense
        fields = [
            'id', 'dealer', 'dealer_username', 'license_type', 'license_type_display',
            'license_number', 'issuing_authority', 'province', 'province_display',
            'issue_date', 'expiry_date', 'status', 'status_display',
            'document', 'verified_by', 'verified_by_username', 'verified_at',
            'rejection_reason', 'is_expired', 'expires_soon', 'days_until_expiry',
            'created_at', 'updated_at', 'notes'
        ]
        read_only_fields = ['verified_by', 'verified_at', 'created_at', 'updated_at', 'status']


class DealerLicenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/submitting new licenses"""
    
    class Meta:
        model = DealerLicense
        fields = [
            'license_type', 'license_number', 'issuing_authority',
            'province', 'issue_date', 'expiry_date', 'document'
        ]
    
    def create(self, validated_data):
        # Automatically set dealer to the current user
        validated_data['dealer'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class DealerLicenseApprovalSerializer(serializers.Serializer):
    """Serializer for license approval/rejection"""
    
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Rejection reason is required when rejecting a license.'
            })
        return data


class DealerVerificationSerializer(serializers.ModelSerializer):
    """Serializer for dealer verification status"""
    
    dealer_username = serializers.CharField(source='dealer.username', read_only=True)
    dealer_email = serializers.EmailField(source='dealer.email', read_only=True)
    dealer_company = serializers.CharField(source='dealer.company_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    badge_display = serializers.CharField(source='get_badge_display', read_only=True)
    verification_percentage = serializers.FloatField(read_only=True)
    has_active_licenses = serializers.BooleanField(read_only=True)
    verified_by_username = serializers.CharField(source='verified_by.username', read_only=True, allow_null=True)
    
    # License summary
    total_licenses = serializers.SerializerMethodField()
    verified_licenses = serializers.SerializerMethodField()
    
    class Meta:
        model = DealerVerification
        fields = [
            'id', 'dealer', 'dealer_username', 'dealer_email', 'dealer_company',
            'status', 'status_display', 'badge', 'badge_display',
            'business_name', 'business_number', 'years_in_business', 'business_start_date',
            'has_insurance', 'insurance_provider', 'insurance_policy_number', 'insurance_expiry',
            'total_sales', 'total_revenue', 'average_rating', 'total_reviews',
            'trust_score', 'license_verified', 'insurance_verified', 'business_verified',
            'identity_verified', 'address_verified', 'verification_percentage',
            'has_active_licenses', 'total_licenses', 'verified_licenses',
            'verified_at', 'verified_by', 'verified_by_username',
            'created_at', 'updated_at', 'notes'
        ]
        read_only_fields = [
            'trust_score', 'badge', 'verified_at', 'verified_by', 'created_at', 'updated_at'
        ]
    
    def get_total_licenses(self, obj):
        return obj.dealer.licenses.count()
    
    def get_verified_licenses(self, obj):
        return obj.dealer.licenses.filter(status='verified').count()


class DealerVerificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating dealer verification details"""
    
    class Meta:
        model = DealerVerification
        fields = [
            'business_name', 'business_number', 'years_in_business', 'business_start_date',
            'has_insurance', 'insurance_provider', 'insurance_policy_number', 'insurance_expiry',
        ]


class DealerVerificationActionSerializer(serializers.Serializer):
    """Serializer for admin verification actions"""
    
    action = serializers.ChoiceField(choices=['verify', 'suspend'], required=True)
    verification_type = serializers.ChoiceField(
        choices=['license', 'insurance', 'business', 'identity', 'address'],
        required=False
    )
    value = serializers.BooleanField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    suspension_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['action'] == 'verify' and not data.get('verification_type'):
            raise serializers.ValidationError({
                'verification_type': 'Verification type is required for verify action.'
            })
        if data['action'] == 'suspend' and not data.get('suspension_reason'):
            raise serializers.ValidationError({
                'suspension_reason': 'Suspension reason is required.'
            })
        return data


class DealerBadgeSerializer(serializers.Serializer):
    """Simple serializer for badge display"""
    
    dealer_id = serializers.IntegerField()
    dealer_username = serializers.CharField()
    badge = serializers.CharField()
    badge_display = serializers.CharField()
    trust_score = serializers.IntegerField()
    verification_percentage = serializers.FloatField()
    total_sales = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
