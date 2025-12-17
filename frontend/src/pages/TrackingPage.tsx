import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ShipmentTimeline } from '../components/tracking/ShipmentTimeline';
import { ShipmentMap } from '../components/tracking/ShipmentMap';
import { ShipmentPhotos } from '../components/tracking/ShipmentPhotos';
import { shipmentsApi } from '../services/api';
import { Package, Calendar, MapPin, Truck } from 'lucide-react';
import { format } from 'date-fns';

interface Shipment {
  id: number;
  tracking_number: string;
  shipping_company: string;
  status: string;
  origin_port: string;
  destination_port: string;
  destination_country: string;
  estimated_departure: string | null;
  actual_departure: string | null;
  estimated_arrival: string | null;
  actual_arrival: string | null;
  current_latitude?: number;
  current_longitude?: number;
  last_location_update?: string;
  has_gps_tracking: boolean;
  milestones: any[];
  photos: any[];
  vehicle_details: {
    year: number;
    make: string;
    model: string;
    vin: string;
    color: string;
  };
}

export const TrackingPage: React.FC = () => {
  const { trackingNumber } = useParams<{ trackingNumber: string }>();
  const [shipment, setShipment] = useState<Shipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'timeline' | 'map' | 'photos'>('timeline');

  useEffect(() => {
    fetchShipment();
  }, [trackingNumber]);

  const fetchShipment = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await shipmentsApi.trackShipment(trackingNumber!);
      setShipment(data);
    } catch (err) {
      setError('Failed to load shipment tracking information');
      console.error('Error fetching shipment:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_transit: 'bg-blue-100 text-blue-800',
      customs: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      delayed: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status: string) => {
    if (status === 'delivered') return '✅';
    if (status === 'in_transit') return '🚢';
    if (status === 'customs') return '📋';
    if (status === 'delayed') return '⚠️';
    return '📦';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !shipment) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 text-lg">{error || 'Shipment not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Track Your Shipment
            </h1>
            <p className="text-lg text-gray-600">
              {shipment.vehicle_details.year} {shipment.vehicle_details.make} {shipment.vehicle_details.model}
            </p>
          </div>
          <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(shipment.status)}`}>
            {getStatusIcon(shipment.status)} {shipment.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="flex items-start gap-3">
            <Package className="w-5 h-5 text-gray-600 mt-1" />
            <div>
              <p className="text-sm text-gray-600">Tracking Number</p>
              <p className="font-semibold text-gray-900">{shipment.tracking_number}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Truck className="w-5 h-5 text-gray-600 mt-1" />
            <div>
              <p className="text-sm text-gray-600">Carrier</p>
              <p className="font-semibold text-gray-900">{shipment.shipping_company}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <MapPin className="w-5 h-5 text-gray-600 mt-1" />
            <div>
              <p className="text-sm text-gray-600">Route</p>
              <p className="font-semibold text-gray-900">
                {shipment.origin_port} → {shipment.destination_port}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-gray-600 mt-1" />
            <div>
              <p className="text-sm text-gray-600">Est. Arrival</p>
              <p className="font-semibold text-gray-900">
                {shipment.estimated_arrival
                  ? format(new Date(shipment.estimated_arrival), 'MMM d, yyyy')
                  : 'TBD'}
              </p>
            </div>
          </div>
        </div>

        {shipment.has_gps_tracking && shipment.last_location_update && (
          <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
            <p className="text-sm text-blue-800">
              🔵 Live GPS tracking active • Last updated: {format(new Date(shipment.last_location_update), 'MMM d, HH:mm')}
            </p>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('timeline')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'timeline'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Timeline
            </button>
            <button
              onClick={() => setActiveTab('map')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'map'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Map View
            </button>
            <button
              onClick={() => setActiveTab('photos')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'photos'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Photos ({shipment.photos.length})
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'timeline' && <ShipmentTimeline milestones={shipment.milestones} />}
      {activeTab === 'map' && (
        <ShipmentMap
          currentLatitude={shipment.current_latitude}
          currentLongitude={shipment.current_longitude}
          originPort={shipment.origin_port}
          destinationPort={shipment.destination_port}
          milestones={shipment.milestones}
        />
      )}
      {activeTab === 'photos' && <ShipmentPhotos photos={shipment.photos} />}
    </div>
  );
};
