import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Vehicle } from '../types';

interface ComparisonContextType {
  selectedVehicles: Vehicle[];
  addToComparison: (vehicle: Vehicle) => void;
  removeFromComparison: (vehicleId: number) => void;
  clearComparison: () => void;
  isInComparison: (vehicleId: number) => boolean;
  maxVehicles: number;
}

const ComparisonContext = createContext<ComparisonContextType | undefined>(undefined);

export const useComparison = () => {
  const context = useContext(ComparisonContext);
  if (!context) {
    throw new Error('useComparison must be used within ComparisonProvider');
  }
  return context;
};

interface ComparisonProviderProps {
  children: ReactNode;
}

export const ComparisonProvider: React.FC<ComparisonProviderProps> = ({ children }) => {
  const [selectedVehicles, setSelectedVehicles] = useState<Vehicle[]>([]);
  const maxVehicles = 4;

  const addToComparison = (vehicle: Vehicle) => {
    if (selectedVehicles.length >= maxVehicles) {
      alert(`You can only compare up to ${maxVehicles} vehicles at once.`);
      return;
    }
    if (!selectedVehicles.find(v => v.id === vehicle.id)) {
      setSelectedVehicles([...selectedVehicles, vehicle]);
    }
  };

  const removeFromComparison = (vehicleId: number) => {
    setSelectedVehicles(selectedVehicles.filter(v => v.id !== vehicleId));
  };

  const clearComparison = () => {
    setSelectedVehicles([]);
  };

  const isInComparison = (vehicleId: number) => {
    return selectedVehicles.some(v => v.id === vehicleId);
  };

  return (
    <ComparisonContext.Provider
      value={{
        selectedVehicles,
        addToComparison,
        removeFromComparison,
        clearComparison,
        isInComparison,
        maxVehicles,
      }}
    >
      {children}
    </ComparisonContext.Provider>
  );
};
