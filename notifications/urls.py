from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.list_notifications, name='list_notifications'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
]
