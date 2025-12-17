import React from 'react';
import { Vehicle } from '../types';
import { useComparison } from '../context/ComparisonContext';

interface ComparisonCheckboxProps {
  vehicle: Vehicle;
}

const ComparisonCheckbox: React.FC<ComparisonCheckboxProps> = ({ vehicle }) => {
  const { isInComparison, addToComparison, removeFromComparison, selectedVehicles, maxVehicles } = useComparison();
  const isChecked = isInComparison(vehicle.id);
  const isDisabled = !isChecked && selectedVehicles.length >= maxVehicles;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    if (e.target.checked) {
      addToComparison(vehicle);
    } else {
      removeFromComparison(vehicle.id);
    }
  };

  return (
    <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
      <input
        type="checkbox"
        checked={isChecked}
        onChange={handleChange}
        disabled={isDisabled}
        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        title={isDisabled ? `Maximum ${maxVehicles} vehicles for comparison` : 'Compare this vehicle'}
      />
      <span className="text-sm text-gray-600">Compare</span>
    </div>
  );
};

export default ComparisonCheckbox;
