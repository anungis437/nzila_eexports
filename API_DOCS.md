# Nzila Export Hub - API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All API endpoints require authentication. Use Django session authentication:
1. Login via `/api-auth/login/`
2. Include session cookie in subsequent requests

## Common Response Codes
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not authorized
- `404 Not Found` - Resource not found

---

## Accounts API

### Get Current User Profile
```http
GET /api/accounts/users/me/
```

**Response:**
```json
{
  "id": 1,
  "username": "buyer1",
  "email": "buyer@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "buyer",
  "company_name": "West African Imports",
  "phone": "+221 77 123 4567",
  "address": "123 Main St",
  "country": "Senegal",
  "preferred_language": "fr"
}
```

### Update Current User Profile
```http
PUT /api/accounts/users/me/
```

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+221 77 123 4567",
  "preferred_language": "fr"
}
```

---

## Vehicles API

### List Vehicles
```http
GET /api/vehicles/vehicles/
```

**Query Parameters:**
- `status` - Filter by status (available, reserved, sold, shipped, delivered)
- `make` - Filter by manufacturer
- `year` - Filter by year
- `condition` - Filter by condition
- `dealer` - Filter by dealer ID
- `search` - Search in make, model, VIN, location
- `ordering` - Sort by field (price_cad, year, mileage, created_at)

**Example:**
```http
GET /api/vehicles/vehicles/?status=available&make=Toyota&ordering=-year
```

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/vehicles/vehicles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "vin": "1HGBH41JXMN109186",
      "condition": "used_good",
      "mileage": 50000,
      "price_cad": "25000.00",
      "status": "available",
      "location": "Toronto, ON",
      "main_image": "/media/vehicles/camry.jpg",
      "dealer_name": "dealer1"
    }
  ]
}
```

### Get Vehicle Details
```http
GET /api/vehicles/vehicles/{id}/
```

**Response:**
```json
{
  "id": 1,
  "dealer": 2,
  "dealer_name": "dealer1",
  "make": "Toyota",
  "model": "Camry",
  "year": 2020,
  "vin": "1HGBH41JXMN109186",
  "condition": "used_good",
  "mileage": 50000,
  "color": "Blue",
  "fuel_type": "Gasoline",
  "transmission": "Automatic",
  "price_cad": "25000.00",
  "status": "available",
  "description": "Well-maintained vehicle in excellent condition",
  "location": "Toronto, ON",
  "main_image": "/media/vehicles/camry.jpg",
  "images": [
    {
      "id": 1,
      "image": "/media/vehicles/camry_interior.jpg",
      "caption": "Interior view",
      "uploaded_at": "2024-12-15T10:30:00Z"
    }
  ],
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-15T10:00:00Z"
}
```

### Create Vehicle (Dealer Only)
```http
POST /api/vehicles/vehicles/
```

**Request:**
```json
{
  "make": "Toyota",
  "model": "Camry",
  "year": 2020,
  "vin": "1HGBH41JXMN109186",
  "condition": "used_good",
  "mileage": 50000,
  "color": "Blue",
  "fuel_type": "Gasoline",
  "transmission": "Automatic",
  "price_cad": "25000.00",
  "description": "Well-maintained vehicle",
  "location": "Toronto, ON"
}
```

---

## Leads API

### List Leads
```http
GET /api/deals/leads/
```

**Query Parameters:**
- `status` - Filter by status (new, contacted, qualified, negotiating, converted, lost)
- `source` - Filter by source (website, referral, broker, direct)
- `broker` - Filter by broker ID

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "buyer": {
        "id": 3,
        "username": "buyer1",
        "email": "buyer@example.com",
        "role": "buyer"
      },
      "vehicle": {
        "id": 1,
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "price_cad": "25000.00"
      },
      "broker": null,
      "status": "new",
      "source": "website",
      "notes": "Interested in purchasing",
      "created_at": "2024-12-15T10:00:00Z",
      "updated_at": "2024-12-15T10:00:00Z",
      "last_contacted": null
    }
  ]
}
```

### Create Lead
```http
POST /api/deals/leads/
```

**Request:**
```json
{
  "vehicle_id": 1,
  "source": "website",
  "notes": "Very interested in this vehicle"
}
```

### Update Lead
```http
PUT /api/deals/leads/{id}/
```

**Request:**
```json
{
  "status": "contacted",
  "notes": "Contacted via phone, interested in viewing",
  "last_contacted": "2024-12-15T14:30:00Z"
}
```

---

## Deals API

### List Deals
```http
GET /api/deals/deals/
```

**Query Parameters:**
- `status` - Filter by status
- `dealer` - Filter by dealer ID
- `broker` - Filter by broker ID

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "lead": 1,
      "vehicle": {
        "id": 1,
        "make": "Toyota",
        "model": "Camry",
        "year": 2020
      },
      "buyer": {
        "id": 3,
        "username": "buyer1"
      },
      "dealer": {
        "id": 2,
        "username": "dealer1"
      },
      "broker": null,
      "status": "pending_docs",
      "agreed_price_cad": "24000.00",
      "notes": "",
      "documents": [],
      "created_at": "2024-12-15T10:00:00Z",
      "updated_at": "2024-12-15T10:00:00Z",
      "completed_at": null
    }
  ]
}
```

### Create Deal
```http
POST /api/deals/deals/
```

**Request:**
```json
{
  "lead": 1,
  "vehicle_id": 1,
  "agreed_price_cad": "24000.00",
  "notes": "Price agreed after negotiation"
}
```

### Update Deal Status
```http
PATCH /api/deals/deals/{id}/
```

**Request:**
```json
{
  "status": "completed"
}
```

---

## Documents API

### List Documents
```http
GET /api/deals/documents/
```

**Query Parameters:**
- `deal` - Filter by deal ID
- `document_type` - Filter by type (title, id, payment_proof, export_permit, customs, other)
- `status` - Filter by status (pending, verified, rejected)

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "deal": 1,
      "document_type": "id",
      "file": "/media/documents/buyer_id.pdf",
      "status": "verified",
      "uploaded_by": {
        "id": 3,
        "username": "buyer1"
      },
      "verified_by": {
        "id": 1,
        "username": "admin"
      },
      "notes": "ID verified successfully",
      "uploaded_at": "2024-12-15T10:00:00Z",
      "verified_at": "2024-12-15T11:00:00Z"
    }
  ]
}
```

### Upload Document
```http
POST /api/deals/documents/
Content-Type: multipart/form-data
```

**Request (Form Data):**
```
deal: 1
document_type: id
file: [binary file]
```

### Verify Document (Admin Only)
```http
PUT /api/deals/documents/{id}/
```

**Request:**
```json
{
  "status": "verified",
  "notes": "Document verified successfully"
}
```

---

## Shipments API

### List Shipments
```http
GET /api/shipments/shipments/
```

**Query Parameters:**
- `status` - Filter by status (pending, in_transit, customs, delivered, delayed)
- `destination_country` - Filter by destination country

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "deal": 1,
      "deal_id": 1,
      "tracking_number": "SHIP123456",
      "shipping_company": "Ocean Freight Inc",
      "origin_port": "Port of Montreal",
      "destination_port": "Port of Dakar",
      "destination_country": "Senegal",
      "status": "in_transit",
      "estimated_departure": "2024-12-20",
      "actual_departure": "2024-12-20",
      "estimated_arrival": "2025-01-15",
      "actual_arrival": null,
      "notes": "",
      "updates": [
        {
          "id": 1,
          "location": "Port of Montreal",
          "status": "Departed",
          "description": "Container loaded and departed",
          "created_at": "2024-12-20T08:00:00Z"
        }
      ],
      "created_at": "2024-12-18T10:00:00Z",
      "updated_at": "2024-12-20T08:00:00Z"
    }
  ]
}
```

### Track Shipment (Public)
```http
GET /api/shipments/shipments/{id}/track/
```

**Response:** Same as shipment detail

### Create Shipment
```http
POST /api/shipments/shipments/
```

**Request:**
```json
{
  "deal": 1,
  "tracking_number": "SHIP123456",
  "shipping_company": "Ocean Freight Inc",
  "origin_port": "Port of Montreal",
  "destination_port": "Port of Dakar",
  "destination_country": "Senegal",
  "estimated_departure": "2024-12-20",
  "estimated_arrival": "2025-01-15"
}
```

---

## Commissions API

### List Commissions
```http
GET /api/commissions/commissions/
```

**Query Parameters:**
- `status` - Filter by status (pending, approved, paid, cancelled)
- `commission_type` - Filter by type (broker, dealer)

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "deal": 1,
      "deal_id": 1,
      "recipient": {
        "id": 2,
        "username": "dealer1",
        "role": "dealer"
      },
      "commission_type": "dealer",
      "amount_cad": "1200.00",
      "percentage": "5.00",
      "status": "pending",
      "notes": "",
      "created_at": "2024-12-15T10:00:00Z",
      "approved_at": null,
      "paid_at": null
    }
  ]
}
```

---

## Automated Workflows

### Document Verification → Deal Advancement

When a document is verified:
1. Document status changed to "verified"
2. System checks if all required documents are verified
3. If yes, deal status automatically advances:
   - `pending_docs` → `docs_verified`
   - `payment_pending` → `payment_received`

### Deal Completion → Commission Creation

When deal status changes to "completed":
1. Dealer commission created (5% of agreed price)
2. Broker commission created (3% of agreed price, if broker involved)
3. Both commissions have status "pending"

### Vehicle Status Updates

Deal status changes automatically update vehicle status:
- Deal pending → Vehicle "reserved"
- Deal ready to ship → Vehicle "sold"
- Deal shipped → Vehicle "shipped"
- Deal completed → Vehicle "delivered"
- Deal cancelled → Vehicle "available"

---

## Filtering & Pagination

### Pagination
All list endpoints support pagination:
```http
GET /api/vehicles/vehicles/?page=2
```

### Filtering
Use query parameters:
```http
GET /api/vehicles/vehicles/?make=Toyota&year=2020
```

### Search
Use the `search` parameter:
```http
GET /api/vehicles/vehicles/?search=camry
```

### Ordering
Use the `ordering` parameter:
```http
GET /api/vehicles/vehicles/?ordering=-price_cad
```
Prefix with `-` for descending order.

---

## Error Handling

### Validation Error (400)
```json
{
  "field_name": [
    "This field is required."
  ]
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

### Permission Denied (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Best Practices

1. **Always authenticate** before making API calls
2. **Use appropriate HTTP methods**: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
3. **Include CSRF token** for state-changing operations
4. **Handle pagination** for list endpoints
5. **Check status codes** to handle errors appropriately
6. **Use filtering** to reduce payload size
7. **Implement retry logic** for network errors
8. **Cache responses** when appropriate

---

## Rate Limiting

Currently not implemented. For production, consider:
- Django REST Framework throttling
- Redis-based rate limiting
- CDN caching for public endpoints

---

## Versioning

Current version: v1 (implicit)
Future versions will be prefixed: `/api/v2/`

---

## Support

For API issues or questions:
- Check this documentation
- Review example requests
- Contact the development team
- Create an issue in the repository
