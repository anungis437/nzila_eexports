from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LogoutView
from .jwt_views import CustomTokenObtainPairView, CustomTokenRefreshView
from .two_factor_views import TwoFactorViewSet
from .privacy_views import (
    export_user_data, request_data_deletion, privacy_settings, 
    update_privacy_settings, grant_initial_consent, consent_history,
    data_retention_info, report_data_breach
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'2fa', TwoFactorViewSet, basename='two-factor')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # PIPEDA & Law 25 Compliance Endpoints
    path('privacy/export/', export_user_data, name='export_user_data'),
    path('privacy/delete/', request_data_deletion, name='request_data_deletion'),
    path('privacy/settings/', privacy_settings, name='privacy_settings'),
    path('privacy/settings/update/', update_privacy_settings, name='update_privacy_settings'),
    path('privacy/consent/grant/', grant_initial_consent, name='grant_initial_consent'),
    path('privacy/consent/history/', consent_history, name='consent_history'),
    path('privacy/retention/', data_retention_info, name='data_retention_info'),
    path('privacy/breach/report/', report_data_breach, name='report_data_breach'),
]
