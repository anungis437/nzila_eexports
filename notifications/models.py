from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """
    Model for storing user notifications across the platform.
    """
    TYPE_CHOICES = [
        ('lead', 'Lead'),
        ('deal', 'Deal'),
        ('commission', 'Commission'),
        ('shipment', 'Shipment'),
        ('vehicle', 'Vehicle'),
        ('document', 'Document'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, null=True)
    
    # Related object references
    related_id = models.IntegerField(blank=True, null=True)
    related_model = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.title}"
    
    def mark_as_read(self):
        """Mark this notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
