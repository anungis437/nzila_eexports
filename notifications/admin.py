from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Related Object', {
            'fields': ('link', 'related_id', 'related_model')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # Notifications should be created programmatically
        return request.user.is_superuser


admin.site.register(Notification, NotificationAdmin)
