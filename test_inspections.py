#!/usr/bin/env python
"""
PHASE 2 - Feature 6: Third-Party Inspection Integration - Test Script

Tests for inspector directory, inspection reports, and review system.

Run this script to validate the inspection feature implementation:
    python test_inspections.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from inspections.models import ThirdPartyInspector, InspectionReport, InspectorReview
from vehicles.models import Vehicle

User = get_user_model()


class InspectionTests:
    """Test suite for third-party inspection integration"""
    
    def __init__(self):
        self.test_user = None
        self.test_vehicle = None
        self.test_inspector = None
        self.test_report = None
        self.test_review = None
        self.passed = 0
        self.failed = 0
    
    def setup(self):
        """Create test data"""
        print("Setting up test data...")
        
        # Create test user (dealer role for vehicle creation)
        self.test_user, _ = User.objects.get_or_create(
            username='inspection_test_user',
            defaults={
                'email': 'inspector_test@example.com',
                'first_name': 'Test',
                'last_name': 'Buyer',
                'role': 'dealer',
            }
        )
        
        # Create test vehicle
        self.test_vehicle, _ = Vehicle.objects.get_or_create(
            vin='TESTINSPECTIONVIN001',
            defaults={
                'dealer': self.test_user,
                'year': 2020,
                'make': 'Toyota',
                'model': 'Camry',
                'price_cad': Decimal('25000.00'),
                'mileage': 45000,
                'color': 'Silver',
                'location': 'Toronto, ON',
                'status': 'available',
            }
        )
        
        print(f"✓ Test user created: {self.test_user.username}")
        print(f"✓ Test vehicle created: {self.test_vehicle}")
    
    def test_create_inspector(self):
        """Test 1: Create third-party inspector"""
        print("\n1. Testing inspector creation...")
        try:
            self.test_inspector = ThirdPartyInspector.objects.create(
                name='John Smith',
                company='Quality Auto Inspections Inc.',
                city='Toronto',
                province='ON',
                address='123 Main St',
                postal_code='M5H 2N2',
                latitude=Decimal('43.6532'),
                longitude=Decimal('-79.3832'),
                phone='+1-416-555-0100',
                email='info@qualityautoinspections.ca',
                website='https://qualityautoinspections.ca',
                certifications='ari',
                additional_certifications='ASE Certified, Red Seal Technician',
                years_experience=15,
                specializations='Luxury vehicles, Electric vehicles, Classic cars',
                mobile_service=True,
                service_radius_km=100,
                inspection_fee=Decimal('199.99'),
                mobile_fee_extra=Decimal('50.00'),
                is_active=True,
                is_verified=True,
            )
            
            assert self.test_inspector.id is not None
            assert self.test_inspector.company == 'Quality Auto Inspections Inc.'
            assert self.test_inspector.rating == Decimal('0.00')
            assert self.test_inspector.total_inspections == 0
            
            print(f"   ✓ Inspector created: {self.test_inspector}")
            print(f"   ✓ Certifications: {self.test_inspector.get_certification_display_list()}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_create_inspection_report(self):
        """Test 2: Create inspection report"""
        print("\n2. Testing inspection report creation...")
        try:
            # Create a dummy PDF file
            pdf_content = b'%PDF-1.4 Test Inspection Report'
            pdf_file = SimpleUploadedFile(
                'inspection_report.pdf',
                pdf_content,
                content_type='application/pdf'
            )
            
            self.test_report = InspectionReport.objects.create(
                vehicle=self.test_vehicle,
                inspector=self.test_inspector,
                buyer=self.test_user,
                report_type='pre_purchase',
                inspection_date=date.today(),
                report_file=pdf_file,
                status='scheduled',
                inspection_fee_paid=Decimal('249.99'),
                payment_status='paid',
            )
            
            assert self.test_report.id is not None
            assert self.test_report.vehicle == self.test_vehicle
            assert self.test_report.inspector == self.test_inspector
            assert self.test_report.status == 'scheduled'
            
            print(f"   ✓ Report created: {self.test_report}")
            print(f"   ✓ Report type: {self.test_report.get_report_type_display()}")
            print(f"   ✓ Fee paid: ${self.test_report.inspection_fee_paid}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_update_inspection_findings(self):
        """Test 3: Update inspection findings"""
        print("\n3. Testing inspection findings update...")
        try:
            self.test_report.overall_condition = 'good'
            self.test_report.issues_found = (
                "Minor Issues:\n"
                "- Slight wear on front brake pads (30% remaining)\n"
                "- Small paint chip on rear bumper\n"
                "- Minor oil seepage from valve cover gasket"
            )
            self.test_report.recommendations = (
                "Recommended Actions:\n"
                "- Replace front brake pads within 3,000 km\n"
                "- Touch up paint chip to prevent rust\n"
                "- Monitor oil seepage; replace gasket if worsens"
            )
            self.test_report.estimated_repair_cost = Decimal('450.00')
            
            # Add component scores
            self.test_report.engine_score = 9
            self.test_report.transmission_score = 10
            self.test_report.suspension_score = 8
            self.test_report.brakes_score = 7
            self.test_report.body_score = 8
            self.test_report.interior_score = 9
            
            self.test_report.save()
            
            avg_score = self.test_report.get_average_score()
            assert avg_score is not None
            assert self.test_report.overall_condition == 'good'
            
            print(f"   ✓ Condition assessment: {self.test_report.get_overall_condition_display()}")
            print(f"   ✓ Average component score: {avg_score}/10")
            print(f"   ✓ Estimated repair cost: ${self.test_report.estimated_repair_cost}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_complete_inspection(self):
        """Test 4: Mark inspection as completed"""
        print("\n4. Testing inspection completion...")
        try:
            initial_count = self.test_inspector.total_inspections
            
            self.test_report.mark_completed()
            self.test_inspector.refresh_from_db()
            
            assert self.test_report.status == 'completed'
            assert self.test_inspector.total_inspections == initial_count + 1
            
            print(f"   ✓ Inspection marked as completed")
            print(f"   ✓ Inspector total inspections: {self.test_inspector.total_inspections}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_create_review(self):
        """Test 5: Create inspector review"""
        print("\n5. Testing inspector review creation...")
        try:
            self.test_review = InspectorReview.objects.create(
                inspector=self.test_inspector,
                buyer=self.test_user,
                inspection_report=self.test_report,
                rating=5,
                review_text=(
                    "Excellent service! John was very thorough and professional. "
                    "He took the time to explain every issue he found and provided "
                    "clear recommendations. The report was detailed and helped me "
                    "make an informed decision. Highly recommend!"
                ),
                professionalism_rating=5,
                thoroughness_rating=5,
                communication_rating=5,
                value_rating=4,
                is_verified_purchase=True,
            )
            
            assert self.test_review.id is not None
            assert self.test_review.rating == 5
            assert self.test_review.is_verified_purchase is True
            
            print(f"   ✓ Review created: {self.test_review}")
            print(f"   ✓ Overall rating: {self.test_review.rating}★")
            print(f"   ✓ Professionalism: {self.test_review.professionalism_rating}★")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_inspector_rating_update(self):
        """Test 6: Verify inspector rating update"""
        print("\n6. Testing inspector rating calculation...")
        try:
            # Refresh inspector to get updated rating
            self.test_inspector.refresh_from_db()
            
            assert self.test_inspector.rating > Decimal('0.00')
            assert self.test_inspector.total_reviews > 0
            
            print(f"   ✓ Inspector rating updated: {self.test_inspector.rating}/5.00")
            print(f"   ✓ Total reviews: {self.test_inspector.total_reviews}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_mark_review_helpful(self):
        """Test 7: Mark review as helpful"""
        print("\n7. Testing helpful vote functionality...")
        try:
            initial_votes = self.test_review.helpful_votes
            
            self.test_review.helpful_votes += 1
            self.test_review.save()
            
            assert self.test_review.helpful_votes == initial_votes + 1
            
            print(f"   ✓ Helpful votes: {self.test_review.helpful_votes}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_search_inspectors(self):
        """Test 8: Search and filter inspectors"""
        print("\n8. Testing inspector search and filtering...")
        try:
            # Test province filter
            ontario_inspectors = ThirdPartyInspector.objects.filter(province='ON')
            assert ontario_inspectors.exists()
            
            # Test city filter
            toronto_inspectors = ThirdPartyInspector.objects.filter(city__icontains='Toronto')
            assert toronto_inspectors.exists()
            
            # Test mobile service filter
            mobile_inspectors = ThirdPartyInspector.objects.filter(mobile_service=True)
            assert mobile_inspectors.exists()
            
            # Test verified filter
            verified_inspectors = ThirdPartyInspector.objects.filter(is_verified=True)
            assert verified_inspectors.exists()
            
            # Test rating filter
            rated_inspectors = ThirdPartyInspector.objects.filter(rating__gte=Decimal('4.0'))
            
            print(f"   ✓ Ontario inspectors: {ontario_inspectors.count()}")
            print(f"   ✓ Toronto inspectors: {toronto_inspectors.count()}")
            print(f"   ✓ Mobile service: {mobile_inspectors.count()}")
            print(f"   ✓ Verified inspectors: {verified_inspectors.count()}")
            print(f"   ✓ 4+ star rated: {rated_inspectors.count()}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_location_distance_calculation(self):
        """Test 9: Test haversine distance calculation"""
        print("\n9. Testing location-based search...")
        try:
            from inspections.views import haversine_distance
            
            # Test distance between Toronto and Ottawa
            toronto_lat, toronto_lon = 43.6532, -79.3832
            ottawa_lat, ottawa_lon = 45.4215, -75.6972
            
            distance_km = haversine_distance(
                toronto_lon, toronto_lat,
                ottawa_lon, ottawa_lat
            )
            
            # Distance should be approximately 350-400 km
            assert 300 < distance_km < 450
            
            print(f"   ✓ Distance calculation working")
            print(f"   ✓ Toronto to Ottawa: {distance_km:.2f} km")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def test_queryset_relationships(self):
        """Test 10: Verify model relationships"""
        print("\n10. Testing model relationships...")
        try:
            # Test inspector -> inspections relationship
            inspector_reports = self.test_inspector.inspections.all()
            assert inspector_reports.exists()
            
            # Test inspector -> reviews relationship
            inspector_reviews = self.test_inspector.reviews.all()
            assert inspector_reviews.exists()
            
            # Test vehicle -> inspection_reports relationship
            vehicle_reports = self.test_vehicle.inspection_reports.all()
            assert vehicle_reports.exists()
            
            # Test report -> review relationship
            report_review = self.test_report.review
            assert report_review is not None
            
            print(f"   ✓ Inspector inspections: {inspector_reports.count()}")
            print(f"   ✓ Inspector reviews: {inspector_reviews.count()}")
            print(f"   ✓ Vehicle reports: {vehicle_reports.count()}")
            print(f"   ✓ Report review: Found")
            self.passed += 1
            return True
        except Exception as e:
            print(f"   ✗ FAILED: {str(e)}")
            self.failed += 1
            return False
    
    def cleanup(self):
        """Clean up test data"""
        print("\nCleaning up test data...")
        try:
            if self.test_review:
                self.test_review.delete()
                print("✓ Test review deleted")
            
            if self.test_report:
                self.test_report.delete()
                print("✓ Test report deleted")
            
            if self.test_inspector:
                self.test_inspector.delete()
                print("✓ Test inspector deleted")
            
            # Don't delete user and vehicle as they might be used elsewhere
        except Exception as e:
            print(f"Warning: Cleanup error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("PHASE 2 - Feature 6: Third-Party Inspection Integration Tests")
        print("=" * 80)
        
        self.setup()
        
        self.test_create_inspector()
        self.test_create_inspection_report()
        self.test_update_inspection_findings()
        self.test_complete_inspection()
        self.test_create_review()
        self.test_inspector_rating_update()
        self.test_mark_review_helpful()
        self.test_search_inspectors()
        self.test_location_distance_calculation()
        self.test_queryset_relationships()
        
        self.cleanup()
        
        print("\n" + "=" * 80)
        print(f"TEST RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 80)
        
        if self.failed == 0:
            print("\n✓ All tests passed! Third-party inspection integration is working correctly.")
            return True
        else:
            print(f"\n✗ {self.failed} test(s) failed. Please review the errors above.")
            return False


if __name__ == '__main__':
    tests = InspectionTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1)
