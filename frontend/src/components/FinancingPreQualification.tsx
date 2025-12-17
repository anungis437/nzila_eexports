import { useState } from 'react';
import { Calculator, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

interface FinancingPreQualificationProps {
  vehiclePrice: number;
}

type CreditScore = 'excellent' | 'good' | 'fair' | 'poor';
type EmploymentStatus = 'employed' | 'self-employed' | 'retired' | 'unemployed';

const CREDIT_SCORE_RATES: Record<CreditScore, { rate: number; label: string }> = {
  excellent: { rate: 5.99, label: 'Excellent (700+)' },
  good: { rate: 7.99, label: 'Good (650-699)' },
  fair: { rate: 12.99, label: 'Fair (600-649)' },
  poor: { rate: 18.99, label: 'Poor (Below 600)' },
};

export default function FinancingPreQualification({ vehiclePrice }: FinancingPreQualificationProps) {
  const [downPaymentPercent, setDownPaymentPercent] = useState(20);
  const [loanTerm, setLoanTerm] = useState(48);
  const [creditScore, setCreditScore] = useState<CreditScore>('good');
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [employmentStatus, setEmploymentStatus] = useState<EmploymentStatus>('employed');
  const [calculated, setCalculated] = useState(false);

  const downPayment = Math.round(vehiclePrice * (downPaymentPercent / 100));
  const loanAmount = vehiclePrice - downPayment;
  const interestRate = CREDIT_SCORE_RATES[creditScore].rate;
  
  // Calculate monthly payment using standard loan formula
  const monthlyRate = interestRate / 100 / 12;
  const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, loanTerm)) / 
                        (Math.pow(1 + monthlyRate, loanTerm) - 1);
  const totalPayable = downPayment + (monthlyPayment * loanTerm);
  const totalInterest = totalPayable - vehiclePrice;

  // Determine eligibility
  const getEligibility = () => {
    const income = parseFloat(monthlyIncome);
    if (!income || income <= 0) return null;

    const debtToIncomeRatio = (monthlyPayment / income) * 100;
    
    if (employmentStatus === 'unemployed') {
      return {
        status: 'not-eligible',
        message: 'Employment required for financing approval',
        icon: AlertTriangle,
        color: 'red',
      };
    }

    if (creditScore === 'poor' && downPaymentPercent < 30) {
      return {
        status: 'needs-improvement',
        message: 'Consider increasing down payment to 30% or more',
        icon: AlertTriangle,
        color: 'amber',
      };
    }

    if (debtToIncomeRatio > 45) {
      return {
        status: 'high-risk',
        message: 'Monthly payment exceeds 45% of income - may need co-signer',
        icon: AlertTriangle,
        color: 'amber',
      };
    }

    if (debtToIncomeRatio > 35) {
      return {
        status: 'conditional',
        message: 'Likely approved with additional documentation',
        icon: CheckCircle,
        color: 'blue',
      };
    }

    return {
      status: 'likely-approved',
      message: 'Strong candidate for financing approval',
      icon: CheckCircle,
      color: 'green',
    };
  };

  const eligibility = calculated ? getEligibility() : null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Calculator className="h-4 w-4" />
          Financing Pre-Qualification
        </h3>
      </div>

      <div className="text-xs text-gray-600 bg-blue-50 rounded-lg p-2">
        Vehicle Price: <strong>${vehiclePrice.toLocaleString()} CAD</strong>
      </div>

      <div className="space-y-4">
        {/* Down Payment */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-medium text-gray-700">Down Payment</label>
            <span className="text-sm font-semibold text-blue-600">{downPaymentPercent}% (${downPayment.toLocaleString()})</span>
          </div>
          <input
            type="range"
            min="10"
            max="50"
            step="5"
            value={downPaymentPercent}
            onChange={(e) => {
              setDownPaymentPercent(Number(e.target.value));
              setCalculated(false);
            }}
            aria-label="Down payment percentage"
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>10%</span>
            <span>50%</span>
          </div>
        </div>

        {/* Loan Term */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Loan Term (months)</label>
          <select
            value={loanTerm}
            onChange={(e) => {
              setLoanTerm(Number(e.target.value));
              setCalculated(false);
            }}
            aria-label="Select loan term"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={12}>12 months</option>
            <option value={24}>24 months</option>
            <option value={36}>36 months</option>
            <option value={48}>48 months</option>
            <option value={60}>60 months</option>
            <option value={72}>72 months</option>
          </select>
        </div>

        {/* Credit Score */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Credit Score</label>
          <select
            value={creditScore}
            onChange={(e) => {
              setCreditScore(e.target.value as CreditScore);
              setCalculated(false);
            }}
            aria-label="Select credit score range"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.entries(CREDIT_SCORE_RATES).map(([key, { label, rate }]) => (
              <option key={key} value={key}>
                {label} - Est. {rate}% APR
              </option>
            ))}
          </select>
        </div>

        {/* Monthly Income */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Monthly Income (CAD)</label>
          <input
            type="number"
            value={monthlyIncome}
            onChange={(e) => {
              setMonthlyIncome(e.target.value);
              setCalculated(false);
            }}
            placeholder="Enter your monthly income"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Employment Status */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Employment Status</label>
          <select
            value={employmentStatus}
            onChange={(e) => {
              setEmploymentStatus(e.target.value as EmploymentStatus);
              setCalculated(false);
            }}
            aria-label="Select employment status"
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="employed">Full-time Employed</option>
            <option value="self-employed">Self-employed</option>
            <option value="retired">Retired</option>
            <option value="unemployed">Unemployed</option>
          </select>
        </div>

        {/* Calculate Button */}
        <button
          onClick={() => setCalculated(true)}
          disabled={!monthlyIncome || parseFloat(monthlyIncome) <= 0}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition text-sm font-medium"
        >
          Check Pre-Qualification
        </button>

        {/* Results */}
        {calculated && (
          <div className="space-y-3 pt-3 border-t border-gray-200">
            {/* Monthly Payment */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-xs text-blue-600 mb-1">
                <TrendingUp className="h-4 w-4" />
                Estimated Monthly Payment
              </div>
              <div className="text-2xl font-bold text-blue-900">
                ${Math.round(monthlyPayment).toLocaleString()} CAD
              </div>
              <div className="text-xs text-blue-600 mt-1">
                at {interestRate}% APR for {loanTerm} months
              </div>
            </div>

            {/* Loan Details */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Loan Amount</span>
                <span className="font-medium">${loanAmount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Interest</span>
                <span className="font-medium">${Math.round(totalInterest).toLocaleString()}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-gray-200">
                <span className="text-gray-900 font-medium">Total Amount Payable</span>
                <span className="font-bold">${Math.round(totalPayable).toLocaleString()}</span>
              </div>
            </div>

            {/* Eligibility Status */}
            {eligibility && (
              <div className={`flex items-start gap-3 rounded-lg p-3 border ${
                eligibility.color === 'green' ? 'bg-green-50 border-green-200' :
                eligibility.color === 'blue' ? 'bg-blue-50 border-blue-200' :
                eligibility.color === 'amber' ? 'bg-amber-50 border-amber-200' :
                'bg-red-50 border-red-200'
              }`}>
                <eligibility.icon className={`h-5 w-5 flex-shrink-0 ${
                  eligibility.color === 'green' ? 'text-green-600' :
                  eligibility.color === 'blue' ? 'text-blue-600' :
                  eligibility.color === 'amber' ? 'text-amber-600' :
                  'text-red-600'
                }`} />
                <div>
                  <div className={`text-sm font-semibold ${
                    eligibility.color === 'green' ? 'text-green-900' :
                    eligibility.color === 'blue' ? 'text-blue-900' :
                    eligibility.color === 'amber' ? 'text-amber-900' :
                    'text-red-900'
                  }`}>
                    {eligibility.message}
                  </div>
                  {parseFloat(monthlyIncome) > 0 && (
                    <div className="text-xs text-gray-600 mt-1">
                      Payment is {Math.round((monthlyPayment / parseFloat(monthlyIncome)) * 100)}% of your monthly income
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="text-xs text-gray-500 pt-2 border-t border-gray-100">
          <strong>Disclaimer:</strong> This is an estimate only and does not constitute a commitment to lend. 
          Actual rates, terms, and approval are subject to credit review and may vary. Financing is subject to 
          approval by our lending partners.
        </div>
      </div>
    </div>
  );
}
