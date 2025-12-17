"""
Seed demo data for critical maritime certifications testing
Creates realistic shipment scenarios with complete certification data

Run with: python manage.py shell < shipments/seed_critical_certifications.py
or: python manage.py runscript seed_critical_certifications (if django-extensions installed)
"""
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from shipments.models import Shipment
from deals.models import Deal
from vehicles.models import Vehicle
from accounts.models import User

# Get or create demo user
demo_user, _ = User.objects.get_or_create(
    email='demo@nzilaexports.com',
    defaults={
        'full_name': 'Demo User',
        'phone_number': '+1-555-0100'
    }
)

print("🚀 Starting critical certifications demo data seeding...\n")

# ===== SCENARIO 1: USA Export (Tesla Model 3) =====
print("📦 SCENARIO 1: USA Export - Tesla Model 3 with full compliance")

vehicle1 = Vehicle.objects.create(
    vin='5YJ3E1EA6JF000001',
    make='Tesla',
    model='Model 3',
    year=2024,
    color='Midnight Silver Metallic',
    mileage=15,
    condition='new',
    price=Decimal('45000.00'),
    currency='USD'
)

deal1 = Deal.objects.create(
    vehicle=vehicle1,
    seller=demo_user,
    buyer=demo_user,
    target_port='New York',
    target_country='USA',
    status='confirmed',
    agreed_price=Decimal('45000.00')
)

shipment1 = Shipment.objects.create(
    deal=deal1,
    tracking_number='US-TESLA-2024-001',
    shipping_company='Maersk Line',
    origin_port='Yokohama, Japan',
    destination_port='Port of New York/New Jersey, USA',
    destination_country='USA',
    status='in_transit',
    estimated_departure=timezone.now() + timedelta(days=2),
    actual_departure=timezone.now() - timedelta(days=5),
    estimated_arrival=timezone.now() + timedelta(days=14),
    notes='Electric vehicle - lithium battery hazmat compliance required',
    
    # Container & Seal
    container_number='MAEU1234567',
    container_type='40HC',
    seal_number='SEAL-2024-12345',
    seal_type='electronic',
    seal_intact=True,
    
    # Vessel Information
    vessel_name='Maersk Sealand',
    voyage_number='024N',
    imo_vessel_number='9074729',  # Valid IMO with check digit
    
    # PRIORITY 1: SOLAS VGM (CRITICAL)
    vgm_weight_kg=Decimal('27500.50'),
    vgm_method='method_1',
    vgm_certified_by='Maersk Line Yokohama',
    vgm_certification_date=timezone.now() - timedelta(days=5),
    vgm_certificate_number='VGM-JP-2024-001234',
    
    # PRIORITY 1: AMS - US Customs (CRITICAL)
    ams_filing_number='AMS20240515123456',
    ams_submission_date=timezone.now() - timedelta(days=6),  # 24+ hours before departure
    ams_status='accepted',
    ams_arrival_notice_date=timezone.now() - timedelta(days=5),
    ams_scac_code='MAEU',
    
    # PRIORITY 2: AES - US Export (filed by exporter in Japan)
    aes_itn_number='X20240515123456789',
    aes_filing_date=timezone.now() - timedelta(days=7),
    schedule_b_code='8703800000',  # Electric vehicles
    export_license_required=False,
    
    # PRIORITY 3: Bill of Lading
    bill_of_lading_number='MAEU-BOL-2024-NY-12345',
    bill_of_lading_type='master',
    bill_of_lading_date=timezone.now() - timedelta(days=5),
    freight_terms='prepaid',
    incoterm='FOB',
    shipper_reference='TESLA-JP-EXP-001',
    consignee_name='Premium Auto Imports LLC',
    consignee_address='123 Import Boulevard, Jersey City, NJ 07302, USA',
    notify_party='Premium Auto Imports LLC - Same as consignee',
    
    # PRIORITY 3: HS Tariff & Customs
    hs_tariff_code='8703.80.00.00',  # Electric vehicles
    customs_value_declared=Decimal('45000.00'),
    customs_value_currency='USD',
    duty_paid=False,
    customs_broker_name='American Customs Brokers Inc',
    customs_broker_license='US-CB-12345',
    
    # PRIORITY 3: Hazmat (Tesla = Lithium Battery)
    contains_hazmat=True,
    un_number='UN3171',
    imdg_class='Class 9',
    hazmat_emergency_contact='+1-650-681-5555 (Tesla Emergency Response)',
    msds_attached=True,
    
    # PRIORITY 2: ISPS Port Security
    isps_facility_security_level='level_1',
    origin_port_isps_certified=True,
    destination_port_isps_certified=True,
    port_facility_security_officer='Yokohama Port Authority',
    ship_security_alert_system=True,
    
    # Lloyd's Register & ISO 28000
    lloyd_register_tracking_id='LR-2024-001234',
    lloyd_register_service_level='premium',
    lloyd_register_status='certificate_issued',
    security_risk_level='low',
    ctpat_compliant=True,
    iso_18602_compliant=True,
)

print(f"✅ Created: {shipment1.tracking_number}")
print(f"   • VGM: {shipment1.vgm_weight_kg}kg via {shipment1.get_vgm_method_display()}")
print(f"   • AMS Status: {shipment1.get_ams_status_display()} ({shipment1.ams_filing_number})")
print(f"   • Hazmat: {shipment1.un_number} - {shipment1.imdg_class}")
print(f"   • B/L: {shipment1.bill_of_lading_number} ({shipment1.get_incoterm_display()})")
print(f"   • Vessel: {shipment1.vessel_name} (IMO {shipment1.imo_vessel_number})\n")


# ===== SCENARIO 2: Canada Import (Honda Accord) =====
print("📦 SCENARIO 2: Canada Import - Honda Accord with ACI clearance")

vehicle2 = Vehicle.objects.create(
    vin='1HGCM82633A123456',
    make='Honda',
    model='Accord',
    year=2023,
    color='Lunar Silver Metallic',
    mileage=8500,
    condition='used',
    price=Decimal('28000.00'),
    currency='CAD'
)

deal2 = Deal.objects.create(
    vehicle=vehicle2,
    seller=demo_user,
    buyer=demo_user,
    target_port='Vancouver',
    target_country='Canada',
    status='confirmed',
    agreed_price=Decimal('28000.00')
)

shipment2 = Shipment.objects.create(
    deal=deal2,
    tracking_number='CA-HONDA-2024-001',
    shipping_company='K-Line',
    origin_port='Los Angeles, USA',
    destination_port='Port of Vancouver, Canada',
    destination_country='Canada',
    status='customs',
    estimated_arrival=timezone.now() + timedelta(days=3),
    
    # Container & Vessel
    container_number='KMTU9876543',
    container_type='40ST',
    vessel_name='K-Line Pacific',
    voyage_number='VP042',
    imo_vessel_number='9167645',
    
    # PRIORITY 1: SOLAS VGM
    vgm_weight_kg=Decimal('24800.00'),
    vgm_method='method_2',
    vgm_certified_by='K-Line America',
    vgm_certification_date=timezone.now() - timedelta(days=10),
    vgm_certificate_number='VGM-US-2024-005678',
    
    # PRIORITY 1: ACI - Canada Customs (CRITICAL)
    aci_submission_date=timezone.now() - timedelta(days=11),  # 24+ hours before arrival
    cargo_control_document_number='CCD20240520001234',
    pars_number='5678',
    paps_number='',  # Marine shipment uses PARS, not PAPS
    release_notification_number='RN-2024-001234',
    aci_status='cleared',
    
    # PRIORITY 3: Bill of Lading
    bill_of_lading_number='KLINE-BOL-2024-VAN-5678',
    bill_of_lading_type='house',
    bill_of_lading_date=timezone.now() - timedelta(days=10),
    freight_terms='collect',
    incoterm='CIF',
    consignee_name='Vancouver Auto Group Ltd',
    consignee_address='456 Marine Drive, Vancouver, BC V6B 2P3, Canada',
    
    # PRIORITY 3: HS Tariff
    hs_tariff_code='8703.23.00.00',  # Gasoline vehicles 1500-3000cc
    customs_value_declared=Decimal('28000.00'),
    customs_value_currency='CAD',
    duty_paid=True,
    customs_broker_name='Canada Customs Clearance Inc',
    customs_broker_license='CA-CB-98765',
    
    # No Hazmat (gasoline vehicle)
    contains_hazmat=False,
    
    # Lloyd's Register
    lloyd_register_tracking_id='LR-2024-005678',
    lloyd_register_service_level='standard',
    security_risk_level='low',
)

print(f"✅ Created: {shipment2.tracking_number}")
print(f"   • VGM: {shipment2.vgm_weight_kg}kg via {shipment2.get_vgm_method_display()}")
print(f"   • ACI Status: {shipment2.get_aci_status_display()} (PARS: {shipment2.pars_number})")
print(f"   • CCD: {shipment2.cargo_control_document_number}")
print(f"   • B/L: {shipment2.bill_of_lading_number} ({shipment2.get_freight_terms_display()})\n")


# ===== SCENARIO 3: EU Import (BMW 5 Series) =====
print("📦 SCENARIO 3: EU Import - BMW 5 Series with ENS clearance")

vehicle3 = Vehicle.objects.create(
    vin='WBAJB0C55JB123456',
    make='BMW',
    model='530i',
    year=2024,
    color='Alpine White',
    mileage=50,
    condition='new',
    price=Decimal('62000.00'),
    currency='EUR'
)

deal3 = Deal.objects.create(
    vehicle=vehicle3,
    seller=demo_user,
    buyer=demo_user,
    target_port='Hamburg',
    target_country='Germany',
    status='confirmed',
    agreed_price=Decimal('62000.00')
)

shipment3 = Shipment.objects.create(
    deal=deal3,
    tracking_number='EU-BMW-2024-001',
    shipping_company='MSC Mediterranean Shipping',
    origin_port='Charleston, USA',
    destination_port='Port of Hamburg, Germany',
    destination_country='Germany',
    status='in_transit',
    estimated_arrival=timezone.now() + timedelta(days=18),
    
    # Container & Vessel
    container_number='MSCU5555555',
    container_type='40HC',
    vessel_name='MSC Gülsün',
    voyage_number='GM124E',
    imo_vessel_number='9839479',
    
    # PRIORITY 1: SOLAS VGM
    vgm_weight_kg=Decimal('26300.00'),
    vgm_method='method_1',
    vgm_certified_by='MSC USA Charleston',
    vgm_certification_date=timezone.now() - timedelta(days=3),
    vgm_certificate_number='VGM-US-2024-009876',
    
    # PRIORITY 2: ENS - EU Entry Summary (CRITICAL for EU)
    ens_mrn_number='24DE12345678901234',  # 18 chars: Year + Country + 14 digits
    ens_lrn_number='LRN-DE-2024-001234',
    ens_filing_date=timezone.now() - timedelta(days=4),
    ens_status='cleared',
    
    # PRIORITY 2: AES - US Export
    aes_itn_number='X20240525987654321',
    aes_filing_date=timezone.now() - timedelta(days=5),
    schedule_b_code='8703230000',  # Gasoline vehicles
    export_license_required=False,
    
    # PRIORITY 3: Bill of Lading
    bill_of_lading_number='MSC-BOL-2024-HAM-9876',
    bill_of_lading_type='master',
    bill_of_lading_date=timezone.now() - timedelta(days=3),
    freight_terms='prepaid',
    incoterm='DDP',  # Delivered Duty Paid - seller pays all costs
    consignee_name='Hamburg Premium Autos GmbH',
    consignee_address='Hafenstraße 100, 20359 Hamburg, Germany',
    
    # PRIORITY 3: HS Tariff
    hs_tariff_code='8703.23.19.00',  # Gasoline vehicles >1500cc
    customs_value_declared=Decimal('62000.00'),
    customs_value_currency='EUR',
    duty_paid=True,
    customs_broker_name='Hamburg Customs Services GmbH',
    customs_broker_license='DE-CB-54321',
    
    # No Hazmat (gasoline vehicle)
    contains_hazmat=False,
    
    # PRIORITY 2: ISPS Port Security
    isps_facility_security_level='level_1',
    origin_port_isps_certified=True,
    destination_port_isps_certified=True,
    
    # Lloyd's Register
    lloyd_register_tracking_id='LR-2024-009876',
    lloyd_register_service_level='premium',
    security_risk_level='low',
)

print(f"✅ Created: {shipment3.tracking_number}")
print(f"   • VGM: {shipment3.vgm_weight_kg}kg")
print(f"   • ENS Status: {shipment3.get_ens_status_display()} (MRN: {shipment3.ens_mrn_number})")
print(f"   • AES ITN: {shipment3.aes_itn_number}")
print(f"   • B/L: {shipment3.bill_of_lading_number} (Incoterm: {shipment3.get_incoterm_display()})\n")


# ===== SCENARIO 4: High-Value Lexus with Enhanced Security =====
print("📦 SCENARIO 4: High-Value Export - Lexus LX600 with enhanced security")

vehicle4 = Vehicle.objects.create(
    vin='JTJBM7FX2N5123456',
    make='Lexus',
    model='LX 600',
    year=2024,
    color='Obsidian Black',
    mileage=10,
    condition='new',
    price=Decimal('118000.00'),
    currency='USD'
)

deal4 = Deal.objects.create(
    vehicle=vehicle4,
    seller=demo_user,
    buyer=demo_user,
    target_port='Dubai',
    target_country='UAE',
    status='confirmed',
    agreed_price=Decimal('118000.00')
)

shipment4 = Shipment.objects.create(
    deal=deal4,
    tracking_number='UAE-LEXUS-2024-001',
    shipping_company='Hapag-Lloyd',
    origin_port='Baltimore, USA',
    destination_port='Jebel Ali, Dubai, UAE',
    destination_country='UAE',
    status='pending',
    estimated_departure=timezone.now() + timedelta(days=5),
    estimated_arrival=timezone.now() + timedelta(days=25),
    
    # Container & Vessel
    container_number='HLCU7777777',
    container_type='40HC',
    seal_type='electronic',
    vessel_name='Hapag-Lloyd Express',
    voyage_number='ME042',
    imo_vessel_number='9629226',
    
    # PRIORITY 1: SOLAS VGM
    vgm_weight_kg=Decimal('29800.00'),
    vgm_method='method_1',
    vgm_certified_by='Hapag-Lloyd Baltimore',
    vgm_certification_date=timezone.now(),
    vgm_certificate_number='VGM-US-2024-011234',
    
    # PRIORITY 2: AES - US Export (high value)
    aes_itn_number='X20240530555555555',
    aes_filing_date=timezone.now() - timedelta(days=1),
    schedule_b_code='8703241000',  # SUVs >3000cc
    export_license_required=False,
    
    # PRIORITY 3: Bill of Lading
    bill_of_lading_number='HLCU-BOL-2024-DXB-1234',
    bill_of_lading_type='master',
    bill_of_lading_date=timezone.now(),
    freight_terms='prepaid',
    incoterm='FOB',
    consignee_name='Dubai Luxury Motors LLC',
    consignee_address='P.O. Box 12345, Jebel Ali Free Zone, Dubai, UAE',
    
    # PRIORITY 3: HS Tariff (high customs value)
    hs_tariff_code='8703.24.10.00',  # SUVs >3000cc
    customs_value_declared=Decimal('118000.00'),
    customs_value_currency='USD',
    duty_paid=False,
    customs_broker_name='UAE Elite Customs Services',
    
    # No Hazmat
    contains_hazmat=False,
    
    # PRIORITY 2: ISPS Port Security (Enhanced due to high value)
    isps_facility_security_level='level_1',
    origin_port_isps_certified=True,
    destination_port_isps_certified=True,
    port_facility_security_officer='Baltimore Port Authority Security',
    ship_security_alert_system=True,
    
    # Lloyd's Register Premium + Insurance
    lloyd_register_tracking_id='LR-2024-011234',
    lloyd_register_service_level='surveyor',  # Enhanced for high value
    security_risk_level='medium',
    ctpat_compliant=True,
    insurance_company='Lloyd\'s of London',
    insurance_policy_number='LL-MARINE-2024-1234',
    insurance_coverage_amount=Decimal('150000.00'),
)

print(f"✅ Created: {shipment4.tracking_number}")
print(f"   • VGM: {shipment4.vgm_weight_kg}kg")
print(f"   • High Value: ${shipment4.customs_value_declared} USD")
print(f"   • Lloyd's Service: {shipment4.get_lloyd_register_service_level_display()}")
print(f"   • Insurance: {shipment4.insurance_company} (${shipment4.insurance_coverage_amount})")
print(f"   • ISPS Level: {shipment4.get_isps_facility_security_level_display()}\n")


# ===== SCENARIO 5: Domestic/Minimal Certifications =====
print("📦 SCENARIO 5: Regional Transport - Minimal certifications (non-international)")

vehicle5 = Vehicle.objects.create(
    vin='2HGCM82633A987654',
    make='Toyota',
    model='Corolla',
    year=2022,
    color='Silver',
    mileage=15000,
    condition='used',
    price=Decimal('18500.00'),
    currency='USD'
)

deal5 = Deal.objects.create(
    vehicle=vehicle5,
    seller=demo_user,
    buyer=demo_user,
    target_port='Miami',
    target_country='USA',
    status='confirmed',
    agreed_price=Decimal('18500.00')
)

shipment5 = Shipment.objects.create(
    deal=deal5,
    tracking_number='US-DOMESTIC-2024-001',
    shipping_company='Regional Auto Transport',
    origin_port='Atlanta, USA',
    destination_port='Miami, USA',
    destination_country='USA',
    status='in_transit',
    estimated_arrival=timezone.now() + timedelta(days=2),
    notes='Domestic US transport - minimal international certifications required',
    
    # No container (truck transport)
    container_number='',
    
    # No VGM (not container shipment)
    vgm_weight_kg=None,
    
    # No AMS (domestic)
    ams_filing_number='',
    
    # Minimal documentation
    bill_of_lading_number='RAT-2024-1234',
    bill_of_lading_type='house',
    freight_terms='collect',
    consignee_name='Miami Auto Sales',
    consignee_address='789 Biscayne Blvd, Miami, FL 33132',
    
    # No hazmat
    contains_hazmat=False,
    
    # Basic security
    security_risk_level='low',
)

print(f"✅ Created: {shipment5.tracking_number}")
print(f"   • Domestic transport (no international certifications required)")
print(f"   • B/L: {shipment5.bill_of_lading_number}\n")


print("=" * 70)
print("✅ SEED DATA COMPLETE!")
print("=" * 70)
print("\n📊 SUMMARY:")
print(f"   • Created 5 vehicles")
print(f"   • Created 5 deals")
print(f"   • Created 5 shipments with varying certification levels:")
print(f"     1. USA Export (Tesla) - Full compliance + Hazmat")
print(f"     2. Canada Import (Honda) - ACI + PARS clearance")
print(f"     3. EU Import (BMW) - ENS + MRN compliance")
print(f"     4. UAE Export (Lexus) - High-value enhanced security")
print(f"     5. USA Domestic (Toyota) - Minimal certifications")
print("\n🔍 View shipments:")
print("   • Django Admin: http://localhost:8000/admin/shipments/shipment/")
print("   • API Endpoint: http://localhost:8000/api/shipments/")
print("\n✨ All critical certifications now implemented at world-class levels!")
