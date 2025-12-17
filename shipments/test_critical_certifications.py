"""
Comprehensive test suite for critical maritime certifications
Tests SOLAS VGM, AMS, ACI, AES, ENS, ISPS Code, HS Tariff, Hazmat, Bill of Lading

Run with: python manage.py test shipments.test_critical_certifications
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Shipment
from .certification_validators import (
    validate_vgm_weight,
    validate_vgm_method,
    validate_ams_24hour_rule,
    validate_scac_code,
    validate_aci_24hour_rule,
    validate_pars_paps_number,
    validate_aes_requirements,
    validate_schedule_b_code,
    validate_mrn_number,
    validate_hs_tariff_code,
    validate_imo_vessel_number,
    validate_hazmat_fields,
    validate_bill_of_lading_completeness,
    validate_isps_security_level,
)
from deals.models import Deal
from vehicles.models import Vehicle


class VGMCertificationTests(TestCase):
    """Test SOLAS VGM (Verified Gross Mass) certification"""
    
    def setUp(self):
        """Create test vehicle and deal"""
        self.vehicle = Vehicle.objects.create(
            vin='1HGCM82633A123456',
            make='Honda',
            model='Accord',
            year=2023,
            color='Blue'
        )
        self.deal = Deal.objects.create(
            vehicle=self.vehicle,
            target_port='Los Angeles',
            target_country='USA',
            status='pending'
        )
    
    def test_vgm_weight_within_limits_20ft(self):
        """VGM weight under 24,000kg for 20ft container passes"""
        try:
            validate_vgm_weight(Decimal('23000.50'), '20ST')
        except ValidationError:
            self.fail("Valid VGM weight should not raise ValidationError")
    
    def test_vgm_weight_exceeds_20ft_limit(self):
        """VGM weight over 24,000kg for 20ft container fails"""
        with self.assertRaises(ValidationError) as context:
            validate_vgm_weight(Decimal('25000.00'), '20ST')
        self.assertIn('exceeds', str(context.exception))
    
    def test_vgm_weight_within_limits_40ft(self):
        """VGM weight under 30,480kg for 40ft container passes"""
        try:
            validate_vgm_weight(Decimal('29500.75'), '40HC')
        except ValidationError:
            self.fail("Valid VGM weight should not raise ValidationError")
    
    def test_vgm_suspiciously_low_weight(self):
        """VGM weight under 1,000kg raises warning"""
        with self.assertRaises(ValidationError) as context:
            validate_vgm_weight(Decimal('500.00'), '20ST')
        self.assertIn('suspiciously low', str(context.exception))
    
    def test_vgm_method_requires_certified_by(self):
        """VGM method without certifier fails"""
        with self.assertRaises(ValidationError):
            validate_vgm_method('method_1', None)
    
    def test_vgm_method_with_certifier_passes(self):
        """VGM method with certifier passes"""
        try:
            validate_vgm_method('method_1', 'ABC Shipping Co.')
        except ValidationError:
            self.fail("Valid VGM method should not raise ValidationError")
    
    def test_shipment_with_complete_vgm(self):
        """Create shipment with complete VGM certification"""
        shipment = Shipment.objects.create(
            deal=self.deal,
            tracking_number='VGM-TEST-001',
            container_type='40HC',
            vgm_weight_kg=Decimal('28500.50'),
            vgm_method='method_1',
            vgm_certified_by='Maersk Line',
            vgm_certification_date=timezone.now(),
            vgm_certificate_number='VGM-CERT-2024-001'
        )
        self.assertEqual(shipment.vgm_weight_kg, Decimal('28500.50'))
        self.assertEqual(shipment.vgm_method, 'method_1')


class AMSCustomsTests(TestCase):
    """Test AMS (Automated Manifest System) US customs compliance"""
    
    def setUp(self):
        """Create test shipment to USA"""
        vehicle = Vehicle.objects.create(
            vin='2HGCM82633A654321',
            make='Toyota',
            model='Camry',
            year=2024
        )
        deal = Deal.objects.create(
            vehicle=vehicle,
            target_port='New York',
            target_country='USA'
        )
        self.shipment = Shipment.objects.create(
            deal=deal,
            tracking_number='AMS-TEST-001',
            destination_country='USA'
        )
    
    def test_ams_filed_25_hours_before_departure(self):
        """AMS filed 25 hours before departure passes 24-hour rule"""
        departure = timezone.now() + timedelta(hours=25)
        submission = timezone.now()
        
        try:
            validate_ams_24hour_rule(submission, departure)
        except ValidationError:
            self.fail("AMS filed 25 hours early should pass")
    
    def test_ams_filed_23_hours_before_departure_fails(self):
        """AMS filed 23 hours before departure violates 24-hour rule"""
        departure = timezone.now() + timedelta(hours=23)
        submission = timezone.now()
        
        with self.assertRaises(ValidationError) as context:
            validate_ams_24hour_rule(submission, departure)
        self.assertIn('24+ hours', str(context.exception))
        self.assertIn('Do Not Load', str(context.exception))
    
    def test_ams_filed_way_in_advance(self):
        """AMS filed 40 days early raises warning"""
        departure = timezone.now() + timedelta(days=40)
        submission = timezone.now()
        
        with self.assertRaises(ValidationError) as context:
            validate_ams_24hour_rule(submission, departure)
        self.assertIn('Unusual timing', str(context.exception))
    
    def test_valid_scac_code(self):
        """Valid 4-letter SCAC code passes"""
        try:
            validate_scac_code('MAEU')  # Maersk
            validate_scac_code('MSCU')  # MSC
            validate_scac_code('COSU')  # COSCO
        except ValidationError:
            self.fail("Valid SCAC codes should pass")
    
    def test_invalid_scac_code_too_short(self):
        """SCAC code with 3 letters fails"""
        with self.assertRaises(ValidationError):
            validate_scac_code('MAE')
    
    def test_invalid_scac_code_lowercase(self):
        """SCAC code with lowercase fails"""
        with self.assertRaises(ValidationError):
            validate_scac_code('maeu')
    
    def test_shipment_with_complete_ams(self):
        """Create shipment with complete AMS filing"""
        self.shipment.ams_filing_number = 'AMS20240101123456'
        self.shipment.ams_submission_date = timezone.now()
        self.shipment.ams_status = 'accepted'
        self.shipment.ams_scac_code = 'MAEU'
        self.shipment.save()
        
        self.assertEqual(self.shipment.ams_status, 'accepted')


class ACICanadaCustomsTests(TestCase):
    """Test ACI (Advance Commercial Information) Canada customs"""
    
    def test_aci_marine_24hour_rule(self):
        """ACI for marine shipment requires 24 hours advance"""
        arrival = timezone.now() + timedelta(hours=24, minutes=30)
        submission = timezone.now()
        
        try:
            validate_aci_24hour_rule(submission, arrival, 'marine')
        except ValidationError:
            self.fail("ACI filed 24.5 hours early should pass")
    
    def test_aci_marine_23_hours_fails(self):
        """ACI for marine < 24 hours fails"""
        arrival = timezone.now() + timedelta(hours=23)
        submission = timezone.now()
        
        with self.assertRaises(ValidationError):
            validate_aci_24hour_rule(submission, arrival, 'marine')
    
    def test_aci_highway_1hour_rule(self):
        """ACI for highway shipment requires 1 hour advance"""
        arrival = timezone.now() + timedelta(hours=1, minutes=15)
        submission = timezone.now()
        
        try:
            validate_aci_24hour_rule(submission, arrival, 'highway')
        except ValidationError:
            self.fail("ACI highway filed 1.25 hours early should pass")
    
    def test_valid_pars_number(self):
        """Valid 4-10 digit PARS number passes"""
        try:
            validate_pars_paps_number('1234', None)
            validate_pars_paps_number('12345678', None)
        except ValidationError:
            self.fail("Valid PARS should pass")
    
    def test_invalid_pars_number(self):
        """Invalid PARS with letters fails"""
        with self.assertRaises(ValidationError):
            validate_pars_paps_number('ABC123', None)
    
    def test_valid_paps_number(self):
        """Valid 4-10 digit PAPS number passes"""
        try:
            validate_pars_paps_number(None, '5678')
        except ValidationError:
            self.fail("Valid PAPS should pass")


class AESExportTests(TestCase):
    """Test AES (Automated Export System) US export compliance"""
    
    def test_aes_not_required_under_2500(self):
        """Export under $2,500 doesn't require AES"""
        try:
            validate_aes_requirements(Decimal('2000.00'), False, None, 'NOEEI 30.37(a)')
        except ValidationError:
            self.fail("Export under $2,500 should not require AES ITN")
    
    def test_aes_required_over_2500(self):
        """Export over $2,500 requires AES ITN or exemption"""
        with self.assertRaises(ValidationError) as context:
            validate_aes_requirements(Decimal('5000.00'), False, None, None)
        self.assertIn('2,500 threshold', str(context.exception))
    
    def test_aes_with_itn_passes(self):
        """Export over $2,500 with ITN passes"""
        try:
            validate_aes_requirements(Decimal('10000.00'), False, 'X20240101234567', None)
        except ValidationError:
            self.fail("Export with valid ITN should pass")
    
    def test_export_license_requires_itn(self):
        """Export requiring license must have AES ITN"""
        with self.assertRaises(ValidationError):
            validate_aes_requirements(Decimal('1000.00'), True, None, None)
    
    def test_valid_schedule_b_code(self):
        """Valid 10-digit Schedule B code passes"""
        try:
            validate_schedule_b_code('8704210000')  # Motor vehicles
        except ValidationError:
            self.fail("Valid Schedule B should pass")
    
    def test_invalid_schedule_b_code(self):
        """Invalid 6-digit Schedule B fails"""
        with self.assertRaises(ValidationError):
            validate_schedule_b_code('870421')


class ENSEUCustomsTests(TestCase):
    """Test ENS (Entry Summary Declaration) EU customs"""
    
    def test_valid_mrn_number(self):
        """Valid 18-character MRN passes"""
        try:
            validate_mrn_number('24GB12345678901234')
        except ValidationError:
            self.fail("Valid MRN should pass")
    
    def test_invalid_mrn_too_short(self):
        """MRN with 16 characters fails"""
        with self.assertRaises(ValidationError):
            validate_mrn_number('24GB123456789012')
    
    def test_invalid_mrn_format(self):
        """MRN without country code fails"""
        with self.assertRaises(ValidationError):
            validate_mrn_number('241234567890123456')


class HSTariffTests(TestCase):
    """Test HS Tariff Code and customs valuation"""
    
    def test_valid_6digit_hs_code(self):
        """Valid 6-digit HS code passes"""
        try:
            validate_hs_tariff_code('870421')
        except ValidationError:
            self.fail("Valid 6-digit HS should pass")
    
    def test_valid_10digit_hts_code(self):
        """Valid 10-digit HTS code passes"""
        try:
            validate_hs_tariff_code('8704.21.00.00')
        except ValidationError:
            self.fail("Valid 10-digit HTS should pass")
    
    def test_invalid_hs_code_letters(self):
        """HS code with letters fails"""
        with self.assertRaises(ValidationError):
            validate_hs_tariff_code('87AB21')


class IMOVesselTests(TestCase):
    """Test IMO vessel number validation"""
    
    def test_valid_imo_with_prefix(self):
        """Valid IMO number with prefix passes"""
        try:
            validate_imo_vessel_number('IMO 9074729')
        except ValidationError:
            self.fail("Valid IMO should pass")
    
    def test_valid_imo_without_prefix(self):
        """Valid IMO number without prefix passes"""
        try:
            validate_imo_vessel_number('9074729')
        except ValidationError:
            self.fail("Valid IMO without prefix should pass")
    
    def test_invalid_imo_check_digit(self):
        """IMO with wrong check digit fails"""
        with self.assertRaises(ValidationError) as context:
            validate_imo_vessel_number('9074720')  # Wrong check digit
        self.assertIn('Check digit', str(context.exception))


class HazmatTests(TestCase):
    """Test hazmat/dangerous goods validation"""
    
    def test_hazmat_requires_un_number(self):
        """Hazmat shipment without UN number fails"""
        with self.assertRaises(ValidationError):
            validate_hazmat_fields(True, None, 'Class 9', '+1-555-0100')
    
    def test_hazmat_requires_imdg_class(self):
        """Hazmat shipment without IMDG class fails"""
        with self.assertRaises(ValidationError):
            validate_hazmat_fields(True, 'UN3171', None, '+1-555-0100')
    
    def test_hazmat_requires_emergency_contact(self):
        """Hazmat shipment without emergency contact fails"""
        with self.assertRaises(ValidationError):
            validate_hazmat_fields(True, 'UN3171', 'Class 9', None)
    
    def test_hazmat_complete_passes(self):
        """Hazmat with all required fields passes"""
        try:
            validate_hazmat_fields(True, 'UN3171', 'Class 9', '+1-555-0100')
        except ValidationError:
            self.fail("Complete hazmat documentation should pass")
    
    def test_valid_un_number_format(self):
        """Valid UN number format passes"""
        try:
            validate_hazmat_fields(True, 'UN3171', 'Class 9', '+1-555-0100')
        except ValidationError:
            self.fail("Valid UN3171 should pass")
    
    def test_invalid_un_number_format(self):
        """Invalid UN number format fails"""
        with self.assertRaises(ValidationError):
            validate_hazmat_fields(True, '3171', 'Class 9', '+1-555-0100')


class BillOfLadingTests(TestCase):
    """Test Bill of Lading completeness validation"""
    
    def test_bol_requires_consignee_name(self):
        """B/L with number requires consignee name"""
        with self.assertRaises(ValidationError):
            validate_bill_of_lading_completeness('BOL-123', None, '123 Main St', 'FOB')
    
    def test_bol_requires_consignee_address(self):
        """B/L with number requires consignee address"""
        with self.assertRaises(ValidationError):
            validate_bill_of_lading_completeness('BOL-123', 'ABC Corp', None, 'FOB')
    
    def test_bol_requires_incoterm(self):
        """B/L with number requires incoterm"""
        with self.assertRaises(ValidationError):
            validate_bill_of_lading_completeness('BOL-123', 'ABC Corp', '123 Main St', None)
    
    def test_bol_complete_passes(self):
        """Complete B/L passes validation"""
        try:
            validate_bill_of_lading_completeness('BOL-123', 'ABC Corp', '123 Main St', 'FOB')
        except ValidationError:
            self.fail("Complete B/L should pass")


class ISPSSecurityTests(TestCase):
    """Test ISPS Code port security validation"""
    
    def test_isps_level1_no_certification_ok(self):
        """ISPS Level 1 works without port certification"""
        try:
            validate_isps_security_level('level_1', False, False)
        except ValidationError:
            self.fail("Level 1 should not require certification")
    
    def test_isps_level2_requires_certification(self):
        """ISPS Level 2 requires both ports certified"""
        with self.assertRaises(ValidationError) as context:
            validate_isps_security_level('level_2', True, False)
        self.assertIn('both origin and destination', str(context.exception))
    
    def test_isps_level3_requires_certification(self):
        """ISPS Level 3 requires both ports certified"""
        with self.assertRaises(ValidationError):
            validate_isps_security_level('level_3', False, True)
    
    def test_isps_level2_with_certification_passes(self):
        """ISPS Level 2 with both ports certified passes"""
        try:
            validate_isps_security_level('level_2', True, True)
        except ValidationError:
            self.fail("Level 2 with certification should pass")


class IntegrationTests(TestCase):
    """Test complete shipment workflows with all certifications"""
    
    def setUp(self):
        """Create test vehicle and deal"""
        self.vehicle = Vehicle.objects.create(
            vin='1HGCM82633A999999',
            make='Tesla',
            model='Model 3',
            year=2024,
            color='White'
        )
        self.deal = Deal.objects.create(
            vehicle=self.vehicle,
            target_port='New York',
            target_country='USA',
            status='confirmed'
        )
    
    def test_complete_us_export_shipment(self):
        """Create complete US export with all certifications"""
        shipment = Shipment.objects.create(
            deal=self.deal,
            tracking_number='COMPLETE-US-001',
            shipping_company='Maersk Line',
            origin_port='Yokohama, Japan',
            destination_port='New York, USA',
            destination_country='USA',
            status='pending',
            estimated_departure=timezone.now() + timedelta(days=7),
            estimated_arrival=timezone.now() + timedelta(days=21),
            
            # Container & Vessel
            container_number='MAEU1234567',
            container_type='40HC',
            vessel_name='Maersk Sealand',
            voyage_number='024N',
            imo_vessel_number='9074729',
            
            # SOLAS VGM
            vgm_weight_kg=Decimal('27500.00'),
            vgm_method='method_1',
            vgm_certified_by='Maersk Line',
            vgm_certification_date=timezone.now(),
            vgm_certificate_number='VGM-2024-001',
            
            # AMS
            ams_filing_number='AMS20240515123456',
            ams_submission_date=timezone.now(),
            ams_status='accepted',
            ams_scac_code='MAEU',
            
            # Bill of Lading
            bill_of_lading_number='MAEU-BOL-2024-12345',
            bill_of_lading_type='master',
            bill_of_lading_date=timezone.now(),
            freight_terms='prepaid',
            incoterm='FOB',
            consignee_name='ABC Auto Imports Inc',
            consignee_address='123 Import Blvd, New York, NY 10001',
            
            # HS Tariff
            hs_tariff_code='8703.80.00.00',
            customs_value_declared=Decimal('45000.00'),
            customs_value_currency='USD',
            
            # Hazmat (Tesla = lithium battery)
            contains_hazmat=True,
            un_number='UN3171',
            imdg_class='Class 9',
            hazmat_emergency_contact='+1-650-681-5555',
            msds_attached=True,
        )
        
        self.assertEqual(shipment.tracking_number, 'COMPLETE-US-001')
        self.assertEqual(shipment.vgm_weight_kg, Decimal('27500.00'))
        self.assertEqual(shipment.ams_status, 'accepted')
        self.assertTrue(shipment.contains_hazmat)
        self.assertEqual(shipment.un_number, 'UN3171')
    
    def test_complete_canada_import_shipment(self):
        """Create complete Canada import with ACI"""
        shipment = Shipment.objects.create(
            deal=self.deal,
            tracking_number='COMPLETE-CA-001',
            destination_country='Canada',
            destination_port='Vancouver, Canada',
            
            # ACI
            aci_submission_date=timezone.now(),
            cargo_control_document_number='CCD20240515001',
            pars_number='1234',
            aci_status='cleared',
            
            # SOLAS VGM
            vgm_weight_kg=Decimal('25000.00'),
            vgm_method='method_2',
            vgm_certified_by='Canada Auto Logistics',
        )
        
        self.assertEqual(shipment.aci_status, 'cleared')
        self.assertEqual(shipment.pars_number, '1234')
