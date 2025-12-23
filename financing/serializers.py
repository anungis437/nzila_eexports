"""
Financing API Serializers

DRF serializers for financing calculator endpoints
"""

from rest_framework import serializers
from .models import InterestRate, LoanScenario, TradeInEstimate
from vehicles.models import Vehicle
from decimal import Decimal


class InterestRateSerializer(serializers.ModelSerializer):
    """Serializer for interest rate lookup"""
    
    credit_tier_display = serializers.CharField(source='get_credit_tier_display', read_only=True)
    loan_term_display = serializers.CharField(source='get_loan_term_months_display', read_only=True)
    monthly_rate = serializers.DecimalField(source='monthly_interest_rate', max_digits=8, decimal_places=6, read_only=True)
    
    class Meta:
        model = InterestRate
        fields = [
            'id', 'credit_tier', 'credit_tier_display', 'loan_term_months', 'loan_term_display',
            'annual_interest_rate', 'monthly_rate', 'effective_date', 'is_active'
        ]


class LoanScenarioSerializer(serializers.ModelSerializer):
    """Detailed loan scenario with all calculations"""
    
    vehicle_details = serializers.SerializerMethodField()
    credit_tier_display = serializers.CharField(source='get_credit_tier_display', read_only=True)
    loan_term_display = serializers.CharField(source='get_loan_term_months_display', read_only=True)
    down_payment_pct = serializers.DecimalField(source='down_payment_percentage', max_digits=5, decimal_places=2, read_only=True)
    ltv_ratio = serializers.DecimalField(source='loan_to_value_ratio', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = LoanScenario
        fields = [
            'id', 'buyer', 'vehicle', 'vehicle_details', 'vehicle_price', 'down_payment', 'down_payment_pct',
            'trade_in_value', 'loan_term_months', 'loan_term_display', 'credit_tier', 'credit_tier_display',
            'province', 'loan_amount', 'monthly_payment', 'total_interest', 'total_cost',
            'annual_interest_rate', 'pst_amount', 'gst_hst_amount', 'documentation_fee',
            'license_registration_fee', 'scenario_name', 'is_favorite', 'ltv_ratio',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'loan_amount', 'monthly_payment', 'total_interest', 'total_cost',
            'annual_interest_rate', 'pst_amount', 'gst_hst_amount'
        ]
    
    def get_vehicle_details(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'year': obj.vehicle.year,
                'make': obj.vehicle.make,
                'model': obj.vehicle.model,
                'vin': obj.vehicle.vin,
            }
        return None


class LoanScenarioCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and calculating loan scenarios"""
    
    class Meta:
        model = LoanScenario
        fields = [
            'vehicle', 'vehicle_price', 'down_payment', 'trade_in_value',
            'loan_term_months', 'credit_tier', 'province', 'scenario_name', 'is_favorite'
        ]
    
    def create(self, validated_data):
        # Set buyer from request context
        validated_data['buyer'] = self.context['request'].user
        
        # Create scenario
        scenario = LoanScenario.objects.create(**validated_data)
        
        # Calculate loan details
        scenario.calculate()
        
        return scenario


class LoanScenarioComparisonSerializer(serializers.Serializer):
    """Serializer for comparing multiple loan scenarios"""
    
    scenario_id = serializers.IntegerField()
    scenario_name = serializers.CharField()
    loan_term_months = serializers.IntegerField()
    down_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_interest = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    annual_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class TradeInEstimateSerializer(serializers.ModelSerializer):
    """Serializer for trade-in value estimates"""
    
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    vehicle_description = serializers.SerializerMethodField()
    value_range = serializers.SerializerMethodField()
    
    class Meta:
        model = TradeInEstimate
        fields = [
            'id', 'buyer', 'year', 'make', 'model', 'trim', 'mileage', 'condition',
            'condition_display', 'province', 'trade_in_value', 'private_party_value',
            'retail_value', 'vehicle_description', 'value_range', 'estimate_date',
            'data_source', 'notes', 'created_at'
        ]
        read_only_fields = [
            'trade_in_value', 'private_party_value', 'retail_value', 'estimate_date', 'data_source'
        ]
    
    def get_vehicle_description(self, obj):
        trim_str = f" {obj.trim}" if obj.trim else ""
        return f"{obj.year} {obj.make} {obj.model}{trim_str}"
    
    def get_value_range(self, obj):
        return {
            'min': obj.trade_in_value,
            'average': obj.private_party_value,
            'max': obj.retail_value,
        }


class TradeInEstimateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating trade-in estimates"""
    
    class Meta:
        model = TradeInEstimate
        fields = ['year', 'make', 'model', 'trim', 'mileage', 'condition', 'province', 'notes']
    
    def create(self, validated_data):
        # Set buyer from request context
        validated_data['buyer'] = self.context['request'].user
        
        # Generate estimate using mock KBB algorithm
        estimates = TradeInEstimate.generate_estimate(
            year=validated_data['year'],
            make=validated_data['make'],
            model=validated_data['model'],
            mileage=validated_data['mileage'],
            condition=validated_data.get('condition', 'good'),
            province=validated_data.get('province', 'ON')
        )
        
        # Add estimates to validated data
        validated_data['trade_in_value'] = estimates['trade_in_value']
        validated_data['private_party_value'] = estimates['private_party_value']
        validated_data['retail_value'] = estimates['retail_value']
        
        # Create estimate
        return TradeInEstimate.objects.create(**validated_data)


class QuickCalculateSerializer(serializers.Serializer):
    """Serializer for quick payment calculation (no DB save)"""
    
    vehicle_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    down_payment = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), min_value=Decimal('0.00'))
    trade_in_value = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), min_value=Decimal('0.00'))
    loan_term_months = serializers.ChoiceField(choices=[12, 24, 36, 48, 60, 72, 84], default=48)
    credit_tier = serializers.ChoiceField(
        choices=['excellent', 'good', 'fair', 'poor', 'bad'],
        default='good'
    )
    province = serializers.CharField(max_length=2, default='ON')
    
    def validate(self, data):
        """Ensure down payment + trade-in doesn't exceed vehicle price"""
        total_upfront = data['down_payment'] + data['trade_in_value']
        if total_upfront > data['vehicle_price']:
            raise serializers.ValidationError(
                "Down payment plus trade-in value cannot exceed vehicle price"
            )
        return data


class QuickCalculateResultSerializer(serializers.Serializer):
    """Serializer for quick calculation results"""
    
    # Input parameters
    vehicle_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    trade_in_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    loan_term_months = serializers.IntegerField()
    credit_tier = serializers.CharField()
    province = serializers.CharField()
    
    # Calculated results
    loan_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_interest = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    annual_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Tax breakdown
    pst_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    gst_hst_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    documentation_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    license_registration_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional info
    down_payment_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_to_value_ratio = serializers.DecimalField(max_digits=5, decimal_places=2)
