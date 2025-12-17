from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SavedSearchViewSet

router = DefaultRouter()
router.register(r'saved-searches', SavedSearchViewSet, basename='savedsearch')

urlpatterns = [
    path('api/', include(router.urls)),
]
