import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, GitCompare, ArrowLeft, Eye } from 'lucide-react';
import { useComparison } from '../context/ComparisonContext';
import VehicleDetailModal from '../components/VehicleDetailModal';
import { Vehicle } from '../types';

const Compare: React.FC = () => {
  const { selectedVehicles, removeFromComparison, clearComparison } = useComparison();
  const navigate = useNavigate();
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);

  if (selectedVehicles.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <GitCompare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Vehicles to Compare</h2>
          <p className="text-gray-600 mb-6">Select vehicles from the listing to compare their specs</p>
          <button
            onClick={() => navigate('/buyer-portal')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Browse Vehicles
          </button>
        </div>
      </div>
    );
  }

  const comparisonRows: Array<{
    label: string;
    key: string;
    format?: (val: any) => React.ReactNode;
  }> = [
    { label: 'Year', key: 'year' },
    { label: 'Make', key: 'make' },
    { label: 'Model', key: 'model' },
    { label: 'VIN', key: 'vin' },
    { label: 'Color', key: 'color' },
    { label: 'Mileage', key: 'mileage', format: (val: any) => `${val?.toLocaleString()} km` },
    { label: 'Transmission', key: 'transmission' },
    { label: 'Fuel Type', key: 'fuel_type' },
    { label: 'Condition', key: 'condition' },
    { label: 'Location', key: 'location' },
    { label: 'FOB Price (USD)', key: 'fob_price_usd', format: (val: any) => `$${val?.toLocaleString()}` },
    { label: 'CNF Price (USD)', key: 'cnf_price_usd', format: (val: any) => `$${val?.toLocaleString()}` },
    { label: 'Status', key: 'status', format: (val: any) => (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
        val === 'available' ? 'bg-green-100 text-green-800' :
        val === 'reserved' ? 'bg-yellow-100 text-yellow-800' :
        val === 'sold' ? 'bg-red-100 text-red-800' :
        'bg-gray-100 text-gray-800'
      }`}>
        {val}
      </span>
    )},
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Go back"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <GitCompare className="w-6 h-6 text-blue-600" />
                  Vehicle Comparison
                </h1>
                <p className="text-sm text-gray-600">Comparing {selectedVehicles.length} vehicles</p>
              </div>
            </div>
            <button
              onClick={() => {
                clearComparison();
                navigate('/buyer-portal');
              }}
              className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
            >
              Clear All
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="overflow-x-auto">
          <table className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 sticky left-0 bg-gray-50 z-10">
                  Specification
                </th>
                {selectedVehicles.map((vehicle) => (
                  <th key={vehicle.id} className="px-6 py-4 text-center min-w-[250px]">
                    <div className="space-y-3">
                      {vehicle.images && vehicle.images.length > 0 ? (
                        <img
                          src={vehicle.images[0].image}
                          alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                          className="w-full h-40 object-cover rounded-lg"
                        />
                      ) : (
                        <div className="w-full h-40 bg-gray-200 rounded-lg flex items-center justify-center">
                          <span className="text-gray-400">No Image</span>
                        </div>
                      )}
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {vehicle.year} {vehicle.make}
                        </h3>
                        <p className="text-sm text-gray-600">{vehicle.model}</p>
                      </div>
                      <div className="flex gap-2 justify-center">
                        <button
                          onClick={() => setSelectedVehicle(vehicle)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => removeFromComparison(vehicle.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Remove from comparison"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row, index) => (
                <tr
                  key={row.key}
                  className={`border-b border-gray-200 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                >
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 sticky left-0 bg-inherit z-10">
                    {row.label}
                  </td>
                  {selectedVehicles.map((vehicle) => {
                    const value = vehicle[row.key as keyof Vehicle];
                    const displayValue: React.ReactNode = row.format ? row.format(value as any) : (value?.toString() || 'N/A');
                    return (
                      <td
                        key={vehicle.id}
                        className="px-6 py-4 text-sm text-gray-700 text-center"
                      >
                        {displayValue}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex gap-4 justify-center">
          <button
            onClick={() => navigate('/buyer-portal')}
            className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Back to Listings
          </button>
          <button
            onClick={clearComparison}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            Clear Comparison
          </button>
        </div>
      </div>

      {selectedVehicle && (
        <VehicleDetailModal
          vehicle={selectedVehicle}
          onClose={() => setSelectedVehicle(null)}
          onEdit={() => {}}
        />
      )}
    </div>
  );
};

export default Compare;
