from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleHistoryReportViewSet,
    AccidentRecordViewSet,
    ServiceRecordViewSet,
    OwnershipRecordViewSet,
    get_comprehensive_history,
    get_carfax_report,
    get_transport_canada_recalls,
    get_quick_summary,
)

router = DefaultRouter()
router.register(r'reports', VehicleHistoryReportViewSet, basename='history-report')
router.register(r'accidents', AccidentRecordViewSet, basename='accident-record')
router.register(r'service', ServiceRecordViewSet, basename='service-record')
router.register(r'ownership', OwnershipRecordViewSet, basename='ownership-record')

urlpatterns = [
    path('', include(router.urls)),
    
    # Canadian Data Integration Endpoints (rate-limited)
    path('<int:vehicle_id>/comprehensive/', get_comprehensive_history, name='comprehensive-history'),
    path('<int:vehicle_id>/carfax/', get_carfax_report, name='carfax-report'),
    path('<int:vehicle_id>/recalls/', get_transport_canada_recalls, name='transport-canada-recalls'),
    path('<int:vehicle_id>/summary/', get_quick_summary, name='quick-summary'),
]
