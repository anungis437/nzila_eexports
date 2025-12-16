# Document Management Feature

## Overview

The Document Management feature provides a comprehensive system for uploading, verifying, sharing, and managing all deal-related documents within the Nzila Export Hub platform. Users can upload various document types, track verification status, view documents in-browser, and share documents securely with stakeholders.

## Key Features

### 1. Document Upload
- **Multi-file support**: Upload PDFs, images (JPG, PNG), and Word documents (DOC, DOCX)
- **File size limit**: Maximum 10MB per document
- **Document types**: 6 predefined categories with custom labeling
- **Deal association**: Link documents to specific deals
- **Notes field**: Add context or instructions with each upload
- **Drag-and-drop**: (Future enhancement) Drop files directly into upload area

### 2. Document Types

#### Vehicle Title
- **Purpose**: Proof of vehicle ownership
- **Required for**: All vehicle export deals
- **French**: Titre de véhicule

#### ID Document
- **Purpose**: Buyer identification verification
- **Required for**: Buyer verification, customs clearance
- **French**: Pièce d'identité

#### Payment Proof
- **Purpose**: Evidence of payment transaction
- **Required for**: Payment verification, deal progression
- **French**: Preuve de paiement

#### Export Permit
- **Purpose**: Government authorization for vehicle export
- **Required for**: International shipping, customs
- **French**: Permis d'exportation

#### Customs Declaration
- **Purpose**: Customs documentation for import/export
- **Required for**: Border crossing, duty calculation
- **French**: Déclaration en douane

#### Other
- **Purpose**: Any additional documents
- **Examples**: Bill of lading, insurance certificates, inspection reports
- **French**: Autre

### 3. Document Verification Workflow

#### Status States
1. **Pending Review** (Yellow)
   - Initial state after upload
   - Awaiting admin/dealer verification
   - Icon: Clock
   - Actions available: View, Download, Delete, Verify/Reject

2. **Verified** (Green)
   - Document approved by authorized user
   - Timestamp recorded with verifier
   - Icon: CheckCircle
   - Actions available: View, Download, Delete

3. **Rejected** (Red)
   - Document does not meet requirements
   - Re-upload required
   - Icon: XCircle
   - Actions available: View, Download, Delete, Re-upload

#### Verification Process
1. User uploads document → Status: Pending
2. Authorized user (admin/dealer) reviews document
3. User clicks "View" to open document modal
4. User clicks "Verify" (green) or "Reject" (red)
5. Status updates immediately
6. Notification sent to uploader (via notifications system)
7. Deal status may auto-advance if all required documents verified

### 4. Document Viewing & Preview

#### In-Browser Preview
- **PDF files**: Full iframe preview with scroll
- **Image files**: Full-resolution display with zoom
- **Word docs**: Download only (no preview)

#### Document Modal Features
- Full-screen document preview
- Document metadata display
  - Document type
  - Upload date and time
  - Verification date and time (if verified)
  - Uploader name
  - Verifier name (if verified)
  - Status badge
  - Notes
- Action buttons
  - Download (opens in new tab)
  - Verify/Reject (for pending documents)
  - Close modal

### 5. Document Sharing

#### Email Sharing
- Share document links via email
- Include custom message
- Recipients receive:
  - Document type
  - Deal ID
  - Custom message
  - Instructions to access via platform

#### Sharing Workflow
1. User clicks share icon on document
2. Enter recipient email address
3. Add optional custom message
4. Click "Share"
5. System sends email with document details
6. Recipient can access via their account (if they have one)

### 6. Search & Filtering

#### Search Bar
- Search by document type name
- Search within notes field
- Real-time filtering as you type

#### Type Filter
- Filter by specific document type
- "All Types" option to show all
- Dropdown with all 6 document types

#### Status Filter
- Filter by verification status
- "All Statuses" option
- Options: Pending, Verified, Rejected

### 7. Permissions & Access Control

#### Role-Based Access
- **Buyers**: Can view documents for their own deals, upload documents
- **Dealers**: Can view/verify documents for their vehicles, upload documents
- **Brokers**: Can view documents for brokered deals, upload documents
- **Admins**: Full access to all documents, can verify/reject all

#### Document Actions by Role
| Action | Buyer | Dealer | Broker | Admin |
|--------|-------|--------|--------|-------|
| Upload | ✅ (own deals) | ✅ (own vehicles) | ✅ (own deals) | ✅ All |
| View | ✅ (own deals) | ✅ (own vehicles) | ✅ (own deals) | ✅ All |
| Download | ✅ (own deals) | ✅ (own vehicles) | ✅ (own deals) | ✅ All |
| Verify | ❌ | ✅ (own vehicles) | ❌ | ✅ All |
| Reject | ❌ | ✅ (own vehicles) | ❌ | ✅ All |
| Delete | ✅ (own uploads) | ✅ (own vehicles) | ✅ (own uploads) | ✅ All |
| Share | ✅ (own deals) | ✅ (own vehicles) | ✅ (own deals) | ✅ All |

### 8. Empty & Loading States

#### Loading State
- Grid of skeleton loaders (6 cards)
- Shimmer animation effect
- Displayed during initial fetch

#### Empty State
- Large FileText icon (16×16 in slate-300)
- "No Documents" heading
- Helpful message: "No documents found for this deal"
- "Upload First Document" button (if user has upload permission)

## Component Architecture

### Frontend Component: `Documents.tsx` (650+ lines)

```typescript
interface Document {
  id: number
  deal: number
  document_type: string
  file: string
  status: 'pending' | 'verified' | 'rejected'
  uploaded_by: number
  verified_by?: number
  notes: string
  uploaded_at: string
  verified_at?: string
}

interface DocumentsProps {
  dealId?: number
  showUpload?: boolean
}
```

**Main Components:**
1. **Documents** - Main page component with list, filters, search
2. **UploadModal** - Modal for uploading new documents
3. **ViewDocumentModal** - Modal for viewing and verifying documents

**State Management:**
- React Query for documents fetching with filters
- useMutation for upload, verify, delete operations
- Local state for modal open/close
- Local state for filters and search

**Key Functions:**
- `getStatusBadge()`: Returns colored status badge component
- `getStatusIcon()`: Returns appropriate Lucide icon for status
- `handleDelete()`: Confirms and deletes document
- `handleVerify()`: Updates document status to verified/rejected
- `filteredDocuments`: Computed array filtered by search term

### Sub-Components

#### UploadModal
- Form for uploading new documents
- Deal selection dropdown (if dealId not provided)
- Document type dropdown (6 options)
- File input with accept filter
- Notes textarea
- Submit with file upload via FormData
- Loading state during upload

#### ViewDocumentModal
- Full-screen document preview
- PDF: iframe embed
- Images: img tag with object-contain
- Document metadata display
- Verify/Reject buttons (for pending documents only)
- Download button (opens in new tab)
- Close button

## Backend API

### Database Model: `deals/models.py`

```python
class Document(models.Model):
    deal = ForeignKey(Deal, on_delete=CASCADE)
    document_type = CharField(max_length=20)  # title, id, payment_proof, export_permit, customs, other
    file = FileField(upload_to='documents/')
    status = CharField(max_length=20, default='pending')  # pending, verified, rejected
    uploaded_by = ForeignKey(User, related_name='uploaded_documents')
    verified_by = ForeignKey(User, related_name='verified_documents', null=True, blank=True)
    notes = TextField(blank=True)
    uploaded_at = DateTimeField(auto_now_add=True)
    verified_at = DateTimeField(null=True, blank=True)
```

**Indexes:**
- Ordering by `-uploaded_at` for most recent first

### API Endpoints

#### 1. List Documents
**Endpoint:** `GET /api/v1/deals/documents/`

**Query Parameters:**
- `deal` (int): Filter by deal ID
- `document_type` (string): Filter by document type
- `status` (string): Filter by status

**Response:**
```json
[
  {
    "id": 1,
    "deal": 123,
    "document_type": "title",
    "file": "/media/documents/vehicle_title_123.pdf",
    "status": "pending",
    "uploaded_by": 5,
    "verified_by": null,
    "notes": "Original vehicle title",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "verified_at": null
  }
]
```

#### 2. Get Document
**Endpoint:** `GET /api/v1/deals/documents/{id}/`

**Response:**
```json
{
  "id": 1,
  "deal": 123,
  "document_type": "title",
  "file": "/media/documents/vehicle_title_123.pdf",
  "status": "verified",
  "uploaded_by": 5,
  "verified_by": 2,
  "notes": "Original vehicle title",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "verified_at": "2024-01-15T14:20:00Z"
}
```

#### 3. Upload Document
**Endpoint:** `POST /api/v1/deals/documents/`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` (file): Document file
- `deal` (int): Deal ID
- `document_type` (string): Document type
- `notes` (string, optional): Additional notes

**Response:**
```json
{
  "id": 2,
  "deal": 123,
  "document_type": "payment_proof",
  "file": "/media/documents/payment_proof_456.pdf",
  "status": "pending",
  "uploaded_by": 5,
  "verified_by": null,
  "notes": "Wire transfer confirmation",
  "uploaded_at": "2024-01-15T11:00:00Z",
  "verified_at": null
}
```

#### 4. Verify/Update Document
**Endpoint:** `PATCH /api/v1/deals/documents/{id}/`

**Request Body:**
```json
{
  "status": "verified",
  "notes": "Document verified - looks good"
}
```

**Response:**
```json
{
  "id": 1,
  "deal": 123,
  "document_type": "title",
  "file": "/media/documents/vehicle_title_123.pdf",
  "status": "verified",
  "uploaded_by": 5,
  "verified_by": 2,
  "notes": "Document verified - looks good",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "verified_at": "2024-01-15T14:30:00Z"
}
```

#### 5. Delete Document
**Endpoint:** `DELETE /api/v1/deals/documents/{id}/`

**Response:** 204 No Content

#### 6. Share Document
**Endpoint:** `POST /api/v1/deals/documents/{id}/share/`

**Request Body:**
```json
{
  "email": "buyer@example.com",
  "message": "Please review this document for Deal #123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Document shared successfully"
}
```

### ViewSet: `DocumentViewSet`

**Permission Rules:**
- Authenticated users only
- Users can only access documents for deals they're involved in:
  - Buyers: Own deals
  - Dealers: Their vehicles
  - Brokers: Brokered deals
  - Admins: All documents

**Methods:**
- `get_queryset()`: Filters documents by user role
- `perform_create()`: Auto-sets `uploaded_by` to current user
- `share()`: Custom action to email document link

## Design System

### Color Palette
- **Pending**: Yellow (#F59E0B) with yellow-50 background
- **Verified**: Green (#10B981) with green-50 background
- **Rejected**: Red (#EF4444) with red-50 background

### Typography
- **Page title**: 2xl (24px), bold, slate-900
- **Document type**: base (16px), semibold, slate-900
- **Status badge**: xs (12px), medium, colored text
- **Notes**: sm (14px), regular, slate-600
- **Dates**: xs (12px), regular, slate-500

### Layout
- **Grid**: Responsive 1-3 columns (mobile → tablet → desktop)
- **Card size**: Auto height, min-height with padding
- **Card padding**: 24px (p-6)
- **Icon size**: 48px × 48px (w-12 h-12) for document icon
- **Status icon**: 20px × 20px (w-5 h-5)
- **Button icons**: 16px × 16px (w-4 h-4)

### Spacing
- **Section gap**: 24px (space-y-6)
- **Grid gap**: 16px (gap-4)
- **Button gap**: 8px (gap-2)
- **Filter grid**: 16px gap (gap-4)

### Animations
- **Card hover**: Shadow transition (hover:shadow-md transition-shadow)
- **Button hover**: Background color transitions
- **Skeleton loader**: Shimmer pulse animation

## Testing Checklist

### Unit Tests
- [ ] Documents component renders correctly
- [ ] Upload modal opens and closes
- [ ] View modal opens and closes with correct document
- [ ] Status badges display correct colors
- [ ] Status icons display correct icons
- [ ] Search filters documents correctly
- [ ] Type filter works correctly
- [ ] Status filter works correctly
- [ ] Delete confirmation dialog appears
- [ ] Upload mutation succeeds
- [ ] Verify mutation updates status
- [ ] Delete mutation removes document
- [ ] Empty state displays when no documents
- [ ] Loading state displays skeleton loaders

### API Tests
- [ ] List documents returns correct data
- [ ] Filter by deal works correctly
- [ ] Filter by document_type works correctly
- [ ] Filter by status works correctly
- [ ] Upload document creates new record
- [ ] Uploaded_by auto-set to current user
- [ ] Verify document updates status and verified_at
- [ ] Verified_by set to current user on verify
- [ ] Delete document removes from database
- [ ] Share document sends email
- [ ] Only authenticated users can access
- [ ] Users see only their related documents

### Integration Tests
- [ ] Upload document flow end-to-end
- [ ] Verify document workflow
- [ ] Reject document workflow
- [ ] Re-upload after rejection
- [ ] Download document opens in new tab
- [ ] PDF preview displays in iframe
- [ ] Image preview displays correctly
- [ ] Share document sends email with correct info
- [ ] Notifications created on status change
- [ ] Deal status updates when docs verified

### Browser Testing
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

### File Type Testing
- [ ] PDF upload and preview
- [ ] JPG upload and preview
- [ ] PNG upload and preview
- [ ] DOC upload (download only)
- [ ] DOCX upload (download only)
- [ ] File size validation (10MB limit)
- [ ] Invalid file type rejection

### Permission Testing
- [ ] Buyer can upload to own deals
- [ ] Buyer cannot verify documents
- [ ] Dealer can verify documents for own vehicles
- [ ] Dealer cannot verify documents for others
- [ ] Broker can view documents for brokered deals
- [ ] Admin can verify all documents
- [ ] Users cannot access others' documents

## Security Considerations

### File Upload Security
- **File type validation**: Server-side MIME type checking
- **File size limit**: 10MB maximum enforced server-side
- **Filename sanitization**: Remove special characters, prevent path traversal
- **Virus scanning**: (Future) Integrate ClamAV or similar
- **Storage isolation**: Files stored in secure media directory

### Access Control
- **Authentication required**: All endpoints require JWT
- **Role-based filtering**: Users only see their documents
- **Verification permissions**: Only dealers/admins can verify
- **File URL obfuscation**: Use secure signed URLs (future)

### Data Privacy
- **Document encryption at rest**: (Future) Encrypt files in storage
- **Secure file transfer**: HTTPS for all uploads/downloads
- **Access logging**: Track who accesses which documents
- **Retention policy**: Delete documents after deal completion + X days

### XSS Prevention
- **File content sanitization**: Strip executable content from uploads
- **PDF.js for preview**: Sandboxed PDF rendering
- **No inline execution**: Disable scripts in document previews

## Performance Optimization

### File Storage
- **Cloud storage**: Use S3 or Azure Blob for scalability
- **CDN integration**: Serve files via CDN for faster downloads
- **Thumbnail generation**: Create image thumbnails for faster preview
- **Lazy loading**: Load document previews on-demand

### Database
- **Indexes**: On `deal`, `document_type`, `status` fields
- **Pagination**: Limit documents per page (currently 50)
- **Caching**: Cache document metadata with Redis

### Frontend
- **React Query caching**: Cache documents list for 5 minutes
- **Lazy component loading**: Load modals only when opened
- **Image optimization**: Compress images before upload (future)
- **Progressive loading**: Show thumbnails, then full documents

## Future Enhancements

### Version Control
- Track document versions/revisions
- View document history
- Revert to previous version
- Compare versions side-by-side

### E-Signatures
- Integrate DocuSign or similar
- Request signatures within platform
- Track signature status
- Auto-update deal status on signed

### OCR & Data Extraction
- Extract data from scanned documents
- Auto-fill form fields from documents
- Validate document data against deal data
- Flag discrepancies for review

### Advanced Preview
- Word document preview (convert to PDF)
- Excel spreadsheet preview
- Multi-page document navigation
- Zoom controls for images
- Annotation tools (highlight, comment)

### Bulk Operations
- Upload multiple documents at once
- Download multiple documents as ZIP
- Bulk verify/reject
- Batch email sharing

### Document Templates
- Provide standard document templates
- Pre-filled forms with deal data
- Downloadable template library
- Custom template creation

### Audit Trail
- Complete document access log
- Who viewed, when, for how long
- Download tracking
- Change history with timestamps

### Compliance Features
- Digital signatures with blockchain verification
- Compliance checklist per document type
- Automatic expiration dates
- Required document reminders

## Deployment Notes

### Environment Variables
```env
MEDIA_ROOT=/path/to/media/files
MEDIA_URL=/media/
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
DEFAULT_FROM_EMAIL=noreply@nzilaexport.com
```

### File Storage Configuration
```python
# settings.py
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

### Nginx Configuration
```nginx
# Serve media files
location /media/ {
    alias /path/to/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Limit upload size
client_max_body_size 10M;
```

### Static Files
No additional static files required. Uses existing Lucide icons and Tailwind CSS.

### Dependencies
- **Frontend**: None (all existing dependencies)
- **Backend**: None (Django's FileField handles uploads)

### Database Migration
```bash
# Document model already exists in deals app
python manage.py makemigrations deals
python manage.py migrate deals
```

### Monitoring
- Track document upload success/failure rates
- Monitor file storage usage
- Alert on unusual upload patterns
- Track verification turnaround time

## Troubleshooting

### Upload Fails
1. Check file size (must be < 10MB)
2. Verify file type is allowed (PDF, JPG, PNG, DOC, DOCX)
3. Check disk space on server
4. Verify MEDIA_ROOT permissions (needs write access)
5. Check Nginx client_max_body_size setting

### Preview Not Working
1. PDF: Check iframe allow-same-origin setting
2. Images: Verify file path is accessible
3. Word docs: Download only, no preview available
4. Check browser console for CORS errors

### Permissions Issues
1. Verify user is authenticated
2. Check user role matches required permissions
3. Verify deal belongs to user
4. Check QuerySet filtering in DocumentViewSet

### Email Sharing Fails
1. Verify DEFAULT_FROM_EMAIL setting
2. Check email server configuration
3. Verify recipient email is valid
4. Check server email sending logs

## Related Documentation
- [API Documentation](API_DOCS.md)
- [Deals Feature](deals/README.md)
- [Notifications Feature](NOTIFICATIONS_FEATURE.md)
- [Security Guide](SECURITY.md)

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ Document upload with 6 document types
- ✅ Document viewing with PDF/image preview
- ✅ Verification workflow (pending → verified/rejected)
- ✅ Search and filtering (type, status, search term)
- ✅ Email sharing functionality
- ✅ Role-based access control
- ✅ Responsive grid layout (1-3 columns)
- ✅ Loading and empty states
- ✅ Bilingual support (EN/FR)

### Planned for Version 1.1.0
- Document version control
- E-signature integration (DocuSign)
- OCR and data extraction
- Advanced preview with annotations
- Bulk operations
- Document templates
