from rest_framework import serializers
from django.db import models
from .models import Lead, Deal, Document
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
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    dealer_name = serializers.CharField(source='dealer.username', read_only=True)
    broker_name = serializers.CharField(source='broker.username', read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    commission_cad = serializers.SerializerMethodField()
    
    def get_commission_cad(self, obj):
        """Calculate total commission for this deal"""
        from commissions.models import Commission
        total = Commission.objects.filter(deal=obj).aggregate(
            total=models.Sum('amount_cad')
        )['total']
        return str(total or 0)
    
    class Meta:
        model = Deal
        fields = ['id', 'lead', 'vehicle', 'vehicle_details', 'buyer', 'buyer_name',
                  'dealer', 'dealer_name', 'broker', 'broker_name', 'status', 
                  'agreed_price_cad', 'payment_method', 'payment_status', 'notes',
                  'documents', 'commission_cad', 'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']
