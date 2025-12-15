from rest_framework import serializers
from .models import Lead, Deal, Document
from vehicles.serializers import VehicleListSerializer
from accounts.serializers import UserSerializer


class LeadSerializer(serializers.ModelSerializer):
    vehicle = VehicleListSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    broker = UserSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Lead
        fields = ['id', 'buyer', 'vehicle', 'vehicle_id', 'broker', 'status',
                  'source', 'notes', 'created_at', 'updated_at', 'last_contacted']
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
    vehicle = VehicleListSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    dealer = UserSerializer(read_only=True)
    broker = UserSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Deal
        fields = ['id', 'lead', 'vehicle', 'vehicle_id', 'buyer', 'dealer',
                  'broker', 'status', 'agreed_price_cad', 'notes',
                  'documents', 'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']
