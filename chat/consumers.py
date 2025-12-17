"""
WebSocket Consumers for Real-Time Chat

This module implements WebSocket consumers for real-time messaging functionality.
Consumers handle WebSocket connections, message broadcasting, typing indicators,
and read receipts.
"""

import json
import logging
from typing import Any, Dict, Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Conversation, Message, MessageRead

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.
    
    Handles:
    - Connection/disconnection
    - Message sending/receiving
    - Typing indicators
    - Read receipts
    - Presence updates
    
    URL pattern: /ws/chat/<conversation_id>/
    """
    
    async def connect(self) -> None:
        """Handle WebSocket connection."""
        self.conversation_id = self.scope.get('url_route', {}).get('kwargs', {}).get('conversation_id')
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope.get('user')
        
        # Verify user is authenticated
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user is participant in conversation
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection success message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'conversation_id': self.conversation_id,
            'timestamp': timezone.now().isoformat()
        }))
        
        # Notify other participant that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'status': 'online'
            }
        )
        
        logger.info(f"User {self.user.id} connected to conversation {self.conversation_id}")
    
    async def disconnect(self, code: int) -> None:
        """Handle WebSocket disconnection."""
        # Notify other participant that user is offline
        if hasattr(self, 'user') and self.user:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        if hasattr(self, 'user') and self.user:
            logger.info(f"User {self.user.id} disconnected from conversation {self.conversation_id}")
    
    async def receive(self, text_data: Optional[str] = None, bytes_data: Optional[bytes] = None) -> None:
        """
        Handle incoming WebSocket messages.
        
        Message types:
        - message: Send a chat message
        - typing: Send typing indicator
        - read: Mark messages as read
        """
        if not text_data:
            return
            
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read':
                await self.handle_read(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal error'
            }))
    
    async def handle_message(self, data: Dict[str, Any]) -> None:
        """Handle incoming chat message."""
        if not self.user:
            return
            
        content = data.get('message', '').strip()
        
        if not content:
            return
        
        # Save message to database
        message = await self.save_message(content)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name() or self.user.username,
                'content': content,
                'timestamp': message.created_at.isoformat(),
                'is_read': False
            }
        )
    
    async def handle_typing(self, data: Dict[str, Any]) -> None:
        """Handle typing indicator."""
        if not self.user:
            return
            
        is_typing = data.get('is_typing', False)
        
        # Broadcast typing status to room (excluding sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'user_name': self.user.get_full_name() or self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read(self, data: Dict[str, Any]) -> None:
        """Handle read receipt."""
        if not self.user:
            return
            
        message_ids = data.get('message_ids', [])
        
        if message_ids:
            await self.mark_messages_read(message_ids)
            
            # Notify sender that messages were read
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'message_ids': message_ids,
                    'reader_id': self.user.id,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    # WebSocket event handlers (called by channel_layer.group_send)
    
    async def chat_message(self, event: Dict[str, Any]) -> None:
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))
    
    async def user_typing(self, event: Dict[str, Any]) -> None:
        """Send typing indicator to WebSocket."""
        if not self.user:
            return
            
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))
    
    async def user_status(self, event: Dict[str, Any]) -> None:
        """Send user status to WebSocket."""
        if not self.user:
            return
            
        # Don't send status update to the user themselves
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'status',
                'user_id': event['user_id'],
                'status': event['status']
            }))
    
    async def messages_read(self, event: Dict[str, Any]) -> None:
        """Send read receipt to WebSocket."""
        if not self.user:
            return
            
        # Only send to sender (not the reader)
        if event['reader_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'read',
                'message_ids': event['message_ids'],
                'reader_id': event['reader_id'],
                'timestamp': event['timestamp']
            }))
    
    # Database operations (synchronous functions called via database_sync_to_async)
    
    @database_sync_to_async
    def check_participant(self):
        """Check if user is participant in conversation."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participant_1 == self.user or conversation.participant_2 == self.user
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content: str) -> Message:
        """Save message to database."""
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        
        # Update conversation's unread count for the other participant
        if conversation.participant_1 == self.user:
            conversation.unread_count_p2 += 1
        else:
            conversation.unread_count_p1 += 1
        conversation.save(update_fields=['unread_count_p1', 'unread_count_p2'])
        
        return message
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read."""
        messages = Message.objects.filter(
            id__in=message_ids,
            conversation_id=self.conversation_id
        ).exclude(sender=self.user)
        
        for message in messages:
            message.is_read = True
            message.read_at = timezone.now()
            message.save(update_fields=['is_read', 'read_at'])
            
            # Create MessageRead record
            MessageRead.objects.get_or_create(
                message=message,
                reader=self.user,
                defaults={'read_at': timezone.now()}
            )
        
        # Update conversation's unread count
        conversation = Conversation.objects.get(id=self.conversation_id)
        if conversation.participant_1 == self.user:
            conversation.unread_count_p1 = max(0, conversation.unread_count_p1 - len(message_ids))
        else:
            conversation.unread_count_p2 = max(0, conversation.unread_count_p2 - len(message_ids))
        conversation.save(update_fields=['unread_count_p1', 'unread_count_p2'])
