import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Icon, LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface ShipmentMapProps {
  currentLatitude?: number;
  currentLongitude?: number;
  originPort?: string;
  destinationPort?: string;
  milestones?: Array<{
    latitude?: number;
    longitude?: number;
    location: string;
    completed_at: string | null;
  }>;
}

// Fix for default marker icon
delete (Icon.Default.prototype as any)._getIconUrl;
Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export const ShipmentMap: React.FC<ShipmentMapProps> = ({
  currentLatitude,
  currentLongitude,
  originPort,
  destinationPort,
  milestones = [],
}) => {
  const [mapCenter, setMapCenter] = useState<LatLngExpression>([0, 0]);
  const [mapZoom, setMapZoom] = useState(3);

  useEffect(() => {
    if (currentLatitude && currentLongitude) {
      setMapCenter([currentLatitude, currentLongitude]);
      setMapZoom(8);
    }
  }, [currentLatitude, currentLongitude]);

  // Create path from completed milestones
  const pathCoordinates: LatLngExpression[] = milestones
    .filter(m => m.completed_at && m.latitude && m.longitude)
    .map(m => [m.latitude!, m.longitude!] as LatLngExpression);

  // Add current location to path if available
  if (currentLatitude && currentLongitude) {
    pathCoordinates.push([currentLatitude, currentLongitude]);
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">Live Tracking</h2>
        {originPort && destinationPort && (
          <p className="text-sm text-gray-600 mt-1">
            {originPort} → {destinationPort}
          </p>
        )}
      </div>
      
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '500px', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Current Location Marker */}
        {currentLatitude && currentLongitude && (
          <Marker position={[currentLatitude, currentLongitude]}>
            <Popup>
              <div className="text-center">
                <p className="font-semibold">Current Location</p>
                <p className="text-sm text-gray-600">Last updated recently</p>
              </div>
            </Popup>
          </Marker>
        )}
        
        {/* Milestone Markers */}
        {milestones
          .filter(m => m.latitude && m.longitude && m.completed_at)
          .map((milestone, index) => (
            <Marker key={index} position={[milestone.latitude!, milestone.longitude!]}>
              <Popup>
                <div className="text-center">
                  <p className="font-semibold">{milestone.location}</p>
                  <p className="text-xs text-gray-600">{milestone.completed_at}</p>
                </div>
              </Popup>
            </Marker>
          ))}
        
        {/* Path Polyline */}
        {pathCoordinates.length > 1 && (
          <Polyline 
            positions={pathCoordinates}
            color="blue"
            weight={3}
            opacity={0.7}
          />
        )}
      </MapContainer>
      
      {!currentLatitude && !currentLongitude && (
        <div className="p-8 text-center text-gray-500">
          <p>GPS tracking not yet available for this shipment</p>
          <p className="text-sm mt-2">Check back later for live location updates</p>
        </div>
      )}
    </div>
  );
};
