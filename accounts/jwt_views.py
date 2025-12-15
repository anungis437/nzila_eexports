"""
JWT Authentication views and utilities
"""
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer with additional user information
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra user info to token response
        data.update({
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'role': self.user.role,
                'company_name': self.user.company_name,
                'preferred_language': self.user.preferred_language,
            }
        })
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT obtain pair view
    """
    serializer_class = CustomTokenObtainPairSerializer
