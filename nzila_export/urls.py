"""
URL configuration for nzila_export project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from .views import home
from .analytics_views import get_analytics_stats, get_revenue_chart, get_pipeline_chart, get_recent_activities
from .settings_views import company_settings, currency_rates, currency_rate_detail

def trigger_error(request):
    """Sentry test endpoint - triggers a division by zero error"""
    division_by_zero = 1 / 0

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    
    # Sentry debug endpoint (only available in DEBUG mode)
    path('sentry-debug/', trigger_error),
    
    # Versioned API endpoints
    path('api/v1/', include('api.v1.urls', namespace='api_v1')),
    
    # Legacy endpoints (deprecated - redirect to v1)
    path('api/accounts/', include('accounts.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/deals/', include('deals.urls')),
    path('api/shipments/', include('shipments.urls')),
    path('api/commissions/', include('commissions.urls')),
    path('api/', include('favorites.urls')),
    path('', include('saved_searches.urls')),
    path('', include('price_alerts.urls')),
    path('', include('recommendations.urls')),
    path('api/vehicle-history/', include('vehicle_history.urls')),
    
    # PHASE 2 - Feature 5: Export Documentation endpoints
    path('api/', include('documents.urls')),
    
    # PHASE 2 - Feature 6: Third-Party Inspection Integration endpoints
    path('api/inspections/', include('inspections.urls')),
    
    # Audit Trail and Compliance endpoints
    path('api/audit/', include('audit.urls')),
    
    # PHASE 3 - Feature 7: Financing Calculator Enhancement endpoints
    path('api/financing/', include('financing.urls')),
    
    # Chat/Messaging endpoints
    path('api/chat/', include('chat.urls')),
    
    # Reviews and Ratings endpoints
    path('api/', include('reviews.urls')),
    
    # Analytics Dashboard endpoints (new comprehensive analytics)
    path('api/analytics-dashboard/', include('analytics_dashboard.urls')),
    
    # Analytics endpoints
    path('api/analytics/', include('analytics.urls')),
    
    # Analytics endpoints (legacy)
    path('api/analytics/stats/', get_analytics_stats, name='analytics-stats'),
    path('api/analytics/revenue/', get_revenue_chart, name='analytics-revenue'),
    path('api/analytics/pipeline/', get_pipeline_chart, name='analytics-pipeline'),
    path('api/analytics/activities/', get_recent_activities, name='analytics-activities'),
    
    # Settings endpoints
    path('api/settings/company/', company_settings, name='company-settings'),
    path('api/settings/currency/', currency_rates, name='currency-rates'),
    path('api/settings/currency/<int:pk>/', currency_rate_detail, name='currency-rate-detail'),
    
    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),
]

# Django Debug Toolbar URLs (only available in DEBUG mode)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
