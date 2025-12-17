from django.db import models
from django.conf import settings
from vehicles.models import Vehicle


class PriceHistory(models.Model):
    """
    Track price changes for vehicles to enable price drop alerts.
    Each price change creates a new record.
    """
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Previous price"
    )
    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="New price after change"
    )
    price_difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Difference (new_price - old_price, negative = drop)"
    )
    percentage_change = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage change ((new-old)/old * 100)"
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notified_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='price_drop_notifications',
        help_text="Users who have been notified about this price change"
    )
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Price History'
        verbose_name_plural = 'Price Histories'
        indexes = [
            models.Index(fields=['vehicle', '-changed_at']),
            models.Index(fields=['-changed_at']),
        ]
    
    def __str__(self):
        direction = "↓" if self.price_difference < 0 else "↑"
        return f"{self.vehicle.vin} - ${self.old_price} {direction} ${self.new_price} ({self.percentage_change}%)"
    
    @property
    def is_price_drop(self):
        """Check if this represents a price decrease"""
        return self.price_difference < 0
    
    @property
    def amount_saved(self):
        """Get absolute amount saved (positive for drops)"""
        return abs(self.price_difference) if self.is_price_drop else 0
