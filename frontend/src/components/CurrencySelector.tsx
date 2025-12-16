import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Globe, Check, Search } from 'lucide-react'
import api from '../lib/api'

interface Currency {
  id: number
  code: string
  name: string
  symbol: string
  is_african: boolean
  country: string
}

interface CurrencySelectorProps {
  value?: string
  onChange: (currencyCode: string) => void
  africanOnly?: boolean
  label?: string
}

export default function CurrencySelector({ value, onChange, africanOnly = false, label }: CurrencySelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const { data: allCurrencies = [] } = useQuery({
    queryKey: ['currencies'],
    queryFn: () => api.getCurrencies(),
  })

  const currencies: Currency[] = africanOnly
    ? allCurrencies.filter((c: Currency) => c.is_african)
    : allCurrencies

  const selectedCurrency = currencies.find((c: Currency) => c.code === value)

  const filteredCurrencies = currencies.filter((c: Currency) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.country.toLowerCase().includes(searchQuery.toLowerCase())
  )

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('.currency-selector')) {
        setIsOpen(false)
      }
    }

    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  return (
    <div className="currency-selector relative">
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-2">
          {label}
        </label>
      )}
      
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 bg-white border border-slate-300 rounded-lg hover:border-blue-400 transition-colors"
      >
        {selectedCurrency ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
              <span className="text-white font-semibold text-sm">
                {selectedCurrency.symbol}
              </span>
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-slate-900">{selectedCurrency.code}</div>
              <div className="text-xs text-slate-500">{selectedCurrency.name}</div>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-slate-500">
            <Globe className="h-5 w-5" />
            <span>Select currency</span>
          </div>
        )}
        <svg
          className={`w-5 h-5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-slate-200 rounded-lg shadow-lg max-h-96 overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b border-slate-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search currencies..."
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
            </div>
          </div>

          {/* Currency List */}
          <div className="overflow-y-auto max-h-80">
            {filteredCurrencies.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                <p className="text-sm">No currencies found</p>
              </div>
            ) : (
              <div className="p-2">
                {filteredCurrencies.map((currency: Currency) => (
                  <button
                    key={currency.id}
                    type="button"
                    onClick={() => {
                      onChange(currency.code)
                      setIsOpen(false)
                      setSearchQuery('')
                    }}
                    className={`w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg transition-colors ${
                      value === currency.code
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-slate-50 text-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        value === currency.code
                          ? 'bg-gradient-to-br from-blue-400 to-blue-600'
                          : 'bg-gradient-to-br from-slate-400 to-slate-600'
                      }`}>
                        <span className="text-white font-semibold text-xs">
                          {currency.symbol}
                        </span>
                      </div>
                      <div className="text-left">
                        <div className="text-sm font-medium flex items-center gap-2">
                          {currency.code}
                          {currency.is_african && (
                            <span className="px-1.5 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                              Africa
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-500">{currency.country}</div>
                      </div>
                    </div>
                    {value === currency.code && (
                      <Check className="h-5 w-5 text-blue-600" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
