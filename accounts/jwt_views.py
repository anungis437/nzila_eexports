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
    Accepts email or username for login
    """
    
    def validate(self, attrs):
        # Try to get user by email first if email-like string provided
        from accounts.models import User
        
        username_or_email = attrs.get(self.username_field)
        
        # If looks like email, convert to username
        if username_or_email and '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                attrs[self.username_field] = user.username
            except User.DoesNotExist:
                pass  # Will fail with invalid credentials in super().validate()
        
        data = super().validate(attrs)
        
        # Add extra user info to token response
        data.update({
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'full_name': self.user.get_full_name() or self.user.username,
                'role': self.user.role,
                'company_name': self.user.company_name,
                'preferred_language': self.user.preferred_language,
                'is_staff': self.user.is_staff,
                'is_superuser': self.user.is_superuser,
                'is_active': self.user.is_active,
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
        
        # Create serializer with refresh token from cookie
        serializer = self.get_serializer(data={'refresh': refresh_token})
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Set new access token in cookie
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        if 'access' in serializer.validated_data:
            response.set_cookie(
                key='access_token',
                value=serializer.validated_data['access'],
                max_age=3600,  # 1 hour
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                path='/'
            )
            # Remove token from response body
            response.data = {'message': 'Token refreshed successfully'}
        
        return response
