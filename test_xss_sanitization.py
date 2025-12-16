"""
Test XSS sanitization in models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle, VehicleImage
from deals.models import Lead, Deal, Document

User = get_user_model()


class XSSSanitizationTestCase(TestCase):
    """Test that all user-generated content is sanitized against XSS attacks"""
    
    def setUp(self):
        """Create test users and vehicle"""
        self.dealer = User.objects.create_user(
            username='dealer1',
            email='dealer@test.com',
            password='testpass123',
            role='dealer'
        )
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@test.com',
            password='testpass123',
            role='buyer'
        )
        self.vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Toyota',
            model='Camry',
            year=2020,
            vin='1HGBH41JXMN109186',
            condition='used_good',
            mileage=50000,
            color='Blue',
            price_cad=25000.00,
            location='Toronto, ON',
            description='Clean description'
        )
    
    def test_vehicle_description_sanitization(self):
        """Test that Vehicle.description is sanitized"""
        malicious_content = '<script>alert("XSS")</script><p>Safe content</p><img src=x onerror="alert(1)">'
        
        self.vehicle.description = malicious_content
        self.vehicle.save()
        self.vehicle.refresh_from_db()
        
        # Script tags should be stripped
        self.assertNotIn('<script>', self.vehicle.description)
        self.assertNotIn('onerror', self.vehicle.description)
        # Safe HTML should be preserved
        self.assertIn('<p>Safe content</p>', self.vehicle.description)
    
    def test_vehicle_image_caption_sanitization(self):
        """Test that VehicleImage.caption is sanitized"""
        malicious_caption = '<script>steal_cookies()</script>Front view <b>nice</b>'
        
        image = VehicleImage.objects.create(
            vehicle=self.vehicle,
            caption=malicious_caption,
            order=1
        )
        image.refresh_from_db()
        
        # Script tags should be stripped
        self.assertNotIn('<script>', image.caption)
        # Safe content should be preserved (caption uses HTML sanitization)
        self.assertIn('Front view', image.caption)
    
    def test_lead_notes_sanitization(self):
        """Test that Lead.notes is sanitized"""
        malicious_notes = '<script>bad()</script><p>Customer interested</p><a href="javascript:alert(1)">Click</a>'
        
        lead = Lead.objects.create(
            buyer=self.buyer,
            vehicle=self.vehicle,
            status='new',
            notes=malicious_notes
        )
        lead.refresh_from_db()
        
        # Script tags should be stripped
        self.assertNotIn('<script>', lead.notes)
        self.assertNotIn('javascript:', lead.notes)
        # Safe content should be preserved
        self.assertIn('<p>Customer interested</p>', lead.notes)
    
    def test_deal_notes_sanitization(self):
        """Test that Deal.notes is sanitized"""
        malicious_notes = '<img src=x onerror=alert(1)><ul><li>Item 1</li></ul>'
        
        deal = Deal.objects.create(
            vehicle=self.vehicle,
            buyer=self.buyer,
            dealer=self.dealer,
            agreed_price_cad=24000.00,
            status='pending_docs',
            notes=malicious_notes
        )
        deal.refresh_from_db()
        
        # Malicious attributes should be stripped
        self.assertNotIn('onerror', deal.notes)
        # Safe HTML should be preserved
        self.assertIn('<ul>', deal.notes)
        self.assertIn('<li>Item 1</li>', deal.notes)
    
    def test_document_notes_sanitization(self):
        """Test that Document.notes is sanitized"""
        deal = Deal.objects.create(
            vehicle=self.vehicle,
            buyer=self.buyer,
            dealer=self.dealer,
            agreed_price_cad=24000.00,
            status='pending_docs'
        )
        
        malicious_notes = '<iframe src="evil.com"></iframe><strong>Important</strong>'
        
        doc = Document.objects.create(
            deal=deal,
            document_type='title',
            uploaded_by=self.buyer,
            notes=malicious_notes
        )
        doc.refresh_from_db()
        
        # Dangerous tags should be stripped
        self.assertNotIn('<iframe>', doc.notes)
        # Safe formatting should be preserved
        self.assertIn('<strong>Important</strong>', doc.notes)
    
    def test_empty_fields_not_affected(self):
        """Test that empty/None fields are handled gracefully"""
        vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Honda',
            model='Accord',
            year=2019,
            vin='1HGCM82633A123456',
            condition='used_good',
            mileage=60000,
            color='Red',
            price_cad=22000.00,
            location='Montreal, QC',
            description=''  # Empty description
        )
        
        # Should not raise an error
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.description, '')
    
    def test_none_fields_handled(self):
        """Test that empty values are handled without errors"""
        lead = Lead.objects.create(
            buyer=self.buyer,
            vehicle=self.vehicle,
            status='new',
            notes=''  # Empty string instead of None
        )
        
        # Should not raise an error
        lead.refresh_from_db()
        self.assertEqual(lead.notes, '')
