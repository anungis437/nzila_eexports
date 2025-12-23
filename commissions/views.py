from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from .models import Commission, BrokerTier, DealerTier, BonusTransaction, InterestRate
from .serializers import (
    CommissionSerializer, BrokerTierSerializer, DealerTierSerializer,
    BonusTransactionSerializer, LeaderboardSerializer, InterestRateSerializer,
    InterestRateMatrixSerializer
)
from utils.permissions import IsAdmin


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
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get commission dashboard for current user"""
        user = request.user
        
        # Get tier info based on user type
        tier_info = None
        if user.is_broker():
            try:
                broker_tier = BrokerTier.objects.get(broker=user)
                tier_info = BrokerTierSerializer(broker_tier).data
            except BrokerTier.DoesNotExist:
                pass
        elif user.is_dealer():
            try:
                dealer_tier = DealerTier.objects.get(dealer=user)
                tier_info = DealerTierSerializer(dealer_tier).data
            except DealerTier.DoesNotExist:
                pass
        
        # Get commission stats
        commissions = Commission.objects.filter(recipient=user)
        
        stats = {
            'pending_commissions': commissions.filter(status='pending').aggregate(
                count=Count('id'),
                total=Sum('amount_cad')
            ),
            'approved_commissions': commissions.filter(status='approved').aggregate(
                count=Count('id'),
                total=Sum('amount_cad')
            ),
            'paid_commissions': commissions.filter(status='paid').aggregate(
                count=Count('id'),
                total=Sum('amount_cad')
            ),
            'total_earnings': commissions.filter(
                status__in=['approved', 'paid']
            ).aggregate(total=Sum('amount_cad'))['total'] or 0,
        }
        
        # Get bonuses
        bonuses = BonusTransaction.objects.filter(user=user).order_by('-created_at')[:5]
        
        return Response({
            'tier_info': tier_info,
            'stats': stats,
            'recent_bonuses': BonusTransactionSerializer(bonuses, many=True).data,
        })
    
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


class BrokerTierViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for broker tier information"""
    queryset = BrokerTier.objects.all()
    serializer_class = BrokerTierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Brokers see only their own tier (unless admin)
        if user.is_broker() and not user.is_admin():
            return BrokerTier.objects.filter(broker=user)
        return super().get_queryset()
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get broker leaderboard with country filtering"""
        period = request.query_params.get('period', 'month')  # month, quarter, all-time
        country = request.query_params.get('country', None)  # Filter by African country
        
        if period == 'month':
            queryset = BrokerTier.objects.filter(deals_this_month__gt=0).order_by('-deals_this_month')
            deals_field = 'deals_this_month'
            volume_field = 'volume_this_month'
        else:  # all-time
            queryset = BrokerTier.objects.filter(total_deals__gt=0).order_by('-total_deals')
            deals_field = 'total_deals'
            volume_field = 'total_commissions_earned'
        
        # Filter by country if specified (mostly African countries)
        if country:
            queryset = queryset.filter(country=country)
        
        # Build leaderboard data
        leaderboard = []
        for rank, broker_tier in enumerate(queryset[:50], start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': broker_tier.broker.id,
                'user_name': broker_tier.broker.get_full_name(),
                'deals': getattr(broker_tier, deals_field),
                'volume': getattr(broker_tier, volume_field),
                'tier': broker_tier.current_tier,
                'tier_display': broker_tier.get_current_tier_display(),
                'commission_rate': broker_tier.get_commission_rate(),
                'country': broker_tier.country,
                'country_display': broker_tier.get_country_display(),
                'city': broker_tier.city,
            })
        
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tier(self, request):
        """Get current user's broker tier"""
        user = request.user
        if not user.is_broker():
            return Response(
                {'error': 'Only brokers have tier information'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        broker_tier, created = BrokerTier.objects.get_or_create(broker=user)
        serializer = self.get_serializer(broker_tier)
        return Response(serializer.data)


class DealerTierViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for dealer tier information"""
    queryset = DealerTier.objects.all()
    serializer_class = DealerTierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Dealers see only their own tier (unless admin)
        if user.is_dealer() and not user.is_admin():
            return DealerTier.objects.filter(dealer=user)
        return super().get_queryset()
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get dealer leaderboard"""
        period = request.query_params.get('period', 'quarter')  # quarter, all-time
        province = request.query_params.get('province', None)
        
        if period == 'quarter':
            queryset = DealerTier.objects.filter(deals_this_quarter__gt=0).order_by('-deals_this_quarter')
            deals_field = 'deals_this_quarter'
        else:  # all-time
            queryset = DealerTier.objects.filter(total_deals__gt=0).order_by('-total_deals')
            deals_field = 'total_deals'
        
        # Filter by province if specified
        if province:
            queryset = queryset.filter(province=province)
        
        # Build leaderboard data
        leaderboard = []
        for rank, dealer_tier in enumerate(queryset[:50], start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': dealer_tier.dealer.id,
                'user_name': dealer_tier.dealer.get_full_name(),
                'deals': getattr(dealer_tier, deals_field),
                'volume': dealer_tier.total_commissions_earned,
                'tier': dealer_tier.current_tier,
                'tier_display': dealer_tier.get_current_tier_display(),
                'commission_rate': dealer_tier.get_total_commission_rate(),
            })
        
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tier(self, request):
        """Get current user's dealer tier"""
        user = request.user
        if not user.is_dealer():
            return Response(
                {'error': 'Only dealers have tier information'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dealer_tier, created = DealerTier.objects.get_or_create(dealer=user)
        serializer = self.get_serializer(dealer_tier)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_profile(self, request, pk=None):
        """Update dealer profile (province, certifications, etc) - Admin only"""
        dealer_tier = self.get_object()
        
        # Update allowed fields
        allowed_fields = ['province', 'city', 'is_rural', 'is_first_nations', 
                         'omvic_certified', 'amvic_certified']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(dealer_tier, field, request.data[field])
        
        dealer_tier.save()
        serializer = self.get_serializer(dealer_tier)
        return Response(serializer.data)


class BonusTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for bonus transactions"""
    queryset = BonusTransaction.objects.all()
    serializer_class = BonusTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'bonus_type', 'user']
    
    def get_queryset(self):
        user = self.request.user
        # Users see only their own bonuses (unless admin)
        if not user.is_admin():
            return BonusTransaction.objects.filter(user=user)
        return super().get_queryset()


class InterestRateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interest rate management (Admin only).
    Provides CRUD operations for managing interest rates by province and credit tier.
    """
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['province', 'credit_tier', 'is_active']
    
    def get_serializer_context(self):
        """Pass request to serializer for created_by field"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def current(self, request):
        """
        Get current rates for all credit tiers, optionally filtered by province.
        Public endpoint for Financing.tsx to fetch rates.
        
        Query params:
        - province (optional): Filter by province code (e.g., 'ON', 'QC')
        """
        province = request.query_params.get('province')
        
        if province:
            rates = InterestRate.get_rate_matrix(province=province)
            return Response({
                'province': province,
                'rates': rates,
                'effective_date': timezone.now().date()
            })
        else:
            # Return rates for all provinces
            all_rates = {}
            for province_code, province_name in InterestRate.PROVINCE_CHOICES:
                all_rates[province_code] = InterestRate.get_rate_matrix(province=province_code)
            
            return Response({
                'all_provinces': all_rates,
                'effective_date': timezone.now().date()
            })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_tier(self, request):
        """
        Get current rate for a specific province and credit tier.
        Public endpoint for Financing.tsx.
        
        Query params:
        - province (required): Province code
        - credit_tier (required): Credit tier code
        """
        province = request.query_params.get('province')
        credit_tier = request.query_params.get('credit_tier')
        
        if not province or not credit_tier:
            return Response(
                {'error': 'Both province and credit_tier parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rate_obj = InterestRate.get_current_rate(province, credit_tier)
        
        if rate_obj:
            return Response({
                'province': province,
                'credit_tier': credit_tier,
                'rate_percentage': rate_obj.rate_percentage,
                'effective_date': rate_obj.effective_date
            })
        else:
            return Response(
                {'error': 'No rate found for the specified province and credit tier'},
                status=status.HTTP_404_NOT_FOUND
            )

