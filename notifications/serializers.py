from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'title',
            'message',
            'is_read',
            'link',
            'related_id',
            'related_model',
            'created_at',
            'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']
