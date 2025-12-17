from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .models import Conversation, Message, MessageRead
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    MessageReadSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationDetailSerializer
    
    def get_queryset(self):
        """Get conversations where current user is a participant"""
        user = self.request.user
        return Conversation.objects.filter(
            Q(participant_1=user) | Q(participant_2=user)
        ).select_related('participant_1', 'participant_2', 'vehicle', 'deal')
    
    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """
        Start a new conversation with another user
        Expects: { "participant_id": 123, "vehicle_id": 456, "subject": "...", "initial_message": "..." }
        """
        participant_id = request.data.get('participant_id')
        vehicle_id = request.data.get('vehicle_id')
        subject = request.data.get('subject', '')
        initial_message = request.data.get('initial_message')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if conversation already exists
        existing = Conversation.objects.filter(
            Q(participant_1=request.user, participant_2_id=participant_id) |
            Q(participant_1_id=participant_id, participant_2=request.user)
        ).first()
        
        if existing:
            # Return existing conversation
            serializer = self.get_serializer(existing)
            return Response(serializer.data)
        
        # Create new conversation
        conversation = Conversation.objects.create(
            participant_1=request.user,
            participant_2_id=participant_id,
            vehicle_id=vehicle_id,
            subject=subject
        )
        
        # Send initial message if provided
        if initial_message:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=initial_message
            )
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark all messages in this conversation as read for current user"""
        conversation = self.get_object()
        conversation.mark_as_read(request.user)
        
        # Update is_read for all messages
        messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
        messages.update(is_read=True, read_at=timezone.now())
        
        return Response({'status': 'marked as read'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive this conversation"""
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.save()
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive this conversation"""
        conversation = self.get_object()
        conversation.is_archived = False
        conversation.save()
        return Response({'status': 'unarchived'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get total unread message count for current user"""
        user = request.user
        conversations = self.get_queryset()
        total_unread = sum([conv.get_unread_count(user) for conv in conversations])
        return Response({'unread_count': total_unread})


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Get messages from conversations where current user is a participant"""
        user = self.request.user
        conversation_id = self.request.query_params.get('conversation_id')
        
        queryset = Message.objects.filter(
            Q(conversation__participant_1=user) | Q(conversation__participant_2=user)
        ).select_related('sender', 'conversation')
        
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Automatically set sender to current user"""
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark this specific message as read"""
        message = self.get_object()
        
        if message.sender != request.user:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
            
            # Create read receipt
            MessageRead.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        return Response({'status': 'marked as read'})
