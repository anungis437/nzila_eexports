from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from decimal import Decimal
import uuid

from .models import Currency, PaymentMethod, Payment, Invoice, InvoiceItem, Transaction
from .serializers import (
    CurrencySerializer, PaymentMethodSerializer, PaymentMethodCreateSerializer,
    PaymentSerializer, PaymentIntentCreateSerializer, PaymentConfirmSerializer,
    RefundSerializer, InvoiceSerializer, InvoiceCreateSerializer, TransactionSerializer
)
from .stripe_service import StripePaymentService, CurrencyService
from .throttles import PaymentRateThrottle
from deals.models import Deal
from utils.pdf_generator import generate_invoice_pdf
from utils.email_service import EmailService
from shipments.models import Shipment


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing currencies"""
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def african(self, request):
        """Get only African currencies"""
        currencies = self.get_queryset().filter(is_african=True)
        serializer = self.get_serializer(currencies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def convert(self, request):
        """Convert amount between currencies"""
        amount = Decimal(request.query_params.get('amount', 0))
        from_code = request.query_params.get('from', 'USD')
        to_code = request.query_params.get('to', 'USD')
        
        from_currency = get_object_or_404(Currency, code=from_code.upper(), is_active=True)
        to_currency = get_object_or_404(Currency, code=to_code.upper(), is_active=True)
        
        converted_amount = CurrencyService.convert_amount(amount, from_currency, to_currency)
        
        return Response({
            'amount': str(amount),
            'from_currency': from_code.upper(),
            'to_currency': to_code.upper(),
            'converted_amount': str(converted_amount),
            'exchange_rate': str(from_currency.exchange_rate_to_usd / to_currency.exchange_rate_to_usd)
        })


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """API endpoint for managing payment methods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new payment method"""
        serializer = PaymentMethodCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            payment_method = StripePaymentService.create_payment_method(
                user=request.user,
                stripe_token=serializer.validated_data['stripe_token'],
                payment_type=serializer.validated_data['type']
            )
            
            if serializer.validated_data.get('set_as_default'):
                payment_method.is_default = True
                payment_method.save()
            
            return Response(
                PaymentMethodSerializer(payment_method).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a payment method"""
        payment_method = self.get_object()
        
        try:
            if payment_method.stripe_payment_method_id:
                StripePaymentService.delete_payment_method(payment_method.stripe_payment_method_id)
            else:
                payment_method.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default"""
        payment_method = self.get_object()
        payment_method.is_default = True
        payment_method.save()
        
        return Response(PaymentMethodSerializer(payment_method).data)


class PaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for managing payments"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]  # Strict rate limiting for payments
    
    def get_queryset(self):
        queryset = Payment.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by deal
        deal_id = self.request.query_params.get('deal_id')
        if deal_id:
            queryset = queryset.filter(deal_id=deal_id)
        
        return queryset.select_related('user', 'currency', 'payment_method', 'deal')
    
    @action(detail=False, methods=['post'])
    def create_intent(self, request):
        """Create a payment intent"""
        serializer = PaymentIntentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Get related objects
        deal = None
        shipment = None
        if data.get('deal_id'):
            deal = get_object_or_404(Deal, id=data['deal_id'])
        if data.get('shipment_id'):
            shipment = get_object_or_404(Shipment, id=data['shipment_id'])
        
        try:
            payment, payment_intent = StripePaymentService.create_payment_intent(
                amount=data['amount'],
                currency_code=data['currency'],
                user=request.user,
                deal=deal,
                shipment=shipment,
                payment_for=data['payment_for'],
                payment_method_id=data.get('payment_method_id'),
                description=data.get('description', '')
            )
            
            return Response({
                'payment': PaymentSerializer(payment).data,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm a payment intent"""
        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            payment, payment_intent = StripePaymentService.confirm_payment(
                serializer.validated_data['payment_intent_id']
            )
            
            return Response({
                'payment': PaymentSerializer(payment).data,
                'status': payment_intent.status,
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Create a refund for a payment"""
        payment = self.get_object()
        serializer = RefundSerializer(data={'payment_id': payment.id, **request.data})
        serializer.is_valid(raise_exception=True)
        
        if not payment.is_refundable:
            return Response(
                {'error': 'Payment is not refundable'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refund = StripePaymentService.create_refund(
                payment=payment,
                amount=serializer.validated_data.get('amount'),
                reason=serializer.validated_data.get('reason', '')
            )
            
            return Response({
                'payment': PaymentSerializer(payment).data,
                'refund': {
                    'id': refund.id,
                    'amount': refund.amount / 100,
                    'status': refund.status,
                }
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payment summary for user"""
        payments = self.get_queryset()
        
        total_paid = payments.filter(status='succeeded').aggregate(
            total=models.Sum('amount_in_usd')
        )['total'] or Decimal('0')
        
        pending = payments.filter(status='pending').count()
        succeeded = payments.filter(status='succeeded').count()
        failed = payments.filter(status='failed').count()
        
        return Response({
            'total_paid_usd': str(total_paid),
            'total_payments': payments.count(),
            'pending': pending,
            'succeeded': succeeded,
            'failed': failed,
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    """API endpoint for managing invoices"""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return Invoice.objects.all()
        return Invoice.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        """Create a new invoice"""
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            with transaction.atomic():
                # Get related objects
                user = get_object_or_404(User, id=data['user_id'])
                currency = get_object_or_404(Currency, code=data['currency'].upper())
                
                deal = None
                shipment = None
                if data.get('deal_id'):
                    deal = get_object_or_404(Deal, id=data['deal_id'])
                if data.get('shipment_id'):
                    shipment = get_object_or_404(Shipment, id=data['shipment_id'])
                
                # Calculate amounts
                subtotal = sum(
                    Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
                    for item in data['items']
                )
                tax_amount = subtotal * (data['tax_rate'] / Decimal('100'))
                total = subtotal + tax_amount - data['discount_amount']
                
                # Generate invoice number
                invoice_number = f"INV-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}"
                
                # Create invoice
                invoice = Invoice.objects.create(
                    user=user,
                    deal=deal,
                    shipment=shipment,
                    invoice_number=invoice_number,
                    subtotal=subtotal,
                    tax_rate=data['tax_rate'],
                    tax_amount=tax_amount,
                    discount_amount=data['discount_amount'],
                    total=total,
                    currency=currency,
                    issue_date=data['issue_date'],
                    due_date=data['due_date'],
                    notes=data.get('notes', ''),
                    terms=data.get('terms', ''),
                )
                
                # Create invoice items
                for i, item_data in enumerate(data['items']):
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description=item_data['description'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price'],
                        amount=Decimal(str(item_data['quantity'])) * Decimal(str(item_data['unit_price'])),
                        order=i
                    )
                
                return Response(
                    InvoiceSerializer(invoice).data,
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send invoice to customer via email"""
        invoice = self.get_object()
        
        # Send email with invoice details
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        from django.template.loader import render_to_string
        
        subject = f'Invoice #{invoice.id} from Nzila Ventures'
        
        # Plain text version
        text_message = f"""
Dear {invoice.user.get_full_name() or invoice.user.email},

Your invoice #{invoice.id} for {invoice.currency.code} {invoice.total} is ready.

Invoice Details:
- Amount: {invoice.currency.symbol}{invoice.total}
- Due Date: {invoice.due_date}
- Status: {invoice.status}

You can view and download your invoice by logging into your account.

Thank you for your business!

Best regards,
Nzila Ventures Team
"""
        
        # HTML version from template
        html_message = render_to_string('emails/invoice_email.html', {
            'invoice': invoice,
            'user_name': invoice.user.get_full_name() or invoice.user.email,
            'user_email': invoice.user.email,
            'payment_url': f'{settings.FRONTEND_URL}/invoices/{invoice.id}',
            'subject': subject,
        })
        
        try:
            msg = EmailMultiAlternatives(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [invoice.user.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            
            invoice.sent_at = timezone.now()
            invoice.status = 'sent'
            invoice.save()
            
            return Response({
                'message': 'Invoice sent successfully',
                'invoice': InvoiceSerializer(invoice).data
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to send email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        
        invoice.status = 'paid'
        invoice.paid_date = timezone.now().date()
        invoice.amount_paid = invoice.total
        invoice.save()
        
        return Response(InvoiceSerializer(invoice).data)
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate and download invoice PDF"""
        invoice = self.get_object()
        
        try:
            # Generate PDF
            pdf_buffer = generate_invoice_pdf(invoice)
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send payment reminder email"""
        invoice = self.get_object()
        
        try:
            # Get recipient email
            recipient_email = invoice.deal.buyer.email if invoice.deal and invoice.deal.buyer else invoice.user.email
            
            # Send reminder email
            EmailService.send_invoice_reminder(invoice, recipient_email)
            
            return Response({
                'message': 'Payment reminder sent successfully',
                'sent_to': recipient_email
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to send reminder: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(user=user)
        
        # Filter by type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset.select_related('user', 'currency', 'payment', 'invoice')


@api_view(['POST'])
@permission_classes([])  # Webhooks don't use authentication - signature verification instead
@csrf_exempt  # Stripe webhooks can't include CSRF tokens
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = StripePaymentService.handle_webhook_event(payload, sig_header)
        return Response({'status': 'success', 'event': event.type})
    
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Import models for aggregation
from django.db import models
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .pdf_service import pdf_generator

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_invoice_pdf(request, payment_id):
    """Generate and download invoice PDF for a payment"""
    payment = get_object_or_404(Payment, pk=payment_id)
    
    # Check permissions - user must own the payment or be admin
    if payment.user != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You do not have permission to view this invoice'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Prepare payment data
    payment_data = {
        'invoice_number': f'INV-{payment.stripe_payment_intent_id}',
        'date': payment.created_at.strftime('%B %d, %Y'),
        'due_date': 'Upon Receipt',
        'status': payment.status,
        'amount': float(payment.amount),
        'currency': payment.currency.code,
        'tax': float(payment.amount * Decimal('0.0')),  # No tax for now
        'payment_method': payment.payment_method.name if payment.payment_method else 'Stripe',
        'transaction_id': payment.stripe_payment_intent_id,
        'payment_date': payment.succeeded_at.strftime('%B %d, %Y') if payment.succeeded_at else 'Pending',
        'notes': payment.description or ''
    }
    
    # Prepare buyer data
    buyer_data = {
        'name': payment.user.get_full_name() or payment.user.email,
        'email': payment.user.email,
        'phone': getattr(payment.user, 'phone', ''),
        'address': ''
    }
    
    # Prepare deal data if exists
    deal_data = None
    if payment.deal:
        deal_data = {
            'description': f'Vehicle Export Service - Deal #{payment.deal.id}',
        }
    
    # Generate PDF
    pdf_buffer = pdf_generator.generate_invoice(payment_data, deal_data, buyer_data)
    
    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{payment.stripe_payment_intent_id}.pdf"'
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_receipt_pdf(request, payment_id):
    """Generate and download receipt PDF for a completed payment"""
    payment = get_object_or_404(Payment, pk=payment_id, status='succeeded')
    
    # Check permissions
    if payment.user != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You do not have permission to view this receipt'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Prepare payment data
    payment_data = {
        'receipt_number': f'RCP-{payment.stripe_payment_intent_id}',
        'amount': float(payment.amount),
        'currency': payment.currency.code,
        'payment_method': payment.payment_method.name if payment.payment_method else 'Stripe',
        'transaction_id': payment.stripe_payment_intent_id,
        'status': payment.status,
    }
    
    # Prepare deal data if exists
    deal_data = None
    if payment.deal:
        deal_data = {
            'description': f'Deal #{payment.deal.id}',
        }
    
    # Generate PDF
    pdf_buffer = pdf_generator.generate_receipt(payment_data, deal_data)
    
    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.stripe_payment_intent_id}.pdf"'
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_deal_report_pdf(request, deal_id):
    """Generate comprehensive deal report PDF"""
    deal = get_object_or_404(Deal, pk=deal_id)
    
    # Check permissions - user must be involved in the deal or be admin
    if deal.buyer != request.user and deal.broker != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You do not have permission to view this report'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Prepare deal data
    deal_data = {
        'deal_number': deal.id,
        'status': deal.get_status_display(),
        'created_date': deal.created_at.strftime('%B %d, %Y'),
        'updated_date': deal.updated_at.strftime('%B %d, %Y'),
        'vehicle': {
            'make': deal.vehicle.make if hasattr(deal, 'vehicle') and deal.vehicle else 'N/A',
            'model': deal.vehicle.model if hasattr(deal, 'vehicle') and deal.vehicle else 'N/A',
            'year': deal.vehicle.year if hasattr(deal, 'vehicle') and deal.vehicle else 'N/A',
            'vin': deal.vehicle.vin if hasattr(deal, 'vehicle') and deal.vehicle else 'N/A',
            'color': getattr(deal.vehicle, 'color', 'N/A') if hasattr(deal, 'vehicle') and deal.vehicle else 'N/A',
        } if hasattr(deal, 'vehicle') else None,
        'financials': {
            'purchase_price': float(deal.agreed_price_cad) if hasattr(deal, 'agreed_price_cad') else 0,
            'commission': 0,  # Commission is tracked separately in Commission model
            'shipping': 0,  # Shipping is tracked separately in Shipment model
            'total': float(deal.agreed_price_cad) if hasattr(deal, 'agreed_price_cad') else 0,
        }
    }
    
    # Generate PDF
    pdf_buffer = pdf_generator.generate_deal_report(deal_data, include_financials=True)
    
    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="deal_report_{deal.id}.pdf"'
    
    return response
