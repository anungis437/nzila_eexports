from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, DealerRatingViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'dealer-ratings', DealerRatingViewSet, basename='dealer-rating')

urlpatterns = [
    path('', include(router.urls)),
]
