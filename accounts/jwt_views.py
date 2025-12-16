"""
JWT Authentication views and utilities with httpOnly cookie support
"""
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from django.conf import settings


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
    Custom JWT obtain pair view with httpOnly cookie support
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def finalize_response(self, request, response, *args, **kwargs):
        """Set JWT tokens as httpOnly cookies for security"""
        response = super().finalize_response(request, response, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK and 'access' in response.data:
            # Set access token in httpOnly cookie
            response.set_cookie(
                key='access_token',
                value=response.data['access'],
                max_age=3600,  # 1 hour
                httponly=True,
                secure=not settings.DEBUG,  # HTTPS only in production
                samesite='Lax',
                path='/'
            )
            
            # Set refresh token in httpOnly cookie
            if 'refresh' in response.data:
                response.set_cookie(
                    key='refresh_token',
                    value=response.data['refresh'],
                    max_age=86400 * 7,  # 7 days
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    path='/'
                )
            
            # Remove tokens from response body for security
            # Keep user info for frontend
            user_data = response.data.get('user', {})
            response.data = {'user': user_data, 'message': 'Authentication successful'}
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT refresh view with httpOnly cookie support
    """
    
    def post(self, request, *args, **kwargs):
        """Override to get refresh token from cookie"""
        # Get refresh token from cookie instead of request body
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found in cookies'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Add refresh token to request data
        request.data._mutable = True if hasattr(request.data, '_mutable') else False
        data = request.data.copy() if hasattr(request.data, 'copy') else {}
        data['refresh'] = refresh_token
        request._full_data = data
        
        response = super().post(request, *args, **kwargs)
        
        # Set new access token in cookie
        if response.status_code == status.HTTP_200_OK and 'access' in response.data:
            response.set_cookie(
                key='access_token',
                value=response.data['access'],
                max_age=3600,  # 1 hour
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                path='/'
            )
            # Remove token from response body
            response.data = {'message': 'Token refreshed successfully'}
        
        return response
