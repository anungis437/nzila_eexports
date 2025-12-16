from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LogoutView
from .jwt_views import CustomTokenObtainPairView, CustomTokenRefreshView
from .two_factor_views import TwoFactorViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'2fa', TwoFactorViewSet, basename='two-factor')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
