from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'company_name', 'country', 'is_active']
    list_filter = ['role', 'is_active', 'country']
    search_fields = ['username', 'email', 'company_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Role & Company'), {
            'fields': ('role', 'company_name', 'phone', 'address', 'country', 'preferred_language')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Role & Company'), {
            'fields': ('role', 'company_name', 'phone', 'address', 'country', 'preferred_language')
        }),
    )
