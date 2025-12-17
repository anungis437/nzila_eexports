from django.test import TestCase
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from deals.models import Deal
from .models import Review, ReviewHelpfulness, DealerRating

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            password='test123',
            full_name='Test Buyer'
        )
        self.dealer = User.objects.create_user(
            email='dealer@test.com',
            password='test123',
            full_name='Test Dealer',
            user_type='dealer'
        )
        self.vehicle = Vehicle.objects.create(
            dealer=self.dealer,
            make='Toyota',
            model='Camry',
            year=2020,
            price=25000,
            condition='used_excellent'
        )
    
    def test_create_review(self):
        review = Review.objects.create(
            buyer=self.buyer,
            dealer=self.dealer,
            vehicle=self.vehicle,
            review_type='vehicle',
            rating=5,
            title='Excellent car!',
            comment='Very satisfied with the purchase.',
            is_verified_purchase=True
        )
        
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.buyer, self.buyer)
        self.assertEqual(review.dealer, self.dealer)
        self.assertTrue(review.is_verified_purchase)
    
    def test_unique_review_constraint(self):
        Review.objects.create(
            buyer=self.buyer,
            dealer=self.dealer,
            vehicle=self.vehicle,
            review_type='vehicle',
            rating=5,
            title='Test',
            comment='Test'
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):
            Review.objects.create(
                buyer=self.buyer,
                dealer=self.dealer,
                vehicle=self.vehicle,
                review_type='vehicle',
                rating=4,
                title='Another review',
                comment='Duplicate'
            )
    
    def test_average_detailed_rating(self):
        review = Review.objects.create(
            buyer=self.buyer,
            dealer=self.dealer,
            vehicle=self.vehicle,
            review_type='vehicle',
            rating=5,
            title='Test',
            comment='Test',
            vehicle_condition_rating=5,
            communication_rating=4,
            delivery_rating=5,
            value_rating=4
        )
        
        # Average = (5 + 4 + 5 + 4) / 4 = 4.5
        self.assertEqual(review.average_detailed_rating, 4.5)


class ReviewHelpfulnessTest(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            password='test123'
        )
        self.dealer = User.objects.create_user(
            email='dealer@test.com',
            password='test123',
            user_type='dealer'
        )
        self.voter = User.objects.create_user(
            email='voter@test.com',
            password='test123'
        )
        self.review = Review.objects.create(
            buyer=self.buyer,
            dealer=self.dealer,
            review_type='dealer',
            rating=5,
            title='Test',
            comment='Test'
        )
    
    def test_mark_helpful(self):
        vote = ReviewHelpfulness.objects.create(
            review=self.review,
            user=self.voter,
            is_helpful=True
        )
        
        self.assertTrue(vote.is_helpful)
        self.assertEqual(vote.review, self.review)
    
    def test_unique_vote_constraint(self):
        ReviewHelpfulness.objects.create(
            review=self.review,
            user=self.voter,
            is_helpful=True
        )
        
        # Try to vote again
        with self.assertRaises(Exception):
            ReviewHelpfulness.objects.create(
                review=self.review,
                user=self.voter,
                is_helpful=False
            )


class DealerRatingTest(TestCase):
    def setUp(self):
        self.dealer = User.objects.create_user(
            email='dealer@test.com',
            password='test123',
            user_type='dealer'
        )
        self.buyer1 = User.objects.create_user(
            email='buyer1@test.com',
            password='test123'
        )
        self.buyer2 = User.objects.create_user(
            email='buyer2@test.com',
            password='test123'
        )
    
    def test_dealer_rating_creation(self):
        rating = DealerRating.objects.create(dealer=self.dealer)
        self.assertEqual(rating.total_reviews, 0)
        self.assertEqual(rating.average_rating, 0)
    
    def test_update_stats(self):
        # Create reviews
        Review.objects.create(
            buyer=self.buyer1,
            dealer=self.dealer,
            review_type='dealer',
            rating=5,
            title='Great!',
            comment='Excellent service',
            is_approved=True,
            would_recommend=True
        )
        Review.objects.create(
            buyer=self.buyer2,
            dealer=self.dealer,
            review_type='dealer',
            rating=4,
            title='Good',
            comment='Good experience',
            is_approved=True,
            would_recommend=True
        )
        
        # Update stats
        rating = DealerRating.objects.create(dealer=self.dealer)
        rating.update_stats()
        
        self.assertEqual(rating.total_reviews, 2)
        self.assertEqual(rating.average_rating, 4.5)
        self.assertEqual(rating.five_star_count, 1)
        self.assertEqual(rating.four_star_count, 1)
        self.assertEqual(rating.recommend_count, 2)
        self.assertEqual(rating.recommend_percentage, 100.0)
