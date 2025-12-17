from django.db import models
from django.conf import settings
from django.utils import timezone
from vehicles.models import Vehicle


class Conversation(models.Model):
    """
    A conversation between two users (buyer <-> dealer or broker <-> dealer)
    """
    participant_1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_p1'
    )
    participant_2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_p2'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )
    deal = models.ForeignKey(
        'deals.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations'
    )
    subject = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    # Track unread counts per participant
    unread_count_p1 = models.IntegerField(default=0)
    unread_count_p2 = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['participant_1', '-updated_at']),
            models.Index(fields=['participant_2', '-updated_at']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['deal']),
            models.Index(fields=['is_archived']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['participant_1', 'participant_2'],
                name='unique_conversation_pair'
            )
        ]
    
    def __str__(self):
        return f"Conversation between {self.participant_1.email} and {self.participant_2.email}"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        if self.participant_1 == user:
            return self.participant_2
        return self.participant_1
    
    def get_unread_count(self, user):
        """Get unread count for a specific user"""
        if self.participant_1 == user:
            return self.unread_count_p1
        return self.unread_count_p2
    
    def mark_as_read(self, user):
        """Mark all messages as read for a specific user"""
        if self.participant_1 == user:
            self.unread_count_p1 = 0
        else:
            self.unread_count_p2 = 0
        self.save()
    
    def increment_unread(self, for_user):
        """Increment unread count for a specific user"""
        if self.participant_1 == for_user:
            self.unread_count_p1 += 1
        else:
            self.unread_count_p2 += 1
        self.save()


class Message(models.Model):
    """
    A message in a conversation
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    attachment = models.FileField(
        upload_to='message_attachments/%Y/%m/%d/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_system_message = models.BooleanField(default=False)  # For automated messages
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update conversation's updated_at and increment unread for recipient
        if is_new:
            self.conversation.updated_at = timezone.now()
            self.conversation.save()
            
            # Increment unread count for the recipient
            recipient = self.conversation.get_other_participant(self.sender)
            self.conversation.increment_unread(recipient)


class MessageRead(models.Model):
    """
    Track when a message was read by a user (read receipts)
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_receipts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reads'
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['message', 'user']]
        indexes = [
            models.Index(fields=['message', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} read message {self.message.id}"
