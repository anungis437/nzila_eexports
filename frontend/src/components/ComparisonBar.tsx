import React from 'react';
import { useNavigate } from 'react-router-dom';
import { X, GitCompare } from 'lucide-react';
import { useComparison } from '../context/ComparisonContext';

const ComparisonBar: React.FC = () => {
  const { selectedVehicles, removeFromComparison, clearComparison } = useComparison();
  const navigate = useNavigate();

  if (selectedVehicles.length === 0) return null;

  const handleCompare = () => {
    navigate('/compare');
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-blue-600 shadow-lg z-40 animate-slide-up">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <GitCompare className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-gray-900">
              {selectedVehicles.length} {selectedVehicles.length === 1 ? 'vehicle' : 'vehicles'} selected
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex gap-2 max-w-md overflow-x-auto">
              {selectedVehicles.map((vehicle) => (
                <div
                  key={vehicle.id}
                  className="flex items-center gap-2 bg-gray-100 rounded-lg px-3 py-1.5 whitespace-nowrap"
                >
                  <span className="text-sm text-gray-700">
                    {vehicle.year} {vehicle.make} {vehicle.model}
                  </span>
                  <button
                    onClick={() => removeFromComparison(vehicle.id)}
                    className="text-gray-500 hover:text-red-600 transition-colors"
                    title="Remove"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            <div className="flex gap-2 border-l pl-4 ml-2">
              <button
                onClick={clearComparison}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
              >
                Clear All
              </button>
              <button
                onClick={handleCompare}
                disabled={selectedVehicles.length < 2}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium transition-colors flex items-center gap-2"
              >
                <GitCompare className="w-4 h-4" />
                Compare Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonBar;
