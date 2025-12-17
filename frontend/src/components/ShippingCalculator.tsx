import { useState } from 'react';
import { Ship, Package, AlertCircle } from 'lucide-react';

interface ShippingCalculatorProps {
  vehicleYear?: number;
  vehicleMake?: string;
  vehicleModel?: string;
}

interface ShippingDestination {
  code: string;
  name: string;
  port: string;
  region: string;
  baseRate: number; // Base shipping cost in CAD
}

const DESTINATIONS: ShippingDestination[] = [
  // West Africa
  { code: 'SN', name: 'Senegal', port: 'Dakar', region: 'West Africa', baseRate: 2500 },
  { code: 'CI', name: 'Côte d\'Ivoire', port: 'Abidjan', region: 'West Africa', baseRate: 2600 },
  { code: 'NG', name: 'Nigeria', port: 'Lagos', region: 'West Africa', baseRate: 2700 },
  { code: 'GH', name: 'Ghana', port: 'Tema', region: 'West Africa', baseRate: 2650 },
  { code: 'BJ', name: 'Benin', port: 'Cotonou', region: 'West Africa', baseRate: 2700 },
  { code: 'TG', name: 'Togo', port: 'Lomé', region: 'West Africa', baseRate: 2650 },
  
  // Central Africa
  { code: 'CM', name: 'Cameroon', port: 'Douala', region: 'Central Africa', baseRate: 2800 },
  { code: 'CD', name: 'DR Congo', port: 'Matadi', region: 'Central Africa', baseRate: 2900 },
  { code: 'CG', name: 'Congo', port: 'Pointe-Noire', region: 'Central Africa', baseRate: 2850 },
  
  // East Africa
  { code: 'KE', name: 'Kenya', port: 'Mombasa', region: 'East Africa', baseRate: 3200 },
  { code: 'TZ', name: 'Tanzania', port: 'Dar es Salaam', region: 'East Africa', baseRate: 3300 },
  { code: 'UG', name: 'Uganda', port: 'Mombasa (Kenya)', region: 'East Africa', baseRate: 3400 },
  
  // Southern Africa
  { code: 'ZA', name: 'South Africa', port: 'Durban', region: 'Southern Africa', baseRate: 3500 },
];

const VEHICLE_SIZE_MULTIPLIERS = {
  sedan: { name: 'Sedan/Compact', multiplier: 1.0 },
  suv: { name: 'SUV/Crossover', multiplier: 1.3 },
  truck: { name: 'Pickup Truck', multiplier: 1.4 },
  van: { name: 'Van/Minivan', multiplier: 1.35 },
  luxury: { name: 'Luxury/Large', multiplier: 1.5 },
};

export default function ShippingCalculator({ vehicleYear, vehicleMake, vehicleModel }: ShippingCalculatorProps) {
  const [destination, setDestination] = useState('');
  const [vehicleSize, setVehicleSize] = useState<keyof typeof VEHICLE_SIZE_MULTIPLIERS>('sedan');
  const [calculated, setCalculated] = useState(false);

  const handleCalculate = () => {
    if (destination) {
      setCalculated(true);
    }
  };

  const getShippingCost = () => {
    if (!destination) return null;

    const dest = DESTINATIONS.find(d => d.code === destination);
    if (!dest) return null;

    const sizeMultiplier = VEHICLE_SIZE_MULTIPLIERS[vehicleSize].multiplier;
    const oceanFreight = Math.round(dest.baseRate * sizeMultiplier);
    const insurance = Math.round(oceanFreight * 0.15);
    const portFees = 500;
    const customsClearance = 800;
    const total = oceanFreight + insurance + portFees + customsClearance;

    return {
      destination: dest,
      oceanFreight,
      insurance,
      portFees,
      customsClearance,
      total,
    };
  };

  const cost = calculated ? getShippingCost() : null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Ship className="h-4 w-4" />
          Shipping Calculator
        </h3>
      </div>

      {vehicleMake && (
        <div className="text-xs text-gray-600 bg-gray-50 rounded-lg p-2">
          Vehicle: {vehicleYear} {vehicleMake} {vehicleModel}
        </div>
      )}

      <div className="space-y-4">
        {/* Destination Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Destination Port</label>
          <select
            value={destination}
            onChange={(e) => {
              setDestination(e.target.value);
              setCalculated(false);
            }}
            aria-label="Select destination port"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select destination...</option>
            {Object.entries(
              DESTINATIONS.reduce((acc, dest) => {
                if (!acc[dest.region]) acc[dest.region] = [];
                acc[dest.region].push(dest);
                return acc;
              }, {} as Record<string, ShippingDestination[]>)
            ).map(([region, destinations]) => (
              <optgroup key={region} label={region}>
                {destinations.map((dest) => (
                  <option key={dest.code} value={dest.code}>
                    {dest.name} ({dest.port})
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* Vehicle Size Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Vehicle Type</label>
          <select
            value={vehicleSize}
            onChange={(e) => {
              setVehicleSize(e.target.value as keyof typeof VEHICLE_SIZE_MULTIPLIERS);
              setCalculated(false);
            }}
            aria-label="Select vehicle type"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.entries(VEHICLE_SIZE_MULTIPLIERS).map(([key, { name }]) => (
              <option key={key} value={key}>
                {name}
              </option>
            ))}
          </select>
        </div>

        {/* Calculate Button */}
        <button
          onClick={handleCalculate}
          disabled={!destination}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition text-sm font-medium"
        >
          Calculate Shipping Cost
        </button>

        {/* Results */}
        {cost && (
          <div className="space-y-3 pt-3 border-t border-gray-200">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-900">
              <Package className="h-4 w-4" />
              Estimated Shipping Costs to {cost.destination.name}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Ocean Freight ({cost.destination.port})</span>
                <span className="font-medium">${cost.oceanFreight.toLocaleString()} CAD</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Marine Insurance</span>
                <span className="font-medium">${cost.insurance.toLocaleString()} CAD</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Port Handling Fees</span>
                <span className="font-medium">${cost.portFees.toLocaleString()} CAD</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Customs Clearance</span>
                <span className="font-medium">${cost.customsClearance.toLocaleString()} CAD</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-gray-200 text-base font-bold">
                <span className="text-gray-900">Total Estimated Cost</span>
                <span className="text-blue-600">${cost.total.toLocaleString()} CAD</span>
              </div>
            </div>

            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <div>
                <strong>Important:</strong> This is an estimate only. Actual costs may vary based on current 
                fuel surcharges, seasonal rates, and specific port requirements. Additional fees may apply 
                for inland transportation from the port to your final destination.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
