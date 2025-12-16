from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'company_name', 'phone', 'country', 'preferred_language',
                  'is_staff', 'is_superuser', 'is_active']
        read_only_fields = ['id', 'is_staff', 'is_superuser']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'company_name', 'phone', 'address', 'country', 
                  'preferred_language', 'is_staff', 'is_superuser', 'is_active']
        read_only_fields = ['id', 'username', 'role', 'is_staff', 'is_superuser']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
