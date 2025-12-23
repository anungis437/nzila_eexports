"""
PHASE 2 - Feature 5: Provincial Title Transfer Guides

Comprehensive guides for transferring vehicle titles across Canadian provinces.
Each province has unique requirements, fees, and processes.

Data sources:
- Provincial government ministry websites
- ServiceOntario, SAAQ (Quebec), ICBC (BC), ServiceAlberta, etc.
"""

from typing import Dict, List


class ProvincialTitleGuides:
    """
    Provincial title transfer guide content for all 13 Canadian provinces/territories
    """
    
    @staticmethod
    def get_guide(province_code: str) -> Dict:
        """
        Get title transfer guide for specific province
        
        Args:
            province_code: 2-letter province code (ON, QC, BC, etc.)
        
        Returns:
            Dict with guide content
        """
        guides = {
            'ON': ProvincialTitleGuides._ontario_guide(),
            'QC': ProvincialTitleGuides._quebec_guide(),
            'BC': ProvincialTitleGuides._british_columbia_guide(),
            'AB': ProvincialTitleGuides._alberta_guide(),
            'MB': ProvincialTitleGuides._manitoba_guide(),
            'SK': ProvincialTitleGuides._saskatchewan_guide(),
            'NS': ProvincialTitleGuides._nova_scotia_guide(),
            'NB': ProvincialTitleGuides._new_brunswick_guide(),
            'NL': ProvincialTitleGuides._newfoundland_guide(),
            'PE': ProvincialTitleGuides._pei_guide(),
            'NT': ProvincialTitleGuides._nwt_guide(),
            'YT': ProvincialTitleGuides._yukon_guide(),
            'NU': ProvincialTitleGuides._nunavut_guide(),
        }
        
        return guides.get(province_code.upper(), ProvincialTitleGuides._generic_guide())
    
    @staticmethod
    def get_all_provinces() -> List[Dict]:
        """
        Get summary list of all provinces with basic info
        
        Returns:
            List of dicts with code, name, authority
        """
        return [
            {'code': 'ON', 'name': 'Ontario', 'authority': 'ServiceOntario'},
            {'code': 'QC', 'name': 'Quebec', 'authority': 'SAAQ'},
            {'code': 'BC', 'name': 'British Columbia', 'authority': 'ICBC'},
            {'code': 'AB', 'name': 'Alberta', 'authority': 'ServiceAlberta'},
            {'code': 'MB', 'name': 'Manitoba', 'authority': 'MPI'},
            {'code': 'SK', 'name': 'Saskatchewan', 'authority': 'SGI'},
            {'code': 'NS', 'name': 'Nova Scotia', 'authority': 'Service Nova Scotia'},
            {'code': 'NB', 'name': 'New Brunswick', 'authority': 'Service New Brunswick'},
            {'code': 'NL', 'name': 'Newfoundland and Labrador', 'authority': 'Service NL'},
            {'code': 'PE', 'name': 'Prince Edward Island', 'authority': 'Access PEI'},
            {'code': 'NT', 'name': 'Northwest Territories', 'authority': 'DMV NWT'},
            {'code': 'YT', 'name': 'Yukon', 'authority': 'Motor Vehicles Yukon'},
            {'code': 'NU', 'name': 'Nunavut', 'authority': 'Motor Vehicles Nunavut'},
        ]
    
    @staticmethod
    def _ontario_guide() -> Dict:
        return {
            'province': 'Ontario',
            'province_code': 'ON',
            'authority': 'ServiceOntario',
            'website': 'https://www.ontario.ca/page/buy-or-sell-used-vehicle-ontario',
            'required_documents': [
                'Vehicle Ownership (pink slip) signed by seller',
                'Bill of Sale with VIN, date, price, and signatures',
                'Safety Standards Certificate (valid 36 days)',
                'Used Vehicle Information Package (UVIP)',
                'Proof of insurance',
                'Valid government-issued ID',
                'Payment for fees and taxes',
            ],
            'fees': {
                'title_transfer': '$32.00',
                'plate_transfer': '$20.00',
                'new_plates': '$27.00',
                'retail_sales_tax': '13% HST on purchase price',
            },
            'tax_exemptions': [
                'Gifts between immediate family members (declaration required)',
                'Inheritance transfers with proper documentation',
            ],
            'process_steps': [
                '1. Obtain Safety Standards Certificate (within 36 days of sale)',
                '2. Seller signs vehicle ownership (back of pink slip)',
                '3. Complete Bill of Sale with all required information',
                '4. Obtain insurance coverage before transfer',
                '5. Visit ServiceOntario centre with all documents',
                '6. Pay transfer fees and applicable taxes',
                '7. Receive new ownership and plate sticker',
            ],
            'timeline': '1-2 business days for in-person transfer',
            'contact': {
                'phone': '1-800-267-8097',
                'hours': 'Monday-Friday: 8:30 AM - 5:00 PM EST',
            },
            'special_notes': [
                'UVIP must be obtained by seller (shows liens, history)',
                'Safety certificate required for most transfers',
                'Emission test not required for ownership transfer',
                'Out-of-province vehicles require additional inspection',
            ],
        }
    
    @staticmethod
    def _quebec_guide() -> Dict:
        return {
            'province': 'Quebec',
            'province_code': 'QC',
            'authority': 'Société de l\'assurance automobile du Québec (SAAQ)',
            'website': 'https://saaq.gouv.qc.ca/en/',
            'required_documents': [
                'Certificate of Registration signed by seller',
                'Bill of Sale (Contract de vente)',
                'Proof of mechanical inspection (inspection sheet)',
                'Proof of insurance',
                'Valid government-issued ID',
                'Payment for fees and taxes',
            ],
            'fees': {
                'registration': '$93.75 per year',
                'title_transfer': 'Included in registration',
                'plate_transfer': '$30.00',
                'sales_tax_qst': '9.975% QST',
                'sales_tax_gst': '5% GST',
            },
            'tax_exemptions': [
                'Gifts between immediate family (declaration required)',
                'Spouse transfers',
            ],
            'process_steps': [
                '1. Vehicle must pass mechanical inspection (within 48 hours of sale for vehicles 4+ years old)',
                '2. Seller signs certificate of registration',
                '3. Complete bill of sale in French or English',
                '4. Obtain insurance coverage',
                '5. Visit SAAQ service centre or authorized dealer',
                '6. Pay registration fees and taxes (QST + GST)',
                '7. Receive new registration certificate and plate sticker',
            ],
            'timeline': 'Same day at SAAQ centre',
            'contact': {
                'phone': '1-800-361-7620',
                'hours': 'Monday-Friday: 8:30 AM - 4:30 PM EST',
            },
            'special_notes': [
                'Mechanical inspection mandatory for vehicles 4+ years old',
                'Both QST and GST apply to used vehicle sales',
                'Registration fees paid annually, not at transfer',
                'Out-of-province vehicles require import inspection',
            ],
        }
    
    @staticmethod
    def _british_columbia_guide() -> Dict:
        return {
            'province': 'British Columbia',
            'province_code': 'BC',
            'authority': 'Insurance Corporation of British Columbia (ICBC)',
            'website': 'https://www.icbc.com/',
            'required_documents': [
                'Transfer/Tax Form (APV9T) signed by both parties',
                'Vehicle registration',
                'Bill of Sale',
                'Proof of vehicle inspection (if out-of-province)',
                'Proof of insurance',
                'Valid government-issued ID',
            ],
            'fees': {
                'transfer_fee': '$32.00',
                'registration': 'Varies by plate type',
                'provincial_sales_tax': '12% PST on private sales (7% on dealer sales)',
            },
            'tax_exemptions': [
                'Gifts between immediate family members',
                'Transfers between spouses',
            ],
            'process_steps': [
                '1. Complete Transfer/Tax Form (APV9T) with seller',
                '2. Obtain BC vehicle inspection if from out-of-province',
                '3. Arrange ICBC Autoplan insurance',
                '4. Visit Autoplan broker or ICBC office',
                '5. Pay transfer fee and PST',
                '6. Receive new registration and decal',
            ],
            'timeline': 'Same day at ICBC or Autoplan broker',
            'contact': {
                'phone': '1-800-663-3051',
                'hours': 'Monday-Friday: 8:00 AM - 5:30 PM PST',
            },
            'special_notes': [
                'Must register within 10 days of becoming BC resident',
                'Out-of-province vehicles require mechanical inspection',
                '12% PST applies to private sales (cannot be avoided)',
                'Insurance and registration done together at ICBC',
            ],
        }
    
    @staticmethod
    def _alberta_guide() -> Dict:
        return {
            'province': 'Alberta',
            'province_code': 'AB',
            'authority': 'ServiceAlberta',
            'website': 'https://www.alberta.ca/register-vehicle',
            'required_documents': [
                'Vehicle Registration (blue card) signed by seller',
                'Bill of Sale',
                'Out-of-province inspection (if applicable)',
                'Proof of insurance',
                'Valid government-issued ID',
            ],
            'fees': {
                'registration_transfer': '$10.50',
                'registration_new': '$84.45 per year',
                'plate_fee': '$10.50',
                'sales_tax': 'No provincial sales tax in Alberta',
            },
            'tax_exemptions': [
                'Alberta has no provincial sales tax on vehicle purchases',
            ],
            'process_steps': [
                '1. Seller signs vehicle registration',
                '2. Complete bill of sale',
                '3. Out-of-province vehicles require inspection within 14 days',
                '4. Obtain insurance coverage',
                '5. Visit registry agent within 14 days of purchase',
                '6. Pay registration fees (no sales tax)',
                '7. Receive new registration and plate',
            ],
            'timeline': 'Same day at registry agent',
            'contact': {
                'phone': '310-0000 then 780-427-7013',
                'hours': 'Monday-Friday: 8:15 AM - 4:30 PM MST',
            },
            'special_notes': [
                'No PST or GST on private vehicle sales',
                'Must transfer within 14 days of purchase or moving to AB',
                'Out-of-province inspection required for imported vehicles',
                'Registry agents are privatized and located throughout province',
            ],
        }
    
    @staticmethod
    def _manitoba_guide() -> Dict:
        return {
            'province': 'Manitoba',
            'province_code': 'MB',
            'authority': 'Manitoba Public Insurance (MPI)',
            'website': 'https://www.mpi.mb.ca/',
            'required_documents': [
                'Certificate of Registration signed by seller',
                'Bill of Sale',
                'Vehicle inspection certificate (if out-of-province)',
                'Proof of insurance',
                'Valid Manitoba driver\'s licence',
            ],
            'fees': {
                'registration': 'Varies by vehicle type and weight',
                'retail_sales_tax': '7% RST on purchase price',
            },
            'tax_exemptions': [
                'Gifts between immediate family members',
            ],
            'process_steps': [
                '1. Obtain vehicle inspection if from out-of-province',
                '2. Complete bill of sale',
                '3. Seller signs certificate of registration',
                '4. Visit MPI Autopac agent',
                '5. Pay registration fees and 7% RST',
                '6. Receive new registration and licence plate',
            ],
            'timeline': 'Same day at Autopac agent',
            'contact': {
                'phone': '204-985-7000 or 1-800-665-2410',
                'hours': 'Monday-Friday: 8:30 AM - 5:00 PM CST',
            },
            'special_notes': [
                'Insurance and registration bundled through MPI',
                '7% RST applies to private vehicle purchases',
                'Out-of-province vehicles require safety inspection',
            ],
        }
    
    @staticmethod
    def _saskatchewan_guide() -> Dict:
        return {
            'province': 'Saskatchewan',
            'province_code': 'SK',
            'authority': 'Saskatchewan Government Insurance (SGI)',
            'website': 'https://www.sgi.sk.ca/',
            'required_documents': [
                'Vehicle Registration (Certificate of Title)',
                'Bill of Sale',
                'SGI Approved Vehicle Inspection (if out-of-province)',
                'Proof of insurance',
                'Valid SK driver\'s licence',
            ],
            'fees': {
                'registration': 'Based on vehicle weight and age',
                'sales_tax': '6% PST on purchase price',
            },
            'tax_exemptions': [
                'Immediate family gifts (with declaration)',
            ],
            'process_steps': [
                '1. Complete SGI-approved inspection if from out-of-province',
                '2. Complete bill of sale',
                '3. Visit SGI motor licence issuer',
                '4. Pay registration fees and 6% PST',
                '5. Receive registration and licence plate',
            ],
            'timeline': 'Same day at motor licence issuer',
            'contact': {
                'phone': '1-800-667-9868',
                'hours': 'Monday-Friday: 8:00 AM - 5:00 PM CST',
            },
            'special_notes': [
                '6% PST on private vehicle purchases',
                'Out-of-province vehicles need SGI inspection',
            ],
        }
    
    @staticmethod
    def _nova_scotia_guide() -> Dict:
        return {
            'province': 'Nova Scotia',
            'province_code': 'NS',
            'authority': 'Service Nova Scotia',
            'website': 'https://beta.novascotia.ca/programs-and-services/register-vehicle',
            'required_documents': [
                'Certificate of Registration',
                'Bill of Sale',
                'Safety inspection certificate (within 14 days)',
                'Proof of insurance',
                'Valid ID',
            ],
            'fees': {
                'registration': '$77.95 for 1 year',
                'harmonized_sales_tax': '15% HST on purchase price',
            },
            'tax_exemptions': [
                'Gifts between immediate family',
            ],
            'process_steps': [
                '1. Obtain safety inspection within 14 days',
                '2. Complete bill of sale',
                '3. Visit Access Nova Scotia centre',
                '4. Pay registration and 15% HST',
                '5. Receive registration',
            ],
            'timeline': 'Same day',
            'contact': {
                'phone': '1-800-898-7668',
                'hours': 'Monday-Friday: 8:00 AM - 5:00 PM AST',
            },
            'special_notes': [
                'Safety inspection mandatory within 14 days',
                '15% HST applies to private sales',
            ],
        }
    
    @staticmethod
    def _new_brunswick_guide() -> Dict:
        return {
            'province': 'New Brunswick',
            'province_code': 'NB',
            'authority': 'Service New Brunswick',
            'website': 'https://www2.gnb.ca/content/gnb/en/services/services_renderer.201458.html',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Vehicle inspection certificate',
                'Proof of insurance',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Varies by vehicle type',
                'harmonized_sales_tax': '15% HST on purchase price',
            },
            'tax_exemptions': [
                'Immediate family gifts',
            ],
            'process_steps': [
                '1. Obtain vehicle inspection',
                '2. Complete bill of sale',
                '3. Visit Service NB centre',
                '4. Pay fees and 15% HST',
                '5. Receive registration',
            ],
            'timeline': 'Same day',
            'contact': {
                'phone': '1-888-762-8600',
                'hours': 'Monday-Friday: 8:30 AM - 4:30 PM AST',
            },
            'special_notes': [
                'Vehicle inspection required',
                '15% HST on private sales',
            ],
        }
    
    @staticmethod
    def _newfoundland_guide() -> Dict:
        return {
            'province': 'Newfoundland and Labrador',
            'province_code': 'NL',
            'authority': 'Service NL',
            'website': 'https://www.gov.nl.ca/dgsnl/',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Safety inspection certificate',
                'Proof of insurance',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Based on vehicle type',
                'harmonized_sales_tax': '15% HST on purchase price',
            },
            'tax_exemptions': [
                'Family gifts',
            ],
            'process_steps': [
                '1. Get safety inspection',
                '2. Complete bill of sale',
                '3. Visit Motor Registration Division',
                '4. Pay fees and 15% HST',
                '5. Receive registration',
            ],
            'timeline': 'Same day',
            'contact': {
                'phone': '709-729-2519',
                'hours': 'Monday-Friday: 8:30 AM - 4:30 PM NST',
            },
            'special_notes': [
                'Safety inspection required',
                '15% HST applies',
            ],
        }
    
    @staticmethod
    def _pei_guide() -> Dict:
        return {
            'province': 'Prince Edward Island',
            'province_code': 'PE',
            'authority': 'Access PEI',
            'website': 'https://www.princeedwardisland.ca/en/service/register-vehicle',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Safety inspection',
                'Proof of insurance',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Varies',
                'harmonized_sales_tax': '15% HST on purchase price',
            },
            'tax_exemptions': [
                'Immediate family gifts',
            ],
            'process_steps': [
                '1. Obtain safety inspection',
                '2. Complete bill of sale',
                '3. Visit Access PEI centre',
                '4. Pay fees and 15% HST',
                '5. Receive registration',
            ],
            'timeline': 'Same day',
            'contact': {
                'phone': '902-368-5200',
                'hours': 'Monday-Friday: 8:30 AM - 5:00 PM AST',
            },
            'special_notes': [
                'Safety inspection mandatory',
                '15% HST on private sales',
            ],
        }
    
    @staticmethod
    def _nwt_guide() -> Dict:
        return {
            'province': 'Northwest Territories',
            'province_code': 'NT',
            'authority': 'Department of Infrastructure',
            'website': 'https://www.gov.nt.ca/en/services/driver-and-vehicle-services',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Varies by vehicle type',
                'sales_tax': 'No territorial sales tax',
            },
            'tax_exemptions': [
                'NWT has no territorial sales tax',
            ],
            'process_steps': [
                '1. Complete bill of sale',
                '2. Visit motor vehicles office',
                '3. Pay registration fees',
                '4. Receive registration',
            ],
            'timeline': 'Same day',
            'contact': {
                'phone': '867-767-9088',
                'hours': 'Monday-Friday: 8:30 AM - 5:00 PM MST',
            },
            'special_notes': [
                'No territorial sales tax',
                'Inspection requirements vary',
            ],
        }
    
    @staticmethod
    def _yukon_guide() -> Dict:
        return {
            'province': 'Yukon',
            'province_code': 'YT',
            'authority': 'Motor Vehicles',
            'website': 'https://yukon.ca/en/motor-vehicles',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Varies',
                'sales_tax': 'No territorial sales tax',
            },
            'tax_exemptions': [
                'Yukon has no territorial sales tax',
            ],
            'process_steps': [
                '1. Complete bill of sale',
                '2. Visit Motor Vehicles office',
                '3. Pay registration fees',
                '4. Receive registration',
            ],
            'timeline': 'Same day',
            'contact': {
                'phone': '867-667-5315',
                'hours': 'Monday-Friday: 8:30 AM - 5:00 PM PST',
            },
            'special_notes': [
                'No territorial sales tax',
            ],
        }
    
    @staticmethod
    def _nunavut_guide() -> Dict:
        return {
            'province': 'Nunavut',
            'province_code': 'NU',
            'authority': 'Motor Vehicles Division',
            'website': 'https://www.gov.nu.ca/economic-development-and-transportation/information/motor-vehicles',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Varies',
                'sales_tax': 'No territorial sales tax',
            },
            'tax_exemptions': [
                'Nunavut has no territorial sales tax',
            ],
            'process_steps': [
                '1. Complete bill of sale',
                '2. Visit motor vehicles office',
                '3. Pay registration fees',
                '4. Receive registration',
            ],
            'timeline': 'Varies by community',
            'contact': {
                'phone': '867-975-5403',
                'hours': 'Monday-Friday: 8:30 AM - 5:00 PM EST',
            },
            'special_notes': [
                'No territorial sales tax',
                'Remote communities may have limited services',
            ],
        }
    
    @staticmethod
    def _generic_guide() -> Dict:
        return {
            'province': 'Unknown',
            'province_code': 'XX',
            'authority': 'Provincial Motor Vehicle Authority',
            'website': 'Contact local registry',
            'required_documents': [
                'Vehicle Registration',
                'Bill of Sale',
                'Proof of insurance',
                'Valid ID',
            ],
            'fees': {
                'registration': 'Varies by province',
                'sales_tax': 'Varies by province',
            },
            'tax_exemptions': [],
            'process_steps': [
                'Contact your provincial motor vehicle registry',
            ],
            'timeline': 'Varies',
            'contact': {
                'phone': 'N/A',
                'hours': 'N/A',
            },
            'special_notes': [
                'Contact your provincial authority for specific requirements',
            ],
        }
