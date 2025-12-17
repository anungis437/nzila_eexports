from django.contrib import admin
from .models import Conversation, Message, MessageRead


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'created_at', 'read_at')
    fields = ('sender', 'content', 'is_read', 'created_at')
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant_1', 'participant_2', 'subject', 'vehicle', 'deal', 'created_at', 'updated_at', 'is_archived')
    list_filter = ('is_archived', 'created_at', 'updated_at')
    search_fields = ('participant_1__email', 'participant_2__email', 'subject', 'vehicle__vin')
    readonly_fields = ('created_at', 'updated_at', 'unread_count_p1', 'unread_count_p2')
    inlines = [MessageInline]
    
    fieldsets = (
        ('Participants', {
            'fields': ('participant_1', 'participant_2')
        }),
        ('Context', {
            'fields': ('vehicle', 'deal', 'subject')
        }),
        ('Status', {
            'fields': ('is_archived', 'unread_count_p1', 'unread_count_p2')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content_preview', 'is_read', 'is_system_message', 'created_at')
    list_filter = ('is_read', 'is_system_message', 'created_at')
    search_fields = ('sender__email', 'content', 'conversation__subject')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('conversation', 'sender', 'content', 'attachment')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_system_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__email', 'message__content')
    readonly_fields = ('read_at',)
