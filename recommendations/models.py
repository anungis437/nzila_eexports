from django.db import models
from django.conf import settings
from vehicles.models import Vehicle


class ViewHistory(models.Model):
    """
    Track vehicle views for recommendation algorithms.
    Used for collaborative filtering (users who viewed X also viewed Y).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='view_history',
        help_text="User who viewed the vehicle (null for anonymous users)"
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Session ID for anonymous users"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='view_records'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        verbose_name = 'View History'
        verbose_name_plural = 'View Histories'
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['session_id', '-viewed_at']),
            models.Index(fields=['vehicle', '-viewed_at']),
        ]
    
    def __str__(self):
        user_identifier = self.user.username if self.user else self.session_id
        return f"{user_identifier} viewed {self.vehicle.vin} at {self.viewed_at}"
