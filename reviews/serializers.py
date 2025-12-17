from rest_framework import serializers
from .models import Review, ReviewHelpfulness, DealerRating
from accounts.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    buyer_location_display = serializers.CharField(source='buyer_location', read_only=True)
    dealer_name = serializers.CharField(source='dealer.full_name', read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    average_detailed_rating = serializers.FloatField(read_only=True)
    helpfulness_ratio = serializers.FloatField(read_only=True)
    can_respond = serializers.SerializerMethodField()
    can_mark_helpful = serializers.SerializerMethodField()
    user_found_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'buyer', 'buyer_name', 'buyer_location_display', 'dealer',
            'dealer_name', 'vehicle', 'vehicle_info', 'review_type', 'rating',
            'title', 'comment', 'vehicle_condition_rating', 'communication_rating',
            'delivery_rating', 'value_rating', 'would_recommend', 'is_verified_purchase',
            'is_approved', 'is_featured', 'dealer_response', 'responded_at',
            'helpful_count', 'not_helpful_count', 'helpfulness_ratio',
            'average_detailed_rating', 'created_at', 'updated_at',
            'can_respond', 'can_mark_helpful', 'user_found_helpful'
        ]
        read_only_fields = [
            'id', 'buyer', 'is_verified_purchase', 'is_approved',
            'helpful_count', 'not_helpful_count', 'created_at', 'updated_at'
        ]
    
    def get_vehicle_info(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'make': obj.vehicle.make,
                'model': obj.vehicle.model,
                'year': obj.vehicle.year,
                'main_image': obj.vehicle.main_image.url if obj.vehicle.main_image else None
            }
        return None
    
    def get_can_respond(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user == obj.dealer
        return False
    
    def get_can_mark_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user != obj.buyer
        return False
    
    def get_user_found_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.helpfulness_votes.filter(user=request.user).first()
            if vote:
                return vote.is_helpful
        return None


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'vehicle', 'dealer', 'review_type', 'rating', 'title', 'comment',
            'vehicle_condition_rating', 'communication_rating', 'delivery_rating',
            'value_rating', 'buyer_location', 'would_recommend'
        ]
    
    def validate(self, data):
        # Ensure buyer has purchased from this dealer
        request = self.context['request']
        buyer = request.user
        dealer = data.get('dealer')
        vehicle = data.get('vehicle')
        
        # Check if buyer has a completed deal with this dealer
        from deals.models import Deal
        has_deal = Deal.objects.filter(
            buyer=buyer,
            vehicle__dealer=dealer,
            status__in=['completed', 'delivered']
        ).exists()
        
        if not has_deal:
            raise serializers.ValidationError(
                "You can only review dealers you've purchased from."
            )
        
        # Check if already reviewed this vehicle
        if vehicle:
            existing = Review.objects.filter(
                buyer=buyer,
                vehicle=vehicle
            ).exists()
            if existing:
                raise serializers.ValidationError(
                    "You've already reviewed this vehicle."
                )
        
        return data
    
    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        validated_data['is_verified_purchase'] = True
        return super().create(validated_data)


class ReviewResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['dealer_response']
    
    def validate(self, data):
        request = self.context['request']
        review = self.instance
        
        if request.user != review.dealer:
            raise serializers.ValidationError(
                "Only the dealer can respond to their reviews."
            )
        
        return data
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        instance.dealer_response = validated_data['dealer_response']
        instance.responded_at = timezone.now()
        instance.save()
        return instance


class DealerRatingSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.full_name', read_only=True)
    dealer_email = serializers.EmailField(source='dealer.email', read_only=True)
    
    class Meta:
        model = DealerRating
        fields = [
            'id', 'dealer', 'dealer_name', 'dealer_email', 'total_reviews',
            'average_rating', 'five_star_count', 'four_star_count',
            'three_star_count', 'two_star_count', 'one_star_count',
            'avg_vehicle_condition', 'avg_communication', 'avg_delivery',
            'avg_value', 'recommend_count', 'recommend_percentage',
            'last_updated'
        ]
        read_only_fields = ['__all__']
