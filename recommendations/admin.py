from django.contrib import admin
from .models import ViewHistory


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'session_id',
        'vehicle',
        'viewed_at',
    ]
    list_filter = [
        'viewed_at',
        'vehicle__make',
        'vehicle__condition',
    ]
    search_fields = [
        'user__username',
        'user__email',
        'session_id',
        'vehicle__vin',
        'vehicle__make',
        'vehicle__model',
    ]
    readonly_fields = ['viewed_at']
    date_hierarchy = 'viewed_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'session_id')
        }),
        ('Vehicle', {
            'fields': ('vehicle',)
        }),
        ('Tracking', {
            'fields': ('viewed_at',)
        }),
    )
