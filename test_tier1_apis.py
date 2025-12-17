"""
API Testing Script for Tier 1 Features
Tests Reviews, Shipment Tracking, and Video Walkaround endpoints
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print('=' * 60)

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test an API endpoint"""
    url = f"{API_BASE}{endpoint}"
    
    print(f"\n{Colors.BLUE}Testing:{Colors.END} {method} {endpoint}")
    if description:
        print(f"  Description: {description}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PATCH":
            response = requests.patch(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print_error(f"Unsupported method: {method}")
            return None
        
        # Check status code
        if response.status_code == expected_status:
            print_success(f"Status: {response.status_code}")
        else:
            print_error(f"Expected {expected_status}, got {response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            if method == "GET" and isinstance(response_data, dict):
                if 'results' in response_data:
                    print_info(f"Results: {len(response_data['results'])} items")
                    if response_data['results']:
                        print(f"  Sample: {json.dumps(response_data['results'][0], indent=2)[:200]}...")
                elif 'count' in response_data:
                    print_info(f"Count: {response_data['count']}")
                else:
                    print(f"  Response: {json.dumps(response_data, indent=2)[:200]}...")
            else:
                print(f"  Response: {json.dumps(response_data, indent=2)[:200]}...")
            
            return response_data
        except:
            if response.text:
                print(f"  Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error("Connection failed. Is the server running?")
        print_info("Start the server with: python manage.py runserver")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_reviews_api():
    """Test Reviews & Ratings API endpoints"""
    print_section("REVIEWS & RATINGS API TESTS")
    
    # 1. List all reviews
    test_endpoint(
        "GET", "/reviews/",
        description="Get all approved reviews"
    )
    
    # 2. Filter reviews by rating
    test_endpoint(
        "GET", "/reviews/?rating=5",
        description="Get 5-star reviews only"
    )
    
    # 3. Search reviews
    test_endpoint(
        "GET", "/reviews/?search=excellent",
        description="Search reviews containing 'excellent'"
    )
    
    # 4. Get featured reviews
    test_endpoint(
        "GET", "/reviews/featured/",
        description="Get featured reviews"
    )
    
    # 5. Order by rating
    test_endpoint(
        "GET", "/reviews/?ordering=-rating",
        description="Get reviews ordered by rating (highest first)"
    )
    
    # 6. Order by helpful count
    test_endpoint(
        "GET", "/reviews/?ordering=-helpful_count",
        description="Get most helpful reviews"
    )
    
    # 7. Get dealer ratings
    test_endpoint(
        "GET", "/dealer-ratings/",
        description="Get all dealer ratings"
    )

def test_shipment_tracking_api():
    """Test Shipment Tracking API endpoints"""
    print_section("SHIPMENT TRACKING API TESTS")
    
    # Get a shipment first
    response = test_endpoint(
        "GET", "/shipments/",
        description="Get all shipments"
    )
    
    if response and 'results' in response and len(response['results']) > 0:
        shipment = response['results'][0]
        shipment_id = shipment['id']
        tracking_number = shipment.get('tracking_number')
        
        print_info(f"Using shipment ID: {shipment_id}")
        
        # Test tracking page
        if tracking_number:
            test_endpoint(
                "GET", f"/shipments/{tracking_number}/track/",
                description="Get shipment tracking details by tracking number"
            )
        
        # Test milestones
        test_endpoint(
            "GET", f"/shipments/{shipment_id}/milestones/",
            description="Get shipment milestones"
        )
        
        # Test photos
        test_endpoint(
            "GET", f"/shipments/{shipment_id}/photos/",
            description="Get shipment photos"
        )
        
        # Note: POST endpoints require authentication
        print_info("\nPOST/PATCH endpoints require authentication:")
        print_info("  - POST /shipments/{id}/update_location/")
        print_info("  - POST /shipments/{id}/milestones/")
        print_info("  - PATCH /shipments/{id}/milestones/{milestone_id}/")
        print_info("  - POST /shipments/{id}/photos/")
    else:
        print_error("No shipments found to test")

def test_video_api():
    """Test Video Walkaround API endpoints"""
    print_section("VIDEO WALKAROUND API TESTS")
    
    # Get a vehicle first
    response = test_endpoint(
        "GET", "/vehicles/",
        description="Get all vehicles"
    )
    
    if response and 'results' in response and len(response['results']) > 0:
        vehicle = response['results'][0]
        vehicle_id = vehicle['id']
        
        print_info(f"Using vehicle ID: {vehicle_id}")
        
        # Test videos endpoint
        test_endpoint(
            "GET", f"/vehicles/{vehicle_id}/videos/",
            description="Get all videos for vehicle"
        )
        
        # Note: POST endpoints require authentication
        print_info("\nPOST endpoints require authentication:")
        print_info("  - POST /vehicles/{id}/upload_video/")
        print_info("  - DELETE /vehicles/{id}/images/{image_id}/")
    else:
        print_error("No vehicles found to test")

def test_integration():
    """Test integrated scenarios"""
    print_section("INTEGRATION TESTS")
    
    # Scenario 1: Get vehicle with reviews
    print("\n📝 Scenario 1: Vehicle with Reviews")
    vehicles_response = test_endpoint(
        "GET", "/vehicles/?limit=1",
        description="Get a vehicle"
    )
    
    if vehicles_response and 'results' in vehicles_response and vehicles_response['results']:
        vehicle_id = vehicles_response['results'][0]['id']
        
        test_endpoint(
            "GET", f"/reviews/?vehicle={vehicle_id}",
            description=f"Get reviews for vehicle {vehicle_id}"
        )
    
    # Scenario 2: Dealer rating with reviews
    print("\n⭐ Scenario 2: Dealer Rating Statistics")
    dealers_response = test_endpoint(
        "GET", "/dealer-ratings/?limit=1",
        description="Get a dealer rating"
    )
    
    if dealers_response and 'results' in dealers_response and dealers_response['results']:
        dealer_rating = dealers_response['results'][0]
        print_info("Dealer Statistics:")
        print(f"  Total Reviews: {dealer_rating.get('total_reviews')}")
        print(f"  Average Rating: {dealer_rating.get('average_rating')}")
        print(f"  5-Star: {dealer_rating.get('five_star_count')}")
        print(f"  4-Star: {dealer_rating.get('four_star_count')}")
        print(f"  3-Star: {dealer_rating.get('three_star_count')}")
        print(f"  2-Star: {dealer_rating.get('two_star_count')}")
        print(f"  1-Star: {dealer_rating.get('one_star_count')}")
        print(f"  Recommend %: {dealer_rating.get('recommend_percentage')}")
    
    # Scenario 3: Shipment with GPS tracking
    print("\n📍 Scenario 3: Active Shipment Tracking")
    shipments_response = test_endpoint(
        "GET", "/shipments/?limit=5",
        description="Get shipments"
    )
    
    if shipments_response and 'results' in shipments_response:
        for shipment in shipments_response['results']:
            if shipment.get('has_gps_tracking'):
                print_info(f"Shipment {shipment.get('tracking_number')} has GPS tracking")
                print(f"  Location: ({shipment.get('current_latitude')}, {shipment.get('current_longitude')})")
                print(f"  Last Update: {shipment.get('last_location_update')}")
                break

def print_summary():
    """Print summary and next steps"""
    print_section("SUMMARY & NEXT STEPS")
    
    print("\n✅ API Testing Complete!")
    print("\n📋 Test Coverage:")
    print("  ✓ Reviews & Ratings API")
    print("  ✓ Shipment Tracking API")
    print("  ✓ Video Walkaround API")
    print("  ✓ Integration Scenarios")
    
    print("\n🔐 Authentication Required for:")
    print("  • Creating/updating reviews")
    print("  • Marking reviews helpful")
    print("  • Dealer responses")
    print("  • Updating GPS location")
    print("  • Creating milestones")
    print("  • Uploading photos")
    print("  • Uploading videos")
    
    print("\n📚 Documentation:")
    print("  • Full API Reference: docs/TIER1_FEATURES_IMPLEMENTATION.md")
    print("  • Review System: docs/REVIEW_SYSTEM_GUIDE.md")
    print("  • Shipment Tracking: docs/SHIPMENT_TRACKING_GUIDE.md")
    print("  • Video Walkarounds: docs/VIDEO_WALKAROUND_GUIDE.md")
    
    print("\n🚀 Frontend Integration:")
    print("  • Import components from @/components/reviews")
    print("  • Import components from @/components/tracking")
    print("  • Import components from @/components/video")
    
    print("\n💡 Tips:")
    print("  • Use the admin panel for manual testing")
    print("  • Check the seed data script for sample data")
    print("  • Enable CORS for frontend testing")
    print("  • Use proper authentication tokens for POST/PATCH/DELETE")

def main():
    print("=" * 60)
    print("TIER 1 FEATURES API TEST SUITE")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if server is running
    print("\n🔍 Checking server status...")
    try:
        response = requests.get(BASE_URL)
        print_success(f"Server is running (Status: {response.status_code})")
    except:
        print_error("Server is not running!")
        print_info("Start the server with: python manage.py runserver")
        return
    
    # Run tests
    try:
        test_reviews_api()
        test_shipment_tracking_api()
        test_video_api()
        test_integration()
        print_summary()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
