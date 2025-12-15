from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Commission
from .serializers import CommissionSerializer


class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'commission_type']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Users see only their own commissions
        if not user.is_admin():
            queryset = queryset.filter(recipient=user)
        
        return queryset
