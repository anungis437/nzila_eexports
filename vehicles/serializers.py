from rest_framework import serializers
from .models import Vehicle, VehicleImage, Offer, VehicleInspectionSlot, InspectionAppointment
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
    lien_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'dealer', 'dealer_name', 'make', 'model', 'year', 'vin',
                  'condition', 'mileage', 'color', 'fuel_type', 'transmission',
                  'price_cad', 'status', 'description', 'location', 'main_image',
                  'images', 'videos_count', 'lien_checked', 'lien_status', 
                  'lien_status_display', 'created_at', 'updated_at']
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
    
    def get_lien_status_display(self, obj):
        """Human-readable lien status"""
        if not obj.lien_checked:
            return 'Not Checked'
        elif obj.lien_status == 'CLEAR':
            return 'Clear - No Liens'
        elif obj.lien_status == 'LIEN_FOUND':
            return 'Lien Found - Needs Resolution'
        else:
            return 'Unknown'


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


class VehicleInspectionSlotSerializer(serializers.ModelSerializer):
    slots_remaining = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    current_bookings = serializers.ReadOnlyField()
    vehicle_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VehicleInspectionSlot
        fields = ['id', 'vehicle', 'vehicle_info', 'date', 'start_time', 'end_time', 
                  'is_available', 'max_attendees', 'slots_remaining', 'current_bookings',
                  'is_past', 'notes', 'created_at']
        read_only_fields = ['id', 'slots_remaining', 'is_past', 'current_bookings', 'created_at']
    
    def get_vehicle_info(self, obj):
        """Return basic vehicle information"""
        return {
            'id': obj.vehicle.id,
            'make': obj.vehicle.make,
            'model': obj.vehicle.model,
            'year': obj.vehicle.year,
            'vin': obj.vehicle.vin,
        }
    
    def validate_notes(self, value):
        """Sanitize notes to prevent XSS"""
        if value:
            return sanitize_text(value)
        return value


class InspectionAppointmentSerializer(serializers.ModelSerializer):
    vehicle = serializers.SerializerMethodField()
    dealer = serializers.SerializerMethodField()
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    slot_date = serializers.DateField(source='slot.date', read_only=True)
    slot_time = serializers.SerializerMethodField()
    
    class Meta:
        model = InspectionAppointment
        fields = ['id', 'slot', 'buyer', 'buyer_name', 'buyer_email', 'vehicle', 
                  'dealer', 'status', 'slot_date', 'slot_time',
                  'contact_phone', 'contact_email', 'number_of_people',
                  'buyer_notes', 'dealer_notes', 'inspection_feedback',
                  'vehicle_rating', 'dealer_rating', 'interested_in_purchase',
                  'created_at', 'confirmed_at', 'completed_at', 'cancelled_at']
        read_only_fields = ['id', 'buyer', 'buyer_name', 'buyer_email', 'vehicle', 
                            'dealer', 'created_at', 'confirmed_at', 'completed_at', 
                            'cancelled_at']
    
    def get_vehicle(self, obj):
        """Return vehicle information"""
        vehicle = obj.vehicle
        if vehicle:
            return {
                'id': vehicle.id,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'vin': vehicle.vin,
                'price_cad': str(vehicle.price_cad),
            }
        return None
    
    def get_dealer(self, obj):
        """Return dealer information"""
        dealer = obj.dealer
        if dealer:
            return {
                'id': dealer.id,
                'name': dealer.full_name or dealer.username,
                'email': dealer.email,
                'phone': dealer.phone,
                'showroom_address': dealer.showroom_address,
                'showroom_city': dealer.showroom_city,
                'showroom_province': dealer.showroom_province,
                'showroom_phone': dealer.showroom_phone,
                'business_hours': dealer.business_hours,
            }
        return None
    
    def get_slot_time(self, obj):
        """Return formatted time range"""
        return f"{obj.slot.start_time.strftime('%I:%M %p')} - {obj.slot.end_time.strftime('%I:%M %p')}"
    
    def validate_buyer_notes(self, value):
        """Sanitize buyer notes"""
        if value:
            return sanitize_text(value)
        return value
    
    def validate_dealer_notes(self, value):
        """Sanitize dealer notes"""
        if value:
            return sanitize_text(value)
        return value
    
    def validate_inspection_feedback(self, value):
        """Sanitize inspection feedback"""
        if value:
            return sanitize_html(value)
        return value
    
    def validate_vehicle_rating(self, value):
        """Ensure rating is between 1 and 5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate_dealer_rating(self, value):
        """Ensure rating is between 1 and 5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class InspectionAppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionAppointment
        fields = ['slot', 'contact_phone', 'contact_email', 'number_of_people', 'buyer_notes']
    
    def validate(self, data):
        """Validate appointment booking"""
        slot = data.get('slot')
        
        # Check if slot is available
        if not slot.is_available:
            raise serializers.ValidationError("This inspection slot is not available")
        
        # Check if slot is in the past
        if slot.is_past:
            raise serializers.ValidationError("Cannot book inspection slot in the past")
        
        # Check if slot has remaining capacity
        if slot.slots_remaining <= 0:
            raise serializers.ValidationError("This inspection slot is fully booked")
        
        return data
    
    def validate_buyer_notes(self, value):
        """Sanitize buyer notes"""
        if value:
            return sanitize_text(value)
        return value
