from django.contrib import admin
from .models import Shipment, ShipmentUpdate
from .certification_models import SecurityRiskAssessment, SecurityIncident, PortVerification, ISO28000AuditLog


class ShipmentUpdateInline(admin.TabularInline):
    model = ShipmentUpdate
    extra = 1
    readonly_fields = ['created_at']
    fields = ['location', 'status', 'notes', 'latitude', 'longitude', 
              'iso_message_type', 'verified_by', 'verification_method', 'created_at']


class SecurityRiskAssessmentInline(admin.StackedInline):
    model = SecurityRiskAssessment
    extra = 0
    readonly_fields = ['assessment_date', 'risk_score', 'overall_risk_level']
    fieldsets = (
        ('Assessment Info', {
            'fields': ('assessed_by', 'assessment_date', 'overall_risk_level', 'risk_score')
        }),
        ('Risk Factor Scores (0-10 each)', {
            'fields': ('route_risk_score', 'value_risk_score', 'destination_risk_score', 
                      'customs_risk_score', 'port_security_score')
        }),
        ('Mitigation', {
            'fields': ('mitigation_measures', 'insurance_required', 
                      'recommended_insurance_amount', 'lloyd_register_recommended')
        }),
    )


class SecurityIncidentInline(admin.TabularInline):
    model = SecurityIncident
    extra = 0
    readonly_fields = ['reported_date', 'reported_by']
    fields = ['incident_type', 'severity', 'incident_date', 'description', 
              'police_report_filed', 'insurance_claim_filed', 'resolved']


class PortVerificationInline(admin.StackedInline):
    model = PortVerification
    extra = 0
    readonly_fields = ['verification_date']
    fieldsets = (
        ('Verification Details', {
            'fields': ('verification_type', 'port_name', 'verification_date', 'verified_by_name')
        }),
        ('Container & Seal', {
            'fields': ('seal_number_verified', 'seal_intact', 'seal_condition_notes')
        }),
        ('Vehicle Inspection', {
            'fields': ('vehicle_condition_status', 'customs_cleared', 'documents_complete')
        }),
        ('Verification Proof', {
            'fields': ('digital_signature', 'photo_ids')
        }),
    )


class ISO28000AuditLogInline(admin.TabularInline):
    model = ISO28000AuditLog
    extra = 0
    readonly_fields = ['action_timestamp', 'action_type', 'performed_by', 'action_description', 
                      'ip_address', 'user_agent']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'deal', 'status', 'shipping_company', 
                    'origin_port', 'destination_port', 'lloyd_register_status',
                    'security_risk_level', 'iso_18602_compliant', 'ams_status', 
                    'aci_status', 'vgm_method']
    list_filter = ['status', 'destination_country', 'shipping_company',
                   'lloyd_register_status', 'security_risk_level', 
                   'iso_18602_compliant', 'ctpat_compliant', 'ams_status',
                   'aci_status', 'ens_status', 'vgm_method', 'contains_hazmat',
                   'bill_of_lading_type', 'freight_terms', 'incoterm']
    search_fields = ['tracking_number', 'deal__id', 'destination_country', 
                    'lloyd_register_tracking_id', 'container_number',
                    'bill_of_lading_number', 'ams_filing_number', 'pars_number',
                    'vessel_name', 'imo_vessel_number']
    readonly_fields = ['created_at', 'updated_at', 'lloyd_register_certificate_date',
                      'iso_28000_audit_date', 'security_assessment_date',
                      'vgm_certification_date', 'ams_submission_date', 'aci_submission_date',
                      'aes_filing_date', 'ens_filing_date', 'bill_of_lading_date']
    inlines = [ShipmentUpdateInline, SecurityRiskAssessmentInline, 
               SecurityIncidentInline, PortVerificationInline, ISO28000AuditLogInline]
    
    fieldsets = (
        ('Deal Information', {
            'fields': ('deal',)
        }),
        ('Shipment Details', {
            'fields': ('tracking_number', 'shipping_company', 'status')
        }),
        ('🚢 Vessel Information', {
            'fields': (
                ('vessel_name', 'voyage_number'),
                ('imo_vessel_number',),
            ),
        }),
        ('📦 Container & Seal Information', {
            'fields': (
                ('container_number', 'container_type'),
                ('seal_number', 'seal_type'),
                ('seal_applied_by', 'seal_applied_at'),
                ('seal_verified_at_origin', 'seal_origin_verifier', 'seal_origin_verification_date'),
                ('seal_verified_at_destination', 'seal_destination_verifier', 'seal_destination_verification_date'),
                ('seal_intact', 'seal_notes'),
            ),
            'classes': ('collapse',)
        }),
        ('⚖️ PRIORITY 1: SOLAS VGM (CRITICAL - Vessel Loading Requirement)', {
            'fields': (
                ('vgm_weight_kg', 'vgm_method'),
                ('vgm_certified_by', 'vgm_certification_date'),
                ('vgm_certificate_number',),
            ),
            'description': '🚨 MANDATORY for all container shipments. Vessel will refuse loading without VGM certification.',
        }),
        ('🇺🇸 PRIORITY 1: AMS - US Customs (CRITICAL)', {
            'fields': (
                ('ams_filing_number', 'ams_status'),
                ('ams_submission_date', 'ams_arrival_notice_date'),
                ('ams_scac_code',),
            ),
            'classes': ('collapse',),
            'description': 'Required 24 hours before departure to USA. Legal requirement since 2002.',
        }),
        ('🇨🇦 PRIORITY 1: ACI - Canada Customs (CRITICAL)', {
            'fields': (
                ('cargo_control_document_number', 'aci_status'),
                ('aci_submission_date',),
                ('pars_number', 'paps_number'),
                ('release_notification_number',),
            ),
            'classes': ('collapse',),
            'description': 'Required 24 hours before arrival in Canada (marine). Essential for CBSA clearance.',
        }),
        ('🇺🇸 PRIORITY 2: AES - US Export System', {
            'fields': (
                ('aes_itn_number', 'aes_exemption_code'),
                ('aes_filing_date',),
                ('schedule_b_code',),
                ('export_license_required', 'export_license_number'),
            ),
            'classes': ('collapse',),
            'description': 'Required for US exports >$2,500 USD. US Census Bureau regulation.',
        }),
        ('🇪🇺 PRIORITY 2: ENS - EU Entry Summary', {
            'fields': (
                ('ens_mrn_number', 'ens_lrn_number'),
                ('ens_filing_date', 'ens_status'),
            ),
            'classes': ('collapse',),
            'description': 'Required before cargo arrives in EU. Import Control System security screening.',
        }),
        ('🏗️ PRIORITY 2: ISPS Code - Port Security', {
            'fields': (
                ('isps_facility_security_level',),
                ('origin_port_isps_certified', 'destination_port_isps_certified'),
                ('port_facility_security_officer',),
                ('ship_security_alert_system',),
            ),
            'classes': ('collapse',),
            'description': 'International Ship & Port Facility Security Code (IMO SOLAS).',
        }),
        ('💰 PRIORITY 3: HS Tariff & Customs Valuation', {
            'fields': (
                ('hs_tariff_code',),
                ('customs_value_declared', 'customs_value_currency'),
                ('duty_paid',),
                ('customs_broker_name', 'customs_broker_license'),
            ),
            'classes': ('collapse',),
            'description': 'Harmonized System classification for duty calculation.',
        }),
        ('☢️ PRIORITY 3: Hazmat & Dangerous Goods', {
            'fields': (
                ('contains_hazmat', 'msds_attached'),
                ('un_number', 'imdg_class'),
                ('hazmat_emergency_contact',),
            ),
            'classes': ('collapse',),
            'description': 'IMDG Code compliance for electric vehicles (lithium batteries = UN3171, Class 9).',
        }),
        ('📄 PRIORITY 3: Bill of Lading & Documentation', {
            'fields': (
                ('bill_of_lading_number', 'bill_of_lading_type'),
                ('bill_of_lading_date',),
                ('freight_terms', 'incoterm'),
                ('shipper_reference',),
                ('consignee_name',),
                ('consignee_address',),
                ('notify_party',),
            ),
            'classes': ('collapse',),
            'description': 'Master/House Bill of Lading and shipping documentation.',
        }),
        ("Lloyd's Register Certification", {
            'fields': (
                ('lloyd_register_tracking_id', 'lloyd_register_service_level'),
                ('lloyd_register_status', 'lloyd_register_certificate_issued'),
                ('lloyd_register_certificate_number', 'lloyd_register_certificate_date'),
                ('lloyd_register_surveyor_origin', 'lloyd_register_surveyor_destination'),
                ('lloyd_register_notes',),
            ),
            'classes': ('collapse',)
        }),
        ('ISO 28000 Security Management', {
            'fields': (
                ('security_risk_level', 'security_assessment_completed'),
                ('security_assessment_by', 'security_assessment_date'),
                ('security_measures_implemented',),
                ('has_security_incident', 'security_incident_description'),
                ('security_incident_reported_to_authorities',),
                ('ctpat_compliant', 'iso_28000_audit_date'),
            ),
            'classes': ('collapse',)
        }),
        ('Insurance', {
            'fields': (
                ('insurance_policy_number', 'insurance_company'),
                ('insurance_coverage_amount',),
            ),
            'classes': ('collapse',)
        }),
        ('ISO 18602 Compliance', {
            'fields': ('iso_18602_compliant',),
            'classes': ('collapse',)
        }),
        ('Locations', {
            'fields': ('origin_port', 'destination_port', 'destination_country')
        }),
        ('Schedule', {
            'fields': ('estimated_departure', 'actual_departure', 
                      'estimated_arrival', 'actual_arrival')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ShipmentUpdate)
class ShipmentUpdateAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'location', 'status', 'iso_message_type', 
                    'verified_by', 'created_at']
    list_filter = ['created_at', 'iso_message_type', 'verification_method']
    search_fields = ['shipment__tracking_number', 'location', 'verified_by']
    readonly_fields = ['created_at']


@admin.register(SecurityRiskAssessment)
class SecurityRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'overall_risk_level', 'risk_score', 
                    'assessed_by', 'assessment_date', 'lloyd_register_recommended']
    list_filter = ['overall_risk_level', 'lloyd_register_recommended', 
                   'insurance_required', 'assessment_date']
    search_fields = ['shipment__tracking_number']
    readonly_fields = ['assessment_date', 'risk_score', 'overall_risk_level']
    
    fieldsets = (
        ('Assessment Info', {
            'fields': ('shipment', 'assessed_by', 'assessment_date', 
                      'overall_risk_level', 'risk_score')
        }),
        ('Risk Factor Scores (0-10 each)', {
            'fields': ('route_risk_score', 'value_risk_score', 'destination_risk_score', 
                      'customs_risk_score', 'port_security_score')
        }),
        ('Mitigation', {
            'fields': ('mitigation_measures', 'insurance_required', 
                      'recommended_insurance_amount', 'lloyd_register_recommended')
        }),
    )


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'incident_type', 'severity', 'incident_date', 
                    'resolved', 'police_report_filed']
    list_filter = ['incident_type', 'severity', 'resolved', 'police_report_filed', 
                   'insurance_claim_filed', 'incident_date']
    search_fields = ['shipment__tracking_number', 'description']
    readonly_fields = ['reported_date', 'reported_by']
    date_hierarchy = 'incident_date'


@admin.register(PortVerification)
class PortVerificationAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'verification_type', 'port_name', 
                    'verification_date', 'seal_intact', 'customs_cleared']
    list_filter = ['verification_type', 'seal_intact', 'customs_cleared', 
                   'documents_complete', 'verification_date']
    search_fields = ['shipment__tracking_number', 'port_name', 'verified_by_name']
    readonly_fields = ['verification_date']
    date_hierarchy = 'verification_date'
    
    fieldsets = (
        ('Verification Details', {
            'fields': ('shipment', 'verification_type', 'port_name', 'port_country',
                      'verification_date', 'verified_by_name', 'verifier_organization')
        }),
        ('Container & Seal', {
            'fields': ('seal_number_verified', 'seal_intact', 'seal_condition_notes')
        }),
        ('Vehicle Inspection', {
            'fields': ('vehicle_condition_status', 'odometer_reading', 'vehicle_condition_notes', 
                      'customs_cleared', 'documents_complete')
        }),
        ('Verification Proof', {
            'fields': ('digital_signature', 'photo_ids', 'verification_certificate_url')
        }),
    )


@admin.register(ISO28000AuditLog)
class ISO28000AuditLogAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'action_type', 'performed_by', 'action_timestamp', 'ip_address']
    list_filter = ['action_type', 'action_timestamp']
    search_fields = ['shipment__tracking_number', 'performed_by__username', 'action_description']
    readonly_fields = ['action_timestamp', 'action_type', 'performed_by', 'performed_by_name',
                      'action_description', 'ip_address', 'user_agent', 'related_object_type', 
                      'related_object_id']
    date_hierarchy = 'action_timestamp'
    
    def has_add_permission(self, request):
        # Audit logs are created automatically, not manually
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Audit logs cannot be deleted (immutable)
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit logs cannot be modified (immutable)
        return False
