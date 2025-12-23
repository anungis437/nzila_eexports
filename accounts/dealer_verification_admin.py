"""
Dealer Verification Admin
Phase 3 - Feature 9
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from accounts.dealer_verification_models import DealerLicense, DealerVerification


@admin.register(DealerLicense)
class DealerLicenseAdmin(admin.ModelAdmin):
    """Admin interface for dealer licenses"""
    
    list_display = [
        'dealer', 'license_type', 'license_number', 'province',
        'status_badge', 'expiry_date', 'expires_soon_badge', 'created_at'
    ]
    list_filter = ['status', 'license_type', 'province', 'created_at']
    search_fields = ['dealer__username', 'dealer__email', 'license_number', 'issuing_authority']
    readonly_fields = ['verified_by', 'verified_at', 'created_at', 'updated_at', 'is_expired', 'days_until_expiry']
    
    fieldsets = [
        ('License Information', {
            'fields': ('dealer', 'license_type', 'license_number', 'issuing_authority', 'province')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date', 'is_expired', 'days_until_expiry')
        }),
        ('Status', {
            'fields': ('status', 'document')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at', 'rejection_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        }),
    ]
    
    actions = ['approve_licenses', 'reject_licenses']
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': 'orange',
            'verified': 'green',
            'expired': 'red',
            'rejected': 'red',
            'suspended': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def expires_soon_badge(self, obj):
        """Display expiration warning"""
        if obj.is_expired:
            return format_html('<span style="color: red;">❌ Expired</span>')
        elif obj.expires_soon:
            return format_html('<span style="color: orange;">⚠️ {} days</span>', obj.days_until_expiry)
        else:
            return format_html('<span style="color: green;">✓ Valid</span>')
    expires_soon_badge.short_description = 'Expires'
    
    def approve_licenses(self, request, queryset):
        """Bulk approve licenses"""
        count = 0
        for license in queryset.filter(status='pending'):
            license.approve(request.user)
            count += 1
        
        self.message_user(request, f'{count} license(s) approved successfully.')
    approve_licenses.short_description = 'Approve selected licenses'
    
    def reject_licenses(self, request, queryset):
        """Bulk reject licenses"""
        count = 0
        for license in queryset.filter(status='pending'):
            license.reject(request.user, 'Rejected by admin')
            count += 1
        
        self.message_user(request, f'{count} license(s) rejected.')
    reject_licenses.short_description = 'Reject selected licenses'


@admin.register(DealerVerification)
class DealerVerificationAdmin(admin.ModelAdmin):
    """Admin interface for dealer verifications"""
    
    list_display = [
        'dealer', 'status_badge', 'badge_display', 'trust_score_display',
        'verification_progress', 'total_sales', 'average_rating', 'verified_at'
    ]
    list_filter = ['status', 'badge', 'license_verified', 'insurance_verified', 'business_verified']
    search_fields = ['dealer__username', 'dealer__email', 'business_name', 'business_number']
    readonly_fields = [
        'trust_score', 'badge', 'verification_percentage',
        'has_active_licenses', 'verified_at', 'verified_by',
        'created_at', 'updated_at'
    ]
    
    fieldsets = [
        ('Dealer', {
            'fields': ('dealer', 'status', 'badge', 'trust_score')
        }),
        ('Business Information', {
            'fields': (
                'business_name', 'business_number', 'years_in_business', 'business_start_date'
            )
        }),
        ('Insurance', {
            'fields': (
                'has_insurance', 'insurance_provider', 'insurance_policy_number', 'insurance_expiry'
            )
        }),
        ('Sales Metrics', {
            'fields': ('total_sales', 'total_revenue', 'average_rating', 'total_reviews')
        }),
        ('Verification Flags', {
            'fields': (
                'license_verified', 'insurance_verified', 'business_verified',
                'identity_verified', 'address_verified', 'verification_percentage'
            )
        }),
        ('Status', {
            'fields': ('verified_at', 'verified_by', 'has_active_licenses')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        }),
    ]
    
    actions = ['verify_dealers', 'update_metrics', 'suspend_dealers']
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'unverified': 'gray',
            'pending': 'orange',
            'verified': 'green',
            'suspended': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def badge_display(self, obj):
        """Display badge with icon"""
        icons = {
            'gold': '🥇',
            'silver': '🥈',
            'bronze': '🥉',
            'none': '⚪',
        }
        icon = icons.get(obj.badge, '')
        return format_html('{} {}', icon, obj.get_badge_display())
    badge_display.short_description = 'Badge'
    
    def trust_score_display(self, obj):
        """Display trust score with color"""
        if obj.trust_score >= 80:
            color = 'green'
        elif obj.trust_score >= 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="font-weight: bold; color: {};">{}/100</span>',
            color,
            obj.trust_score
        )
    trust_score_display.short_description = 'Trust Score'
    
    def verification_progress(self, obj):
        """Display verification percentage as progress bar"""
        percentage = obj.verification_percentage
        if percentage >= 80:
            color = 'green'
        elif percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; padding: 2px; text-align: center; border-radius: 3px; color: white;">'
            '{}%'
            '</div></div>',
            percentage, color, int(percentage)
        )
    verification_progress.short_description = 'Progress'
    
    def verify_dealers(self, request, queryset):
        """Bulk verify dealers"""
        count = 0
        for verification in queryset:
            verification.verify_dealer(request.user)
            count += 1
        
        self.message_user(request, f'{count} dealer(s) verified successfully.')
    verify_dealers.short_description = 'Verify selected dealers'
    
    def update_metrics(self, request, queryset):
        """Bulk update metrics"""
        count = 0
        for verification in queryset:
            verification.update_metrics()
            count += 1
        
        self.message_user(request, f'{count} dealer verification(s) updated.')
    update_metrics.short_description = 'Update metrics for selected dealers'
    
    def suspend_dealers(self, request, queryset):
        """Bulk suspend dealers"""
        count = 0
        for verification in queryset:
            verification.suspend_dealer('Suspended by admin')
            count += 1
        
        self.message_user(request, f'{count} dealer(s) suspended.')
    suspend_dealers.short_description = 'Suspend selected dealers'
