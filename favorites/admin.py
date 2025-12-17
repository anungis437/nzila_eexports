from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'vehicle__make', 'vehicle__model', 'vehicle__vin']
    raw_id_fields = ['user', 'vehicle']
    date_hierarchy = 'created_at'
