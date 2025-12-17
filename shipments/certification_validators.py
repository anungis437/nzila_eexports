"""
Validation utilities for critical maritime certifications
Ensures compliance with SOLAS, AMS, ACI, AES, ENS, ISPS, and other regulations
"""
from datetime import datetime, timedelta
from decimal import Decimal
import re
from django.core.exceptions import ValidationError


# ===== SOLAS VGM VALIDATION =====

def validate_vgm_weight(weight_kg, container_type):
    """
    Validate VGM weight against container capacity limits
    
    SOLAS Convention requires accurate VGM before vessel loading.
    Container weight limits based on ISO 668 standards.
    
    Args:
        weight_kg: Verified Gross Mass in kilograms
        container_type: Container type code (e.g., '20ST', '40HC')
    
    Raises:
        ValidationError: If weight exceeds container capacity
    """
    if not weight_kg:
        return  # VGM optional for non-container shipments
    
    # Container weight limits (kg) - includes tare weight
    CONTAINER_LIMITS = {
        '20ST': 24000,  # 20ft Standard
        '20HC': 24000,  # 20ft High Cube
        '40ST': 30480,  # 40ft Standard
        '40HC': 30480,  # 40ft High Cube
        '45HC': 30480,  # 45ft High Cube
    }
    
    limit = CONTAINER_LIMITS.get(container_type, 30480)  # Default to 40ft limit
    
    if weight_kg > limit:
        raise ValidationError(
            f"VGM weight {weight_kg}kg exceeds {container_type} container limit of {limit}kg. "
            f"Vessel will refuse loading. Verify cargo weight and container selection."
        )
    
    if weight_kg < 1000:
        raise ValidationError(
            f"VGM weight {weight_kg}kg suspiciously low for container shipment. "
            f"Minimum container tare weight is ~2,200kg for 20ft, ~3,800kg for 40ft. "
            f"Review VGM calculation method (Method 1 or Method 2)."
        )


def validate_vgm_method(method, certified_by):
    """
    Validate VGM certification method per SOLAS requirements
    
    Method 1: Weigh packed container on calibrated scale
    Method 2: Weigh all cargo + packing materials, add container tare weight
    
    Args:
        method: 'method_1' or 'method_2'
        certified_by: Name/company that certified the VGM
    
    Raises:
        ValidationError: If method incomplete or invalid
    """
    if method and not certified_by:
        raise ValidationError(
            "VGM certification requires 'Certified By' field. "
            "Must be shipper or authorized party per SOLAS VI/2."
        )


# ===== AMS (US CUSTOMS) VALIDATION =====

def validate_ams_24hour_rule(submission_date, departure_date):
    """
    Validate AMS 24-hour advance manifest rule (19 CFR 4.7)
    
    US Customs requires AMS filing 24 hours before vessel departure to USA.
    Failure results in 'Do Not Load' message and severe penalties.
    
    Args:
        submission_date: DateTime AMS was submitted to US CBP
        departure_date: DateTime vessel departs origin port
    
    Raises:
        ValidationError: If submitted < 24 hours before departure
    """
    if not submission_date or not departure_date:
        return  # AMS optional for non-US shipments
    
    hours_before = (departure_date - submission_date).total_seconds() / 3600
    
    if hours_before < 24:
        raise ValidationError(
            f"AMS filed only {hours_before:.1f} hours before departure. "
            f"US CBP requires 24+ hours (19 CFR 4.7). "
            f"Vessel may receive 'Do Not Load' message. File AMS immediately."
        )
    
    if hours_before > 720:  # 30 days
        raise ValidationError(
            f"AMS filed {hours_before/24:.0f} days before departure. "
            f"Unusual timing - verify departure date accuracy."
        )


def validate_scac_code(scac):
    """
    Validate Standard Carrier Alpha Code (SCAC)
    
    SCAC is 4-letter code assigned by National Motor Freight Traffic Association.
    Required for AMS filing and US customs clearance.
    
    Args:
        scac: 4-letter carrier code (e.g., 'MAEU' for Maersk)
    
    Raises:
        ValidationError: If format invalid
    """
    if not scac:
        return
    
    if not re.match(r'^[A-Z]{4}$', scac):
        raise ValidationError(
            f"Invalid SCAC code '{scac}'. Must be exactly 4 uppercase letters. "
            f"Examples: MAEU (Maersk), MSCU (MSC), COSU (COSCO)."
        )


# ===== ACI (CANADA CUSTOMS) VALIDATION =====

def validate_aci_24hour_rule(submission_date, arrival_date, transport_mode='marine'):
    """
    Validate ACI pre-arrival notification timing per CBSA requirements
    
    Canada requires advance cargo information:
    - Marine: 24 hours before arrival at first Canadian port
    - Rail: 2 hours before arrival
    - Highway: 1 hour before arrival
    
    Args:
        submission_date: DateTime ACI was submitted to CBSA
        arrival_date: DateTime vessel/truck arrives in Canada
        transport_mode: 'marine', 'rail', or 'highway'
    
    Raises:
        ValidationError: If timing requirements not met
    """
    if not submission_date or not arrival_date:
        return  # ACI optional for non-Canada shipments
    
    hours_before = (arrival_date - submission_date).total_seconds() / 3600
    
    REQUIRED_HOURS = {
        'marine': 24,
        'rail': 2,
        'highway': 1,
    }
    
    required = REQUIRED_HOURS.get(transport_mode, 24)
    
    if hours_before < required:
        raise ValidationError(
            f"ACI filed only {hours_before:.1f} hours before arrival. "
            f"CBSA requires {required}+ hours for {transport_mode} transport. "
            f"Shipment may be refused entry to Canada."
        )


def validate_pars_paps_number(pars, paps):
    """
    Validate PARS/PAPS numbers for Canadian customs
    
    PARS: Pre-Arrival Review System (commercial imports)
    PAPS: Pre-Arrival Processing System (highway shipments)
    
    Args:
        pars: PARS number (typically 4 digits)
        paps: PAPS number (typically 4 digits)
    """
    if pars and not re.match(r'^\d{4,10}$', pars):
        raise ValidationError(
            f"Invalid PARS number '{pars}'. Must be 4-10 digits assigned by CBSA."
        )
    
    if paps and not re.match(r'^\d{4,10}$', paps):
        raise ValidationError(
            f"Invalid PAPS number '{paps}'. Must be 4-10 digits assigned by CBSA."
        )


# ===== AES (US EXPORT) VALIDATION =====

def validate_aes_requirements(customs_value, export_license_required, aes_itn_number, aes_exemption_code):
    """
    Validate AES export filing requirements per 15 CFR 30
    
    US Census Bureau requires AES filing for exports >$2,500 USD.
    Some exports exempt (e.g., Canada <$2,500, personal effects).
    
    Args:
        customs_value: Declared value in USD
        export_license_required: Boolean if export license needed
        aes_itn_number: Internal Transaction Number from AES
        aes_exemption_code: Exemption code if filing not required
    
    Raises:
        ValidationError: If AES requirements not met
    """
    if customs_value and customs_value > 2500:
        if not aes_itn_number and not aes_exemption_code:
            raise ValidationError(
                f"Export value ${customs_value:.2f} requires AES filing (>$2,500 threshold). "
                f"Either obtain AES ITN number or provide exemption code if applicable. "
                f"Common exemptions: NOEEI 30.37(a) for Canada <$2,500."
            )
    
    if export_license_required and not aes_itn_number:
        raise ValidationError(
            "Export license required items MUST have AES ITN number. "
            "File AES through AESDirect or ACE before export departure."
        )


def validate_schedule_b_code(code):
    """
    Validate Schedule B export classification code
    
    Schedule B is 10-digit commodity code for US exports.
    Based on Harmonized System (first 6 digits = HS code).
    
    Args:
        code: 10-digit Schedule B code
    
    Raises:
        ValidationError: If format invalid
    """
    if not code:
        return
    
    if not re.match(r'^\d{10}$', code):
        raise ValidationError(
            f"Invalid Schedule B code '{code}'. Must be exactly 10 digits. "
            f"Search codes at: https://uscensus.prod.3ceonline.com/"
        )


# ===== ENS (EU ENTRY SUMMARY) VALIDATION =====

def validate_mrn_number(mrn):
    """
    Validate EU Movement Reference Number (MRN)
    
    MRN is 18-character alphanumeric issued by EU Import Control System.
    Format: YY[CC]XXXXXXXXXXXX[C] (year + country + 13 digits + check digit)
    
    Args:
        mrn: 18-character MRN from EU ICS
    
    Raises:
        ValidationError: If format invalid
    """
    if not mrn:
        return
    
    if not re.match(r'^[0-9]{2}[A-Z]{2}[A-Z0-9]{14}$', mrn):
        raise ValidationError(
            f"Invalid MRN '{mrn}'. Must be 18 characters: "
            f"YY (year) + CC (country) + 14 alphanumeric. "
            f"Example: 22GB123456789012345"
        )


# ===== HS TARIFF CODE VALIDATION =====

def validate_hs_tariff_code(code):
    """
    Validate Harmonized System tariff code
    
    HS codes classify goods for customs duties internationally.
    Format: 6 digits (international) + up to 6 more (national subheadings)
    
    Args:
        code: HS/HTS tariff code (6-12 digits)
    
    Raises:
        ValidationError: If format invalid
    """
    if not code:
        return
    
    # Allow 6-12 digit codes (periods optional: 8704.21 or 870421)
    clean_code = code.replace('.', '')
    
    if not re.match(r'^\d{6,12}$', clean_code):
        raise ValidationError(
            f"Invalid HS code '{code}'. Must be 6-12 digits. "
            f"Example: 8704.21 (Motor vehicles for goods transport). "
            f"Search codes at: https://www.trade.gov/harmonized-system-hs-codes"
        )


# ===== IMO VESSEL NUMBER VALIDATION =====

def validate_imo_vessel_number(imo):
    """
    Validate IMO ship identification number with check digit
    
    IMO number is 7-digit permanent vessel ID assigned by Lloyd's Register.
    Format: IMO + 7 digits where last digit is check digit.
    
    Args:
        imo: IMO number (can include 'IMO' prefix)
    
    Raises:
        ValidationError: If format or check digit invalid
    """
    if not imo:
        return
    
    # Remove 'IMO' prefix if present
    imo_digits = imo.replace('IMO', '').replace(' ', '').strip()
    
    if not re.match(r'^\d{7}$', imo_digits):
        raise ValidationError(
            f"Invalid IMO number '{imo}'. Must be 7 digits (or 'IMO' + 7 digits). "
            f"Example: IMO 9074729"
        )
    
    # Validate check digit (sum of first 6 digits * position, last digit = modulo 10)
    digits = [int(d) for d in imo_digits]
    check_sum = sum(digits[i] * (7 - i) for i in range(6))
    check_digit = check_sum % 10
    
    if digits[6] != check_digit:
        raise ValidationError(
            f"Invalid IMO number '{imo}'. Check digit {digits[6]} incorrect "
            f"(should be {check_digit}). Verify IMO number accuracy."
        )


# ===== HAZMAT VALIDATION =====

def validate_hazmat_fields(contains_hazmat, un_number, imdg_class, emergency_contact):
    """
    Validate dangerous goods documentation per IMDG Code
    
    International Maritime Dangerous Goods (IMDG) Code requires:
    - UN Number: 4-digit hazard classification
    - IMDG Class: Hazard category (1-9)
    - Emergency Contact: 24/7 phone for incidents
    
    Args:
        contains_hazmat: Boolean if shipment has dangerous goods
        un_number: UN hazard number (e.g., UN3171)
        imdg_class: IMDG hazard class (e.g., 'Class 9')
        emergency_contact: 24/7 emergency phone
    
    Raises:
        ValidationError: If hazmat documentation incomplete
    """
    if contains_hazmat:
        if not un_number:
            raise ValidationError(
                "Hazmat shipments require UN Number. "
                "Electric vehicles: UN3171 (Battery-powered vehicles). "
                "Search UN numbers: https://unece.org/transport/dangerous-goods"
            )
        
        if not imdg_class:
            raise ValidationError(
                "Hazmat shipments require IMDG Class. "
                "Electric vehicles: Class 9 (Miscellaneous dangerous substances). "
                "Classes: 1=Explosives, 2=Gases, 3=Flammable liquids, etc."
            )
        
        if not emergency_contact:
            raise ValidationError(
                "Hazmat shipments require 24/7 emergency contact phone. "
                "Must be reachable during transport for incident response."
            )
    
    # Validate UN number format
    if un_number and not re.match(r'^UN\d{4}$', un_number.upper()):
        raise ValidationError(
            f"Invalid UN number '{un_number}'. Must be format 'UN####'. "
            f"Example: UN3171 for battery-powered vehicles."
        )


# ===== BILL OF LADING VALIDATION =====

def validate_bill_of_lading_completeness(bill_number, consignee_name, consignee_address, incoterm):
    """
    Validate Bill of Lading completeness for customs clearance
    
    Customs authorities require complete B/L documentation including:
    - B/L Number: Unique identifier for shipment
    - Consignee: Party receiving goods (name + address)
    - Incoterms: Terms of delivery and responsibility
    
    Args:
        bill_number: Bill of Lading number
        consignee_name: Name of receiving party
        consignee_address: Full address of consignee
        incoterm: Incoterms 2020 code (EXW, FOB, CIF, etc.)
    
    Raises:
        ValidationError: If B/L documentation incomplete
    """
    if bill_number:  # If B/L started, require complete info
        if not consignee_name:
            raise ValidationError(
                "Bill of Lading requires consignee name for customs clearance."
            )
        
        if not consignee_address:
            raise ValidationError(
                "Bill of Lading requires complete consignee address for delivery."
            )
        
        if not incoterm:
            raise ValidationError(
                "Bill of Lading requires Incoterm (FOB, CIF, DDP, etc.). "
                "Determines who pays duties and when risk transfers. "
                "Most common for vehicle exports: FOB (seller loads, buyer pays shipping)."
            )


# ===== ISPS CODE VALIDATION =====

def validate_isps_security_level(level, origin_certified, destination_certified):
    """
    Validate ISPS Code port facility security requirements
    
    International Ship and Port Facility Security (ISPS) Code requires:
    - Level 1: Normal security measures
    - Level 2: Heightened security (increased threat)
    - Level 3: Exceptional security (probable/imminent attack)
    
    Args:
        level: Security level (1, 2, or 3)
        origin_certified: Boolean if origin port ISPS certified
        destination_certified: Boolean if destination port ISPS certified
    
    Raises:
        ValidationError: If security requirements not met
    """
    if level in ['level_2', 'level_3']:
        if not origin_certified or not destination_certified:
            raise ValidationError(
                f"ISPS Security {level.upper()} requires both origin and destination "
                f"ports to have valid ISPS certification. Non-compliant ports may refuse "
                f"vessel entry. Verify port security status before booking."
            )
