import React, { useEffect, useState } from 'react';
import { Car, ArrowRight } from 'lucide-react';
import api from '../lib/api';

interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  price_cad: string;
  condition: string;
  mileage: number;
  location: string;
  main_image: string | null;
}

interface SimilarVehicle {
  vehicle: Vehicle;
  similarity_score: number;
  reason: string;
}

interface SimilarVehiclesProps {
  referenceVehicleId: number;
  onVehicleClick: (vehicle: Vehicle) => void;
}

export const SimilarVehicles: React.FC<SimilarVehiclesProps> = ({
  referenceVehicleId,
  onVehicleClick,
}) => {
  const [similarVehicles, setSimilarVehicles] = useState<SimilarVehicle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSimilarVehicles = async () => {
      try {
        const response = await api.get(
          `/api/recommendations/similar/?vehicle_id=${referenceVehicleId}`
        );
        setSimilarVehicles(response.data.similar_vehicles || []);
      } catch (error) {
        console.error('Failed to fetch similar vehicles:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSimilarVehicles();
  }, [referenceVehicleId]);

  if (loading) {
    return (
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Similar Vehicles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse bg-gray-100 h-32 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (similarVehicles.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 pt-6 border-t border-gray-200">
      <h3 className="text-xl font-bold text-gray-900 mb-4">
        Similar Vehicles You Might Like
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {similarVehicles.slice(0, 4).map((item) => (
          <div
            key={item.vehicle.id}
            onClick={() => onVehicleClick(item.vehicle)}
            className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
          >
            <div className="flex gap-4 p-4">
              {/* Vehicle Image */}
              <div className="flex-shrink-0 w-24 h-24 bg-gray-100 rounded-lg overflow-hidden">
                {item.vehicle.main_image ? (
                  <img
                    src={item.vehicle.main_image}
                    alt={`${item.vehicle.year} ${item.vehicle.make} ${item.vehicle.model}`}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Car className="w-8 h-8 text-gray-400" />
                  </div>
                )}
              </div>

              {/* Vehicle Info */}
              <div className="flex-grow">
                <h4 className="font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                  {item.vehicle.year} {item.vehicle.make} {item.vehicle.model}
                </h4>
                <p className="text-sm text-gray-600 mb-2">
                  {item.vehicle.mileage.toLocaleString()} km • {item.vehicle.location}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-blue-600">
                    ${parseFloat(item.vehicle.price_cad).toLocaleString()}
                  </span>
                  <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            </div>

            {/* Similarity Reason */}
            <div className="px-4 pb-3">
              <div className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded inline-block">
                {item.reason}
              </div>
            </div>
          </div>
        ))}
      </div>

      {similarVehicles.length > 4 && (
        <div className="mt-4 text-center">
          <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
            View all {similarVehicles.length} similar vehicles →
          </button>
        </div>
      )}
    </div>
  );
};

// Track vehicle views for recommendation algorithm
export const trackVehicleView = async (vehicleId: number) => {
  try {
    await api.post('/api/recommendations/track-view/', {
      vehicle_id: vehicleId,
    });
  } catch (error) {
    console.error('Failed to track vehicle view:', error);
  }
};
