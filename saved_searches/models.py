from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class SavedSearch(models.Model):
    """
    Store user search criteria and send email alerts when new matching vehicles arrive.
    Supports all filters from BuyerPortal: make, year range, price range, condition, mileage, etc.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(
        max_length=255,
        help_text="User-friendly name for this saved search (e.g., 'Toyota Camry under $15k')"
    )
    
    # Search criteria fields (matching BuyerPortal filters)
    make = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    year_min = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    year_max = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    price_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    price_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    condition = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('salvage', 'Salvage'),
        ]
    )
    mileage_max = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Notification settings
    email_notifications = models.BooleanField(
        default=True,
        help_text="Send email when new matching vehicles are added"
    )
    notification_frequency = models.CharField(
        max_length=20,
        default='immediate',
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
        ]
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_notified_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    match_count = models.IntegerField(
        default=0,
        help_text="Number of vehicles currently matching this search"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['email_notifications', 'notification_frequency']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    def get_search_criteria_display(self):
        """Return human-readable description of search criteria"""
        criteria = []
        if self.make:
            criteria.append(f"Make: {self.make}")
        if self.model:
            criteria.append(f"Model: {self.model}")
        if self.year_min or self.year_max:
            if self.year_min and self.year_max:
                criteria.append(f"Year: {self.year_min}-{self.year_max}")
            elif self.year_min:
                criteria.append(f"Year: {self.year_min}+")
            else:
                criteria.append(f"Year: up to {self.year_max}")
        if self.price_min or self.price_max:
            if self.price_min and self.price_max:
                criteria.append(f"Price: ${self.price_min:,.0f}-${self.price_max:,.0f}")
            elif self.price_min:
                criteria.append(f"Price: ${self.price_min:,.0f}+")
            else:
                criteria.append(f"Price: up to ${self.price_max:,.0f}")
        if self.condition:
            criteria.append(f"Condition: {self.get_condition_display()}")
        if self.mileage_max:
            criteria.append(f"Mileage: up to {self.mileage_max:,} km")
        
        return ', '.join(criteria) if criteria else 'All vehicles'
