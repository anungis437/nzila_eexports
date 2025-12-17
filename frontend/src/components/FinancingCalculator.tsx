import React from 'react';
import { Calculator, DollarSign, Calendar, TrendingUp, PiggyBank } from 'lucide-react';

interface FinancingCalculatorProps {
  vehiclePrice: number;
  currency?: string;
  language: 'en' | 'fr';
}

export const FinancingCalculator: React.FC<FinancingCalculatorProps> = ({
  vehiclePrice,
  currency = 'CAD',
  language
}) => {
  const [downPayment, setDownPayment] = React.useState(vehiclePrice * 0.2); // 20% default
  const [interestRate, setInterestRate] = React.useState(6.5);
  const [loanTerm, setLoanTerm] = React.useState(60); // 5 years default
  const [tradeInValue, setTradeInValue] = React.useState(0);

  // Calculate financing details
  const effectivePrice = vehiclePrice - tradeInValue;
  const actualLoanAmount = Math.max(0, effectivePrice - downPayment);
  const monthlyInterestRate = interestRate / 100 / 12;
  const numberOfPayments = loanTerm;

  // Monthly payment calculation (standard amortization formula)
  const monthlyPayment = actualLoanAmount > 0 && monthlyInterestRate > 0
    ? actualLoanAmount * (monthlyInterestRate * Math.pow(1 + monthlyInterestRate, numberOfPayments)) /
      (Math.pow(1 + monthlyInterestRate, numberOfPayments) - 1)
    : actualLoanAmount > 0 ? actualLoanAmount / numberOfPayments : 0;

  const totalInterest = (monthlyPayment * numberOfPayments) - actualLoanAmount;
  const totalCost = effectivePrice + totalInterest;

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat(language === 'fr' ? 'fr-CA' : 'en-CA', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Handle down payment percentage presets
  const setDownPaymentPercent = (percent: number) => {
    setDownPayment((effectivePrice * percent) / 100);
  };

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-blue-100 rounded-lg">
          <Calculator className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            {language === 'fr' ? 'Calculateur de financement' : 'Financing Calculator'}
          </h3>
          <p className="text-sm text-gray-600">
            {language === 'fr' ? 'Estimez vos paiements mensuels' : 'Estimate your monthly payments'}
          </p>
        </div>
      </div>

      {/* Vehicle Price Display */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-700">
            {language === 'fr' ? 'Prix du véhicule' : 'Vehicle Price'}
          </span>
          <span className="text-2xl font-bold text-blue-600">{formatCurrency(vehiclePrice)}</span>
        </div>
      </div>

      {/* Trade-In Value */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <div className="flex items-center gap-2">
            <PiggyBank className="w-4 h-4" />
            {language === 'fr' ? 'Valeur de reprise' : 'Trade-In Value'} ({language === 'fr' ? 'optionnel' : 'optional'})
          </div>
        </label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
          <input
            type="number"
            min="0"
            max={vehiclePrice}
            step="1000"
            value={tradeInValue}
            onChange={(e) => setTradeInValue(Math.min(Number(e.target.value), vehiclePrice))}
            className="w-full pl-8 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label={language === 'fr' ? 'Valeur de reprise' : 'Trade-In Value'}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {language === 'fr'
            ? 'Réduisez le prix en échangeant votre véhicule actuel'
            : 'Reduce the price by trading in your current vehicle'}
        </p>
      </div>

      {/* Effective Price (after trade-in) */}
      {tradeInValue > 0 && (
        <div className="bg-green-50 rounded-lg p-3 mb-6">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">
              {language === 'fr' ? 'Prix effectif' : 'Effective Price'}
            </span>
            <span className="text-lg font-bold text-green-600">{formatCurrency(effectivePrice)}</span>
          </div>
        </div>
      )}

      {/* Down Payment */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              {language === 'fr' ? 'Mise de fonds' : 'Down Payment'}
            </div>
          </label>
          <span className="text-sm text-gray-600">
            {((downPayment / effectivePrice) * 100).toFixed(0)}%
          </span>
        </div>
        <input
          type="range"
          min="0"
          max={effectivePrice}
          step="1000"
          value={downPayment}
          onChange={(e) => setDownPayment(Number(e.target.value))}
          className="w-full"
          aria-label={language === 'fr' ? 'Mise de fonds' : 'Down Payment'}
        />
        <div className="flex items-center justify-between mt-2">
          <input
            type="number"
            min="0"
            max={effectivePrice}
            step="1000"
            value={downPayment}
            onChange={(e) => setDownPayment(Math.min(Number(e.target.value), effectivePrice))}
            className="w-32 px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label={language === 'fr' ? 'Montant de la mise de fonds' : 'Down payment amount'}
          />
          <div className="flex gap-2">
            {[10, 20, 30].map((percent) => (
              <button
                key={percent}
                onClick={() => setDownPaymentPercent(percent)}
                className="px-3 py-1 text-sm border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {percent}%
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Interest Rate */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              {language === 'fr' ? 'Taux d\'intérêt annuel' : 'Annual Interest Rate'}
            </div>
          </label>
          <span className="text-sm text-gray-600">{interestRate.toFixed(2)}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="20"
          step="0.25"
          value={interestRate}
          onChange={(e) => setInterestRate(Number(e.target.value))}
          className="w-full"
          aria-label={language === 'fr' ? 'Taux d\'intérêt annuel' : 'Annual Interest Rate'}
        />
        <div className="flex items-center justify-between mt-2">
          <input
            type="number"
            min="0"
            max="20"
            step="0.25"
            value={interestRate}
            onChange={(e) => setInterestRate(Number(e.target.value))}
            className="w-32 px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label={language === 'fr' ? 'Taux d\'intérêt' : 'Interest rate'}
          />
          <p className="text-xs text-gray-500">
            {language === 'fr'
              ? 'Les taux varient de 4% à 15%'
              : 'Rates typically range from 4% to 15%'}
          </p>
        </div>
      </div>

      {/* Loan Term */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              {language === 'fr' ? 'Durée du prêt' : 'Loan Term'}
            </div>
          </label>
          <span className="text-sm text-gray-600">
            {loanTerm} {language === 'fr' ? 'mois' : 'months'} ({(loanTerm / 12).toFixed(1)} {language === 'fr' ? 'ans' : 'years'})
          </span>
        </div>
        <input
          type="range"
          min="12"
          max="84"
          step="12"
          value={loanTerm}
          onChange={(e) => setLoanTerm(Number(e.target.value))}
          className="w-full"
          aria-label={language === 'fr' ? 'Durée du prêt' : 'Loan Term'}
        />
        <div className="flex justify-between mt-2">
          {[24, 36, 48, 60, 72, 84].map((months) => (
            <button
              key={months}
              onClick={() => setLoanTerm(months)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                loanTerm === months
                  ? 'bg-blue-600 text-white'
                  : 'border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {months / 12}y
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="border-t-2 border-gray-200 pt-6 space-y-4">
        {/* Monthly Payment - Primary Result */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
          <div className="text-sm opacity-90 mb-1">
            {language === 'fr' ? 'Paiement mensuel estimé' : 'Estimated Monthly Payment'}
          </div>
          <div className="text-4xl font-bold">{formatCurrency(monthlyPayment)}</div>
          <div className="text-sm opacity-75 mt-2">
            {language === 'fr' ? 'pour' : 'for'} {loanTerm} {language === 'fr' ? 'mois' : 'months'}
          </div>
        </div>

        {/* Breakdown */}
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-gray-200">
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Montant du prêt' : 'Loan Amount'}
            </span>
            <span className="font-semibold text-gray-900">{formatCurrency(actualLoanAmount)}</span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-gray-200">
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Intérêts totaux' : 'Total Interest'}
            </span>
            <span className="font-semibold text-orange-600">{formatCurrency(totalInterest)}</span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-gray-200">
            <span className="text-sm text-gray-600">
              {language === 'fr' ? 'Paiements totaux' : 'Total of Payments'}
            </span>
            <span className="font-semibold text-gray-900">{formatCurrency(monthlyPayment * numberOfPayments)}</span>
          </div>

          <div className="flex items-center justify-between py-3 bg-gray-50 rounded-lg px-4">
            <span className="text-sm font-medium text-gray-900">
              {language === 'fr' ? 'Coût total' : 'Total Cost'}
            </span>
            <span className="text-xl font-bold text-gray-900">{formatCurrency(totalCost)}</span>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-xs text-yellow-800">
          {language === 'fr'
            ? '⚠️ Cette estimation est fournie à titre indicatif uniquement. Les taux et conditions réels peuvent varier selon votre profil de crédit et le prêteur. Contactez-nous pour une offre de financement personnalisée.'
            : '⚠️ This estimate is for informational purposes only. Actual rates and terms may vary based on your credit profile and lender. Contact us for a personalized financing quote.'}
        </p>
      </div>
    </div>
  );
};
