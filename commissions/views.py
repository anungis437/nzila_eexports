from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Commission
from .serializers import CommissionSerializer


class CommissionViewSet(viewsets.ModelViewSet):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'commission_type', 'recipient']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Users see only their own commissions (unless admin)
        if not user.is_admin():
            queryset = queryset.filter(recipient=user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a commission (admin only)"""
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can approve commissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        commission = self.get_object()
        if commission.status != 'pending':
            return Response(
                {'error': 'Only pending commissions can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        commission.status = 'approved'
        commission.approved_at = timezone.now()
        commission.save()
        
        serializer = self.get_serializer(commission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark commission as paid (admin only)"""
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can mark commissions as paid'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        commission = self.get_object()
        if commission.status != 'approved':
            return Response(
                {'error': 'Only approved commissions can be marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        if request.data.get('notes'):
            commission.notes = request.data['notes']
        commission.save()
        
        serializer = self.get_serializer(commission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a commission (admin only)"""
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can cancel commissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        commission = self.get_object()
        if commission.status in ['paid', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel paid or already cancelled commissions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        commission.status = 'cancelled'
        commission.save()
        
        serializer = self.get_serializer(commission)
        return Response(serializer.data)
