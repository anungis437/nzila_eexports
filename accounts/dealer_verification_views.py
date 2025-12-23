"""
Dealer Verification ViewSets
Phase 3 - Feature 9
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from accounts.dealer_verification_models import DealerLicense, DealerVerification
from accounts.models import User
from accounts.dealer_verification_serializers import (
    DealerLicenseSerializer,
    DealerLicenseCreateSerializer,
    DealerLicenseApprovalSerializer,
    DealerVerificationSerializer,
    DealerVerificationUpdateSerializer,
    DealerVerificationActionSerializer,
    DealerBadgeSerializer,
)


class DealerLicenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for dealer licenses.
    
    Dealers can:
    - List their own licenses
    - Create new license submissions
    - View license status
    
    Admins can:
    - List all licenses
    - Approve/reject licenses
    - Update license details
    """
    queryset = DealerLicense.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DealerLicenseCreateSerializer
        elif self.action == 'approve_reject':
            return DealerLicenseApprovalSerializer
        return DealerLicenseSerializer
    
    def get_queryset(self):
        """Filter licenses based on user role"""
        user = self.request.user
        if user.role == 'admin':
            # Admins see all licenses
            return DealerLicense.objects.all()
        elif user.role == 'dealer':
            # Dealers only see their own licenses
            return DealerLicense.objects.filter(dealer=user)
        else:
            # Other users can't access licenses
            return DealerLicense.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_licenses(self, request):
        """Get current dealer's licenses"""
        if request.user.role != 'dealer':
            return Response(
                {'error': 'Only dealers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        licenses = DealerLicense.objects.filter(dealer=request.user)
        serializer = DealerLicenseSerializer(licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending license submissions (admin only)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        licenses = DealerLicense.objects.filter(status='pending')
        serializer = DealerLicenseSerializer(licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """Approve or reject a license submission (admin only)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        license_obj = self.get_object()
        serializer = DealerLicenseApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        notes = serializer.validated_data.get('notes', '')
        
        if action_type == 'approve':
            license_obj.approve(request.user)
            
            # Update dealer verification
            try:
                verification = DealerVerification.objects.get(dealer=license_obj.dealer)
                verification.license_verified = True
                verification.update_metrics()
            except DealerVerification.DoesNotExist:
                # Create verification if doesn't exist
                verification = DealerVerification.objects.create(dealer=license_obj.dealer)
                verification.license_verified = True
                verification.update_metrics()
            
            return Response({
                'message': 'License approved successfully',
                'license': DealerLicenseSerializer(license_obj).data,
                'verification': DealerVerificationSerializer(verification).data
            })
        
        else:  # reject
            rejection_reason = serializer.validated_data['rejection_reason']
            license_obj.reject(request.user, rejection_reason)
            
            return Response({
                'message': 'License rejected',
                'license': DealerLicenseSerializer(license_obj).data
            })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get licenses expiring within 30 days"""
        licenses = [
            license for license in self.get_queryset()
            if license.expires_soon and not license.is_expired
        ]
        serializer = DealerLicenseSerializer(licenses, many=True)
        return Response(serializer.data)


class DealerVerificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for dealer verification status.
    
    Dealers can:
    - View their own verification status
    - Update business information
    - Request verification
    
    Admins can:
    - View all verifications
    - Update verification flags
    - Approve/suspend dealers
    
    Public users can:
    - View verified dealer badges (read-only)
    """
    queryset = DealerVerification.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'badges']:
            # Public can view basic verification info
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return DealerVerificationUpdateSerializer
        elif self.action == 'verification_action':
            return DealerVerificationActionSerializer
        return DealerVerificationSerializer
    
    def get_queryset(self):
        """Filter based on user role and action"""
        user = self.request.user
        
        # Public endpoints show verified dealers only
        if not user.is_authenticated:
            return DealerVerification.objects.filter(status='verified')
        
        if user.role == 'admin':
            # Admins see all verifications
            return DealerVerification.objects.all()
        elif user.role == 'dealer':
            # Dealers only see their own verification
            return DealerVerification.objects.filter(dealer=user)
        else:
            # Other users see verified dealers
            return DealerVerification.objects.filter(status='verified')
    
    @action(detail=False, methods=['get'])
    def my_verification(self, request):
        """Get current dealer's verification status"""
        if request.user.role != 'dealer':
            return Response(
                {'error': 'Only dealers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        verification, created = DealerVerification.objects.get_or_create(dealer=request.user)
        serializer = DealerVerificationSerializer(verification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def badges(self, request):
        """Get all verified dealers with badges (public)"""
        verifications = DealerVerification.objects.filter(
            status='verified'
        ).exclude(badge='none').order_by('-trust_score')
        
        badges_data = [
            {
                'dealer_id': v.dealer.id,
                'dealer_username': v.dealer.username,
                'badge': v.badge,
                'badge_display': v.get_badge_display(),
                'trust_score': v.trust_score,
                'verification_percentage': v.verification_percentage,
                'total_sales': v.total_sales,
                'average_rating': v.average_rating,
            }
            for v in verifications
        ]
        
        serializer = DealerBadgeSerializer(badges_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def gold_dealers(self, request):
        """Get gold badge dealers"""
        verifications = DealerVerification.objects.filter(
            status='verified',
            badge='gold'
        ).order_by('-trust_score')
        serializer = DealerVerificationSerializer(verifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verification_action(self, request, pk=None):
        """Admin action to update verification flags or dealer status"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        verification = self.get_object()
        serializer = DealerVerificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        
        if action_type == 'verify':
            verification_type = serializer.validated_data['verification_type']
            value = serializer.validated_data.get('value', True)
            
            # Update the appropriate verification flag
            if verification_type == 'license':
                verification.license_verified = value
            elif verification_type == 'insurance':
                verification.insurance_verified = value
            elif verification_type == 'business':
                verification.business_verified = value
            elif verification_type == 'identity':
                verification.identity_verified = value
            elif verification_type == 'address':
                verification.address_verified = value
            
            # If all verifications are complete, mark dealer as verified
            if all([
                verification.license_verified,
                verification.insurance_verified,
                verification.business_verified,
                verification.identity_verified,
                verification.address_verified
            ]):
                verification.verify_dealer(request.user)
            else:
                verification.update_metrics()
            
            return Response({
                'message': f'{verification_type.title()} verification updated',
                'verification': DealerVerificationSerializer(verification).data
            })
        
        else:  # suspend
            suspension_reason = serializer.validated_data['suspension_reason']
            verification.suspend_dealer(suspension_reason)
            
            return Response({
                'message': 'Dealer suspended',
                'verification': DealerVerificationSerializer(verification).data
            })
    
    @action(detail=True, methods=['post'])
    def update_metrics(self, request, pk=None):
        """Manually trigger metrics recalculation"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        verification = self.get_object()
        verification.update_metrics()
        
        return Response({
            'message': 'Metrics updated successfully',
            'verification': DealerVerificationSerializer(verification).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall verification statistics (admin only)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_dealers': DealerVerification.objects.count(),
            'verified_dealers': DealerVerification.objects.filter(status='verified').count(),
            'pending_dealers': DealerVerification.objects.filter(status='pending').count(),
            'suspended_dealers': DealerVerification.objects.filter(status='suspended').count(),
            'gold_badges': DealerVerification.objects.filter(badge='gold').count(),
            'silver_badges': DealerVerification.objects.filter(badge='silver').count(),
            'bronze_badges': DealerVerification.objects.filter(badge='bronze').count(),
            'pending_licenses': DealerLicense.objects.filter(status='pending').count(),
            'expiring_licenses': len([
                l for l in DealerLicense.objects.filter(status='verified')
                if l.expires_soon and not l.is_expired
            ]),
        }
        
        return Response(stats)
