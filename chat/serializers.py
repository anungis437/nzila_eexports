from rest_framework import serializers
from .models import Conversation, Message, MessageRead
from accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_email', 'sender_name',
            'content', 'attachment', 'attachment_url', 'created_at',
            'is_read', 'read_at', 'is_system_message'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'is_read', 'read_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if hasattr(obj.sender, 'get_full_name') else obj.sender.email
    
    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing conversations
    """
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'other_participant', 'subject', 'last_message',
            'unread_count', 'vehicle_info', 'created_at', 'updated_at',
            'is_archived'
        ]
    
    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return {
                'id': other.id,
                'email': other.email,
                'full_name': other.get_full_name() if hasattr(other, 'get_full_name') else other.email,
                'role': other.role if hasattr(other, 'role') else None
            }
        return None
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content[:100],
                'created_at': last_msg.created_at,
                'sender_email': last_msg.sender.email
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_unread_count(request.user)
        return 0
    
    def get_vehicle_info(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'make': obj.vehicle.make,
                'model': obj.vehicle.model,
                'year': obj.vehicle.year,
                'vin': obj.vehicle.vin
            }
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer with all messages
    """
    messages = MessageSerializer(many=True, read_only=True)
    participant_1_info = UserSerializer(source='participant_1', read_only=True)
    participant_2_info = UserSerializer(source='participant_2', read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participant_1', 'participant_2', 'participant_1_info',
            'participant_2_info', 'vehicle', 'vehicle_info', 'deal', 'subject',
            'messages', 'unread_count', 'created_at', 'updated_at', 'is_archived'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_vehicle_info(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'make': obj.vehicle.make,
                'model': obj.vehicle.model,
                'year': obj.vehicle.year,
                'vin': obj.vehicle.vin,
                'price_cad': float(obj.vehicle.price_cad) if obj.vehicle.price_cad else None
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_unread_count(request.user)
        return 0


class MessageReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageRead
        fields = ['id', 'message', 'user', 'read_at']
        read_only_fields = ['id', 'read_at']
