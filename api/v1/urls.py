"""
API v1 URL Configuration
Namespaced API endpoints for versioning
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets from apps
from accounts.views import UserViewSet
from vehicles.views import VehicleViewSet
from deals.views import LeadViewSet, DealViewSet, DocumentViewSet
from shipments.views import ShipmentViewSet
from commissions.views import CommissionViewSet

# Import JWT views
from accounts.jwt_views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

# Import privacy views
from accounts import privacy_views

# Create router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'deals', DealViewSet, basename='deal')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'commissions', CommissionViewSet, basename='commission')

app_name = 'api_v1'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # JWT Authentication
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # GDPR/PIPEDA Compliance
    path('privacy/export/', privacy_views.export_user_data, name='export_data'),
    path('privacy/delete/', privacy_views.request_data_deletion, name='request_deletion'),
    path('privacy/settings/', privacy_views.privacy_settings, name='privacy_settings'),
    path('privacy/settings/update/', privacy_views.update_privacy_settings, name='update_privacy_settings'),
]
