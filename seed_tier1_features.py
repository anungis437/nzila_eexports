"""
Seed data for Tier 1 features: Reviews, Shipment Tracking, and Video Walkarounds
"""
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from vehicles.models import Vehicle, VehicleImage
from deals.models import Deal
from shipments.models import Shipment
from reviews.models import Review, DealerRating
from shipments.tracking_models import ShipmentMilestone, ShipmentPhoto

User = get_user_model()

# Sample data
REVIEW_TITLES = [
    "Excellent Experience!",
    "Great Vehicle, Fast Delivery",
    "Highly Recommend This Dealer",
    "Vehicle as Described",
    "Smooth Transaction",
    "Good Communication",
    "Very Professional Service",
    "Happy with My Purchase",
    "Quick and Easy Process",
    "Outstanding Customer Service",
]

REVIEW_COMMENTS = [
    "The vehicle was exactly as described. Delivery was fast and the dealer was very responsive to all my questions.",
    "Great experience from start to finish. The dealer was professional and the vehicle is in excellent condition.",
    "Communication was excellent throughout the process. Vehicle arrived on time and in perfect condition.",
    "Very happy with my purchase. The dealer went above and beyond to ensure everything was perfect.",
    "The vehicle exceeded my expectations. Would definitely buy from this dealer again.",
    "Professional service and transparent communication. The shipment tracking was very helpful.",
    "Vehicle condition was exactly as shown in photos and videos. Very satisfied with the entire process.",
    "Dealer was very responsive and helpful. The vehicle is in great shape and I'm very happy.",
    "Smooth transaction with no surprises. The dealer was honest and professional throughout.",
    "Excellent value for money. The vehicle is running perfectly and looks great.",
]

LOCATIONS = [
    "Lagos, Nigeria",
    "Nairobi, Kenya",
    "Accra, Ghana",
    "Dar es Salaam, Tanzania",
    "Kampala, Uganda",
    "Addis Ababa, Ethiopia",
    "Kigali, Rwanda",
    "Lusaka, Zambia",
    "Harare, Zimbabwe",
    "Johannesburg, South Africa",
]

MILESTONE_DATA = {
    'pickup': {
        'locations': ['Vancouver, BC', 'Toronto, ON', 'Montreal, QC', 'Calgary, AB'],
        'descriptions': [
            'Vehicle picked up from dealer location',
            'Loaded and secured for transport',
            'Initial inspection completed',
        ]
    },
    'departed_origin': {
        'locations': ['En route to port', 'Highway 401', 'Trans-Canada Highway'],
        'descriptions': [
            'Vehicle departed from origin city',
            'En route to shipping port',
            'Transport carrier on schedule',
        ]
    },
    'in_transit': {
        'locations': ['Pacific Ocean', 'Atlantic Ocean', 'Mediterranean Sea'],
        'descriptions': [
            'Vehicle loaded on cargo ship',
            'Sailing across ocean',
            'On schedule for arrival',
        ]
    },
    'arrived_port': {
        'locations': ['Mombasa Port', 'Lagos Port', 'Dar es Salaam Port', 'Durban Port'],
        'descriptions': [
            'Vehicle arrived at destination port',
            'Unloading from cargo ship',
            'Ready for customs clearance',
        ]
    },
    'customs_clearance': {
        'locations': ['Customs Office', 'Port Authority'],
        'descriptions': [
            'Documentation submitted',
            'Customs inspection in progress',
            'Duties and taxes processed',
        ]
    },
    'out_for_delivery': {
        'locations': ['Final leg to destination', 'Local transport carrier'],
        'descriptions': [
            'Vehicle loaded for final delivery',
            'En route to buyer location',
            'Expected arrival within 24 hours',
        ]
    },
    'delivered': {
        'locations': LOCATIONS,
        'descriptions': [
            'Vehicle successfully delivered',
            'Buyer inspection completed',
            'Transaction completed',
        ]
    }
}

# GPS coordinates for realistic tracking
GPS_ROUTES = {
    'vancouver_to_mombasa': [
        (49.2827, -123.1207),  # Vancouver
        (48.4284, -123.3656),  # Victoria
        (20.0000, -150.0000),  # Pacific Ocean
        (-10.0000, 140.0000),  # Mid Pacific
        (-1.2921, 36.8219),    # Nairobi
        (-4.0435, 39.6682),    # Mombasa
    ],
    'toronto_to_lagos': [
        (43.6532, -79.3832),   # Toronto
        (45.5017, -73.5673),   # Montreal
        (40.7128, -74.0060),   # New York
        (25.7617, -80.1918),   # Miami
        (0.0000, -40.0000),    # Atlantic Ocean
        (6.5244, 3.3792),      # Lagos
    ],
}

def create_reviews():
    """Create sample reviews for vehicles with completed deals"""
    print("\n=== Creating Reviews ===")
    
    # Get buyers and dealers
    buyers = User.objects.filter(role='buyer')[:10]
    dealers = User.objects.filter(role='dealer')[:5]
    
    if not buyers.exists():
        print("❌ No buyers found. Please create buyers first.")
        return
    
    if not dealers.exists():
        print("❌ No dealers found. Please create dealers first.")
        return
    
    # Get vehicles
    vehicles = Vehicle.objects.filter(status__in=['sold', 'delivered'])[:20]
    
    if not vehicles.exists():
        print("❌ No sold/delivered vehicles found.")
        return
    
    reviews_created = 0
    
    for vehicle in vehicles:
        # Random chance to create a review (70%)
        if random.random() > 0.7:
            continue
        
        # Pick a random buyer
        buyer = random.choice(buyers)
        dealer = vehicle.dealer
        
        # Check if review already exists
        if Review.objects.filter(buyer=buyer, vehicle=vehicle).exists():
            continue
        
        # Create review
        rating = random.choices([5, 4, 3, 2, 1], weights=[50, 30, 15, 4, 1])[0]
        
        review = Review.objects.create(
            buyer=buyer,
            dealer=dealer,
            vehicle=vehicle,
            rating=rating,
            vehicle_condition_rating=random.randint(max(1, rating-1), min(5, rating+1)),
            communication_rating=random.randint(max(1, rating-1), min(5, rating+1)),
            delivery_rating=random.randint(max(1, rating-1), min(5, rating+1)),
            value_rating=random.randint(max(1, rating-1), min(5, rating+1)),
            title=random.choice(REVIEW_TITLES),
            comment=random.choice(REVIEW_COMMENTS),
            is_verified_purchase=True,
            is_approved=True,
            is_featured=(rating == 5 and random.random() > 0.7),
            buyer_location=random.choice(LOCATIONS),
            would_recommend=(rating >= 4),
            created_at=timezone.now() - timedelta(days=random.randint(1, 60))
        )
        
        # Random chance for dealer response (40%)
        if random.random() < 0.4:
            review.dealer_response = f"Thank you for your review! We're glad you're happy with your {vehicle.year} {vehicle.make} {vehicle.model}."
            review.responded_at = review.created_at + timedelta(hours=random.randint(1, 48))
            review.save()
        
        # Random helpfulness votes
        review.helpful_count = random.randint(0, 15)
        review.not_helpful_count = random.randint(0, 3)
        review.save()
        
        reviews_created += 1
        print(f"✅ Created review for {vehicle} by {buyer.email} ({rating} stars)")
    
    print(f"\n✅ Created {reviews_created} reviews")
    
    # Update dealer ratings
    print("\n=== Updating Dealer Ratings ===")
    for dealer in dealers:
        rating, created = DealerRating.objects.get_or_create(dealer=dealer)
        rating.update_stats()
        print(f"✅ Updated rating for {dealer.email}: {rating.average_rating:.2f} stars ({rating.total_reviews} reviews)")

def create_shipment_tracking():
    """Create shipment tracking data with GPS and milestones"""
    print("\n=== Creating Shipment Tracking Data ===")
    
    # Get recent shipments
    shipments = Shipment.objects.all()[:10]
    
    if not shipments.exists():
        print("❌ No shipments found. Please create shipments first.")
        return
    
    milestone_order = ['pickup', 'departed_origin', 'in_transit', 'arrived_port', 
                       'customs_clearance', 'out_for_delivery', 'delivered']
    
    for shipment in shipments:
        print(f"\n📦 Processing shipment: {shipment.tracking_number}")
        
        # Determine how many milestones are completed (random)
        completed_count = random.randint(2, 7)
        route = random.choice(list(GPS_ROUTES.values()))
        
        # Create milestones
        for i, milestone_type in enumerate(milestone_order):
            is_completed = i < completed_count
            milestone_info = MILESTONE_DATA[milestone_type]
            
            # GPS coordinates
            if i < len(route):
                lat, lng = route[i]
            else:
                lat, lng = route[-1]
            
            milestone = ShipmentMilestone.objects.create(
                shipment=shipment,
                milestone_type=milestone_type,
                title=milestone_type.replace('_', ' ').title(),
                description=random.choice(milestone_info['descriptions']),
                location=random.choice(milestone_info['locations']),
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lng)),
                is_completed=is_completed,
                completed_at=timezone.now() - timedelta(days=7-i) if is_completed else None,
                order=i
            )
            
            status = "✅" if is_completed else "⏳"
            print(f"  {status} {milestone.title} - {milestone.location}")
        
        # Set current GPS location to last completed milestone
        if completed_count > 0:
            last_milestone = ShipmentMilestone.objects.filter(
                shipment=shipment, 
                is_completed=True
            ).order_by('-order').first()
            
            if last_milestone:
                shipment.current_latitude = last_milestone.latitude
                shipment.current_longitude = last_milestone.longitude
                shipment.last_location_update = last_milestone.completed_at
                shipment.save()
                print(f"  📍 Current location: {last_milestone.location}")
        
        # Create some photos for completed milestones
        completed_milestones = ShipmentMilestone.objects.filter(
            shipment=shipment,
            is_completed=True
        )[:3]
        
        photo_types = ['loading', 'in_transit', 'arrival', 'customs', 'delivery']
        
        for milestone in completed_milestones:
            # 60% chance to add a photo
            if random.random() < 0.6:
                photo_type = random.choice(photo_types)
                
                # Note: In production, you would upload actual images
                # For now, we'll just create the database entries
                print(f"  📷 Photo placeholder: {photo_type} at {milestone.location}")
    
    print(f"\n✅ Created tracking data for {shipments.count()} shipments")

def create_video_walkarounds():
    """Create video walkaround entries for vehicles"""
    print("\n=== Creating Video Walkaround Entries ===")
    
    vehicles = Vehicle.objects.filter(status='available')[:10]
    
    if not vehicles.exists():
        print("❌ No available vehicles found.")
        return
    
    videos_created = 0
    
    for vehicle in vehicles:
        # Random chance to add video (50%)
        if random.random() > 0.5:
            continue
        
        # Create 1-2 video entries per vehicle
        num_videos = random.randint(1, 2)
        
        for i in range(num_videos):
            caption = random.choice([
                "360-degree exterior walkaround",
                "Interior features and condition",
                "Engine start and sound",
                "Test drive footage",
                "Close-up of special features",
            ])
            
            # Note: In production, you would upload actual video files
            # For now, we'll just create the database entries
            video_media = VehicleImage.objects.create(
                vehicle=vehicle,
                media_type='video',
                caption=caption,
                duration_seconds=random.randint(60, 300),
                order=vehicle.images.count()
            )
            
            videos_created += 1
            print(f"✅ Created video entry for {vehicle} - {caption}")
    
    print(f"\n✅ Created {videos_created} video entries")
    print("⚠️  Note: Video files are not uploaded. Upload real videos via API or admin.")

def main():
    print("=" * 60)
    print("TIER 1 FEATURES SEED DATA GENERATOR")
    print("=" * 60)
    
    # Create seed data
    create_reviews()
    create_shipment_tracking()
    create_video_walkarounds()
    
    print("\n" + "=" * 60)
    print("✅ SEED DATA GENERATION COMPLETE")
    print("=" * 60)
    
    # Summary
    print("\n📊 Summary:")
    print(f"  Reviews: {Review.objects.count()}")
    print(f"  Dealer Ratings: {DealerRating.objects.count()}")
    print(f"  Shipment Milestones: {ShipmentMilestone.objects.count()}")
    print(f"  Video Entries: {VehicleImage.objects.filter(media_type='video').count()}")
    
    print("\n🧪 Next Steps:")
    print("  1. Run the test script: python test_tier1_apis.py")
    print("  2. Start the server: python manage.py runserver")
    print("  3. Access the admin panel to view the data")
    print("  4. Test the frontend components")

if __name__ == '__main__':
    main()
