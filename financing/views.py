"""
Financing Calculator API Views

ViewSets for financing endpoints:
- Interest rate lookup
- Loan scenario management
- Trade-in value estimation
- Quick payment calculation
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from decimal import Decimal

from .models import InterestRate, LoanScenario, TradeInEstimate
from .serializers import (
    InterestRateSerializer,
    LoanScenarioSerializer,
    LoanScenarioCreateSerializer,
    LoanScenarioComparisonSerializer,
    TradeInEstimateSerializer,
    TradeInEstimateCreateSerializer,
    QuickCalculateSerializer,
    QuickCalculateResultSerializer,
)


class InterestRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving current interest rates
    
    List: Get all active interest rates
    Retrieve: Get specific rate by ID
    rates_by_tier: Get rates for a specific credit tier
    """
    
    queryset = InterestRate.objects.filter(is_active=True).order_by('credit_tier', 'loan_term_months')
    serializer_class = InterestRateSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by credit tier
        credit_tier = self.request.query_params.get('credit_tier')
        if credit_tier:
            queryset = queryset.filter(credit_tier=credit_tier)
        
        # Filter by loan term
        loan_term = self.request.query_params.get('loan_term_months')
        if loan_term:
            queryset = queryset.filter(loan_term_months=loan_term)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def rates_by_tier(self, request):
        """
        Get all rates grouped by credit tier
        
        Returns: {
            'excellent': [...],
            'good': [...],
            'fair': [...],
            'poor': [...],
            'bad': [...]
        }
        """
        rates_by_tier = {}
        
        for tier_code, tier_display in InterestRate.CREDIT_TIER_CHOICES:
            rates = InterestRate.objects.filter(
                credit_tier=tier_code,
                is_active=True
            ).order_by('loan_term_months')
            
            rates_by_tier[tier_code] = InterestRateSerializer(rates, many=True).data
        
        return Response(rates_by_tier)
    
    @action(detail=False, methods=['get'])
    def current_rate(self, request):
        """
        Get current rate for specific credit tier and loan term
        
        Query params:
        - credit_tier: excellent/good/fair/poor/bad
        - loan_term_months: 12/24/36/48/60/72/84
        """
        credit_tier = request.query_params.get('credit_tier', 'good')
        loan_term_months = request.query_params.get('loan_term_months', 48)
        
        try:
            rate = InterestRate.objects.filter(
                credit_tier=credit_tier,
                loan_term_months=int(loan_term_months),
                is_active=True
            ).order_by('-effective_date').first()
            
            if rate:
                return Response(InterestRateSerializer(rate).data)
            else:
                return Response(
                    {'error': 'No rate found for specified parameters'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except ValueError:
            return Response(
                {'error': 'Invalid loan_term_months parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoanScenarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for loan scenario management
    
    List: Get all scenarios for current user
    Create: Create new scenario with calculations
    Retrieve: Get specific scenario
    Update: Update scenario and recalculate
    Delete: Remove scenario
    compare: Compare multiple scenarios
    """
    
    serializer_class = LoanScenarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own scenarios
        return LoanScenario.objects.filter(buyer=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LoanScenarioCreateSerializer
        return LoanScenarioSerializer
    
    def perform_update(self, serializer):
        """Recalculate after update"""
        scenario = serializer.save()
        scenario.calculate()
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Quick calculation without saving to database
        
        Use for "what-if" scenarios before saving
        """
        serializer = QuickCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create temporary scenario for calculation
        temp_scenario = LoanScenario(
            buyer=request.user,
            vehicle_price=serializer.validated_data['vehicle_price'],
            down_payment=serializer.validated_data['down_payment'],
            trade_in_value=serializer.validated_data['trade_in_value'],
            loan_term_months=serializer.validated_data['loan_term_months'],
            credit_tier=serializer.validated_data['credit_tier'],
            province=serializer.validated_data['province'],
        )
        
        # Calculate (don't save)
        temp_scenario.calculate()
        
        # Return calculated values
        result = {
            'vehicle_price': temp_scenario.vehicle_price,
            'down_payment': temp_scenario.down_payment,
            'trade_in_value': temp_scenario.trade_in_value,
            'loan_term_months': temp_scenario.loan_term_months,
            'credit_tier': temp_scenario.credit_tier,
            'province': temp_scenario.province,
            'loan_amount': temp_scenario.loan_amount,
            'monthly_payment': temp_scenario.monthly_payment,
            'total_interest': temp_scenario.total_interest,
            'total_cost': temp_scenario.total_cost,
            'annual_interest_rate': temp_scenario.annual_interest_rate,
            'pst_amount': temp_scenario.pst_amount,
            'gst_hst_amount': temp_scenario.gst_hst_amount,
            'documentation_fee': temp_scenario.documentation_fee,
            'license_registration_fee': temp_scenario.license_registration_fee,
            'down_payment_percentage': temp_scenario.down_payment_percentage,
            'loan_to_value_ratio': temp_scenario.loan_to_value_ratio,
        }
        
        result_serializer = QuickCalculateResultSerializer(result)
        return Response(result_serializer.data)
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """
        Compare multiple loan scenarios
        
        Query params:
        - scenario_ids: comma-separated list of scenario IDs to compare
        """
        scenario_ids_str = request.query_params.get('scenario_ids', '')
        
        if not scenario_ids_str:
            return Response(
                {'error': 'scenario_ids parameter required (comma-separated list)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            scenario_ids = [int(id_str.strip()) for id_str in scenario_ids_str.split(',')]
        except ValueError:
            return Response(
                {'error': 'Invalid scenario_ids format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get scenarios (ensure user owns them)
        scenarios = LoanScenario.objects.filter(
            id__in=scenario_ids,
            buyer=request.user
        ).order_by('monthly_payment')
        
        if not scenarios.exists():
            return Response(
                {'error': 'No scenarios found with provided IDs'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build comparison data
        comparison = []
        for scenario in scenarios:
            comparison.append({
                'scenario_id': scenario.id,
                'scenario_name': scenario.scenario_name or f"Scenario {scenario.id}",
                'loan_term_months': scenario.loan_term_months,
                'down_payment': scenario.down_payment,
                'monthly_payment': scenario.monthly_payment,
                'total_interest': scenario.total_interest,
                'total_cost': scenario.total_cost,
                'annual_interest_rate': scenario.annual_interest_rate,
            })
        
        serializer = LoanScenarioComparisonSerializer(comparison, many=True)
        
        # Add summary
        response_data = {
            'scenarios': serializer.data,
            'summary': {
                'lowest_monthly_payment': min(c['monthly_payment'] for c in comparison),
                'highest_monthly_payment': max(c['monthly_payment'] for c in comparison),
                'lowest_total_interest': min(c['total_interest'] for c in comparison),
                'highest_total_interest': max(c['total_interest'] for c in comparison),
            }
        }
        
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status for scenario"""
        scenario = self.get_object()
        scenario.is_favorite = not scenario.is_favorite
        scenario.save()
        
        return Response({
            'id': scenario.id,
            'is_favorite': scenario.is_favorite
        })


class TradeInEstimateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for trade-in value estimation
    
    List: Get all estimates for current user
    Create: Request new trade-in estimate
    Retrieve: Get specific estimate
    Delete: Remove estimate
    """
    
    serializer_class = TradeInEstimateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own estimates
        return TradeInEstimate.objects.filter(buyer=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TradeInEstimateCreateSerializer
        return TradeInEstimateSerializer
    
    @action(detail=False, methods=['post'])
    def quick_estimate(self, request):
        """
        Get quick trade-in estimate without saving to database
        
        Useful for "what-if" scenarios
        """
        # Validate input
        required_fields = ['year', 'make', 'model', 'mileage']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            estimates = TradeInEstimate.generate_estimate(
                year=int(request.data['year']),
                make=request.data['make'],
                model=request.data['model'],
                mileage=int(request.data['mileage']),
                condition=request.data.get('condition', 'good'),
                province=request.data.get('province', 'ON')
            )
            
            return Response({
                'year': request.data['year'],
                'make': request.data['make'],
                'model': request.data['model'],
                'mileage': request.data['mileage'],
                'condition': request.data.get('condition', 'good'),
                'province': request.data.get('province', 'ON'),
                'trade_in_value': estimates['trade_in_value'],
                'private_party_value': estimates['private_party_value'],
                'retail_value': estimates['retail_value'],
                'data_source': 'KBB Canada (Mock)',
            })
        except (ValueError, KeyError) as e:
            return Response(
                {'error': f'Invalid input: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
