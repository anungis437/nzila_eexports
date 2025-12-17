from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, track_view

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')

urlpatterns = [
    path('', include(router.urls)),
    path('api/recommendations/track-view/', track_view, name='track-view'),
]
