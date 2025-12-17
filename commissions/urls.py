from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommissionViewSet, BrokerTierViewSet, DealerTierViewSet, BonusTransactionViewSet
)

router = DefaultRouter()
router.register(r'commissions', CommissionViewSet)
router.register(r'broker-tiers', BrokerTierViewSet, basename='broker-tier')
router.register(r'dealer-tiers', DealerTierViewSet, basename='dealer-tier')
router.register(r'bonuses', BonusTransactionViewSet, basename='bonus')

urlpatterns = [
    path('', include(router.urls)),
]
