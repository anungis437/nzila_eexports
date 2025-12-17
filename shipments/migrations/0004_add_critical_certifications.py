# Generated migration for critical maritime certifications
# Priority 1: SOLAS VGM, AMS, ACI
# Priority 2: AES, ENS, ISPS Code
# Priority 3: HS Tariff, Hazmat, Bill of Lading

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0003_add_marine_cargo_certification'),
    ]

    operations = [
        # ===== PRIORITY 1: SOLAS VGM (Verified Gross Mass) =====
        migrations.AddField(
            model_name='shipment',
            name='vgm_weight_kg',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='SOLAS VGM: Total verified gross mass in kilograms (container + cargo)',
                max_digits=10,
                null=True,
                verbose_name='VGM Weight (kg)'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='vgm_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Certified'),
                    ('method_1', 'Method 1: Weigh Packed Container'),
                    ('method_2', 'Method 2: Calculate Cargo + Tare Weight'),
                ],
                help_text='SOLAS VGM certification method (mandatory for container shipments)',
                max_length=20,
                verbose_name='VGM Method'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='vgm_certified_by',
            field=models.CharField(
                blank=True,
                help_text='Name/company who certified the VGM (authorized weigher)',
                max_length=255,
                verbose_name='VGM Certified By'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='vgm_certification_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Date/time when VGM was certified (must be before vessel loading)',
                null=True,
                verbose_name='VGM Certification Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='vgm_certificate_number',
            field=models.CharField(
                blank=True,
                help_text='VGM certificate or weighbridge ticket number',
                max_length=100,
                verbose_name='VGM Certificate Number'
            ),
        ),
        
        # ===== PRIORITY 1: AMS (US Automated Manifest System) =====
        migrations.AddField(
            model_name='shipment',
            name='ams_filing_number',
            field=models.CharField(
                blank=True,
                help_text='US Customs AMS filing number (24-hour advance manifest rule)',
                max_length=100,
                verbose_name='AMS Filing Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ams_submission_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Date/time AMS manifest submitted to US CBP (must be 24hrs before departure)',
                null=True,
                verbose_name='AMS Submission Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ams_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Required'),
                    ('pending', 'Pending Submission'),
                    ('submitted', 'Submitted to CBP'),
                    ('accepted', 'Accepted by CBP'),
                    ('rejected', 'Rejected - Needs Correction'),
                    ('amended', 'Amended Filing'),
                ],
                help_text='US CBP AMS filing status',
                max_length=20,
                verbose_name='AMS Status'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ams_arrival_notice_date',
            field=models.DateField(
                blank=True,
                help_text='CBP arrival notice date (permission to discharge cargo)',
                null=True,
                verbose_name='AMS Arrival Notice Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ams_scac_code',
            field=models.CharField(
                blank=True,
                help_text='Standard Carrier Alpha Code (4 letters, e.g., MAEU for Maersk)',
                max_length=4,
                verbose_name='SCAC Code'
            ),
        ),
        
        # ===== PRIORITY 1: ACI (Canada Advance Commercial Information) =====
        migrations.AddField(
            model_name='shipment',
            name='aci_submission_date',
            field=models.DateTimeField(
                blank=True,
                help_text='CBSA ACI submission date (must be 24hrs before marine arrival)',
                null=True,
                verbose_name='ACI Submission Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='cargo_control_document_number',
            field=models.CharField(
                blank=True,
                help_text='CBSA Cargo Control Document (CCD) number',
                max_length=50,
                verbose_name='CCD Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='pars_number',
            field=models.CharField(
                blank=True,
                help_text='Pre-Arrival Review System (PARS) number for customs clearance',
                max_length=50,
                verbose_name='PARS Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='paps_number',
            field=models.CharField(
                blank=True,
                help_text='Pre-Arrival Processing System (PAPS) number (for truck/rail)',
                max_length=50,
                verbose_name='PAPS Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='release_notification_number',
            field=models.CharField(
                blank=True,
                help_text='CBSA release notification number (RNS)',
                max_length=50,
                verbose_name='Release Notification Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='aci_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Required'),
                    ('pending', 'Pending Submission'),
                    ('submitted', 'Submitted to CBSA'),
                    ('cleared', 'Customs Cleared'),
                    ('inspection', 'Selected for Inspection'),
                    ('released', 'Released from Customs'),
                ],
                help_text='CBSA ACI processing status',
                max_length=20,
                verbose_name='ACI Status'
            ),
        ),
        
        # ===== PRIORITY 2: AES (US Automated Export System) =====
        migrations.AddField(
            model_name='shipment',
            name='aes_itn_number',
            field=models.CharField(
                blank=True,
                help_text='AES Internal Transaction Number (ITN) for US exports >$2,500',
                max_length=50,
                verbose_name='AES ITN Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='aes_filing_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Date AES export information submitted to US Census Bureau',
                null=True,
                verbose_name='AES Filing Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='aes_exemption_code',
            field=models.CharField(
                blank=True,
                help_text='AES exemption code if ITN not required (e.g., NOEEI 30.37(a))',
                max_length=20,
                verbose_name='AES Exemption Code'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='schedule_b_code',
            field=models.CharField(
                blank=True,
                help_text='Schedule B export classification code (e.g., 8703.23.0040 for passenger vehicles)',
                max_length=10,
                verbose_name='Schedule B Code'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='export_license_required',
            field=models.BooleanField(
                default=False,
                help_text='True if US export license required (rare for vehicles)',
                verbose_name='Export License Required'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='export_license_number',
            field=models.CharField(
                blank=True,
                max_length=50,
                verbose_name='Export License Number'
            ),
        ),
        
        # ===== PRIORITY 2: ENS (EU Entry Summary Declaration) =====
        migrations.AddField(
            model_name='shipment',
            name='ens_mrn_number',
            field=models.CharField(
                blank=True,
                help_text='EU Movement Reference Number (MRN) - 18 digits',
                max_length=18,
                verbose_name='ENS MRN Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ens_filing_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Date ENS filed with EU Import Control System (ICS)',
                null=True,
                verbose_name='ENS Filing Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ens_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Required'),
                    ('pending', 'Pending Filing'),
                    ('submitted', 'Submitted to ICS'),
                    ('cleared', 'Cleared - No Risk'),
                    ('inspection', 'Selected for Inspection'),
                    ('released', 'Released from Customs'),
                ],
                help_text='EU ICS Entry Summary Declaration status',
                max_length=20,
                verbose_name='ENS Status'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ens_lrn_number',
            field=models.CharField(
                blank=True,
                help_text='Local Reference Number (LRN) assigned by declarant',
                max_length=50,
                verbose_name='ENS LRN Number'
            ),
        ),
        
        # ===== PRIORITY 2: ISPS Code (Port Facility Security) =====
        migrations.AddField(
            model_name='shipment',
            name='isps_facility_security_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Assessed'),
                    ('level_1', 'Level 1 - Normal Security'),
                    ('level_2', 'Level 2 - Heightened Risk'),
                    ('level_3', 'Level 3 - Exceptional Risk'),
                ],
                help_text='ISPS Code security level at origin/destination ports',
                max_length=10,
                verbose_name='ISPS Security Level'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='origin_port_isps_certified',
            field=models.BooleanField(
                default=False,
                help_text='True if origin port holds ISPS Code certification',
                verbose_name='Origin Port ISPS Certified'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='destination_port_isps_certified',
            field=models.BooleanField(
                default=False,
                help_text='True if destination port holds ISPS Code certification',
                verbose_name='Destination Port ISPS Certified'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='port_facility_security_officer',
            field=models.CharField(
                blank=True,
                help_text='Name of PFSO (Port Facility Security Officer) at primary port',
                max_length=255,
                verbose_name='Port Facility Security Officer'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='ship_security_alert_system',
            field=models.BooleanField(
                default=False,
                help_text='True if vessel equipped with SSAS (Ship Security Alert System)',
                verbose_name='SSAS Equipped'
            ),
        ),
        
        # ===== PRIORITY 3: HS Tariff & Classification =====
        migrations.AddField(
            model_name='shipment',
            name='hs_tariff_code',
            field=models.CharField(
                blank=True,
                help_text='Harmonized System tariff code (6-10 digits, e.g., 8703.23 for passenger vehicles)',
                max_length=12,
                verbose_name='HS Tariff Code'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='customs_value_declared',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Declared customs value for duty calculation (in destination currency)',
                max_digits=12,
                null=True,
                verbose_name='Customs Value Declared'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='customs_value_currency',
            field=models.CharField(
                blank=True,
                help_text='ISO 4217 currency code (e.g., USD, EUR, NGN)',
                max_length=3,
                verbose_name='Customs Currency'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='duty_paid',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Import duty amount paid at destination customs',
                max_digits=12,
                null=True,
                verbose_name='Duty Paid'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='customs_broker_name',
            field=models.CharField(
                blank=True,
                help_text='Licensed customs broker handling clearance at destination',
                max_length=255,
                verbose_name='Customs Broker'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='customs_broker_license',
            field=models.CharField(
                blank=True,
                help_text='Customs broker license number',
                max_length=100,
                verbose_name='Broker License Number'
            ),
        ),
        
        # ===== PRIORITY 3: Hazmat & Dangerous Goods =====
        migrations.AddField(
            model_name='shipment',
            name='contains_hazmat',
            field=models.BooleanField(
                default=False,
                help_text='True if shipment contains hazardous materials (batteries, fluids, etc)',
                verbose_name='Contains Hazmat'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='un_number',
            field=models.CharField(
                blank=True,
                help_text='UN Number for hazardous materials (e.g., UN3171 for battery-powered vehicles)',
                max_length=10,
                verbose_name='UN Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='imdg_class',
            field=models.CharField(
                blank=True,
                help_text='IMDG Code hazard class (e.g., Class 9 for lithium batteries in EVs)',
                max_length=10,
                verbose_name='IMDG Class'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='hazmat_emergency_contact',
            field=models.CharField(
                blank=True,
                help_text='24/7 emergency contact for hazmat incidents (CHEMTREC, CANUTEC, etc)',
                max_length=255,
                verbose_name='Hazmat Emergency Contact'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='msds_attached',
            field=models.BooleanField(
                default=False,
                help_text='True if Material Safety Data Sheet (MSDS/SDS) is attached',
                verbose_name='MSDS Attached'
            ),
        ),
        
        # ===== PRIORITY 3: Bill of Lading Validation =====
        migrations.AddField(
            model_name='shipment',
            name='bill_of_lading_number',
            field=models.CharField(
                blank=True,
                help_text='Master Bill of Lading (MBL) or House Bill of Lading (HBL) number',
                max_length=100,
                verbose_name='Bill of Lading Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='bill_of_lading_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Issued'),
                    ('master', 'Master B/L (MBL)'),
                    ('house', 'House B/L (HBL)'),
                    ('seaway', 'Sea Waybill'),
                    ('telex', 'Telex Release'),
                ],
                max_length=20,
                verbose_name='B/L Type'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='bill_of_lading_date',
            field=models.DateField(
                blank=True,
                help_text='Date Bill of Lading issued by carrier',
                null=True,
                verbose_name='B/L Issue Date'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='freight_terms',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Specified'),
                    ('prepaid', 'Freight Prepaid'),
                    ('collect', 'Freight Collect'),
                    ('third_party', 'Third Party Billing'),
                ],
                help_text='Freight payment terms (affects customs clearance)',
                max_length=20,
                verbose_name='Freight Terms'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='incoterm',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Not Specified'),
                    ('EXW', 'EXW - Ex Works'),
                    ('FCA', 'FCA - Free Carrier'),
                    ('FOB', 'FOB - Free On Board'),
                    ('CFR', 'CFR - Cost and Freight'),
                    ('CIF', 'CIF - Cost, Insurance, Freight'),
                    ('DAP', 'DAP - Delivered at Place'),
                    ('DDP', 'DDP - Delivered Duty Paid'),
                ],
                help_text='Incoterms 2020 delivery terms',
                max_length=10,
                verbose_name='Incoterm'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='shipper_reference',
            field=models.CharField(
                blank=True,
                help_text='Shipper reference number for internal tracking',
                max_length=100,
                verbose_name='Shipper Reference'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='consignee_name',
            field=models.CharField(
                blank=True,
                help_text='Legal name of consignee (must match import documentation)',
                max_length=255,
                verbose_name='Consignee Name'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='consignee_address',
            field=models.TextField(
                blank=True,
                help_text='Complete consignee address for customs clearance',
                verbose_name='Consignee Address'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='notify_party',
            field=models.CharField(
                blank=True,
                help_text='Notify party on B/L (typically customs broker or importer)',
                max_length=255,
                verbose_name='Notify Party'
            ),
        ),
        
        # ===== Vessel/Voyage Information =====
        migrations.AddField(
            model_name='shipment',
            name='vessel_name',
            field=models.CharField(
                blank=True,
                help_text='Name of vessel carrying cargo',
                max_length=255,
                verbose_name='Vessel Name'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='voyage_number',
            field=models.CharField(
                blank=True,
                help_text='Voyage number assigned by carrier',
                max_length=50,
                verbose_name='Voyage Number'
            ),
        ),
        migrations.AddField(
            model_name='shipment',
            name='imo_vessel_number',
            field=models.CharField(
                blank=True,
                help_text='IMO vessel identification number (7 digits)',
                max_length=10,
                verbose_name='IMO Vessel Number'
            ),
        ),
    ]
