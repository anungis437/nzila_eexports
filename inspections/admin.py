"""
PHASE 2 - Feature 6: Third-Party Inspection Integration

Django admin interface for inspections
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ThirdPartyInspector, InspectionReport, InspectorReview


@admin.register(ThirdPartyInspector)
class ThirdPartyInspectorAdmin(admin.ModelAdmin):
    """Admin interface for third-party inspectors"""
    
    list_display = [
        'company', 'name', 'city', 'province', 'rating_display',
        'total_inspections', 'total_reviews', 'verification_status',
        'is_active', 'created_at'
    ]
    list_filter = [
        'province', 'certifications', 'is_active', 'is_verified',
        'mobile_service', 'created_at'
    ]
    search_fields = ['company', 'name', 'city', 'email', 'phone']
    ordering = ['-rating', '-total_inspections']
    readonly_fields = ['rating', 'total_inspections', 'total_reviews', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company', 'email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'province', 'postal_code', 'latitude', 'longitude')
        }),
        ('Qualifications', {
            'fields': (
                'certifications', 'additional_certifications',
                'years_experience', 'specializations'
            )
        }),
        ('Services & Pricing', {
            'fields': (
                'mobile_service', 'service_radius_km',
                'inspection_fee', 'mobile_fee_extra'
            )
        }),
        ('Statistics', {
            'fields': ('rating', 'total_inspections', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """Display rating with stars"""
        if obj.rating > 0:
            stars = '⭐' * int(obj.rating)
            return format_html(
                '<span title="{}">{} {}</span>',
                f'{obj.rating}/5.00',
                stars,
                f'({obj.rating})'
            )
        return '-'
    rating_display.short_description = 'Rating'
    
    def verification_status(self, obj):
        """Display verification status with icon"""
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: orange;">⚠ Not Verified</span>')
    verification_status.short_description = 'Verification'
    
    actions = ['mark_verified', 'mark_unverified', 'mark_active', 'mark_inactive']
    
    def mark_verified(self, request, queryset):
        """Mark selected inspectors as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} inspectors marked as verified.')
    mark_verified.short_description = 'Mark selected as verified'
    
    def mark_unverified(self, request, queryset):
        """Mark selected inspectors as unverified"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} inspectors marked as unverified.')
    mark_unverified.short_description = 'Mark selected as unverified'
    
    def mark_active(self, request, queryset):
        """Mark selected inspectors as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} inspectors marked as active.')
    mark_active.short_description = 'Mark selected as active'
    
    def mark_inactive(self, request, queryset):
        """Mark selected inspectors as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} inspectors marked as inactive.')
    mark_inactive.short_description = 'Mark selected as inactive'


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    """Admin interface for inspection reports"""
    
    list_display = [
        'id', 'vehicle_display', 'inspector_display', 'buyer_display',
        'report_type', 'inspection_date', 'status', 'condition_display',
        'payment_status', 'created_at'
    ]
    list_filter = [
        'status', 'report_type', 'overall_condition',
        'payment_status', 'inspection_date', 'created_at'
    ]
    search_fields = [
        'vehicle__make', 'vehicle__model', 'vehicle__vin',
        'inspector__company', 'buyer__username', 'buyer__email'
    ]
    ordering = ['-inspection_date', '-created_at']
    readonly_fields = ['created_at', 'updated_at', 'average_score_display']
    
    fieldsets = (
        ('Relationships', {
            'fields': ('vehicle', 'inspector', 'buyer')
        }),
        ('Inspection Details', {
            'fields': (
                'report_type', 'inspection_date', 'report_file', 'status'
            )
        }),
        ('Findings', {
            'fields': (
                'overall_condition', 'issues_found', 'recommendations',
                'estimated_repair_cost'
            )
        }),
        ('Component Scores', {
            'fields': (
                'engine_score', 'transmission_score', 'suspension_score',
                'brakes_score', 'body_score', 'interior_score',
                'average_score_display'
            ),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': ('inspection_fee_paid', 'payment_status')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_display(self, obj):
        """Display vehicle information"""
        return f"{obj.vehicle.year} {obj.vehicle.make} {obj.vehicle.model}"
    vehicle_display.short_description = 'Vehicle'
    
    def inspector_display(self, obj):
        """Display inspector company"""
        return obj.inspector.company
    inspector_display.short_description = 'Inspector'
    
    def buyer_display(self, obj):
        """Display buyer username"""
        return obj.buyer.username
    buyer_display.short_description = 'Buyer'
    
    def condition_display(self, obj):
        """Display condition with color coding"""
        if not obj.overall_condition:
            return '-'
        
        colors = {
            'excellent': 'green',
            'good': 'darkgreen',
            'fair': 'orange',
            'poor': 'red',
            'not_recommended': 'darkred'
        }
        color = colors.get(obj.overall_condition, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_overall_condition_display()
        )
    condition_display.short_description = 'Condition'
    
    def average_score_display(self, obj):
        """Display average component score"""
        avg = obj.get_average_score()
        if avg is not None:
            return f"{avg}/10"
        return '-'
    average_score_display.short_description = 'Average Score'
    
    actions = ['mark_completed', 'mark_paid']
    
    def mark_completed(self, request, queryset):
        """Mark selected inspections as completed"""
        for report in queryset:
            if report.status != 'completed':
                report.mark_completed()
        self.message_user(request, f'{queryset.count()} inspections marked as completed.')
    mark_completed.short_description = 'Mark selected as completed'
    
    def mark_paid(self, request, queryset):
        """Mark selected inspections as paid"""
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f'{updated} inspections marked as paid.')
    mark_paid.short_description = 'Mark selected as paid'


@admin.register(InspectorReview)
class InspectorReviewAdmin(admin.ModelAdmin):
    """Admin interface for inspector reviews"""
    
    list_display = [
        'id', 'inspector_display', 'buyer_display', 'rating_display',
        'helpful_votes', 'is_verified_purchase', 'is_published', 'created_at'
    ]
    list_filter = [
        'rating', 'is_verified_purchase', 'is_published', 'created_at'
    ]
    search_fields = [
        'inspector__company', 'buyer__username',
        'review_text'
    ]
    ordering = ['-created_at']
    readonly_fields = ['helpful_votes', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Relationships', {
            'fields': ('inspector', 'buyer', 'inspection_report')
        }),
        ('Rating', {
            'fields': ('rating',)
        }),
        ('Review', {
            'fields': ('review_text',)
        }),
        ('Detailed Ratings', {
            'fields': (
                'professionalism_rating', 'thoroughness_rating',
                'communication_rating', 'value_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_published', 'helpful_votes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def inspector_display(self, obj):
        """Display inspector company"""
        return obj.inspector.company
    inspector_display.short_description = 'Inspector'
    
    def buyer_display(self, obj):
        """Display buyer username"""
        return obj.buyer.username
    buyer_display.short_description = 'Reviewer'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '⭐' * obj.rating
        return format_html(
            '<span title="{}/5">{}</span>',
            obj.rating,
            stars
        )
    rating_display.short_description = 'Rating'
    
    actions = ['publish_reviews', 'unpublish_reviews']
    
    def publish_reviews(self, request, queryset):
        """Publish selected reviews"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} reviews published.')
    publish_reviews.short_description = 'Publish selected reviews'
    
    def unpublish_reviews(self, request, queryset):
        """Unpublish selected reviews"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} reviews unpublished.')
    unpublish_reviews.short_description = 'Unpublish selected reviews'
