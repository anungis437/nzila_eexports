# Tier 1 Features Implementation Guide

## Overview

This document provides a comprehensive guide to the three high-impact Tier 1 features implemented for the Nzila Export Hub platform to enhance the buyer experience in the African vehicle export market.

**Implementation Date:** January 2025  
**Status:** Completed ✅

---

## Table of Contents

1. [Reviews & Ratings System](#reviews--ratings-system)
2. [Shipment Tracking](#shipment-tracking)
3. [Video Walkarounds](#video-walkarounds)
4. [Technical Architecture](#technical-architecture)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Frontend Components](#frontend-components)

---

## Reviews & Ratings System

### Purpose
Builds trust and credibility through social proof and dealer accountability. Enables buyers to share experiences and dealers to maintain reputation scores.

### Key Features

#### 1. Comprehensive Review Model
- **Overall Rating:** 1-5 stars
- **Detailed Sub-Ratings:**
  - Vehicle Condition (actual vs. listed)
  - Communication (responsiveness)
  - Delivery (timeliness)
  - Value (worth the price)
- **Verification:** Verified purchase badge for completed deals
- **Moderation:** Admin approval workflow
- **Featured Reviews:** Highlight exceptional experiences

#### 2. Engagement Features
- **Helpfulness Voting:** Buyers can mark reviews as helpful/not helpful
- **Dealer Responses:** Dealers can respond to reviews with transparency
- **Buyer Location:** Show where the buyer is from
- **Recommendation:** Would recommend dealer (yes/no)

#### 3. Dealer Rating Aggregates
- **Average Rating:** Cached overall score
- **Rating Distribution:** 5-star to 1-star breakdown
- **Category Averages:** Per sub-rating averages
- **Recommendation Rate:** Percentage who would recommend
- **Auto-Update:** Statistics refresh when reviews change

### Database Models

**Review Model:**
```python
- buyer: ForeignKey(User)
- dealer: ForeignKey(User, dealer role)
- vehicle: ForeignKey(Vehicle)
- rating: IntegerField(1-5)
- vehicle_condition_rating: IntegerField(1-5)
- communication_rating: IntegerField(1-5)
- delivery_rating: IntegerField(1-5)
- value_rating: IntegerField(1-5)
- title: CharField(max_length=200)
- comment: TextField
- is_verified_purchase: BooleanField
- is_approved: BooleanField (admin moderation)
- is_featured: BooleanField
- dealer_response: TextField (nullable)
- responded_at: DateTimeField (nullable)
- helpful_count: IntegerField
- not_helpful_count: IntegerField
- buyer_location: CharField (nullable)
- would_recommend: BooleanField
- Unique constraint: (buyer, vehicle)
```

**ReviewHelpfulness Model:**
```python
- review: ForeignKey(Review)
- user: ForeignKey(User)
- is_helpful: BooleanField
- Unique constraint: (review, user)
```

**DealerRating Model:**
```python
- dealer: OneToOneField(User)
- total_reviews: IntegerField
- average_rating: DecimalField
- five_star_count, four_star_count, ... one_star_count
- avg_vehicle_condition, avg_communication, avg_delivery, avg_value
- recommend_count: IntegerField
- recommend_percentage: DecimalField
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews/` | List all approved reviews |
| POST | `/api/reviews/` | Create new review |
| GET | `/api/reviews/{id}/` | Get review details |
| PATCH | `/api/reviews/{id}/` | Update review (owner only) |
| DELETE | `/api/reviews/{id}/` | Delete review (owner only) |
| POST | `/api/reviews/{id}/mark_helpful/` | Vote helpful/not helpful |
| POST | `/api/reviews/{id}/respond/` | Dealer response |
| GET | `/api/reviews/featured/` | Get featured reviews |
| GET | `/api/dealer-ratings/` | List dealer ratings |
| GET | `/api/dealer-ratings/{id}/` | Get dealer rating |
| POST | `/api/dealer-ratings/{id}/refresh/` | Refresh statistics |

**Query Parameters:**
- `dealer`: Filter by dealer ID
- `vehicle`: Filter by vehicle ID
- `rating`: Filter by rating (1-5)
- `is_approved`: Filter by approval status
- `search`: Search in title/comment
- `ordering`: Sort by created_at, rating, helpful_count

### Frontend Components

1. **RatingStars** (`components/reviews/RatingStars.tsx`)
   - Interactive star rating input
   - Configurable sizes (sm, md, lg)
   - Readonly mode for display
   - Hover states

2. **ReviewCard** (`components/reviews/ReviewCard.tsx`)
   - Display review with all details
   - Verified purchase badge
   - Featured review badge
   - Detailed ratings grid
   - Dealer response section
   - Helpfulness voting buttons
   - Dealer response form (dealers only)

3. **ReviewForm** (`components/reviews/ReviewForm.tsx`)
   - Multi-step review submission
   - Overall rating with large stars
   - Title and comment fields
   - Detailed ratings grid
   - Buyer location (optional)
   - Would recommend checkbox
   - Validation and error handling

4. **ReviewList** (`components/reviews/ReviewList.tsx`)
   - Summary stats card
   - Rating distribution bars
   - Filter controls (rating, sort)
   - Paginated review list
   - Empty state handling

### Use Cases

**Buyer Submits Review:**
1. Buyer completes a vehicle purchase
2. Accesses review form from deal history
3. Submits overall rating + detailed ratings + comment
4. Review enters moderation queue
5. Admin approves → appears on dealer/vehicle page
6. Dealer rating statistics auto-update

**Dealer Responds to Review:**
1. Dealer receives notification of new review
2. Views review on dashboard
3. Submits professional response
4. Response appears below review
5. Builds trust through transparency

---

## Shipment Tracking

### Purpose
Reduces buyer anxiety and support burden through real-time shipment visibility. Addresses the #1 question: "Where's my car?"

### Key Features

#### 1. GPS Tracking
- **Current Location:** Latitude/longitude coordinates
- **Last Updated:** Timestamp of last GPS ping
- **Map Visualization:** Interactive map with markers
- **Route History:** Polyline connecting completed locations

#### 2. Milestone System
7 standard milestones:
- **Pickup:** Vehicle collected from dealer
- **Departed Origin:** Left initial location
- **In Transit:** Actively moving
- **Arrived Port:** Reached port/border
- **Customs Clearance:** Undergoing customs processing
- **Out for Delivery:** Final leg to buyer
- **Delivered:** Received by buyer

Each milestone includes:
- Title and description
- Location name
- GPS coordinates
- Completion timestamp
- Order number for sequencing

#### 3. Photo Documentation
7 photo types:
- **Loading:** Vehicle being loaded
- **In Transit:** Photos during journey
- **Arrival:** Arriving at destination
- **Customs:** Customs documentation
- **Delivery:** Final delivery
- **Damage:** Any damage reports
- **Other:** Miscellaneous photos

Each photo includes:
- Image file
- Caption and description
- Location name + GPS coordinates
- Taken at timestamp
- Uploaded by user

### Database Models

**Shipment Model (Extended):**
```python
- current_latitude: DecimalField (max_digits=9, decimal_places=6)
- current_longitude: DecimalField (max_digits=9, decimal_places=6)
- last_location_update: DateTimeField (nullable)
```

**ShipmentMilestone Model:**
```python
- shipment: ForeignKey(Shipment)
- milestone_type: CharField(choices)
- title: CharField
- description: TextField
- location: CharField
- latitude/longitude: DecimalField (nullable)
- completed_at: DateTimeField (nullable)
- is_completed: BooleanField
- order: PositiveIntegerField
```

**ShipmentPhoto Model:**
```python
- shipment: ForeignKey(Shipment)
- photo: ImageField
- photo_type: CharField(choices)
- caption: CharField
- description: TextField
- location: CharField
- latitude/longitude: DecimalField (nullable)
- taken_at: DateTimeField
- uploaded_by: ForeignKey(User)
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/shipments/{id}/track/` | Get tracking details |
| POST | `/api/shipments/{id}/update_location/` | Update GPS coordinates |
| GET | `/api/shipments/{id}/milestones/` | List milestones |
| POST | `/api/shipments/{id}/milestones/` | Create milestone |
| PATCH | `/api/shipments/{id}/milestones/{milestone_id}/` | Update milestone |
| GET | `/api/shipments/{id}/photos/` | List photos |
| POST | `/api/shipments/{id}/photos/` | Upload photo |

**GPS Update Request:**
```json
{
  "latitude": 34.0522,
  "longitude": -118.2437
}
```

**Milestone Create Request:**
```json
{
  "milestone_type": "in_transit",
  "title": "En Route to Port",
  "description": "Vehicle is on the highway heading to the port",
  "location": "Highway 1, California",
  "latitude": 34.0522,
  "longitude": -118.2437
}
```

### Frontend Components

1. **ShipmentTimeline** (`components/tracking/ShipmentTimeline.tsx`)
   - Vertical timeline visualization
   - Milestone status indicators (completed=green, current=blue, pending=gray)
   - Location and timestamps
   - Responsive design

2. **ShipmentMap** (`components/tracking/ShipmentMap.tsx`)
   - Leaflet map integration
   - Current location marker (red)
   - Completed milestone markers (blue)
   - Polyline showing route
   - Popups with details
   - Auto-centering

3. **ShipmentPhotos** (`components/tracking/ShipmentPhotos.tsx`)
   - Gallery grouped by photo type
   - Grid layout (responsive)
   - Click to view full-size
   - Caption and location display
   - Timestamp formatting

4. **TrackingPage** (`pages/TrackingPage.tsx`)
   - Vehicle details header
   - Status badge with color coding
   - GPS active indicator
   - Tab navigation (Timeline, Map, Photos)
   - Loading and error states

### Use Cases

**Carrier Updates Location:**
1. Carrier's GPS system sends coordinates
2. API call to `/update_location/`
3. Timestamp recorded
4. Map updates with new position
5. Buyers see real-time movement

**Milestone Completion:**
1. Carrier marks milestone as completed
2. API call to `/milestones/{id}/`
3. `completed_at` timestamp set
4. Timeline UI updates
5. Next milestone becomes current
6. Buyer receives notification

**Photo Upload:**
1. Carrier takes photo at location
2. Uploads via mobile app or web
3. GPS coordinates auto-attached
4. Photo appears in gallery
5. Buyer can view documentation

---

## Video Walkarounds

### Purpose
Enables visual verification of vehicle condition before purchase. Reduces fraud concerns and post-purchase disputes in African market where buyers cannot physically inspect vehicles.

### Key Features

#### 1. Hybrid Media Model
- **Media Types:** Images and videos
- **File Organization:** Date-based directory structure
- **Video Fields:** Duration, thumbnail, caption
- **Validation:** 100MB file size limit

#### 2. Video Player
- **HTML5 Video:** Native playback
- **Custom Controls:** Play/pause, seek, volume, fullscreen
- **Progress Bar:** Visual timeline
- **Auto-hide Controls:** Clean viewing experience
- **Loading States:** Spinner during load
- **Error Handling:** Graceful failure messages

#### 3. Video Upload
- **Drag-and-Drop:** Intuitive file selection
- **Progress Tracking:** Real-time upload percentage
- **File Validation:** Type and size checks
- **Caption Field:** Add descriptions
- **Preview:** Review before upload
- **Guidelines:** Best practices for dealers

### Database Model

**VehicleImage Model (Extended to VehicleMedia):**
```python
- vehicle: ForeignKey(Vehicle)
- media_type: CharField(choices=['image', 'video'])
- image: ImageField (nullable, upload_to='vehicles/images/%Y/%m/%d/')
- video: FileField (nullable, upload_to='vehicles/videos/%Y/%m/%d/')
- thumbnail: ImageField (nullable, upload_to='vehicles/thumbnails/%Y/%m/%d/')
- duration_seconds: IntegerField (nullable)
- caption: CharField
- order: PositiveIntegerField
- Properties: is_video, media_url
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/vehicles/{id}/upload_video/` | Upload video walkaround |
| GET | `/api/vehicles/{id}/videos/` | List all videos for vehicle |
| DELETE | `/api/vehicles/{id}/images/{image_id}/` | Delete image or video |

**Video Upload Request (multipart/form-data):**
```
video: [File]
caption: "360 degree walkaround showing exterior condition"
media_type: "video"
```

**Video Upload Response:**
```json
{
  "id": 123,
  "media_type": "video",
  "video": "/media/vehicles/videos/2025/01/15/walkaround.mp4",
  "thumbnail": "/media/vehicles/thumbnails/2025/01/15/walkaround_thumb.jpg",
  "duration_seconds": 180,
  "caption": "360 degree walkaround showing exterior condition",
  "order": 0,
  "is_video": true,
  "media_url": "/media/vehicles/videos/2025/01/15/walkaround.mp4"
}
```

### Frontend Components

1. **VideoPlayer** (`components/video/VideoPlayer.tsx`)
   - HTML5 video element
   - Custom control bar
   - Play/pause/seek/volume controls
   - Fullscreen support
   - Time display (current / duration)
   - Loading spinner
   - Error handling
   - Title overlay
   - Auto-hide controls on play

2. **VideoUpload** (`components/video/VideoUpload.tsx`)
   - Drag-and-drop zone
   - File type validation
   - Size validation (100MB)
   - Preview player
   - Caption input
   - Upload progress bar
   - Success/error feedback
   - Guidelines display
   - Cancel functionality

3. **VideoGallery** (`components/video/VideoGallery.tsx`)
   - Grid of video thumbnails
   - Play icon overlay
   - Duration badge
   - Caption display
   - Modal video player
   - Empty state message

### Use Cases

**Dealer Uploads Video:**
1. Dealer records 360° walkaround
2. Opens vehicle edit form
3. Drags video into upload zone
4. Adds caption describing content
5. Clicks "Upload Video"
6. Progress bar shows upload
7. Video appears in vehicle listing

**Buyer Views Video:**
1. Buyer browses vehicle listing
2. Sees "Videos" tab with badge count
3. Clicks to view video gallery
4. Clicks thumbnail to play
5. Video opens in modal player
6. Full controls available
7. Closes modal when finished

---

## Technical Architecture

### Backend Stack
- **Framework:** Django 6.0 + Django REST Framework
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Storage:** File system (dev), S3/CloudFront (prod recommended)
- **Caching:** Django ORM cached aggregates
- **Validation:** Model-level + serializer-level

### Frontend Stack
- **Framework:** React + TypeScript
- **Mapping:** Leaflet + react-leaflet
- **Dates:** date-fns
- **Icons:** lucide-react
- **Styling:** Tailwind CSS

### File Organization
```
vehicles/
  images/%Y/%m/%d/
  videos/%Y/%m/%d/
  thumbnails/%Y/%m/%d/
shipments/
  photos/%Y/%m/%d/
```

### Performance Optimizations

1. **Database Indexes:**
   - Reviews: (dealer, is_approved), (vehicle, is_approved)
   - Milestones: (shipment, order), (shipment, is_completed)
   - Photos: (shipment, -created_at)

2. **Query Optimization:**
   - `select_related()` for foreign keys
   - `prefetch_related()` for reverse relationships
   - Cached dealer rating aggregates

3. **File Handling:**
   - Date-based upload paths for organization
   - File size validation before upload
   - Thumbnail generation for videos (future)

---

## Database Schema

### Reviews Schema
```sql
CREATE TABLE reviews_review (
    id INTEGER PRIMARY KEY,
    buyer_id INTEGER REFERENCES auth_user(id),
    dealer_id INTEGER REFERENCES auth_user(id),
    vehicle_id INTEGER REFERENCES vehicles_vehicle(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    vehicle_condition_rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    communication_rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    delivery_rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    value_rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    comment TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    dealer_response TEXT NULL,
    responded_at TIMESTAMP NULL,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    buyer_location VARCHAR(100) NULL,
    would_recommend BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(buyer_id, vehicle_id)
);

CREATE INDEX idx_reviews_dealer_approved ON reviews_review(dealer_id, is_approved);
CREATE INDEX idx_reviews_vehicle_approved ON reviews_review(vehicle_id, is_approved);
```

### Shipment Tracking Schema
```sql
-- Shipment table extensions
ALTER TABLE shipments_shipment ADD COLUMN current_latitude DECIMAL(9,6) NULL;
ALTER TABLE shipments_shipment ADD COLUMN current_longitude DECIMAL(9,6) NULL;
ALTER TABLE shipments_shipment ADD COLUMN last_location_update TIMESTAMP NULL;

CREATE TABLE shipments_shipmentmilestone (
    id INTEGER PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments_shipment(id),
    milestone_type VARCHAR(50),
    title VARCHAR(200),
    description TEXT,
    location VARCHAR(200),
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    completed_at TIMESTAMP NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    "order" INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_milestone_shipment_order ON shipments_shipmentmilestone(shipment_id, "order");
CREATE INDEX idx_milestone_shipment_completed ON shipments_shipmentmilestone(shipment_id, is_completed);

CREATE TABLE shipments_shipmentphoto (
    id INTEGER PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments_shipment(id),
    photo VARCHAR(255),
    photo_type VARCHAR(50),
    caption VARCHAR(200),
    description TEXT,
    location VARCHAR(200),
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    taken_at TIMESTAMP,
    uploaded_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP
);

CREATE INDEX idx_photo_shipment_created ON shipments_shipmentphoto(shipment_id, created_at DESC);
```

### Video Schema
```sql
-- VehicleImage table modifications
ALTER TABLE vehicles_vehicleimage ADD COLUMN media_type VARCHAR(10) DEFAULT 'image';
ALTER TABLE vehicles_vehicleimage ADD COLUMN video VARCHAR(255) NULL;
ALTER TABLE vehicles_vehicleimage ADD COLUMN thumbnail VARCHAR(255) NULL;
ALTER TABLE vehicles_vehicleimage ADD COLUMN duration_seconds INTEGER NULL;
ALTER TABLE vehicles_vehicleimage MODIFY image VARCHAR(255) NULL;
```

---

## Getting Started

### Running Migrations
```bash
python manage.py migrate reviews
python manage.py migrate shipments
python manage.py migrate vehicles
```

### Testing API Endpoints
```bash
# Create a review
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": 1,
    "rating": 5,
    "vehicle_condition_rating": 5,
    "communication_rating": 4,
    "delivery_rating": 5,
    "value_rating": 5,
    "title": "Excellent Experience!",
    "comment": "Vehicle was exactly as described. Fast delivery.",
    "would_recommend": true
  }'

# Update shipment location
curl -X POST http://localhost:8000/api/shipments/1/update_location/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 34.0522,
    "longitude": -118.2437
  }'

# Upload video
curl -X POST http://localhost:8000/api/vehicles/1/upload_video/ \
  -H "Authorization: Bearer <token>" \
  -F "video=@walkaround.mp4" \
  -F "caption=360 degree walkaround" \
  -F "media_type=video"
```

### Frontend Integration
```tsx
// Reviews
import { ReviewList, ReviewForm, RatingStars } from '@/components/reviews';

<ReviewList dealerId={dealer.id} />
<ReviewForm vehicleId={vehicle.id} onSuccess={handleSuccess} />
<RatingStars value={4.5} readonly />

// Tracking
import { ShipmentTimeline, ShipmentMap, ShipmentPhotos } from '@/components/tracking';

<ShipmentTimeline milestones={shipment.milestones} />
<ShipmentMap shipment={shipment} />
<ShipmentPhotos photos={shipment.photos} />

// Videos
import { VideoPlayer, VideoUpload, VideoGallery } from '@/components/video';

<VideoGallery videos={vehicle.videos} />
<VideoUpload vehicleId={vehicle.id} onSuccess={handleRefresh} />
<VideoPlayer videoUrl={video.video} thumbnail={video.thumbnail} />
```

---

## Next Steps

### Phase 1: Testing & Refinement (1-2 weeks)
- [ ] Create comprehensive test suite
- [ ] Load testing with realistic data
- [ ] User acceptance testing
- [ ] Bug fixes and polish

### Phase 2: Production Deployment (1 week)
- [ ] Configure production file storage (S3 + CloudFront)
- [ ] Set up video transcoding pipeline
- [ ] Configure CDN for video delivery
- [ ] Database optimization
- [ ] Monitoring and alerts

### Phase 3: Feature Enhancements (Ongoing)
- [ ] Video transcoding (multiple quality levels)
- [ ] Review moderation dashboard
- [ ] GPS tracking mobile app
- [ ] Email notifications for milestones
- [ ] Review analytics dashboard
- [ ] Video thumbnails auto-generation

---

## Support & Troubleshooting

### Common Issues

**Reviews not appearing:**
- Check `is_approved` field (admin must approve)
- Verify unique constraint (one review per buyer per vehicle)
- Check user permissions

**GPS not updating:**
- Verify latitude/longitude validation (-90 to 90, -180 to 180)
- Check `last_location_update` timestamp
- Ensure proper authentication

**Video upload failing:**
- Check file size (max 100MB)
- Verify video format (MP4 recommended)
- Check storage permissions
- Review network timeout settings

### Performance Tips

1. **Database Optimization:**
   - Run `ANALYZE` regularly
   - Monitor slow queries
   - Add indexes as needed

2. **File Storage:**
   - Use CDN for video delivery
   - Enable CloudFront caching
   - Consider video compression

3. **API Optimization:**
   - Implement pagination
   - Use query parameter filtering
   - Cache dealer rating statistics

---

## Conclusion

The Tier 1 features provide a comprehensive trust-building framework for the African vehicle export market:

- **Reviews** build credibility through social proof
- **Tracking** reduces anxiety through transparency
- **Videos** prevent fraud through visual verification

Together, these features address the top buyer concerns and create a competitive advantage in the marketplace.

**Estimated Impact:**
- 30-40% reduction in "where's my car?" support tickets
- 20-25% increase in buyer confidence scores
- 15-20% decrease in post-purchase disputes
- Improved dealer accountability and reputation

**Total Development Time:** 8-10 weeks (Reviews: 2-3 weeks, Tracking: 3-4 weeks, Videos: 3-4 weeks)

For detailed guides on each feature, see:
- [Review System Guide](./REVIEW_SYSTEM_GUIDE.md)
- [Shipment Tracking Guide](./SHIPMENT_TRACKING_GUIDE.md)
- [Video Walkaround Guide](./VIDEO_WALKAROUND_GUIDE.md)
- [API Reference](./TIER1_API_REFERENCE.md)
