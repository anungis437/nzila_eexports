from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Favorite(models.Model):
    """
    User favorites/watchlist for vehicles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['vehicle']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.vehicle}"
