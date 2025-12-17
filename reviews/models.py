from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from vehicles.models import Vehicle
from nzila_export.sanitizers import sanitize_html


class Review(models.Model):
    """Buyer reviews for completed deals"""
    
    REVIEW_TYPE_CHOICES = [
        ('vehicle', _('Vehicle Review')),
        ('dealer', _('Dealer Review')),
        ('platform', _('Platform Review')),
    ]
    
    # Relationships
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name=_('Buyer')
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name=_('Vehicle')
    )
    dealer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        limit_choices_to={'role': 'dealer'},
        verbose_name=_('Dealer')
    )
    
    # Review Content
    review_type = models.CharField(
        max_length=20,
        choices=REVIEW_TYPE_CHOICES,
        default='vehicle',
        verbose_name=_('Review Type')
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Overall Rating'),
        help_text=_('1-5 stars')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Review Title')
    )
    comment = models.TextField(
        verbose_name=_('Review Comment'),
        help_text=_('Share your experience')
    )
    
    # Detailed Ratings
    vehicle_condition_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_('Vehicle Condition'),
        help_text=_('How accurate was the vehicle description?')
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_('Communication'),
        help_text=_('How responsive was the dealer?')
    )
    delivery_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_('Delivery'),
        help_text=_('Was delivery timely and professional?')
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name=_('Value for Money'),
        help_text=_('Was the vehicle worth the price?')
    )
    
    # Buyer Information (optional)
    buyer_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Buyer Location'),
        help_text=_('City, Country (optional)')
    )
    would_recommend = models.BooleanField(
        default=True,
        verbose_name=_('Would Recommend'),
        help_text=_('Would you recommend this dealer?')
    )
    
    # Verification & Status
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name=_('Verified Purchase'),
        help_text=_('Review from actual buyer')
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name=_('Approved'),
        help_text=_('Moderation status')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Showcase this review')
    )
    
    # Dealer Response
    dealer_response = models.TextField(
        blank=True,
        verbose_name=_('Dealer Response'),
        help_text=_('Dealer can respond to review')
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Response Date')
    )
    
    # Helpfulness Tracking
    helpful_count = models.IntegerField(
        default=0,
        verbose_name=_('Helpful Count')
    )
    not_helpful_count = models.IntegerField(
        default=0,
        verbose_name=_('Not Helpful Count')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dealer', 'is_approved']),
            models.Index(fields=['vehicle', 'is_approved']),
            models.Index(fields=['rating']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['buyer', 'vehicle'],
                name='unique_buyer_vehicle_review'
            )
        ]
    
    def __str__(self):
        return f"{self.buyer.full_name} - {self.rating}★ - {self.title[:50]}"
    
    def save(self, *args, **kwargs):
        # Sanitize HTML in text fields
        self.title = sanitize_html(self.title)
        self.comment = sanitize_html(self.comment)
        if self.dealer_response:
            self.dealer_response = sanitize_html(self.dealer_response)
        super().save(*args, **kwargs)
    
    @property
    def average_detailed_rating(self):
        """Calculate average of detailed ratings if provided"""
        ratings = [
            r for r in [
                self.vehicle_condition_rating,
                self.communication_rating,
                self.delivery_rating,
                self.value_rating
            ] if r is not None
        ]
        return sum(ratings) / len(ratings) if ratings else self.rating
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        total = self.helpful_count + self.not_helpful_count
        return (self.helpful_count / total * 100) if total > 0 else 0


class ReviewHelpfulness(models.Model):
    """Track which users found reviews helpful"""
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpfulness_votes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    is_helpful = models.BooleanField(
        verbose_name=_('Is Helpful')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Review Helpfulness Vote')
        verbose_name_plural = _('Review Helpfulness Votes')
        unique_together = ('review', 'user')
    
    def __str__(self):
        helpful = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.full_name} marked review as {helpful}"


class DealerRating(models.Model):
    """Aggregated dealer ratings (cached for performance)"""
    
    dealer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rating_stats',
        limit_choices_to={'role': 'dealer'}
    )
    
    # Overall Stats
    total_reviews = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    
    # Rating Distribution
    five_star_count = models.IntegerField(default=0)
    four_star_count = models.IntegerField(default=0)
    three_star_count = models.IntegerField(default=0)
    two_star_count = models.IntegerField(default=0)
    one_star_count = models.IntegerField(default=0)
    
    # Detailed Ratings
    avg_vehicle_condition = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    avg_communication = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    avg_delivery = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    avg_value = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    
    # Recommendation Stats
    recommend_count = models.IntegerField(default=0)
    recommend_percentage = models.IntegerField(default=0)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Dealer Rating Statistics')
        verbose_name_plural = _('Dealer Rating Statistics')
    
    def __str__(self):
        return f"{self.dealer.full_name} - {self.average_rating}★ ({self.total_reviews} reviews)"
    
    def update_stats(self):
        """Recalculate all statistics from approved reviews"""
        from django.db.models import Avg, Count, Q
        
        reviews = Review.objects.filter(
            dealer=self.dealer,
            is_approved=True
        )
        
        self.total_reviews = reviews.count()
        
        if self.total_reviews > 0:
            # Average rating
            self.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
            
            # Rating distribution
            self.five_star_count = reviews.filter(rating=5).count()
            self.four_star_count = reviews.filter(rating=4).count()
            self.three_star_count = reviews.filter(rating=3).count()
            self.two_star_count = reviews.filter(rating=2).count()
            self.one_star_count = reviews.filter(rating=1).count()
            
            # Detailed ratings
            self.avg_vehicle_condition = reviews.aggregate(
                Avg('vehicle_condition_rating')
            )['vehicle_condition_rating__avg'] or 0.0
            
            self.avg_communication = reviews.aggregate(
                Avg('communication_rating')
            )['communication_rating__avg'] or 0.0
            
            self.avg_delivery = reviews.aggregate(
                Avg('delivery_rating')
            )['delivery_rating__avg'] or 0.0
            
            self.avg_value = reviews.aggregate(
                Avg('value_rating')
            )['value_rating__avg'] or 0.0
            
            # Recommendation stats
            self.recommend_count = reviews.filter(would_recommend=True).count()
            self.recommend_percentage = int(
                (self.recommend_count / self.total_reviews) * 100
            )
        
        self.save()
