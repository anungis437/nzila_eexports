import React, { useState } from 'react';
import { RatingStars } from './RatingStars';
import { api } from '../../services/api';

interface ReviewFormProps {
  vehicleId?: number;
  dealerId: number;
  reviewType: 'vehicle' | 'dealer';
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ReviewForm: React.FC<ReviewFormProps> = ({
  vehicleId,
  dealerId,
  reviewType,
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    rating: 0,
    title: '',
    comment: '',
    vehicle_condition_rating: 0,
    communication_rating: 0,
    delivery_rating: 0,
    value_rating: 0,
    buyer_location: '',
    would_recommend: true,
  });

  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.rating === 0) {
      setErrors({ rating: 'Please select a rating' });
      return;
    }

    if (!formData.title.trim() || !formData.comment.trim()) {
      setErrors({
        title: !formData.title.trim() ? 'Title is required' : '',
        comment: !formData.comment.trim() ? 'Review is required' : '',
      });
      return;
    }

    setSubmitting(true);
    setErrors({});

    try {
      await api.post('/api/reviews/', {
        ...formData,
        vehicle: vehicleId,
        dealer: dealerId,
        review_type: reviewType,
      });

      if (onSuccess) onSuccess();
    } catch (error: any) {
      setErrors(error.response?.data || { general: 'Failed to submit review' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Write a Review
      </h2>

      {errors.general && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {errors.general}
        </div>
      )}

      {/* Overall Rating */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Overall Rating *
        </label>
        <RatingStars
          rating={formData.rating}
          onRatingChange={(rating) => setFormData({ ...formData, rating })}
          size="lg"
        />
        {errors.rating && <p className="text-red-500 text-sm mt-1">{errors.rating}</p>}
      </div>

      {/* Title */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Review Title *
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="e.g., Excellent service and great car!"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
      </div>

      {/* Comment */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Review *
        </label>
        <textarea
          value={formData.comment}
          onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
          placeholder="Share details about your experience..."
          rows={6}
          className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.comment && <p className="text-red-500 text-sm mt-1">{errors.comment}</p>}
      </div>

      {/* Detailed Ratings */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Ratings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reviewType === 'vehicle' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vehicle Condition
              </label>
              <RatingStars
                rating={formData.vehicle_condition_rating}
                onRatingChange={(rating) =>
                  setFormData({ ...formData, vehicle_condition_rating: rating })
                }
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Communication
            </label>
            <RatingStars
              rating={formData.communication_rating}
              onRatingChange={(rating) =>
                setFormData({ ...formData, communication_rating: rating })
              }
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Delivery Experience
            </label>
            <RatingStars
              rating={formData.delivery_rating}
              onRatingChange={(rating) =>
                setFormData({ ...formData, delivery_rating: rating })
              }
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Value for Money
            </label>
            <RatingStars
              rating={formData.value_rating}
              onRatingChange={(rating) =>
                setFormData({ ...formData, value_rating: rating })
              }
            />
          </div>
        </div>
      </div>

      {/* Location */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Location (Optional)
        </label>
        <input
          type="text"
          value={formData.buyer_location}
          onChange={(e) => setFormData({ ...formData, buyer_location: e.target.value })}
          placeholder="e.g., Lagos, Nigeria"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Would Recommend */}
      <div className="mb-6">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={formData.would_recommend}
            onChange={(e) =>
              setFormData({ ...formData, would_recommend: e.target.checked })
            }
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-medium text-gray-700">
            I would recommend this {reviewType === 'vehicle' ? 'vehicle' : 'dealer'}
          </span>
        </label>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-6 py-3 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="flex-1 px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Submitting...' : 'Submit Review'}
        </button>
      </div>
    </form>
  );
};
