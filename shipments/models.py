from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


# Import tracking models
from .tracking_models import ShipmentMilestone, ShipmentPhoto


class Shipment(models.Model):
    """Shipment model for tracking vehicle deliveries"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_transit', _('In Transit')),
        ('customs', _('At Customs')),
        ('delivered', _('Delivered')),
        ('delayed', _('Delayed')),
    ]
    
    deal = models.OneToOneField(
        'deals.Deal',
        on_delete=models.CASCADE,
        related_name='shipment',
        verbose_name=_('Deal')
    )
    
    # Shipment Details
    tracking_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Tracking Number')
    )
    shipping_company = models.CharField(
        max_length=255,
        verbose_name=_('Shipping Company')
    )
    
    # Locations
    origin_port = models.CharField(
        max_length=255,
        verbose_name=_('Origin Port')
    )
    destination_port = models.CharField(
        max_length=255,
        verbose_name=_('Destination Port')
    )
    destination_country = models.CharField(
        max_length=100,
        verbose_name=_('Destination Country')
    )
    
    # Status & Dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    estimated_departure = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Departure')
    )
    actual_departure = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Actual Departure')
    )
    estimated_arrival = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Estimated Arrival')
    )
    actual_arrival = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Actual Arrival')
    )
    
    # Additional Info
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    # GPS Tracking
    current_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name=_('Current Latitude')
    )
    current_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name=_('Current Longitude')
    )
    last_location_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Location Update')
    )
    
    # ===== MARINE CARGO CERTIFICATION FIELDS (ISO 6346 / ISO 18602) =====
    
    # Container Tracking (ISO 6346 Standard)
    container_number = models.CharField(
        max_length=11,
        blank=True,
        help_text=_('ISO 6346 container number: 4 letters (owner code) + 7 digits'),
        verbose_name=_('Container Number')
    )
    
    container_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('20ft_standard', _('20ft Standard Container')),
            ('40ft_standard', _('40ft Standard Container')),
            ('40ft_high_cube', _('40ft High Cube Container')),
            ('roro', _('RoRo (Roll-on/Roll-off)')),
            ('flatbed', _('Flatbed')),
            ('specialized', _('Specialized Vehicle Carrier')),
        ],
        verbose_name=_('Container/Transport Type')
    )
    
    # Container Seal Tracking (Tamper Evidence)
    seal_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('High-security bolt seal or electronic seal number'),
        verbose_name=_('Seal Number')
    )
    
    seal_type = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('bolt', _('High-Security Bolt Seal')),
            ('cable', _('Cable Seal')),
            ('electronic', _('Electronic Seal (e-seal)')),
            ('barrier', _('Barrier Seal')),
        ],
        verbose_name=_('Seal Type')
    )
    
    seal_applied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Seal Applied At')
    )
    
    seal_applied_by = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of person/organization who applied seal'),
        verbose_name=_('Seal Applied By')
    )
    
    seal_verified_at_origin = models.BooleanField(
        default=False,
        help_text=_('Verified intact at Canadian port before departure'),
        verbose_name=_('Seal Verified at Origin')
    )
    
    seal_origin_verifier = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Origin Verifier Name')
    )
    
    seal_origin_verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Origin Verification Date')
    )
    
    seal_verified_at_destination = models.BooleanField(
        default=False,
        help_text=_('Verified intact at destination port upon arrival'),
        verbose_name=_('Seal Verified at Destination')
    )
    
    seal_destination_verifier = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Destination Verifier Name')
    )
    
    seal_destination_verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Destination Verification Date')
    )
    
    seal_intact = models.BooleanField(
        default=True,
        help_text=_('False if seal was tampered with or broken'),
        verbose_name=_('Seal Intact')
    )
    
    seal_notes = models.TextField(
        blank=True,
        help_text=_('Any issues or observations about container seal'),
        verbose_name=_('Seal Notes')
    )
    
    # ===== LLOYD'S REGISTER CERTIFICATION =====
    
    lloyd_register_tracking_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        help_text=_('Lloyd\'s Register Cargo Tracking Service reference number'),
        verbose_name=_('LR Tracking ID')
    )
    
    lloyd_register_service_level = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('none', _('No LR Service')),
            ('standard', _('Standard Monitoring')),
            ('premium', _('Premium 24/7 Monitoring')),
            ('surveyor', _('Full Surveyor Service')),
        ],
        default='none',
        verbose_name=_('LR Service Level')
    )
    
    lloyd_register_certificate_issued = models.BooleanField(
        default=False,
        help_text=_('True if LR Certificate of Safe Delivery was issued'),
        verbose_name=_('LR Certificate Issued')
    )
    
    lloyd_register_certificate_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('LR Certificate Number')
    )
    
    lloyd_register_certificate_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('LR Certificate Date')
    )
    
    lloyd_register_surveyor_origin = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of LR surveyor who inspected at origin'),
        verbose_name=_('LR Origin Surveyor')
    )
    
    lloyd_register_surveyor_destination = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of LR surveyor who inspected at destination'),
        verbose_name=_('LR Destination Surveyor')
    )
    
    lloyd_register_status = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('not_registered', _('Not Registered')),
            ('pending_origin', _('Pending Origin Inspection')),
            ('origin_approved', _('Origin Inspection Approved')),
            ('in_monitoring', _('Active Monitoring')),
            ('arrived', _('Arrived - Pending Destination Inspection')),
            ('destination_approved', _('Destination Inspection Approved')),
            ('certificate_issued', _('Certificate Issued')),
            ('discrepancy', _('Discrepancy Reported')),
        ],
        default='not_registered',
        verbose_name=_('LR Status')
    )
    
    lloyd_register_notes = models.TextField(
        blank=True,
        verbose_name=_('LR Notes')
    )
    
    # ===== ISO 28000 SECURITY MANAGEMENT =====
    
    security_risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Low Risk')),
            ('medium', _('Medium Risk')),
            ('high', _('High Risk')),
            ('critical', _('Critical Risk')),
        ],
        default='low',
        help_text=_('Security risk assessment based on route, value, destination'),
        verbose_name=_('Security Risk Level')
    )
    
    security_assessment_completed = models.BooleanField(
        default=False,
        help_text=_('True if pre-shipment security risk assessment was completed'),
        verbose_name=_('Security Assessment Completed')
    )
    
    security_assessment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Security Assessment Date')
    )
    
    security_assessment_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_assessments',
        verbose_name=_('Security Assessment By')
    )
    
    security_measures_implemented = models.TextField(
        blank=True,
        help_text=_('List of security measures implemented (GPS tracker, seal, insurance, etc)'),
        verbose_name=_('Security Measures Implemented')
    )
    
    insurance_company = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Insurance Company')
    )
    
    insurance_policy_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Insurance Policy Number')
    )
    
    insurance_coverage_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Insurance coverage amount in CAD'),
        verbose_name=_('Insurance Coverage (CAD)')
    )
    
    # ISO 28000 requires incident tracking
    has_security_incident = models.BooleanField(
        default=False,
        help_text=_('True if any security incident occurred during shipment'),
        verbose_name=_('Has Security Incident')
    )
    
    security_incident_description = models.TextField(
        blank=True,
        verbose_name=_('Security Incident Description')
    )
    
    security_incident_reported_to_authorities = models.BooleanField(
        default=False,
        verbose_name=_('Incident Reported to Authorities')
    )
    
    # C-TPAT Compliance (US Customs)
    ctpat_compliant = models.BooleanField(
        default=False,
        help_text=_('True if shipment meets C-TPAT security requirements'),
        verbose_name=_('C-TPAT Compliant')
    )
    
    # ISO 18602 Compliance Flag
    iso_18602_compliant = models.BooleanField(
        default=False,
        help_text=_('True if tracking data meets ISO 18602 standards'),
        verbose_name=_('ISO 18602 Compliant')
    )
    
    # ISO 28000 Certification Status
    iso_28000_audit_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last ISO 28000 compliance audit for this shipment'),
        verbose_name=_('ISO 28000 Audit Date')
    )
    
    # ===== PRIORITY 1: SOLAS VGM (Verified Gross Mass) - CRITICAL =====
    
    vgm_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('SOLAS VGM: Total verified gross mass in kilograms (container + cargo)'),
        verbose_name=_('VGM Weight (kg)')
    )
    
    vgm_method = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', _('Not Certified')),
            ('method_1', _('Method 1: Weigh Packed Container')),
            ('method_2', _('Method 2: Calculate Cargo + Tare Weight')),
        ],
        help_text=_('SOLAS VGM certification method (mandatory for container shipments)'),
        verbose_name=_('VGM Method')
    )
    
    vgm_certified_by = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name/company who certified the VGM (authorized weigher)'),
        verbose_name=_('VGM Certified By')
    )
    
    vgm_certification_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date/time when VGM was certified (must be before vessel loading)'),
        verbose_name=_('VGM Certification Date')
    )
    
    vgm_certificate_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('VGM certificate or weighbridge ticket number'),
        verbose_name=_('VGM Certificate Number')
    )
    
    # ===== PRIORITY 1: AMS (US Automated Manifest System) - CRITICAL =====
    
    ams_filing_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('US Customs AMS filing number (24-hour advance manifest rule)'),
        verbose_name=_('AMS Filing Number')
    )
    
    ams_submission_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date/time AMS manifest submitted to US CBP (must be 24hrs before departure)'),
        verbose_name=_('AMS Submission Date')
    )
    
    ams_status = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', _('Not Required')),
            ('pending', _('Pending Submission')),
            ('submitted', _('Submitted to CBP')),
            ('accepted', _('Accepted by CBP')),
            ('rejected', _('Rejected - Needs Correction')),
            ('amended', _('Amended Filing')),
        ],
        help_text=_('US CBP AMS filing status'),
        verbose_name=_('AMS Status')
    )
    
    ams_arrival_notice_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('CBP arrival notice date (permission to discharge cargo)'),
        verbose_name=_('AMS Arrival Notice Date')
    )
    
    ams_scac_code = models.CharField(
        max_length=4,
        blank=True,
        help_text=_('Standard Carrier Alpha Code (4 letters, e.g., MAEU for Maersk)'),
        verbose_name=_('SCAC Code')
    )
    
    # ===== PRIORITY 1: ACI (Canada Advance Commercial Information) - CRITICAL =====
    
    aci_submission_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('CBSA ACI submission date (must be 24hrs before marine arrival)'),
        verbose_name=_('ACI Submission Date')
    )
    
    cargo_control_document_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('CBSA Cargo Control Document (CCD) number'),
        verbose_name=_('CCD Number')
    )
    
    pars_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Pre-Arrival Review System (PARS) number for customs clearance'),
        verbose_name=_('PARS Number')
    )
    
    paps_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Pre-Arrival Processing System (PAPS) number (for truck/rail)'),
        verbose_name=_('PAPS Number')
    )
    
    release_notification_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('CBSA release notification number (RNS)'),
        verbose_name=_('Release Notification Number')
    )
    
    aci_status = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', _('Not Required')),
            ('pending', _('Pending Submission')),
            ('submitted', _('Submitted to CBSA')),
            ('cleared', _('Customs Cleared')),
            ('inspection', _('Selected for Inspection')),
            ('released', _('Released from Customs')),
        ],
        help_text=_('CBSA ACI processing status'),
        verbose_name=_('ACI Status')
    )
    
    # ===== PRIORITY 2: AES (US Automated Export System) - HIGH =====
    
    aes_itn_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('AES Internal Transaction Number (ITN) for US exports >$2,500'),
        verbose_name=_('AES ITN Number')
    )
    
    aes_filing_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date AES export information submitted to US Census Bureau'),
        verbose_name=_('AES Filing Date')
    )
    
    aes_exemption_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('AES exemption code if ITN not required (e.g., NOEEI 30.37(a))'),
        verbose_name=_('AES Exemption Code')
    )
    
    schedule_b_code = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('Schedule B export classification code (e.g., 8703.23.0040 for passenger vehicles)'),
        verbose_name=_('Schedule B Code')
    )
    
    export_license_required = models.BooleanField(
        default=False,
        help_text=_('True if US export license required (rare for vehicles)'),
        verbose_name=_('Export License Required')
    )
    
    export_license_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Export License Number')
    )
    
    # ===== PRIORITY 2: ENS (EU Entry Summary Declaration) - HIGH =====
    
    ens_mrn_number = models.CharField(
        max_length=18,
        blank=True,
        help_text=_('EU Movement Reference Number (MRN) - 18 digits'),
        verbose_name=_('ENS MRN Number')
    )
    
    ens_filing_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date ENS filed with EU Import Control System (ICS)'),
        verbose_name=_('ENS Filing Date')
    )
    
    ens_status = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', _('Not Required')),
            ('pending', _('Pending Filing')),
            ('submitted', _('Submitted to ICS')),
            ('cleared', _('Cleared - No Risk')),
            ('inspection', _('Selected for Inspection')),
            ('released', _('Released from Customs')),
        ],
        help_text=_('EU ICS Entry Summary Declaration status'),
        verbose_name=_('ENS Status')
    )
    
    ens_lrn_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Local Reference Number (LRN) assigned by declarant'),
        verbose_name=_('ENS LRN Number')
    )
    
    # ===== PRIORITY 2: ISPS Code (Port Facility Security) - HIGH =====
    
    isps_facility_security_level = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ('', _('Not Assessed')),
            ('level_1', _('Level 1 - Normal Security')),
            ('level_2', _('Level 2 - Heightened Risk')),
            ('level_3', _('Level 3 - Exceptional Risk')),
        ],
        help_text=_('ISPS Code security level at origin/destination ports'),
        verbose_name=_('ISPS Security Level')
    )
    
    origin_port_isps_certified = models.BooleanField(
        default=False,
        help_text=_('True if origin port holds ISPS Code certification'),
        verbose_name=_('Origin Port ISPS Certified')
    )
    
    destination_port_isps_certified = models.BooleanField(
        default=False,
        help_text=_('True if destination port holds ISPS Code certification'),
        verbose_name=_('Destination Port ISPS Certified')
    )
    
    port_facility_security_officer = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of PFSO (Port Facility Security Officer) at primary port'),
        verbose_name=_('Port Facility Security Officer')
    )
    
    ship_security_alert_system = models.BooleanField(
        default=False,
        help_text=_('True if vessel equipped with SSAS (Ship Security Alert System)'),
        verbose_name=_('SSAS Equipped')
    )
    
    # ===== PRIORITY 3: HS Tariff & Classification - MEDIUM =====
    
    hs_tariff_code = models.CharField(
        max_length=12,
        blank=True,
        help_text=_('Harmonized System tariff code (6-10 digits, e.g., 8703.23 for passenger vehicles)'),
        verbose_name=_('HS Tariff Code')
    )
    
    customs_value_declared = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Declared customs value for duty calculation (in destination currency)'),
        verbose_name=_('Customs Value Declared')
    )
    
    customs_value_currency = models.CharField(
        max_length=3,
        blank=True,
        help_text=_('ISO 4217 currency code (e.g., USD, EUR, NGN)'),
        verbose_name=_('Customs Currency')
    )
    
    duty_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Import duty amount paid at destination customs'),
        verbose_name=_('Duty Paid')
    )
    
    customs_broker_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Licensed customs broker handling clearance at destination'),
        verbose_name=_('Customs Broker')
    )
    
    customs_broker_license = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Customs broker license number'),
        verbose_name=_('Broker License Number')
    )
    
    # ===== PRIORITY 3: Hazmat & Dangerous Goods - MEDIUM =====
    
    contains_hazmat = models.BooleanField(
        default=False,
        help_text=_('True if shipment contains hazardous materials (batteries, fluids, etc)'),
        verbose_name=_('Contains Hazmat')
    )
    
    un_number = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('UN Number for hazardous materials (e.g., UN3171 for battery-powered vehicles)'),
        verbose_name=_('UN Number')
    )
    
    imdg_class = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('IMDG Code hazard class (e.g., Class 9 for lithium batteries in EVs)'),
        verbose_name=_('IMDG Class')
    )
    
    hazmat_emergency_contact = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('24/7 emergency contact for hazmat incidents (CHEMTREC, CANUTEC, etc)'),
        verbose_name=_('Hazmat Emergency Contact')
    )
    
    msds_attached = models.BooleanField(
        default=False,
        help_text=_('True if Material Safety Data Sheet (MSDS/SDS) is attached'),
        verbose_name=_('MSDS Attached')
    )
    
    # ===== PRIORITY 3: Bill of Lading Validation - MEDIUM =====
    
    bill_of_lading_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Master Bill of Lading (MBL) or House Bill of Lading (HBL) number'),
        verbose_name=_('Bill of Lading Number')
    )
    
    bill_of_lading_type = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', _('Not Issued')),
            ('master', _('Master B/L (MBL)')),
            ('house', _('House B/L (HBL)')),
            ('seaway', _('Sea Waybill')),
            ('telex', _('Telex Release')),
        ],
        verbose_name=_('B/L Type')
    )
    
    bill_of_lading_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date Bill of Lading issued by carrier'),
        verbose_name=_('B/L Issue Date')
    )
    
    freight_terms = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', _('Not Specified')),
            ('prepaid', _('Freight Prepaid')),
            ('collect', _('Freight Collect')),
            ('third_party', _('Third Party Billing')),
        ],
        help_text=_('Freight payment terms (affects customs clearance)'),
        verbose_name=_('Freight Terms')
    )
    
    incoterm = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ('', _('Not Specified')),
            ('EXW', _('EXW - Ex Works')),
            ('FCA', _('FCA - Free Carrier')),
            ('FOB', _('FOB - Free On Board')),
            ('CFR', _('CFR - Cost and Freight')),
            ('CIF', _('CIF - Cost, Insurance, Freight')),
            ('DAP', _('DAP - Delivered at Place')),
            ('DDP', _('DDP - Delivered Duty Paid')),
        ],
        help_text=_('Incoterms 2020 delivery terms'),
        verbose_name=_('Incoterm')
    )
    
    shipper_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Shipper reference number for internal tracking'),
        verbose_name=_('Shipper Reference')
    )
    
    consignee_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Legal name of consignee (must match import documentation)'),
        verbose_name=_('Consignee Name')
    )
    
    consignee_address = models.TextField(
        blank=True,
        help_text=_('Complete consignee address for customs clearance'),
        verbose_name=_('Consignee Address')
    )
    
    notify_party = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Notify party on B/L (typically customs broker or importer)'),
        verbose_name=_('Notify Party')
    )
    
    # Vessel/Voyage Information
    vessel_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of vessel carrying cargo'),
        verbose_name=_('Vessel Name')
    )
    
    voyage_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Voyage number assigned by carrier'),
        verbose_name=_('Voyage Number')
    )
    
    imo_vessel_number = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('IMO vessel identification number (7 digits)'),
        verbose_name=_('IMO Vessel Number')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Shipment')
        verbose_name_plural = _('Shipments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Shipment {self.tracking_number} - Deal #{self.deal.id}"


class ShipmentUpdate(models.Model):
    """Tracking updates for shipments"""
    
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name=_('Shipment')
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name=_('Location')
    )
    status = models.CharField(
        max_length=255,
        verbose_name=_('Status')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    
    # ISO 18602 Compliance Fields
    iso_message_type = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('IFTSTA', _('Status Report')),
            ('GATELOC', _('Gate Location')),
            ('CUSCAR', _('Customs Cargo Report')),
            ('CONTRL', _('Control Message')),
            ('APERAK', _('Application Error and Acknowledgement')),
        ],
        help_text=_('UN/EDIFACT message type for EDI integration'),
        verbose_name=_('ISO Message Type')
    )
    
    iso_message_xml = models.TextField(
        blank=True,
        help_text=_('ISO 18602 compliant XML message for port systems'),
        verbose_name=_('ISO Message XML')
    )
    
    verified_by = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Port authority, surveyor, or customs official who verified this update'),
        verbose_name=_('Verified By')
    )
    
    verification_method = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('visual', _('Visual Inspection')),
            ('rfid', _('RFID Scan')),
            ('gps', _('GPS Verification')),
            ('document', _('Document Verification')),
            ('surveyor', _('Professional Surveyor')),
            ('customs', _('Customs Authority')),
        ],
        verbose_name=_('Verification Method')
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name=_('Latitude')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name=_('Longitude')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Shipment Update')
        verbose_name_plural = _('Shipment Updates')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.shipment.tracking_number} - {self.created_at}"
