from rest_framework import serializers
from django.db import models
from decimal import Decimal
from .models import Lead, Deal, Document
from .financial_models import DealFinancialTerms, PaymentMilestone, FinancingOption, FinancingInstallment
from vehicles.serializers import VehicleListSerializer
from accounts.serializers import UserSerializer


class LeadSerializer(serializers.ModelSerializer):
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    broker_name = serializers.CharField(source='broker.username', read_only=True)
    
    class Meta:
        model = Lead
        fields = ['id', 'buyer', 'buyer_name', 'vehicle', 'vehicle_details', 
                  'broker', 'broker_name', 'status', 'source', 'notes', 
                  'created_at', 'updated_at', 'last_contacted']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'deal', 'document_type', 'file', 'status',
                  'uploaded_by', 'verified_by', 'notes',
                  'uploaded_at', 'verified_at']
        read_only_fields = ['id', 'uploaded_at', 'verified_at']


class DealSerializer(serializers.ModelSerializer):
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    buyer_name = serializers.SerializerMethodField()
    dealer_name = serializers.SerializerMethodField()
    broker_name = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True, read_only=True)
    commission_cad = serializers.SerializerMethodField()
    
    # Financial fields
    financial_terms = serializers.SerializerMethodField()
    payment_summary = serializers.SerializerMethodField()
    
    def get_buyer_name(self, obj):
        return obj.buyer.username if obj.buyer else None
    
    def get_dealer_name(self, obj):
        return obj.dealer.username if obj.dealer else None
    
    def get_broker_name(self, obj):
        return obj.broker.username if obj.broker else None
    
    def get_commission_cad(self, obj):
        """Calculate total commission for this deal"""
        from commissions.models import Commission
        total = Commission.objects.filter(deal=obj).aggregate(
            total=models.Sum('amount_cad')
        )['total']
        return str(total or 0)
    
    def get_financial_terms(self, obj):
        """Get financial terms summary."""
        if not hasattr(obj, 'financial_terms'):
            return None
        # Only include if explicitly requested
        if 'financial_terms' in self.context.get('expand', []):
            return DealFinancialTermsSerializer(obj.financial_terms).data
        return {'id': obj.financial_terms.id}
    
    def get_payment_summary(self, obj):
        """Get payment status summary."""
        return obj.get_payment_status_summary()
    
    class Meta:
        model = Deal
        fields = ['id', 'lead', 'vehicle', 'vehicle_details', 'buyer', 'buyer_name',
                  'dealer', 'dealer_name', 'broker', 'broker_name', 'status', 
                  'agreed_price_cad', 'payment_method', 'payment_status', 'notes',
                  'documents', 'commission_cad', 'financial_terms', 'payment_summary',
                  'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']

class BuyerDealSerializer(serializers.ModelSerializer):
    """Simplified deal serializer for buyers - hides internal business details"""
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    dealer_name = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True, read_only=True)
    
    def get_dealer_name(self, obj):
        return obj.dealer.username if obj.dealer else None
    
    class Meta:
        model = Deal
        fields = ['id', 'vehicle', 'vehicle_details', 'dealer_name', 'status', 
                  'agreed_price_cad', 'payment_method', 'payment_status', 
                  'documents', 'notes', 'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']


# ============================================================================
# Financial Serializers
# ============================================================================

class FinancingInstallmentSerializer(serializers.ModelSerializer):
    """Serializer for individual financing installments."""
    
    is_late = serializers.BooleanField(read_only=True)
    days_late = serializers.IntegerField(source='calculate_days_late', read_only=True)
    
    class Meta:
        model = FinancingInstallment
        fields = [
            'id', 'installment_number', 'due_date', 'amount_due',
            'principal_amount', 'interest_amount', 'amount_paid',
            'late_fee', 'remaining_balance', 'status', 'is_late',
            'days_late', 'paid_at'
        ]
        read_only_fields = [
            'id', 'principal_amount', 'interest_amount', 'remaining_balance',
            'is_late', 'days_late', 'paid_at'
        ]


class FinancingOptionSerializer(serializers.ModelSerializer):
    """Serializer for financing options with installment schedule."""
    
    installments = FinancingInstallmentSerializer(many=True, read_only=True)
    installments_summary = serializers.SerializerMethodField()
    
    def get_installments_summary(self, obj):
        """Get summary statistics for installments."""
        installments = obj.installments.all()
        return {
            'total': installments.count(),
            'paid': installments.filter(status='paid').count(),
            'pending': installments.filter(status='pending').count(),
            'late': installments.filter(status='late').count(),
            'total_paid': sum(i.amount_paid for i in installments),
            'total_remaining': sum(i.amount_due - i.amount_paid for i in installments)
        }
    
    class Meta:
        model = FinancingOption
        fields = [
            'id', 'deal', 'financing_type', 'lender_name',
            'financed_amount', 'down_payment', 'interest_rate',
            'term_months', 'monthly_payment', 'total_interest',
            'total_amount', 'first_payment_date', 'final_payment_date',
            'status', 'installments', 'installments_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'monthly_payment', 'total_interest', 'total_amount',
            'installments_summary', 'created_at', 'updated_at'
        ]
    
    def validate_term_months(self, value):
        """Validate term months is positive."""
        if value <= 0:
            raise serializers.ValidationError("Term months must be greater than 0")
        return value
    
    def validate_interest_rate(self, value):
        """Validate interest rate is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Interest rate cannot be negative")
        return value


class PaymentMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for payment milestones."""
    
    is_overdue = serializers.BooleanField(read_only=True)
    amount_remaining = serializers.DecimalField(
        source='get_amount_remaining',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    payment_percentage = serializers.DecimalField(
        source='get_payment_percentage',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = PaymentMilestone
        fields = [
            'id', 'name', 'milestone_type', 'sequence', 'amount_due',
            'amount_paid', 'due_date', 'status', 'is_overdue',
            'amount_remaining', 'payment_percentage', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_overdue', 'amount_remaining', 'payment_percentage',
            'created_at', 'updated_at'
        ]


class DealFinancialTermsSerializer(serializers.ModelSerializer):
    """Serializer for deal financial terms."""
    
    milestones = PaymentMilestoneSerializer(many=True, read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    payment_progress_percentage = serializers.DecimalField(
        source='get_payment_progress_percentage',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    is_deposit_overdue = serializers.BooleanField(read_only=True)
    is_balance_overdue = serializers.BooleanField(read_only=True)
    fully_paid = serializers.BooleanField(source='is_fully_paid', read_only=True)
    
    class Meta:
        model = DealFinancialTerms
        fields = [
            'id', 'deal', 'total_price', 'currency', 'currency_code',
            'deposit_percentage', 'deposit_amount', 'deposit_paid',
            'deposit_paid_at', 'deposit_due_date', 'balance_remaining',
            'balance_due_date', 'total_paid', 'payment_progress_percentage',
            'is_deposit_overdue', 'is_balance_overdue', 'fully_paid',
            'is_financed', 'milestones',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'deposit_amount', 'balance_remaining', 'total_paid',
            'payment_progress_percentage', 'is_deposit_overdue',
            'is_balance_overdue', 'fully_paid', 'created_at', 'updated_at'
        ]
    
    def validate_deposit_percentage(self, value):
        """Validate deposit percentage is between 0 and 100."""
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Deposit percentage must be between 0 and 100"
            )
        return value


class ProcessPaymentSerializer(serializers.Serializer):
    """Serializer for processing payments."""
    
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    payment_method = serializers.ChoiceField(
        choices=['card', 'bank_transfer', 'wire', 'crypto', 'other'],
        default='card'
    )
    reference_number = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True
    )


class ApplyFinancingSerializer(serializers.Serializer):
    """Serializer for applying financing to a deal."""
    
    financed_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    down_payment = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00')
    )
    interest_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00')
    )
    term_months = serializers.IntegerField(
        min_value=1,
        max_value=120
    )
    lender_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )
    
    def validate(self, data):
        """Validate that down_payment doesn't exceed financed_amount."""
        if data['down_payment'] > data['financed_amount']:
            raise serializers.ValidationError(
                "Down payment cannot exceed financed amount"
            )
        return data
