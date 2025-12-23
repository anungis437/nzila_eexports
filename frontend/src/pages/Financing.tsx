import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calculator, DollarSign, TrendingUp, Loader2, Info } from 'lucide-react'
import { useState } from 'react'
import api from '@/lib/api'

interface FinancingCalculation {
  vehicle_price: string
  down_payment: string
  loan_amount: string
  interest_rate: string
  monthly_payment: string
  total_interest: string
  total_cost: string
  pst: string
  gst_hst: string
  total_taxes: string
  total_with_taxes: string
}

export default function Financing() {
  const [vehiclePrice, setVehiclePrice] = useState('25000')
  const [downPayment, setDownPayment] = useState('5000')
  const [termMonths, setTermMonths] = useState('60')
  const [province, setProvince] = useState('ON')
  const [creditScore, setCreditScore] = useState('720')
  const [calculation, setCalculation] = useState<FinancingCalculation | null>(null)
  const [calculating, setCalculating] = useState(false)

  // Fallback interest rates (used if API fails)
  const getInterestRateFallback = (score: number): number => {
    if (score >= 750) return 4.99
    if (score >= 680) return 6.99
    if (score >= 620) return 9.99
    if (score >= 550) return 14.99
    return 19.99
  }

  // Fetch interest rate from backend API
  const getInterestRate = async (prov: string, score: number): Promise<number> => {
    try {
      // Determine credit tier from score
      let credit_tier = 'very_poor'
      if (score >= 750) credit_tier = 'excellent'
      else if (score >= 680) credit_tier = 'good'
      else if (score >= 620) credit_tier = 'fair'
      else if (score >= 550) credit_tier = 'poor'

      // Call backend API
      const response = await api.get(`/api/commissions/interest-rates/by_tier/`, {
        params: { province: prov, credit_tier }
      })
      
      return parseFloat(response.data.rate_percentage)
    } catch (error) {
      console.warn('Failed to fetch interest rate from API, using fallback:', error)
      return getInterestRateFallback(score)
    }
  }

  const getTaxRates = (prov: string): { pst: number, gst: number } => {
    const taxRates: Record<string, { pst: number, gst: number }> = {
      'ON': { pst: 0, gst: 0.13 }, // HST
      'QC': { pst: 0.09975, gst: 0.05 },
      'BC': { pst: 0.07, gst: 0.05 },
      'AB': { pst: 0, gst: 0.05 },
      'MB': { pst: 0.07, gst: 0.05 },
      'SK': { pst: 0.06, gst: 0.05 },
      'NS': { pst: 0, gst: 0.15 }, // HST
      'NB': { pst: 0, gst: 0.15 }, // HST
      'NL': { pst: 0, gst: 0.15 }, // HST
      'PE': { pst: 0, gst: 0.15 }, // HST
      'NT': { pst: 0, gst: 0.05 },
      'YT': { pst: 0, gst: 0.05 },
      'NU': { pst: 0, gst: 0.05 }
    }
    return taxRates[prov] || { pst: 0, gst: 0.05 }
  }

  const calculateFinancing = async () => {
    setCalculating(true)
    try {
      const price = parseFloat(vehiclePrice)
      const down = parseFloat(downPayment)
      const score = parseInt(creditScore)
      const months = parseInt(termMonths)

      // Fetch dynamic interest rate from backend
      const interestRate = await getInterestRate(province, score)
      const monthlyRate = interestRate / 100 / 12
      const loanAmount = price - down

      // Calculate monthly payment using loan formula
      const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1)
      const totalPayment = monthlyPayment * months
      const totalInterest = totalPayment - loanAmount

      // Calculate taxes
      const taxes = getTaxRates(province)
      const pstAmount = price * taxes.pst
      const gstAmount = price * taxes.gst
      const totalTaxes = pstAmount + gstAmount
      const totalWithTaxes = price + totalTaxes

      setCalculation({
        vehicle_price: price.toFixed(2),
        down_payment: down.toFixed(2),
        loan_amount: loanAmount.toFixed(2),
        interest_rate: interestRate.toFixed(2),
        monthly_payment: monthlyPayment.toFixed(2),
        total_interest: totalInterest.toFixed(2),
        total_cost: totalPayment.toFixed(2),
        pst: pstAmount.toFixed(2),
        gst_hst: gstAmount.toFixed(2),
        total_taxes: totalTaxes.toFixed(2),
        total_with_taxes: totalWithTaxes.toFixed(2)
      })
    } catch (error) {
      console.error('Calculation error:', error)
      alert('Error calculating financing. Please check your inputs.')
    } finally {
      setCalculating(false)
    }
  }

  const provinces = [
    { code: 'ON', name: 'Ontario' },
    { code: 'QC', name: 'Quebec' },
    { code: 'BC', name: 'British Columbia' },
    { code: 'AB', name: 'Alberta' },
    { code: 'MB', name: 'Manitoba' },
    { code: 'SK', name: 'Saskatchewan' },
    { code: 'NS', name: 'Nova Scotia' },
    { code: 'NB', name: 'New Brunswick' },
    { code: 'NL', name: 'Newfoundland' },
    { code: 'PE', name: 'Prince Edward Island' },
    { code: 'NT', name: 'Northwest Territories' },
    { code: 'YT', name: 'Yukon' },
    { code: 'NU', name: 'Nunavut' }
  ]

  const creditTiers = [
    { min: 750, max: 850, label: 'Excellent (750+)' },
    { min: 680, max: 749, label: 'Good (680-749)' },
    { min: 620, max: 679, label: 'Fair (620-679)' },
    { min: 550, max: 619, label: 'Poor (550-619)' },
    { min: 300, max: 549, label: 'Very Poor (300-549)' }
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Calculator className="h-8 w-8 text-blue-600" />
          Financing Calculator
        </h1>
        <p className="text-gray-600 mt-2">
          Calculate monthly payments with Canadian provincial taxes and interest rates
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vehicle Price (CAD)
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="number"
                  value={vehiclePrice}
                  onChange={(e) => setVehiclePrice(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="25000"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Down Payment (CAD)
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="number"
                  value={downPayment}
                  onChange={(e) => setDownPayment(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="5000"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="loan-term-select">
                Loan Term (Months)
              </label>
              <select
                id="loan-term-select"
                value={termMonths}
                onChange={(e) => setTermMonths(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="12">12 months</option>
                <option value="24">24 months</option>
                <option value="36">36 months</option>
                <option value="48">48 months</option>
                <option value="60">60 months</option>
                <option value="72">72 months</option>
                <option value="84">84 months</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="province-select">
                Province
              </label>
              <select
                id="province-select"
                value={province}
                onChange={(e) => setProvince(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {provinces.map((prov) => (
                  <option key={prov.code} value={prov.code}>
                    {prov.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Credit Score
              </label>
              <input
                type="number"
                value={creditScore}
                onChange={(e) => setCreditScore(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="720"
                min="300"
                max="850"
              />
              <div className="mt-2 space-y-1">
                {creditTiers.map((tier) => (
                  <div
                    key={tier.label}
                    className={`text-xs ${
                      parseInt(creditScore) >= tier.min && parseInt(creditScore) <= tier.max
                        ? 'text-blue-600 font-medium'
                        : 'text-gray-500'
                    }`}
                  >
                    {tier.label}
                  </div>
                ))}
              </div>
            </div>

            <Button
              onClick={calculateFinancing}
              disabled={calculating}
              className="w-full"
            >
              {calculating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Calculating...
                </>
              ) : (
                <>
                  <Calculator className="mr-2 h-4 w-4" />
                  Calculate Payment
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="space-y-6">
          {calculation ? (
            <>
              <Card className="bg-gradient-to-br from-blue-600 to-blue-700 text-white">
                <CardHeader>
                  <CardTitle className="text-white">Monthly Payment</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold">
                    ${parseFloat(calculation.monthly_payment).toFixed(2)}
                  </div>
                  <p className="text-blue-100 mt-2">
                    {termMonths} months at {parseFloat(calculation.interest_rate).toFixed(2)}% APR
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Loan Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Vehicle Price:</span>
                    <span className="font-semibold">${parseFloat(calculation.vehicle_price).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Down Payment:</span>
                    <span className="font-semibold">-${parseFloat(calculation.down_payment).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="text-gray-600">Loan Amount:</span>
                    <span className="font-semibold">${parseFloat(calculation.loan_amount).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Interest:</span>
                    <span className="font-semibold text-red-600">+${parseFloat(calculation.total_interest).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="font-medium">Total Cost:</span>
                    <span className="font-bold text-lg">${parseFloat(calculation.total_cost).toLocaleString()}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Canadian Taxes ({province})</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {parseFloat(calculation.pst) > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">PST:</span>
                      <span className="font-semibold">${parseFloat(calculation.pst).toLocaleString()}</span>
                    </div>
                  )}
                  {parseFloat(calculation.gst_hst) > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">{province === 'ON' || province === 'NB' || province === 'NS' || province === 'NL' || province === 'PE' ? 'HST' : 'GST'}:</span>
                      <span className="font-semibold">${parseFloat(calculation.gst_hst).toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between border-t pt-2">
                    <span className="font-medium">Total Taxes:</span>
                    <span className="font-bold">${parseFloat(calculation.total_taxes).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="font-medium">Grand Total (with taxes):</span>
                    <span className="font-bold text-lg text-blue-600">${parseFloat(calculation.total_with_taxes).toLocaleString()}</span>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Calculator className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">
                  Enter your loan details and click "Calculate Payment" to see your financing options
                </p>
              </CardContent>
            </Card>
          )}

          {/* Rate Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Info className="h-4 w-4" />
                Interest Rates by Credit Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Excellent (750+)</span>
                  <span className="font-semibold text-blue-600">5.99%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Good (680-749)</span>
                  <span className="font-semibold text-blue-600">7.99%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Fair (620-679)</span>
                  <span className="font-semibold text-blue-600">9.99%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Poor (550-619)</span>
                  <span className="font-semibold text-blue-600">12.99%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Very Poor (&lt;550)</span>
                  <span className="font-semibold text-blue-600">15.99%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
