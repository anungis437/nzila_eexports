from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# All certification endpoints are available through ViewSet actions:
# POST   /shipments/{id}/lloyd-register/register/
# GET    /shipments/{id}/lloyd-register/status/
# GET    /shipments/{id}/lloyd-register/certificate/
# GET    /shipments/{id}/iso18602/xml/
# GET    /shipments/{id}/iso18602/edifact/
# POST   /shipments/{id}/security/assess/
# GET    /shipments/{id}/security/audit-log/
# GET    /shipments/{id}/certification/compliance-report/
