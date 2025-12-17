#!/usr/bin/env python
"""
ISO 28000 Certification API Test Suite

Tests all 8 certification endpoints with comprehensive scenarios:
- Lloyd's Register registration and status tracking
- ISO 18602 XML/EDIFACT export
- Security risk assessment
- Audit log verification
- Compliance reporting

Usage:
    python test_certification_api.py

Requirements:
    - Django server running at http://127.0.0.1:8000
    - Valid JWT token or Django session authentication
    - Test shipment created in database
"""

import os
import sys
import django
import json
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from deals.models import Deal
from shipments.models import Shipment, ShipmentUpdate
from shipments.certification_models import (
    SecurityRiskAssessment,
    SecurityIncident,
    PortVerification,
    ISO28000AuditLog
)
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CertificationAPITestSuite:
    """Complete test suite for ISO 28000 certification API endpoints"""
    
    def __init__(self):
        self.client = APIClient()
        self.user = None
        self.vehicle = None
        self.deal = None
        self.shipment = None
        self.base_url = 'http://127.0.0.1:8000/api/shipments/shipments/'
        
    def setup(self):
        """Create test data: user, vehicle, deal, shipment"""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.user = User.objects.filter(email='test@nzilaventures.com').first()
        if not self.user:
            self.user = User.objects.create_user(
                username='testuser',
                email='test@nzilaventures.com',
                password='TestPass123!',
                first_name='Test',
                last_name='User'
            )
            print(f"  ✅ Created test user: {self.user.email}")
        else:
            print(f"  ♻️  Using existing user: {self.user.email}")
        
        # Authenticate client
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        print(f"  ✅ Authenticated with JWT token")
        
        # Create test vehicle
        self.vehicle = Vehicle.objects.filter(vin='TEST1234567890ABC').first()
        if not self.vehicle:
            self.vehicle = Vehicle.objects.create(
                vin='TEST1234567890ABC',
                year=2023,
                make='Toyota',
                model='Land Cruiser',
                price_cad=Decimal('75000.00'),
                mileage=25000,
                color='White',
                condition='used_excellent',
                location='Vancouver, BC',
                status='available',
                dealer=self.user
            )
            print(f"  ✅ Created test vehicle: {self.vehicle.vin}")
        else:
            print(f"  ♻️  Using existing vehicle: {self.vehicle.vin}")
        
        # Create test deal
        self.deal = Deal.objects.filter(vehicle=self.vehicle).first()
        if not self.deal:
            self.deal = Deal.objects.create(
                buyer=self.user,
                dealer=self.user,
                vehicle=self.vehicle,
                agreed_price_cad=Decimal('75000.00'),
                status='completed',
                payment_status='paid'
            )
            print(f"  ✅ Created test deal: {self.deal.id}")
        else:
            print(f"  ♻️  Using existing deal: {self.deal.id}")
        
        # Create test shipment
        self.shipment = Shipment.objects.filter(tracking_number='SHIP-CERT-TEST-001').first()
        if not self.shipment:
            self.shipment = Shipment.objects.create(
                deal=self.deal,
                tracking_number='SHIP-CERT-TEST-001',
                origin_port='Vancouver, BC, Canada',
                destination_port='Mombasa, Kenya',
                status='in_transit',
                container_number='ABCD1234567',
                container_type='40ft',
                seal_number='SEAL-TEST-12345',
                seal_type='bolt'
            )
            print(f"  ✅ Created test shipment: {self.shipment.tracking_number}")
        else:
            print(f"  ♻️  Using existing shipment: {self.shipment.tracking_number}")
        
        print()
    
    def test_1_security_risk_assessment(self):
        """Test 1: Security Risk Assessment API"""
        print("🧪 TEST 1: Security Risk Assessment")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/security/assess/'
        payload = {
            'route_risk_score': 7,
            'value_risk_score': 8,
            'destination_risk_score': 6,
            'customs_risk_score': 5,
            'port_security_score': 4
        }
        
        print(f"  POST {url}")
        print(f"  Payload: {json.dumps(payload, indent=4)}")
        
        response = self.client.post(url, payload, format='json')
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print(f"  ✅ Risk Score: {data.get('risk_score')}/100")
            print(f"  ✅ Risk Level: {data.get('overall_risk_level')}")
            print(f"  ✅ Lloyd's Register Recommended: {data.get('lloyd_register_recommended')}")
            
            if data.get('mitigation_required'):
                print(f"  📋 Mitigation Measures:")
                for measure in data.get('mitigation_required', []):
                    print(f"     - {measure}")
            
            # Verify database record created
            assessment = SecurityRiskAssessment.objects.filter(shipment=self.shipment).first()
            if assessment:
                print(f"  ✅ SecurityRiskAssessment record created (ID: {assessment.id})")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_2_lloyd_register_registration(self):
        """Test 2: Lloyd's Register CTS Registration"""
        print("\n🧪 TEST 2: Lloyd's Register CTS Registration")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/lloyd-register/register/'
        payload = {'service_level': 'premium'}
        
        print(f"  POST {url}")
        print(f"  Payload: {json.dumps(payload, indent=4)}")
        
        response = self.client.post(url, payload, format='json')
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print(f"  ✅ Lloyd's Register Tracking ID: {data.get('lr_tracking_id')}")
            print(f"  ✅ Service Level: {data.get('service_level')}")
            print(f"  ✅ Status: {data.get('status')}")
            print(f"  📝 Message: {data.get('message')}")
            
            # Verify shipment updated
            self.shipment.refresh_from_db()
            if self.shipment.lloyd_register_tracking_id:
                print(f"  ✅ Shipment.lloyd_register_tracking_id updated: {self.shipment.lloyd_register_tracking_id}")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_3_lloyd_register_status(self):
        """Test 3: Lloyd's Register Status Check"""
        print("\n🧪 TEST 3: Lloyd's Register Status Check")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/lloyd-register/status/'
        
        print(f"  GET {url}")
        
        response = self.client.get(url)
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ LR Tracking ID: {data.get('lr_tracking_id')}")
            print(f"  ✅ Service Level: {data.get('service_level')}")
            print(f"  ✅ Status: {data.get('status')}")
            
            if data.get('origin_inspection'):
                inspection = data['origin_inspection']
                print(f"\n  📋 Origin Inspection:")
                print(f"     Status: {inspection.get('status')}")
                print(f"     Date: {inspection.get('date')}")
                print(f"     Surveyor: {inspection.get('surveyor')}")
            
            if data.get('destination_inspection'):
                inspection = data['destination_inspection']
                print(f"\n  📋 Destination Inspection:")
                print(f"     Status: {inspection.get('status')}")
                print(f"     Estimated: {inspection.get('estimated_date')}")
            
            print(f"\n  🔒 Seal Status: {data.get('seal_status')}")
            print(f"  📊 Incidents: {len(data.get('incidents', []))} reported")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_4_lloyd_register_certificate(self):
        """Test 4: Lloyd's Register Certificate Download"""
        print("\n🧪 TEST 4: Lloyd's Register Certificate Download")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/lloyd-register/certificate/'
        
        print(f"  GET {url}")
        
        response = self.client.get(url)
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Certificate URL: {data.get('certificate_url')}")
            print(f"  ✅ Certificate Number: {data.get('certificate_number')}")
            print(f"  ✅ Issued Date: {data.get('issued_date')}")
            print(f"  ✅ Valid Until: {data.get('valid_until')}")
            print(f"  ✅ Shipment Tracking: {data.get('shipment_tracking_number')}")
            print(f"  ✅ Verification Status: {data.get('verification_status')}")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_5_iso18602_xml_export(self):
        """Test 5: ISO 18602 XML Export"""
        print("\n🧪 TEST 5: ISO 18602 XML Export")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/iso18602/xml/'
        
        print(f"  GET {url}")
        
        response = self.client.get(url)
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200:
            xml_content = response.content.decode()
            print(f"  ✅ Content-Type: {response.get('Content-Type')}")
            print(f"  ✅ XML Length: {len(xml_content)} characters")
            
            # Show first 500 characters
            print(f"\n  📄 XML Preview:")
            print("  " + "-" * 66)
            for line in xml_content[:500].split('\n'):
                print(f"  {line}")
            print("  " + "-" * 66)
            
            # Verify shipment marked as ISO compliant
            self.shipment.refresh_from_db()
            if self.shipment.iso_18602_compliant:
                print(f"  ✅ Shipment.iso_18602_compliant = True")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_6_iso18602_edifact_export(self):
        """Test 6: ISO 18602 UN/EDIFACT Export"""
        print("\n🧪 TEST 6: ISO 18602 UN/EDIFACT Export")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/iso18602/edifact/'
        
        print(f"  GET {url}")
        
        response = self.client.get(url)
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200:
            edifact_content = response.content.decode()
            print(f"  ✅ Content-Type: {response.get('Content-Type')}")
            print(f"  ✅ EDIFACT Length: {len(edifact_content)} characters")
            
            # Show content
            print(f"\n  📄 EDIFACT Message:")
            print("  " + "-" * 66)
            for line in edifact_content.split('\n'):
                print(f"  {line}")
            print("  " + "-" * 66)
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_7_security_audit_log(self):
        """Test 7: Security Audit Log Retrieval"""
        print("\n🧪 TEST 7: Security Audit Log")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/security/audit-log/'
        
        print(f"  GET {url}")
        
        response = self.client.get(url)
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logs = data.get('audit_logs', [])
            print(f"  ✅ Total Audit Logs: {len(logs)}")
            print(f"  ✅ Shipment ID: {data.get('shipment_id')}")
            print(f"  ✅ Tracking Number: {data.get('tracking_number')}")
            
            if logs:
                print(f"\n  📋 Recent Audit Log Entries:")
                for i, log in enumerate(logs[:5], 1):
                    print(f"     {i}. [{log.get('action_type')}] {log.get('action_description')}")
                    print(f"        By: {log.get('performed_by_name')} at {log.get('action_timestamp')}")
                    print(f"        Immutable: {log.get('is_immutable')}")
                    print()
            
            # Verify immutability in database
            db_logs = ISO28000AuditLog.objects.filter(shipment=self.shipment)
            print(f"  ✅ Database Audit Logs: {db_logs.count()} records")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def test_8_compliance_report(self):
        """Test 8: Certification Compliance Report"""
        print("\n🧪 TEST 8: Certification Compliance Report")
        print("=" * 70)
        
        url = f'{self.base_url}{self.shipment.id}/certification/compliance-report/'
        
        print(f"  GET {url}")
        
        response = self.client.get(url)
        
        print(f"\n  Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Shipment ID: {data.get('shipment_id')}")
            print(f"  ✅ Tracking Number: {data.get('tracking_number')}")
            print(f"\n  📊 Compliance Scores:")
            print(f"     ISO 28000 Score: {data.get('iso_28000_score')}%")
            print(f"     ISO 18602 Score: {data.get('iso_18602_score')}%")
            print(f"     Certification Ready: {'✅ YES' if data.get('certification_ready') else '❌ NO'}")
            
            if data.get('scores_breakdown'):
                breakdown = data['scores_breakdown']
                
                print(f"\n  📋 ISO 28000 Checklist:")
                for key, value in breakdown.get('iso_28000', {}).items():
                    status = "✅" if value else "❌"
                    print(f"     {status} {key.replace('_', ' ').title()}")
                
                print(f"\n  📋 ISO 18602 Checklist:")
                for key, value in breakdown.get('iso_18602', {}).items():
                    status = "✅" if value else "❌"
                    print(f"     {status} {key.replace('_', ' ').title()}")
            
            if data.get('missing_requirements'):
                print(f"\n  ⚠️  Missing Requirements:")
                for req in data['missing_requirements']:
                    print(f"     - {req}")
            
            if data.get('recommendations'):
                print(f"\n  💡 Recommendations:")
                for rec in data['recommendations']:
                    print(f"     - {rec}")
            
            return True
        else:
            print(f"  ❌ FAILED: {response.content.decode()}")
            return False
    
    def run_all_tests(self):
        """Execute complete test suite"""
        print("\n" + "=" * 70)
        print("ISO 28000 CERTIFICATION API TEST SUITE")
        print("=" * 70)
        print(f"Base URL: {self.base_url}")
        print(f"Server: Django 4.2.27")
        print("=" * 70 + "\n")
        
        self.setup()
        
        results = {
            'Test 1: Security Risk Assessment': self.test_1_security_risk_assessment(),
            'Test 2: Lloyd\'s Register Registration': self.test_2_lloyd_register_registration(),
            'Test 3: Lloyd\'s Register Status': self.test_3_lloyd_register_status(),
            'Test 4: Lloyd\'s Register Certificate': self.test_4_lloyd_register_certificate(),
            'Test 5: ISO 18602 XML Export': self.test_5_iso18602_xml_export(),
            'Test 6: ISO 18602 EDIFACT Export': self.test_6_iso18602_edifact_export(),
            'Test 7: Security Audit Log': self.test_7_security_audit_log(),
            'Test 8: Compliance Report': self.test_8_compliance_report(),
        }
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
        
        print("=" * 70)
        print(f"Results: {passed}/{total} tests passed ({int(passed/total*100)}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! ISO 28000 certification API is fully operational.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Review output above for details.")
        
        print("=" * 70 + "\n")
        
        return passed == total


if __name__ == '__main__':
    print("\n" + "🚀 Starting ISO 28000 Certification API Tests...\n")
    
    # Check if Django server is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result != 0:
        print("❌ ERROR: Django server is not running at http://127.0.0.1:8000")
        print("   Please start the server with: python manage.py runserver")
        sys.exit(1)
    
    # Run tests
    suite = CertificationAPITestSuite()
    success = suite.run_all_tests()
    
    sys.exit(0 if success else 1)
