import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, CheckCircle } from 'lucide-react';
import { RatingStars } from './RatingStars';
import { format } from 'date-fns';
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

interface ReviewCardProps {
  review: Review;
  onResponseSubmit?: () => void;
}

export const ReviewCard: React.FC<ReviewCardProps> = ({ review, onResponseSubmit }) => {
  const [showResponseForm, setShowResponseForm] = useState(false);
  const [response, setResponse] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [userVote, setUserVote] = useState<boolean | null>(review.user_found_helpful ?? null);

  const handleMarkHelpful = async (isHelpful: boolean) => {
    try {
      await api.post(`/api/reviews/${review.id}/mark_helpful/`, { is_helpful: isHelpful });
      setUserVote(isHelpful);
    } catch (error) {
      console.error('Error marking review helpful:', error);
    }
  };

  const handleSubmitResponse = async () => {
    if (!response.trim()) return;

    setSubmitting(true);
    try {
      await api.post(`/api/reviews/${review.id}/respond/`, { dealer_response: response });
      setShowResponseForm(false);
      setResponse('');
      if (onResponseSubmit) onResponseSubmit();
    } catch (error) {
      console.error('Error submitting response:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <RatingStars rating={review.rating} readonly size="md" />
            {review.is_verified_purchase && (
              <span className="flex items-center gap-1 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                Verified Purchase
              </span>
            )}
            {review.is_featured && (
              <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                Featured
              </span>
            )}
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{review.title}</h3>
          <p className="text-sm text-gray-600">
            by {review.buyer_name} {review.buyer_location_display && `from ${review.buyer_location_display}`} 
            {' '} • {format(new Date(review.created_at), 'MMM d, yyyy')}
          </p>
        </div>
      </div>

      {/* Vehicle Info */}
      {review.vehicle_info && (
        <div className="flex items-center gap-3 mb-4 p-3 bg-gray-50 rounded">
          {review.vehicle_info.main_image && (
            <img 
              src={review.vehicle_info.main_image} 
              alt={`${review.vehicle_info.make} ${review.vehicle_info.model}`}
              className="w-16 h-16 object-cover rounded"
            />
          )}
          <div>
            <p className="font-medium text-gray-900">
              {review.vehicle_info.year} {review.vehicle_info.make} {review.vehicle_info.model}
            </p>
          </div>
        </div>
      )}

      {/* Review Comment */}
      <p className="text-gray-700 mb-4 whitespace-pre-wrap">{review.comment}</p>

      {/* Detailed Ratings */}
      {(review.vehicle_condition_rating || review.communication_rating || 
        review.delivery_rating || review.value_rating) && (
        <div className="grid grid-cols-2 gap-4 mb-4 p-4 bg-gray-50 rounded">
          {review.vehicle_condition_rating && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Vehicle Condition</p>
              <RatingStars rating={review.vehicle_condition_rating} readonly size="sm" />
            </div>
          )}
          {review.communication_rating && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Communication</p>
              <RatingStars rating={review.communication_rating} readonly size="sm" />
            </div>
          )}
          {review.delivery_rating && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Delivery</p>
              <RatingStars rating={review.delivery_rating} readonly size="sm" />
            </div>
          )}
          {review.value_rating && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Value</p>
              <RatingStars rating={review.value_rating} readonly size="sm" />
            </div>
          )}
        </div>
      )}

      {/* Would Recommend */}
      {review.would_recommend && (
        <p className="text-green-600 font-medium mb-4">
          ✓ Would recommend this {review.review_type === 'vehicle' ? 'vehicle' : 'dealer'}
        </p>
      )}

      {/* Dealer Response */}
      {review.dealer_response && (
        <div className="mt-4 p-4 bg-blue-50 rounded border-l-4 border-blue-500">
          <p className="text-sm font-medium text-blue-900 mb-1">
            Response from {review.dealer_name}
          </p>
          <p className="text-sm text-gray-700 mb-1">{review.dealer_response}</p>
          {review.responded_at && (
            <p className="text-xs text-gray-500">
              {format(new Date(review.responded_at), 'MMM d, yyyy')}
            </p>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center gap-4">
          {review.can_mark_helpful && (
            <>
              <button
                onClick={() => handleMarkHelpful(true)}
                className={`flex items-center gap-1 text-sm ${
                  userVote === true ? 'text-green-600' : 'text-gray-600 hover:text-green-600'
                }`}
                disabled={userVote !== null}
              >
                <ThumbsUp className="w-4 h-4" />
                Helpful ({review.helpful_count})
              </button>
              <button
                onClick={() => handleMarkHelpful(false)}
                className={`flex items-center gap-1 text-sm ${
                  userVote === false ? 'text-red-600' : 'text-gray-600 hover:text-red-600'
                }`}
                disabled={userVote !== null}
              >
                <ThumbsDown className="w-4 h-4" />
                Not Helpful ({review.not_helpful_count})
              </button>
            </>
          )}
        </div>

        {review.can_respond && !review.dealer_response && (
          <button
            onClick={() => setShowResponseForm(!showResponseForm)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showResponseForm ? 'Cancel' : 'Respond'}
          </button>
        )}
      </div>

      {/* Response Form */}
      {showResponseForm && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <textarea
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Write your response..."
            className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={() => setShowResponseForm(false)}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitResponse}
              disabled={submitting || !response.trim()}
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Response'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
