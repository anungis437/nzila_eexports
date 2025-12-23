"""
PHASE 2 - Feature 6: Third-Party Inspection Integration

DRF serializers for inspection models
"""

from rest_framework import serializers
from .models import ThirdPartyInspector, InspectionReport, InspectorReview


class ThirdPartyInspectorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inspector directory listings"""
    
    certification_display = serializers.CharField(source='get_certifications_display', read_only=True)
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    
    class Meta:
        model = ThirdPartyInspector
        fields = [
            'id', 'company', 'name', 'city', 'province', 'province_display',
            'certification_display', 'rating', 'total_inspections', 'total_reviews',
            'inspection_fee', 'mobile_service', 'is_verified', 'is_active'
        ]


class ThirdPartyInspectorDetailSerializer(serializers.ModelSerializer):
    """Full serializer for inspector detail view"""
    
    certification_display = serializers.CharField(source='get_certifications_display', read_only=True)
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    certification_list = serializers.SerializerMethodField()
    specialization_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ThirdPartyInspector
        fields = '__all__'
        read_only_fields = ['rating', 'total_inspections', 'total_reviews', 'created_at', 'updated_at']
    
    def get_certification_list(self, obj):
        """Get all certifications as a list"""
        return obj.get_certification_display_list()
    
    def get_specialization_list(self, obj):
        """Get specializations as a list"""
        if obj.specializations:
            return [s.strip() for s in obj.specializations.split(',')]
        return []


class InspectorReviewSerializer(serializers.ModelSerializer):
    """Serializer for inspector reviews"""
    
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    inspector_name = serializers.CharField(source='inspector.company', read_only=True)
    
    class Meta:
        model = InspectorReview
        fields = [
            'id', 'inspector', 'inspector_name', 'buyer', 'buyer_name',
            'inspection_report', 'rating', 'review_text',
            'professionalism_rating', 'thoroughness_rating',
            'communication_rating', 'value_rating',
            'helpful_votes', 'is_verified_purchase', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'helpful_votes', 'is_verified_purchase', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure buyer has actually used this inspector"""
        request = self.context.get('request')
        if request and request.user:
            inspection_report = data.get('inspection_report')
            if inspection_report and inspection_report.buyer != request.user:
                raise serializers.ValidationError(
                    "You can only review inspections you requested."
                )
        return data


class InspectionReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for inspection report listings"""
    
    vehicle_info = serializers.SerializerMethodField()
    inspector_name = serializers.CharField(source='inspector.company', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_overall_condition_display', read_only=True)
    
    class Meta:
        model = InspectionReport
        fields = [
            'id', 'vehicle', 'vehicle_info', 'inspector', 'inspector_name',
            'report_type', 'report_type_display', 'inspection_date',
            'status', 'status_display', 'overall_condition', 'condition_display',
            'inspection_fee_paid', 'payment_status', 'created_at'
        ]
    
    def get_vehicle_info(self, obj):
        """Get basic vehicle information"""
        return f"{obj.vehicle.year} {obj.vehicle.make} {obj.vehicle.model}"


class InspectionReportDetailSerializer(serializers.ModelSerializer):
    """Full serializer for inspection report detail view"""
    
    vehicle_info = serializers.SerializerMethodField()
    inspector_details = ThirdPartyInspectorListSerializer(source='inspector', read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_overall_condition_display', read_only=True)
    average_score = serializers.SerializerMethodField()
    review = InspectorReviewSerializer(read_only=True)
    
    class Meta:
        model = InspectionReport
        fields = '__all__'
        read_only_fields = ['buyer', 'created_at', 'updated_at']
    
    def get_vehicle_info(self, obj):
        """Get detailed vehicle information"""
        return {
            'id': obj.vehicle.id,
            'year': obj.vehicle.year,
            'make': obj.vehicle.make,
            'model': obj.vehicle.model,
            'vin': obj.vehicle.vin,
        }
    
    def get_average_score(self, obj):
        """Get calculated average score"""
        return obj.get_average_score()


class InspectionReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new inspection reports"""
    
    class Meta:
        model = InspectionReport
        fields = [
            'vehicle', 'inspector', 'report_type', 'inspection_date',
            'report_file', 'inspection_fee_paid', 'notes'
        ]
    
    def validate(self, data):
        """Validate inspection report data"""
        request = self.context.get('request')
        if request and request.user:
            # Set buyer to current user
            data['buyer'] = request.user
        
        # Validate inspection fee matches inspector's fee
        inspector = data.get('inspector')
        fee_paid = data.get('inspection_fee_paid')
        
        if inspector and fee_paid:
            expected_fee = inspector.inspection_fee
            if inspector.mobile_service:
                expected_fee += inspector.mobile_fee_extra
            
            if fee_paid < expected_fee:
                raise serializers.ValidationError({
                    'inspection_fee_paid': f'Fee must be at least {expected_fee} CAD'
                })
        
        return data


class InspectionReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating inspection report findings"""
    
    class Meta:
        model = InspectionReport
        fields = [
            'status', 'overall_condition', 'issues_found', 'recommendations',
            'estimated_repair_cost', 'engine_score', 'transmission_score',
            'suspension_score', 'brakes_score', 'body_score', 'interior_score',
            'payment_status', 'notes'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.instance
        if instance and instance.status == 'completed' and value != 'completed':
            raise serializers.ValidationError(
                "Cannot change status of completed inspection"
            )
        return value
