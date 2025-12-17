from django.contrib import admin
from .models import SavedSearch


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'user',
        'criteria_display',
        'match_count',
        'is_active',
        'email_notifications',
        'created_at',
    ]
    list_filter = [
        'is_active',
        'email_notifications',
        'notification_frequency',
        'condition',
        'created_at',
    ]
    search_fields = [
        'name',
        'user__email',
        'user__first_name',
        'user__last_name',
        'make',
        'model',
    ]
    readonly_fields = ['created_at', 'updated_at', 'last_notified_at', 'match_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Search Criteria', {
            'fields': (
                ('make', 'model'),
                ('year_min', 'year_max'),
                ('price_min', 'price_max'),
                'condition',
                'mileage_max',
            )
        }),
        ('Notification Settings', {
            'fields': (
                'email_notifications',
                'notification_frequency',
            )
        }),
        ('Statistics', {
            'fields': (
                'match_count',
                'last_notified_at',
                'created_at',
                'updated_at',
            )
        }),
    )
    
    def criteria_display(self, obj):
        """Display search criteria in admin list"""
        return obj.get_search_criteria_display()
    criteria_display.short_description = 'Search Criteria'
