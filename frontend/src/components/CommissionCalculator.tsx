import { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { Calculator, DollarSign, Percent, TrendingUp } from 'lucide-react'

interface CommissionCalculatorProps {
  dealAmount: number
  onCalculate?: (amount: number, percentage: number) => void
  defaultPercentage?: number
  commissionType?: 'broker' | 'dealer'
}

export default function CommissionCalculator({
  dealAmount,
  onCalculate,
  defaultPercentage,
  commissionType = 'broker',
}: CommissionCalculatorProps) {
  const { language } = useLanguage()
  const [percentage, setPercentage] = useState<number>(
    defaultPercentage || (commissionType === 'broker' ? 3 : 5)
  )
  const [commissionAmount, setCommissionAmount] = useState<number>(0)

  useEffect(() => {
    const amount = (dealAmount * percentage) / 100
    setCommissionAmount(amount)
    if (onCalculate) {
      onCalculate(amount, percentage)
    }
  }, [dealAmount, percentage, onCalculate])

  const presetPercentages = commissionType === 'broker' 
    ? [2, 3, 4, 5]
    : [3, 5, 7, 10]

  return (
    <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-green-100 rounded-lg">
          <Calculator className="w-5 h-5 text-green-600" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900">
            {language === 'fr' ? 'Calculateur de commission' : 'Commission Calculator'}
          </h3>
          <p className="text-sm text-slate-600">
            {language === 'fr' 
              ? `Commission ${commissionType === 'broker' ? 'courtier' : 'revendeur'}`
              : `${commissionType === 'broker' ? 'Broker' : 'Dealer'} commission`}
          </p>
        </div>
      </div>

      {/* Deal Amount Display */}
      <div className="bg-white/80 backdrop-blur rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 mb-1">
          <DollarSign className="w-4 h-4 text-slate-500" />
          <span className="text-sm text-slate-600">
            {language === 'fr' ? 'Prix de la transaction' : 'Deal Amount'}
          </span>
        </div>
        <p className="text-2xl font-bold text-slate-900">
          ${dealAmount.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          <span className="text-sm font-normal text-slate-500 ml-2">CAD</span>
        </p>
      </div>

      {/* Percentage Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          <div className="flex items-center gap-2">
            <Percent className="w-4 h-4" />
            {language === 'fr' ? 'Pourcentage de commission' : 'Commission Percentage'}
          </div>
        </label>
        <div className="flex items-center gap-3">
          <input
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={percentage}
            onChange={(e) => setPercentage(parseFloat(e.target.value) || 0)}
            className="flex-1 px-4 py-2.5 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
          />
          <span className="text-lg font-semibold text-slate-700">%</span>
        </div>
        
        {/* Preset Percentages */}
        <div className="flex gap-2 mt-3">
          {presetPercentages.map((preset) => (
            <button
              key={preset}
              onClick={() => setPercentage(preset)}
              className={`flex-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                percentage === preset
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-slate-700 hover:bg-green-100'
              }`}
            >
              {preset}%
            </button>
          ))}
        </div>
      </div>

      {/* Commission Amount Result */}
      <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-5 text-white">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-5 h-5" />
          <span className="text-sm opacity-90">
            {language === 'fr' ? 'Montant de la commission' : 'Commission Amount'}
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold">
            ${commissionAmount.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className="text-sm opacity-90">CAD</span>
        </div>
        <div className="mt-3 pt-3 border-t border-green-400/30">
          <p className="text-sm opacity-90">
            {percentage}% {language === 'fr' ? 'de' : 'of'} ${dealAmount.toLocaleString('en-CA')}
          </p>
        </div>
      </div>

      {/* Info Text */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-900">
          {language === 'fr' 
            ? `Calcul automatique basé sur le prix convenu. Les ${commissionType === 'broker' ? 'courtiers' : 'revendeurs'} reçoivent généralement ${commissionType === 'broker' ? '2-5%' : '3-10%'}.`
            : `Automatic calculation based on agreed price. ${commissionType === 'broker' ? 'Brokers' : 'Dealers'} typically receive ${commissionType === 'broker' ? '2-5%' : '3-10%'}.`}
        </p>
      </div>
    </div>
  )
}
