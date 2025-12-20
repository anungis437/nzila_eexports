from rest_framework import serializers
from .models import Vehicle, VehicleImage, Offer
from utils.sanitization import sanitize_html, sanitize_text


class VehicleImageSerializer(serializers.ModelSerializer):
    media_url = serializers.CharField(read_only=True)
    is_video = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'video', 'media_type', 'caption', 'is_primary', 
                  'order', 'duration_seconds', 'thumbnail', 'uploaded_at', 
                  'media_url', 'is_video']
        read_only_fields = ['id', 'uploaded_at']
    
    def validate(self, data):
        """Validate that either image or video is provided based on media_type"""
        media_type = data.get('media_type', 'image')
        
        if media_type == 'image' and not data.get('image'):
            raise serializers.ValidationError("Image file is required for image media type")
        
        if media_type == 'video' and not data.get('video'):
            raise serializers.ValidationError("Video file is required for video media type")
        
        # Validate video file size (max 100MB)
        if media_type == 'video' and data.get('video'):
            video = data['video']
            if video.size > 100 * 1024 * 1024:  # 100MB in bytes
                raise serializers.ValidationError("Video file size must be less than 100MB")
        
        return data


class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)
    dealer_name = serializers.CharField(source='dealer.username', read_only=True)
    videos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'dealer', 'dealer_name', 'make', 'model', 'year', 'vin',
                  'condition', 'mileage', 'color', 'fuel_type', 'transmission',
                  'price_cad', 'status', 'description', 'location', 'main_image',
                  'images', 'videos_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_description(self, value):
        """Sanitize vehicle description to prevent XSS attacks"""
        if value:
            return sanitize_html(value)
        return value
    
    def validate_location(self, value):
        """Sanitize location text"""
        if value:
            return sanitize_text(value)
        return value
    
    def get_videos_count(self, obj):
        """Count how many videos are attached to this vehicle"""
        return obj.images.filter(media_type='video').count()


class VehicleListSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.username', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'vin', 'condition', 'mileage',
                  'price_cad', 'status', 'location', 'main_image', 'dealer_name']


class OfferSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Offer
        fields = [
            'id', 'vehicle', 'vehicle_info', 'buyer', 'buyer_name', 'buyer_email',
            'offer_amount_cad', 'message', 'status', 'counter_amount_cad',
            'counter_message', 'dealer_notes', 'valid_until', 'is_expired',
            'created_at', 'updated_at', 'responded_at'
        ]
        read_only_fields = ['id', 'buyer', 'created_at', 'updated_at', 'responded_at']
    
    def get_vehicle_info(self, obj):
        return {
            'id': obj.vehicle.id,
            'make': obj.vehicle.make,
            'model': obj.vehicle.model,
            'year': obj.vehicle.year,
            'price_cad': str(obj.vehicle.price_cad),
        }
    
    def validate_offer_amount_cad(self, value):
        """Ensure offer amount is reasonable"""
        if value <= 0:
            raise serializers.ValidationError("Offer amount must be greater than 0")
        return value
    
    def validate_message(self, value):
        """Sanitize offer message to prevent XSS"""
        if value:
            return sanitize_text(value)
        return value
    
    def validate_counter_message(self, value):
        """Sanitize counter offer message"""
        if value:
            return sanitize_text(value)
        return value
    
    def validate_dealer_notes(self, value):
        """Sanitize dealer notes"""
        if value:
            return sanitize_text(value)
        return value


class OfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['vehicle', 'offer_amount_cad', 'message', 'valid_until']
    
    def validate(self, data):
        vehicle = data.get('vehicle')
        if vehicle.status not in ['available', 'reserved']:
            raise serializers.ValidationError("Cannot make an offer on this vehicle")
        return data
