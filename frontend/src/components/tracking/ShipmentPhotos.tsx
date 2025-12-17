import React from 'react';
import { format } from 'date-fns';
import { Download, ExternalLink } from 'lucide-react';

interface ShipmentPhoto {
  id: number;
  photo: string;
  photo_type: string;
  photo_type_display: string;
  caption: string;
  description: string;
  location: string;
  taken_at: string;
  uploaded_by_name?: string;
}

interface ShipmentPhotosProps {
  photos: ShipmentPhoto[];
}

export const ShipmentPhotos: React.FC<ShipmentPhotosProps> = ({ photos }) => {
  const photosByType = photos.reduce((acc, photo) => {
    if (!acc[photo.photo_type]) {
      acc[photo.photo_type] = [];
    }
    acc[photo.photo_type].push(photo);
    return acc;
  }, {} as Record<string, ShipmentPhoto[]>);

  if (photos.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-600">No photos available yet</p>
        <p className="text-sm text-gray-500 mt-2">
          Photos will be added as your shipment progresses
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Shipment Photos</h2>
      
      {Object.entries(photosByType).map(([type, typePhotos]) => (
        <div key={type} className="mb-8 last:mb-0">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            {typePhotos[0].photo_type_display}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {typePhotos.map((photo) => (
              <div key={photo.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-video bg-gray-100">
                  <img
                    src={photo.photo}
                    alt={photo.caption || photo.photo_type_display}
                    className="w-full h-full object-cover cursor-pointer"
                    onClick={() => window.open(photo.photo, '_blank')}
                  />
                </div>
                
                <div className="p-3">
                  {photo.caption && (
                    <p className="font-medium text-gray-900 mb-1">{photo.caption}</p>
                  )}
                  
                  {photo.description && (
                    <p className="text-sm text-gray-600 mb-2">{photo.description}</p>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div>
                      {photo.location && <p>📍 {photo.location}</p>}
                      {photo.taken_at && (
                        <p>{format(new Date(photo.taken_at), 'MMM d, yyyy')}</p>
                      )}
                    </div>
                    
                    <a
                      href={photo.photo}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-700"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
