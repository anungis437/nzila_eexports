from django.urls import path
from . import views

urlpatterns = [
    path('revenue-trends/', views.revenue_trends, name='analytics-revenue-trends'),
    path('deal-pipeline/', views.deal_pipeline, name='analytics-deal-pipeline'),
    path('conversion-funnel/', views.conversion_funnel, name='analytics-conversion-funnel'),
    path('dealer-performance/', views.dealer_performance, name='analytics-dealer-performance'),
    path('buyer-behavior/', views.buyer_behavior, name='analytics-buyer-behavior'),
    path('inventory-insights/', views.inventory_insights, name='analytics-inventory-insights'),
    path('dashboard-summary/', views.dashboard_summary, name='analytics-dashboard-summary'),
]
