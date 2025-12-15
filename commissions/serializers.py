from rest_framework import serializers
from .models import Commission
from accounts.serializers import UserSerializer


class CommissionSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    deal_id = serializers.IntegerField(source='deal.id', read_only=True)
    
    class Meta:
        model = Commission
        fields = ['id', 'deal', 'deal_id', 'recipient', 'commission_type',
                  'amount_cad', 'percentage', 'status', 'notes',
                  'created_at', 'approved_at', 'paid_at']
        read_only_fields = ['id', 'created_at', 'approved_at', 'paid_at']
