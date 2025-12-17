import { useState } from 'react';
import { ArrowRightLeft } from 'lucide-react';
import { CURRENCIES, convertCurrency, formatCurrency, Currency } from '../utils/currency';

interface CurrencyConverterProps {
  baseAmount: number;
  baseCurrency?: string;
}

export default function CurrencyConverter({ baseAmount, baseCurrency = 'CAD' }: CurrencyConverterProps) {
  const [targetCurrency, setTargetCurrency] = useState('XOF');
  const [showAllCurrencies, setShowAllCurrencies] = useState(false);

  const convertedAmount = convertCurrency(baseAmount, baseCurrency, targetCurrency);
  
  // Filter currencies to show (African currencies by default)
  const displayCurrencies = showAllCurrencies 
    ? CURRENCIES 
    : CURRENCIES.filter((c: Currency) => c.isAfrican);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Currency Converter</h3>
        <button
          onClick={() => setShowAllCurrencies(!showAllCurrencies)}
          className="text-xs text-blue-600 hover:text-blue-700"
        >
          {showAllCurrencies ? 'Show African Only' : 'Show All'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
        {/* From Currency */}
        <div className="space-y-2">
          <label className="text-xs text-gray-600">From</label>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">{baseCurrency}</div>
            <div className="text-lg font-bold text-gray-900">
              {formatCurrency(baseAmount, baseCurrency)}
            </div>
          </div>
        </div>

        {/* Arrow */}
        <div className="flex justify-center md:mt-6">
          <ArrowRightLeft className="h-5 w-5 text-gray-400" />
        </div>

        {/* To Currency */}
        <div className="space-y-2">
          <label className="text-xs text-gray-600">To</label>
          <div className="space-y-2">
            <select
              value={targetCurrency}
              onChange={(e) => setTargetCurrency(e.target.value)}
              aria-label="Select target currency"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {displayCurrencies.map((currency: Currency) => (
                <option key={currency.code} value={currency.code}>
                  {currency.code} - {currency.name}
                </option>
              ))}
            </select>
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-xs text-blue-600 mb-1">
                {CURRENCIES.find((c: Currency) => c.code === targetCurrency)?.name}
              </div>
              <div className="text-lg font-bold text-blue-900">
                {formatCurrency(convertedAmount, targetCurrency)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick conversion buttons */}
      <div className="pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 mb-2">Popular Currencies:</div>
        <div className="flex flex-wrap gap-2">
          {['XOF', 'XAF', 'NGN', 'CDF', 'USD'].map((code) => (
            <button
              key={code}
              onClick={() => setTargetCurrency(code)}
              className={`px-3 py-1 text-xs rounded-full transition ${
                targetCurrency === code
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {code}
            </button>
          ))}
        </div>
      </div>

      <div className="text-xs text-gray-500 pt-2 border-t border-gray-100">
        * Exchange rates are approximate and may vary. Check with your bank for exact rates.
      </div>
    </div>
  );
}
