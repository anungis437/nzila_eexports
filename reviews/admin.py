from django.contrib import admin
from .models import Review, ReviewHelpfulness, DealerRating


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'dealer', 'vehicle', 'rating', 'review_type', 
                    'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['review_type', 'rating', 'is_verified_purchase', 'is_approved', 
                   'would_recommend', 'created_at']
    search_fields = ['buyer__email', 'buyer__full_name', 'dealer__email', 
                     'title', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count', 'not_helpful_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('buyer', 'dealer', 'vehicle', 'review_type')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment', 'buyer_location', 'would_recommend')
        }),
        ('Detailed Ratings', {
            'fields': ('vehicle_condition_rating', 'communication_rating', 
                      'delivery_rating', 'value_rating'),
            'classes': ('collapse',)
        }),
        ('Status & Verification', {
            'fields': ('is_verified_purchase', 'is_approved', 'is_featured')
        }),
        ('Dealer Response', {
            'fields': ('dealer_response', 'responded_at'),
            'classes': ('collapse',)
        }),
        ('Helpfulness', {
            'fields': ('helpful_count', 'not_helpful_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReviewHelpfulness)
class ReviewHelpfulnessAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__title', 'user__email']


@admin.register(DealerRating)
class DealerRatingAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'average_rating', 'total_reviews', 
                    'recommend_percentage', 'last_updated']
    readonly_fields = ['total_reviews', 'average_rating', 'five_star_count',
                      'four_star_count', 'three_star_count', 'two_star_count',
                      'one_star_count', 'avg_vehicle_condition', 'avg_communication',
                      'avg_delivery', 'avg_value', 'recommend_count',
                      'recommend_percentage', 'last_updated']
    
    def has_add_permission(self, request):
        return False  # Created automatically
