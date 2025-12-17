# ISO 28000 Certification API - Quick Reference

## Base URL
```
http://127.0.0.1:8000/api/shipments/
```

## Authentication
All endpoints require JWT authentication:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Lloyd's Register Certification Endpoints

### 1. Register with Lloyd's Register
**Register shipment for third-party verification**

```bash
POST /api/shipments/{id}/lloyd-register/register/
Content-Type: application/json

{
  "service_level": "standard"  # or "premium" or "surveyor"
}
```

**Response:**
```json
{
  "success": true,
  "lr_tracking_id": "LR-2024-1234567",
  "service_level": "standard",
  "status": "pending_origin",
  "message": "Successfully registered with Lloyd's Register"
}
```

**Service Levels:**
- **standard** ($500-800): Tracking ID, status updates, certificate
- **premium** ($1,200-2,000): + Origin/destination inspections by surveyor
- **surveyor** ($2,500-4,500): + Physical surveyor, vehicle condition reports

---

### 2. Get Lloyd's Register Status
**Check verification status from Lloyd's Register**

```bash
GET /api/shipments/{id}/lloyd-register/status/
```

**Response:**
```json
{
  "lr_tracking_id": "LR-2024-1234567",
  "service_level": "premium",
  "status": "in_transit",
  "origin_inspection": {
    "status": "completed",
    "date": "2024-12-15T10:30:00Z",
    "surveyor": "John Smith - Lloyd's Register"
  },
  "destination_inspection": {
    "status": "pending",
    "estimated_date": "2024-12-30"
  },
  "seal_status": "verified_intact",
  "incidents": []
}
```

**Status Values:**
- `pending_origin`: Waiting for origin inspection
- `origin_verified`: Origin inspection completed
- `in_transit`: Shipment departed
- `destination_arrival`: Arrived at destination
- `destination_verified`: Destination inspection completed
- `completed`: Certificate issued
- `incident_reported`: Security incident occurred
- `cancelled`: Registration cancelled

---

### 3. Download Lloyd's Register Certificate
**Get Certificate of Safe Delivery PDF**

```bash
GET /api/shipments/{id}/lloyd-register/certificate/
```

**Response:**
```json
{
  "certificate_url": "https://lr.org/certificates/LR-2024-1234567.pdf",
  "certificate_number": "LR-CTS-2024-1234567",
  "issued_date": "2024-12-30T15:45:00Z",
  "valid_until": "2025-12-30",
  "shipment_tracking_number": "SHIP-2024-001",
  "verification_status": "completed"
}
```

---

## ISO 18602 Export Endpoints

### 4. Export to ISO 18602 XML
**Generate ISO-compliant XML for port systems**

```bash
GET /api/shipments/{id}/iso18602/xml/
```

**Response:** (XML format)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TrackingMessage>
  <Header>
    <MessageID>NZILA-SHIP-2024-001</MessageID>
    <Timestamp>2024-12-17T00:00:00Z</Timestamp>
  </Header>
  <Container>
    <ContainerNumber>ABCD1234567</ContainerNumber>
    <SealNumber>SEAL-12345678</SealNumber>
  </Container>
  <Cargo>
    <VIN>4T1B11HK1KU123456</VIN>
    <Description>2020 Toyota Camry</Description>
  </Cargo>
  <Route>
    <OriginPort>Vancouver, BC</OriginPort>
    <DestinationPort>Mombasa, Kenya</DestinationPort>
  </Route>
</TrackingMessage>
```

---

### 5. Export to UN/EDIFACT
**Generate UN/EDIFACT IFTSTA message for customs**

```bash
GET /api/shipments/{id}/iso18602/edifact/
```

**Response:** (EDIFACT format)
```
UNH+1+IFTSTA:D:95B:UN'
BGM+23+NZILA-SHIP-2024-001+9'
DTM+137:202412170000:203'
LOC+5+CAVAN::Vancouver BC::CA'
LOC+7+KEMBA::Mombasa::KE'
EQD+CN+ABCD1234567++22G1'
SEL+SEAL-12345678+CA'
UNT+7+1'
```

---

## Security & Risk Assessment Endpoints

### 6. Assess Security Risk
**Calculate risk score (0-100) for shipment**

```bash
POST /api/shipments/{id}/security/assess/
Content-Type: application/json

{
  "route_risk_score": 7,        # 0-10: Piracy, instability
  "value_risk_score": 8,         # 0-10: Vehicle value
  "destination_risk_score": 6,   # 0-10: Country security
  "customs_risk_score": 5,       # 0-10: Customs complexity
  "port_security_score": 4       # 0-10: Port security level
}
```

**Response:**
```json
{
  "risk_assessment_id": 123,
  "overall_risk_level": "high",
  "risk_score": 60,
  "breakdown": {
    "route_risk": 7,
    "value_risk": 8,
    "destination_risk": 6,
    "customs_risk": 5,
    "port_security": 4
  },
  "mitigation_required": [
    "Lloyd's Register monitoring recommended",
    "Insurance at 125% vehicle value",
    "Origin inspection by LR surveyor"
  ],
  "lloyd_register_recommended": true,
  "recommended_insurance_amount": 31250.00
}
```

**Risk Levels:**
- **Low (0-30)**: Standard insurance, basic security
- **Medium (31-60)**: Enhanced security, seal verification
- **High (61-85)**: Lloyd's Register monitoring recommended
- **Critical (86-100)**: Lloyd's Register surveyor mandatory

---

### 7. Get Security Audit Log
**Retrieve immutable audit trail (ISO 28000 requirement)**

```bash
GET /api/shipments/{id}/security/audit-log/
```

**Response:**
```json
{
  "shipment_id": 1,
  "tracking_number": "SHIP-2024-001",
  "audit_logs": [
    {
      "id": 1,
      "action_type": "lr_registered",
      "action_timestamp": "2024-12-17T10:00:00Z",
      "performed_by": "admin@nzilaventures.com",
      "performed_by_name": "John Doe",
      "action_description": "Registered with Lloyd's Register CTS - Service Level: premium",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "is_immutable": true
    },
    {
      "id": 2,
      "action_type": "risk_assessment",
      "action_timestamp": "2024-12-17T10:15:00Z",
      "performed_by": "admin@nzilaventures.com",
      "performed_by_name": "John Doe",
      "action_description": "Security risk assessment completed - Risk Level: high (60 points)",
      "related_object_type": "SecurityRiskAssessment",
      "related_object_id": 123,
      "ip_address": "192.168.1.100",
      "is_immutable": true
    }
  ],
  "total_logs": 2
}
```

**Action Types:**
- `risk_assessment`: Security risk assessment
- `incident_report`: Security incident reported
- `seal_applied`: Container seal applied
- `seal_verified`: Container seal verified
- `lr_registered`: Lloyd's Register CTS registered
- `lr_inspection`: LR surveyor inspection
- `port_verification`: Port verification
- `insurance_updated`: Insurance information updated
- `customs_cleared`: Customs clearance
- `security_measure`: Security measure implemented
- `document_upload`: Security document uploaded
- `access_granted`: Security access granted
- `system_alert`: Security system alert

---

## Compliance Reporting Endpoint

### 8. Get Certification Compliance Report
**Calculate ISO 28000 & ISO 18602 readiness scores**

```bash
GET /api/shipments/{id}/certification/compliance-report/
```

**Response:**
```json
{
  "shipment_id": 1,
  "tracking_number": "SHIP-2024-001",
  "iso_28000_score": 60,
  "iso_18602_score": 40,
  "certification_ready": false,
  "scores_breakdown": {
    "iso_28000": {
      "risk_assessment_complete": true,
      "security_measures_documented": true,
      "insurance_policy_active": false,
      "audit_log_maintained": true,
      "incident_response_plan": false
    },
    "iso_18602": {
      "container_tracking": true,
      "gps_tracking": false,
      "milestone_data": true,
      "port_verification": false,
      "electronic_data_interchange": true
    }
  },
  "missing_requirements": [
    "Insurance policy number not provided",
    "Incident response plan not documented",
    "GPS tracking not enabled",
    "Port verification not completed"
  ],
  "recommendations": [
    "Complete port origin verification",
    "Enable GPS tracking for container",
    "Update insurance policy information",
    "Document incident response procedures"
  ]
}
```

**Certification Thresholds:**
- ✅ **Certification Ready**: Both scores ≥ 80%
- 🟡 **Partial Compliance**: One score ≥ 80%
- ❌ **Not Ready**: Both scores < 80%

---

## Common Use Cases

### Scenario 1: High-Value Luxury Vehicle Shipment
```bash
# Step 1: Calculate risk score
POST /api/shipments/123/security/assess/
{
  "route_risk_score": 5,
  "value_risk_score": 10,  # $150,000 vehicle
  "destination_risk_score": 4,
  "customs_risk_score": 3,
  "port_security_score": 3
}
# Response: risk_score = 50 (Medium), LR recommended = false

# Step 2: Register with Lloyd's Register (premium service)
POST /api/shipments/123/lloyd-register/register/
{"service_level": "premium"}

# Step 3: Check compliance readiness
GET /api/shipments/123/certification/compliance-report/
# Response: iso_28000_score = 80%, iso_18602_score = 60%
```

### Scenario 2: Critical Risk Route (High Piracy Zone)
```bash
# Step 1: Calculate risk score
POST /api/shipments/456/security/assess/
{
  "route_risk_score": 10,  # Gulf of Aden - piracy zone
  "value_risk_score": 7,
  "destination_risk_score": 8,
  "customs_risk_score": 7,
  "port_security_score": 6
}
# Response: risk_score = 76 (High), LR mandatory recommended

# Step 2: Register with Lloyd's Register (surveyor service)
POST /api/shipments/456/lloyd-register/register/
{"service_level": "surveyor"}

# Step 3: Monitor status
GET /api/shipments/456/lloyd-register/status/
# Check origin_inspection.status before departure
```

### Scenario 3: Customs Export Documentation
```bash
# Export to XML for port system
GET /api/shipments/789/iso18602/xml/
# Save as shipment-789.xml

# Export to UN/EDIFACT for customs
GET /api/shipments/789/iso18602/edifact/
# Submit to CBSA customs system
```

---

## Error Codes

### 400 Bad Request
```json
{
  "error": "Shipment already registered with Lloyd's Register",
  "lr_tracking_id": "LR-2024-1234567"
}
```

### 404 Not Found
```json
{
  "detail": "Shipment not found"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```

### 500 Internal Server Error
```json
{
  "error": "Lloyd's Register API unavailable",
  "fallback": "Using mock data for development"
}
```

---

## Rate Limits

**Standard Tier:**
- 100 requests/minute per API key
- 10,000 requests/day

**Premium Tier** (Lloyd's Register subscribers):
- 500 requests/minute
- Unlimited daily requests

---

## Support

### Technical Issues
- Email: support@nzilaventures.com
- Phone: +1 (XXX) XXX-XXXX

### Lloyd's Register Support
- 24/7 Hotline: +44 20 7709 9166
- Email: cargo.tracking@lr.org

### Documentation
- Full Procedures Manual: `/docs/ISO28000_PROCEDURES.md`
- Implementation Summary: `/docs/ISO28000_IMPLEMENTATION_SUMMARY.md`

---

**Last Updated**: December 17, 2025
**API Version**: 1.0
**ISO 28000 Version**: 2022
**ISO 18602 Version**: 2013
