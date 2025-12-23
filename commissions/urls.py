from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommissionViewSet, BrokerTierViewSet, DealerTierViewSet, BonusTransactionViewSet,
    InterestRateViewSet
)

router = DefaultRouter()
router.register(r'commissions', CommissionViewSet)
router.register(r'broker-tiers', BrokerTierViewSet, basename='broker-tier')
router.register(r'dealer-tiers', DealerTierViewSet, basename='dealer-tier')
router.register(r'bonuses', BonusTransactionViewSet, basename='bonus')
router.register(r'interest-rates', InterestRateViewSet, basename='interest-rate')

urlpatterns = [
    path('', include(router.urls)),
]
