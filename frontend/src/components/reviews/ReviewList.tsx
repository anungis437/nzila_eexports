import React, { useState, useEffect } from 'react';
import { ReviewCard } from './ReviewCard';
import { RatingStars } from './RatingStars';
import { api } from '../../services/api';

interface Review {
  id: number;
  buyer_name: string;
  buyer_location_display: string;
  dealer_name: string;
  vehicle_info?: {
    id: number;
    make: string;
    model: string;
    year: number;
    main_image: string;
  };
  review_type: 'vehicle' | 'dealer';
  rating: number;
  title: string;
  comment: string;
  vehicle_condition_rating?: number;
  communication_rating?: number;
  delivery_rating?: number;
  value_rating?: number;
  would_recommend: boolean;
  is_verified_purchase: boolean;
  is_featured: boolean;
  dealer_response?: string;
  responded_at?: string;
  helpful_count: number;
  not_helpful_count: number;
  helpfulness_ratio: number;
  average_detailed_rating: number;
  created_at: string;
  can_respond: boolean;
  can_mark_helpful: boolean;
  user_found_helpful?: boolean | null;
}

interface ReviewListProps {
  vehicleId?: number;
  dealerId?: number;
  showFilters?: boolean;
}

export const ReviewList: React.FC<ReviewListProps> = ({
  vehicleId,
  dealerId,
  showFilters = true,
}) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    rating: '',
    sortBy: 'created_at',
  });

  useEffect(() => {
    fetchReviews();
  }, [vehicleId, dealerId, filters]);

  const fetchReviews = async () => {
    setLoading(true);
    setError(null);

    try {
      const params: Record<string, any> = {
        ordering: filters.sortBy === 'helpful' ? '-helpful_count' : '-created_at',
      };

      if (vehicleId) params.vehicle = vehicleId;
      if (dealerId) params.dealer = dealerId;
      if (filters.rating) params.rating = filters.rating;

      const response = await api.get('/api/reviews/', { params });
      setReviews(response.data.results || response.data);
    } catch (err) {
      setError('Failed to load reviews');
      console.error('Error fetching reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateRatingDistribution = () => {
    const distribution: Record<number, number> = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
    reviews.forEach((review) => {
      distribution[review.rating] = (distribution[review.rating] || 0) + 1;
    });
    return distribution;
  };

  const averageRating =
    reviews.length > 0
      ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length
      : 0;

  const ratingDistribution = calculateRatingDistribution();

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      {reviews.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-start gap-6">
            <div className="text-center">
              <div className="text-5xl font-bold text-gray-900 mb-2">
                {averageRating.toFixed(1)}
              </div>
              <RatingStars rating={averageRating} readonly size="lg" />
              <p className="text-sm text-gray-600 mt-2">
                Based on {reviews.length} {reviews.length === 1 ? 'review' : 'reviews'}
              </p>
            </div>

            <div className="flex-1">
              <h3 className="font-medium text-gray-900 mb-3">Rating Distribution</h3>
              {[5, 4, 3, 2, 1].map((rating) => {
                const count = ratingDistribution[rating] || 0;
                const percentage = reviews.length > 0 ? (count / reviews.length) * 100 : 0;
                return (
                  <div key={rating} className="flex items-center gap-2 mb-2">
                    <span className="text-sm text-gray-600 w-8">{rating}★</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-yellow-400 h-2 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      {showFilters && reviews.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Rating
              </label>
              <select
                value={filters.rating}
                onChange={(e) => setFilters({ ...filters, rating: e.target.value })}
                className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Ratings</option>
                <option value="5">5 Stars</option>
                <option value="4">4 Stars</option>
                <option value="3">3 Stars</option>
                <option value="2">2 Stars</option>
                <option value="1">1 Star</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                className="p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Most Recent</option>
                <option value="helpful">Most Helpful</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Reviews */}
      {reviews.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-600 text-lg">No reviews yet</p>
          <p className="text-gray-500 text-sm mt-2">
            Be the first to share your experience!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <ReviewCard key={review.id} review={review} onResponseSubmit={fetchReviews} />
          ))}
        </div>
      )}
    </div>
  );
};
