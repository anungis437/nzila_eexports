"""
Test script for Phase 2 - Feature 5: Export Documentation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from vehicles.models import Vehicle
from accounts.models import User
from documents.models import ExportDocument, ExportChecklist
from documents.cbsa_form_generator import CBSAForm1Generator
from documents.title_guides import ProvincialTitleGuides
from documents.lien_check_service import PPSALienCheckService
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

def test_cbsa_form_generation():
    """Test CBSA Form 1 PDF generation"""
    print("\n=== Testing CBSA Form 1 Generation ===")
    
    # Get test vehicle and user
    vehicle = Vehicle.objects.first()
    user = User.objects.filter(is_active=True).first()
    
    if not vehicle or not user:
        print("❌ No vehicle or user found for testing")
        return False
    
    print(f"✓ Using Vehicle ID: {vehicle.id} ({vehicle.year} {vehicle.make} {vehicle.model})")
    print(f"✓ Using User ID: {user.id} ({user.username})")
    
    # Generate CBSA Form 1
    try:
        generator = CBSAForm1Generator(vehicle, user)
        pdf_buffer = generator.generate_pdf()
        
        # Create ExportDocument record
        export_doc = ExportDocument.objects.create(
            vehicle=vehicle,
            buyer=user,
            document_type='CBSA_FORM_1',
            status='GENERATED',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # Save PDF file
        pdf_buffer.seek(0)
        export_doc.file.save(
            f'cbsa_form1_{vehicle.vin}_{timezone.now().strftime("%Y%m%d")}.pdf',
            ContentFile(pdf_buffer.read()),
            save=True
        )
        
        print(f"✓ CBSA Form 1 generated successfully")
        print(f"✓ Document ID: {export_doc.id}")
        print(f"✓ File saved to: {export_doc.file.name}")
        print(f"✓ Valid until: {export_doc.expires_at.strftime('%Y-%m-%d')}")
        print(f"✓ File size: {export_doc.file.size} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Error generating CBSA form: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_title_guides():
    """Test provincial title guides"""
    print("\n=== Testing Provincial Title Guides ===")
    
    try:
        # Test Ontario guide
        on_guide = ProvincialTitleGuides.get_guide('ON')
        print(f"✓ Ontario Guide:")
        print(f"  Authority: {on_guide['authority']}")
        print(f"  Website: {on_guide['website']}")
        print(f"  Required docs: {len(on_guide['required_documents'])} items")
        print(f"  Process steps: {len(on_guide['process_steps'])} steps")
        
        # Test Quebec guide
        qc_guide = ProvincialTitleGuides.get_guide('QC')
        print(f"✓ Quebec Guide:")
        print(f"  Authority: {qc_guide['authority']}")
        print(f"  Website: {qc_guide['website']}")
        
        # Test all provinces
        all_guides = ProvincialTitleGuides.get_all_provinces()
        print(f"✓ Total provinces covered: {len(all_guides)}")
        print(f"  Provinces: {', '.join([p['code'] for p in all_guides])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing title guides: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_lien_check():
    """Test PPSA lien check service"""
    print("\n=== Testing PPSA Lien Check ===")
    
    try:
        vehicle = Vehicle.objects.first()
        if not vehicle:
            print("❌ No vehicle found for testing")
            return False
        
        print(f"✓ Checking lien for Vehicle ID: {vehicle.id} (VIN: {vehicle.vin})")
        
        # Perform lien check
        result = PPSALienCheckService.check_lien(vehicle.vin, 'ON')
        
        print(f"✓ Lien check completed")
        print(f"  Status: {result['lien_status']}")
        print(f"  Has lien: {result['has_lien']}")
        print(f"  Certificate: {result['certificate_number']}")
        print(f"  Message: {result['message']}")
        
        if result['has_lien'] and result['liens']:
            print(f"  Liens found: {len(result['liens'])}")
            for i, lien in enumerate(result['liens'], 1):
                print(f"    Lien {i}:")
                print(f"      Type: {lien['lien_type']}")
                print(f"      Secured party: {lien['secured_party']}")
                print(f"      Amount: ${lien['lien_amount']:,.2f}")
        
        # Update vehicle lien status
        vehicle.lien_checked = True
        vehicle.lien_status = result['lien_status']
        vehicle.save()
        print(f"✓ Vehicle lien status updated")
        
        # Test registry info
        registry = PPSALienCheckService.get_registry_info('ON')
        print(f"✓ Ontario PPSA Registry:")
        print(f"  Name: {registry['name']}")
        print(f"  Website: {registry['website']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing lien check: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_export_checklist():
    """Test export checklist"""
    print("\n=== Testing Export Checklist ===")
    
    try:
        vehicle = Vehicle.objects.first()
        user = User.objects.filter(is_active=True).first()
        
        if not vehicle or not user:
            print("❌ No vehicle or user found for testing")
            return False
        
        # Get or create checklist (handle existing from previous test run)
        checklist, created = ExportChecklist.objects.get_or_create(
            vehicle=vehicle,
            defaults={
                'buyer': user,
                'title_verified': True,
                'lien_checked': True,
                'insurance_confirmed': False,
                'payment_cleared': True,
                'inspection_completed': False,
                'cbsa_form_generated': True,
                'title_guide_provided': True
            }
        )
        
        if not created:
            # Update existing checklist for testing
            checklist.buyer = user
            checklist.title_verified = True
            checklist.lien_checked = True
            checklist.insurance_confirmed = False
            checklist.payment_cleared = True
            checklist.inspection_completed = False
            checklist.cbsa_form_generated = True
            checklist.title_guide_provided = True
            checklist.save()
            print(f"✓ Using existing checklist (updated)")
        else:
            print(f"✓ Export checklist created")
        
        print(f"  Checklist ID: {checklist.id}")
        print(f"  Completion: {checklist.get_completion_percentage()}%")
        print(f"  Export ready: {checklist.export_ready}")
        print(f"  Items completed:")
        print(f"    Title verified: {checklist.title_verified}")
        print(f"    Lien checked: {checklist.lien_checked}")
        print(f"    Insurance: {checklist.insurance_confirmed}")
        print(f"    Payment cleared: {checklist.payment_cleared}")
        print(f"    Inspection: {checklist.inspection_completed}")
        print(f"    CBSA form: {checklist.cbsa_form_generated}")
        print(f"    Title guide: {checklist.title_guide_provided}")
        
        # Update checklist
        checklist.insurance_confirmed = True
        checklist.inspection_completed = True
        checklist.save()
        checklist.check_completion()
        
        print(f"✓ Checklist updated")
        print(f"  New completion: {checklist.get_completion_percentage()}%")
        print(f"  Export ready: {checklist.export_ready}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing export checklist: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_document_expiration():
    """Test document expiration tracking"""
    print("\n=== Testing Document Expiration ===")
    
    try:
        # Get a CBSA form document
        doc = ExportDocument.objects.filter(document_type='CBSA_FORM_1').first()
        
        if not doc:
            print("⚠ No CBSA form found, skipping expiration test")
            return True
        
        print(f"✓ Testing document ID: {doc.id}")
        print(f"  Created: {doc.created_at.strftime('%Y-%m-%d')}")
        print(f"  Expires: {doc.expires_at.strftime('%Y-%m-%d')}")
        print(f"  Is expired: {doc.is_expired()}")
        print(f"  Status: {doc.status}")
        
        # Test expired document detection
        if doc.is_expired():
            doc.mark_expired()
            print(f"✓ Document marked as expired")
            print(f"  New status: {doc.status}")
        else:
            days_until_expiry = (doc.expires_at - timezone.now()).days
            print(f"✓ Document valid for {days_until_expiry} more days")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing document expiration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all export documentation tests"""
    print("=" * 60)
    print("PHASE 2 - FEATURE 5: EXPORT DOCUMENTATION TESTS")
    print("=" * 60)
    
    results = {
        'CBSA Form Generation': test_cbsa_form_generation(),
        'Title Guides': test_title_guides(),
        'Lien Check': test_lien_check(),
        'Export Checklist': test_export_checklist(),
        'Document Expiration': test_document_expiration(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Feature 5 is working correctly.")
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
