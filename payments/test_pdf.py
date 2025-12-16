from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from io import BytesIO
from decimal import Decimal
import PyPDF2

from payments.pdf_service import pdf_generator, PDFGenerator
from payments.models import Payment, Currency, PaymentMethod
from deals.models import Deal

User = get_user_model()


class PDFGeneratorTest(TestCase):
    """Test PDF generation service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_active=True
        )
        self.generator = PDFGenerator()

    def test_generator_initialization(self):
        """Test PDF generator initializes correctly"""
        self.assertIsNotNone(self.generator.styles)
        self.assertIn('CustomTitle', self.generator.styles.byName)
        self.assertIn('SectionHeader', self.generator.styles.byName)

    def test_generate_invoice_pdf(self):
        """Test generating invoice PDF"""
        payment_data = {
            'invoice_number': 'INV-001',
            'date': timezone.now().strftime('%B %d, %Y'),
            'due_date': 'Upon Receipt',
            'status': 'pending',
            'amount': 1000.00,
            'currency': 'USD',
            'tax': 0.00,
            'payment_method': 'Stripe',
            'transaction_id': 'test_transaction',
            'payment_date': 'Pending',
            'notes': 'Test invoice'
        }
        
        buyer_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'address': '123 Test St'
        }
        
        deal_data = {
            'description': 'Vehicle Export Service - Deal #1'
        }
        
        pdf_buffer = self.generator.generate_invoice(payment_data, deal_data, buyer_data)
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_buffer, BytesIO)
        self.assertGreater(pdf_buffer.getbuffer().nbytes, 0)
        
        # Verify PDF is valid
        pdf_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        self.assertGreater(len(pdf_reader.pages), 0)

    def test_generate_receipt_pdf(self):
        """Test generating receipt PDF"""
        payment_data = {
            'receipt_number': 'RCP-001',
            'amount': 1500.00,
            'currency': 'USD',
            'payment_method': 'Credit Card',
            'transaction_id': 'test_transaction',
            'status': 'Completed'
        }
        
        pdf_buffer = self.generator.generate_receipt(payment_data)
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_buffer, BytesIO)
        self.assertGreater(pdf_buffer.getbuffer().nbytes, 0)
        
        # Verify PDF is valid
        pdf_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        self.assertGreater(len(pdf_reader.pages), 0)

    def test_generate_deal_report_pdf(self):
        """Test generating deal report PDF"""
        deal_data = {
            'deal_number': 123,
            'status': 'approved',
            'created_date': timezone.now().strftime('%B %d, %Y'),
            'updated_date': timezone.now().strftime('%B %d, %Y'),
            'stage': 'payment_pending',
            'vehicle': {
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2023,
                'vin': '1234567890ABCDEFG',
                'color': 'Silver'
            },
            'financials': {
                'purchase_price': 25000.00,
                'commission': 2500.00,
                'shipping': 1500.00,
                'total': 29000.00
            }
        }
        
        pdf_buffer = self.generator.generate_deal_report(deal_data, include_financials=True)
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_buffer, BytesIO)
        self.assertGreater(pdf_buffer.getbuffer().nbytes, 0)
        
        # Verify PDF is valid
        pdf_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        self.assertGreater(len(pdf_reader.pages), 0)

    def test_invoice_pdf_content(self):
        """Test invoice PDF contains expected content"""
        payment_data = {
            'invoice_number': 'INV-TEST-001',
            'amount': 5000.00,
            'currency': 'USD'
        }
        
        pdf_buffer = self.generator.generate_invoice(payment_data)
        pdf_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        
        # Extract text from first page
        first_page = pdf_reader.pages[0]
        text = first_page.extract_text()
        
        # Verify key content is present
        self.assertIn('INVOICE', text)
        self.assertIn('INV-TEST-001', text)

    def test_pdf_with_missing_optional_data(self):
        """Test PDF generation with missing optional fields"""
        payment_data = {
            'invoice_number': 'INV-002',
            'amount': 1000.00,
            'currency': 'USD'
        }
        
        # Should not raise an error
        pdf_buffer = self.generator.generate_invoice(payment_data)
        self.assertIsNotNone(pdf_buffer)


class PDFAPIEndpointsTest(APITestCase):
    """Test PDF generation API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='buyer'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.dealer = User.objects.create_user(
            username='dealer',
            email='dealer@example.com',
            password='dealerpass123',
            role='dealer'
        )
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_active=True
        )
        # Create a vehicle for deal tests
        from vehicles.models import Vehicle
        self.vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Toyota',
            model='Camry',
            year=2020,
            vin='1HGBH41JXMN109187',
            mileage=30000,
            color='Blue',
            price_cad=Decimal('25000.00'),
            status='available'
        )
        self.client = APIClient()

    def test_generate_invoice_pdf_authenticated(self):
        """Test authenticated user can generate invoice PDF"""
        # Create a payment
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_001',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/invoice-pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertGreater(len(response.content), 0)

    def test_generate_receipt_pdf_succeeded_payment(self):
        """Test generating receipt PDF for succeeded payment"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1500.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1500.00'),
            stripe_payment_intent_id='test_intent_002',
            status='succeeded',
            succeeded_at=timezone.now()
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/receipt-pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertGreater(len(response.content), 0)

    def test_generate_receipt_pdf_pending_payment(self):
        """Test cannot generate receipt for pending payment"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_003',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/receipt-pdf/')
        
        # Should return 404 because payment is not succeeded
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_generate_pdf_permission_denied(self):
        """Test user cannot generate PDF for another user's payment"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        payment = Payment.objects.create(
            user=other_user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_004',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/invoice-pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_generate_any_pdf(self):
        """Test admin can generate PDF for any payment"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_005',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/invoice-pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_generate_deal_report_pdf(self):
        """Test generating deal report PDF"""
        deal = Deal.objects.create(
            vehicle=self.vehicle,
            buyer=self.user,
            dealer=self.dealer,
            agreed_price_cad=Decimal('20000.00'),
            status='pending_docs'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/deals/{deal.id}/report-pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('deal_report', response['Content-Disposition'])

    def test_unauthenticated_pdf_request(self):
        """Test unauthenticated user cannot generate PDFs"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_006',
            status='pending'
        )
        
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/invoice-pdf/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pdf_filename_generation(self):
        """Test PDF files have correct filenames"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_007',
            status='pending'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/invoice-pdf/')
        
        self.assertIn('invoice_test_intent_007.pdf', response['Content-Disposition'])

    def test_pdf_content_type_header(self):
        """Test PDF response has correct content type"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('1000.00'),
            stripe_payment_intent_id='test_intent_008',
            status='succeeded',
            succeeded_at=timezone.now()
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/payments/payments/{payment.id}/receipt-pdf/')
        
        self.assertEqual(response['Content-Type'], 'application/pdf')


class PDFIntegrationTest(TestCase):
    """Integration tests for PDF generation with real data"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_active=True
        )

    def test_full_invoice_generation_workflow(self):
        """Test complete invoice generation from payment to PDF"""
        # Create payment
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('5000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('5000.00'),
            stripe_payment_intent_id='pi_test_full_workflow',
            status='pending',
            description='Test payment for vehicle export'
        )
        
        # Prepare data
        payment_data = {
            'invoice_number': f'INV-{payment.stripe_payment_intent_id}',
            'date': payment.created_at.strftime('%B %d, %Y'),
            'amount': float(payment.amount),
            'currency': payment.currency.code,
            'status': payment.status,
            'transaction_id': payment.stripe_payment_intent_id
        }
        
        buyer_data = {
            'name': self.user.get_full_name(),
            'email': self.user.email
        }
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_invoice(payment_data, buyer_data=buyer_data)
        
        # Verify
        self.assertIsNotNone(pdf_buffer)
        self.assertGreater(pdf_buffer.getbuffer().nbytes, 0)
        
        # Verify PDF structure
        pdf_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        self.assertEqual(len(pdf_reader.pages), 1)

    def test_receipt_generation_with_confirmed_payment(self):
        """Test receipt generation for confirmed payment"""
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('3000.00'),
            currency=self.currency,
            amount_in_usd=Decimal('3000.00'),
            stripe_payment_intent_id='pi_test_receipt',
            status='succeeded',
            succeeded_at=timezone.now()
        )
        
        payment_data = {
            'receipt_number': f'RCP-{payment.stripe_payment_intent_id}',
            'amount': float(payment.amount),
            'currency': payment.currency.code,
            'payment_method': 'Stripe',
            'transaction_id': payment.stripe_payment_intent_id,
            'status': payment.status
        }
        
        pdf_buffer = pdf_generator.generate_receipt(payment_data)
        
        self.assertIsNotNone(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        self.assertGreater(len(pdf_reader.pages), 0)
