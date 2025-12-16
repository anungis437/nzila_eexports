"""
Two-Factor Authentication (2FA) views
Supports both SMS and TOTP (Authenticator App) methods
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pyotp
import qrcode
import io
import base64
from django.conf import settings

User = get_user_model()


class TwoFactorViewSet(viewsets.ViewSet):
    """ViewSet for managing two-factor authentication"""
    permission_classes = [IsAuthenticated]

    def _send_sms_code(self, phone_number, code):
        """Send SMS verification code using Twilio"""
        try:
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            message = client.messages.create(
                body=f'Your Nzila Export verification code is: {code}. Valid for 5 minutes.',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            return True, message.sid
        except TwilioRestException as e:
            return False, str(e)

    @action(detail=False, methods=['post'], url_path='enable-totp')
    def enable_totp(self, request):
        """
        Enable TOTP (Time-based One-Time Password) for the user
        Returns QR code for scanning with authenticator app
        """
        user = request.user

        # Generate secret key if not exists
        if not user.two_factor_secret:
            user.two_factor_secret = pyotp.random_base32()
            user.save()

        # Generate TOTP URI
        totp = pyotp.TOTP(user.two_factor_secret)
        uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='Nzila Export Hub'
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'secret': user.two_factor_secret,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'manual_entry': f'Key: {user.two_factor_secret}',
            'message': 'Scan the QR code with your authenticator app'
        })

    @action(detail=False, methods=['post'], url_path='verify-totp')
    def verify_totp(self, request):
        """
        Verify TOTP code and enable 2FA
        """
        user = request.user
        code = request.data.get('code')

        if not code:
            return Response(
                {'error': 'Verification code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.two_factor_secret:
            return Response(
                {'error': '2FA setup not initiated. Call enable-totp first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify the code
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code, valid_window=1):  # Allow 30 seconds window
            user.two_factor_enabled = True
            user.save()
            return Response({
                'success': True,
                'message': '2FA successfully enabled'
            })
        else:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='disable')
    def disable_2fa(self, request):
        """Disable 2FA for the user"""
        user = request.user
        password = request.data.get('password')

        # Verify password
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.save()

        return Response({
            'success': True,
            'message': '2FA has been disabled'
        })

    @action(detail=False, methods=['post'], url_path='send-sms')
    def send_sms_code(self, request):
        """Send SMS verification code"""
        user = request.user
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate 6-digit code
        code = pyotp.random_base32()[:6]
        
        # Store code temporarily (you might want to use Redis for production)
        # For now, we'll store it in the session
        request.session[f'sms_code_{user.id}'] = code
        request.session[f'sms_phone_{user.id}'] = phone_number
        request.session.set_expiry(300)  # 5 minutes

        # Send SMS
        success, result = self._send_sms_code(phone_number, code)

        if success:
            return Response({
                'success': True,
                'message': 'Verification code sent via SMS',
                'phone_number': phone_number[-4:]  # Show last 4 digits only
            })
        else:
            return Response(
                {'error': f'Failed to send SMS: {result}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='verify-sms')
    def verify_sms_code(self, request):
        """Verify SMS code and mark phone as verified"""
        user = request.user
        code = request.data.get('code')

        if not code:
            return Response(
                {'error': 'Verification code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get stored code from session
        stored_code = request.session.get(f'sms_code_{user.id}')
        stored_phone = request.session.get(f'sms_phone_{user.id}')

        if not stored_code:
            return Response(
                {'error': 'No verification code found. Please request a new one'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if code == stored_code:
            user.phone_verified = True
            user.phone_number = stored_phone
            user.save()

            # Clear session
            del request.session[f'sms_code_{user.id}']
            del request.session[f'sms_phone_{user.id}']

            return Response({
                'success': True,
                'message': 'Phone number verified successfully'
            })
        else:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='status')
    def get_2fa_status(self, request):
        """Get current 2FA status for the user"""
        user = request.user
        
        return Response({
            'two_factor_enabled': user.two_factor_enabled,
            'phone_verified': user.phone_verified,
            'has_secret': bool(user.two_factor_secret),
            'methods': {
                'totp': user.two_factor_enabled and user.two_factor_secret,
                'sms': user.phone_verified
            }
        })

    @action(detail=False, methods=['post'], url_path='authenticate')
    def authenticate_2fa(self, request):
        """
        Authenticate with 2FA code during login
        This should be called after successful username/password authentication
        """
        user = request.user
        code = request.data.get('code')
        method = request.data.get('method', 'totp')  # 'totp' or 'sms'

        if not code:
            return Response(
                {'error': 'Verification code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if method == 'totp':
            if not user.two_factor_secret:
                return Response(
                    {'error': 'TOTP not configured'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            totp = pyotp.TOTP(user.two_factor_secret)
            if totp.verify(code, valid_window=1):
                return Response({
                    'success': True,
                    'message': '2FA authentication successful'
                })
            else:
                return Response(
                    {'error': 'Invalid authentication code'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        elif method == 'sms':
            # SMS verification logic (similar to verify_sms_code)
            stored_code = request.session.get(f'sms_code_{user.id}')
            
            if not stored_code:
                return Response(
                    {'error': 'No verification code found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if code == stored_code:
                del request.session[f'sms_code_{user.id}']
                return Response({
                    'success': True,
                    'message': '2FA authentication successful'
                })
            else:
                return Response(
                    {'error': 'Invalid authentication code'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(
            {'error': 'Invalid authentication method'},
            status=status.HTTP_400_BAD_REQUEST
        )
