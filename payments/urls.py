from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CurrencyViewSet, PaymentMethodViewSet, PaymentViewSet,
    InvoiceViewSet, TransactionViewSet, stripe_webhook,
    generate_invoice_pdf, generate_receipt_pdf, generate_deal_report_pdf
)

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
    path('payments/<int:payment_id>/invoice-pdf/', generate_invoice_pdf, name='invoice-pdf'),
    path('payments/<int:payment_id>/receipt-pdf/', generate_receipt_pdf, name='receipt-pdf'),
    path('deals/<int:deal_id>/report-pdf/', generate_deal_report_pdf, name='deal-report-pdf'),
]
