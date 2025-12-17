// Re-export everything from lib/api for backward compatibility
export * from '../lib/api';
export { api as default } from '../lib/api';

import { api } from '../lib/api';

// Extended API methods for Tier 1 features

/**
 * Reviews & Ratings API
 */
export const reviewsApi = {
  // Get reviews (with optional filters)
  getReviews: async (params?: {
    vehicle?: number;
    dealer?: number;
    rating?: number;
    search?: string;
    ordering?: string;
  }) => {
    const response = await api.get('/reviews/', { params });
    return response.data.results || response.data;
  },

  // Get featured reviews
  getFeaturedReviews: async () => {
    const response = await api.get('/reviews/featured/');
    return response.data.results || response.data;
  },

  // Create a review
  createReview: async (data: {
    vehicle: number;
    rating: number;
    title: string;
    comment: string;
    vehicle_condition_rating?: number;
    communication_rating?: number;
    delivery_rating?: number;
    value_rating?: number;
    would_recommend?: boolean;
  }) => {
    const response = await api.post('/reviews/', data);
    return response.data;
  },

  // Mark review as helpful/not helpful
  markHelpful: async (reviewId: number, helpful: boolean) => {
    const response = await api.post(`/reviews/${reviewId}/mark_helpful/`, {
      helpful,
    });
    return response.data;
  },

  // Dealer responds to review
  respondToReview: async (reviewId: number, response_text: string) => {
    const response = await api.post(`/reviews/${reviewId}/respond/`, {
      response_text,
    });
    return response.data;
  },

  // Get dealer ratings
  getDealerRatings: async (dealerId?: number) => {
    const url = dealerId ? `/dealer-ratings/${dealerId}/` : '/dealer-ratings/';
    const response = await api.get(url);
    return response.data;
  },
};

/**
 * Shipment Tracking API
 */
export const shipmentsApi = {
  // Get all shipments
  getShipments: async (params?: { status?: string; search?: string }) => {
    const response = await api.get('/shipments/', { params });
    return response.data.results || response.data;
  },

  // Track shipment by ID or tracking number
  trackShipment: async (identifier: string | number) => {
    const isNumeric = !isNaN(Number(identifier));
    const endpoint = isNumeric
      ? `/shipments/${identifier}/track/`
      : `/shipments/${identifier}/track/`;
    const response = await api.get(endpoint);
    return response.data;
  },

  // Get shipment milestones
  getMilestones: async (shipmentId: number) => {
    const response = await api.get(`/shipments/${shipmentId}/milestones/`);
    return response.data;
  },

  // Create a milestone
  createMilestone: async (shipmentId: number, data: {
    milestone_type: string;
    title?: string;
    description?: string;
    location?: string;
    latitude?: number;
    longitude?: number;
  }) => {
    const response = await api.post(`/shipments/${shipmentId}/milestones/`, data);
    return response.data;
  },

  // Update milestone
  updateMilestone: async (
    shipmentId: number,
    milestoneId: number,
    data: {
      is_completed?: boolean;
      completed_at?: string;
      notes?: string;
    }
  ) => {
    const response = await api.patch(
      `/shipments/${shipmentId}/milestones/${milestoneId}/`,
      data
    );
    return response.data;
  },

  // Update GPS location
  updateLocation: async (
    shipmentId: number,
    latitude: number,
    longitude: number
  ) => {
    const response = await api.post(`/shipments/${shipmentId}/update_location/`, {
      latitude,
      longitude,
    });
    return response.data;
  },

  // Get shipment photos
  getPhotos: async (shipmentId: number) => {
    const response = await api.get(`/shipments/${shipmentId}/photos/`);
    return response.data;
  },

  // Upload shipment photo
  uploadPhoto: async (shipmentId: number, photo: File, caption?: string) => {
    const formData = new FormData();
    formData.append('photo', photo);
    if (caption) formData.append('caption', caption);

    const response = await api.post(`/shipments/${shipmentId}/photos/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

/**
 * Video Walkarounds API
 */
export const videosApi = {
  // Get videos for a vehicle
  getVehicleVideos: async (vehicleId: number) => {
    const response = await api.get(`/vehicles/${vehicleId}/videos/`);
    return response.data;
  },

  // Upload video for vehicle
  uploadVideo: async (
    vehicleId: number,
    video: File,
    data: {
      caption?: string;
      media_type?: 'video';
      order?: number;
    }
  ) => {
    const formData = new FormData();
    formData.append('video', video);
    formData.append('media_type', data.media_type || 'video');
    if (data.caption) formData.append('caption', data.caption);
    if (data.order !== undefined) formData.append('order', data.order.toString());

    const response = await api.post(
      `/vehicles/${vehicleId}/upload_video/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Delete video/media
  deleteMedia: async (vehicleId: number, mediaId: number) => {
    await api.delete(`/vehicles/${vehicleId}/images/${mediaId}/`);
  },

  // Get vehicle with all media (images + videos)
  getVehicleMedia: async (vehicleId: number) => {
    const response = await api.get(`/vehicles/${vehicleId}/`);
    return response.data;
  },
};

// Re-export for convenience
export { api };
