import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { DollarSign, TrendingUp, RefreshCw, Save, AlertCircle } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { format } from 'date-fns'

export default function CurrencySettings() {
  const { language } = useLanguage()
  const queryClient = useQueryClient()

  const { data: rates, isLoading } = useQuery({
    queryKey: ['currencyRates'],
    queryFn: api.getCurrencyRates,
  })

  const [formData, setFormData] = useState({
    cad_to_xof: rates?.cad_to_xof || 450.0,
    xof_to_cad: rates?.xof_to_cad || 0.0022,
    auto_update: rates?.auto_update || false,
  })

  const [isSaving, setIsSaving] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const updateRateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.updateCurrencyRate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currencyRates'] })
      setSuccessMessage(language === 'fr' ? 'Taux mis à jour avec succès!' : 'Rates updated successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    // Update each rate individually
    const ratesData = rates as any
    if (ratesData && Array.isArray(ratesData)) {
      Promise.all(
        ratesData.map((rate: any) => 
          updateRateMutation.mutateAsync({ 
            id: rate.id, 
            data: { rate: rate.rate } 
          })
        )
      ).finally(() => setIsSaving(false))
    } else {
      setIsSaving(false)
    }
  }

  const handleRefresh = () => {
    setIsRefreshing(true)
    // Just refetch the rates from the server
    queryClient.invalidateQueries({ queryKey: ['currencyRates'] })
    setTimeout(() => {
      setIsRefreshing(false)
      setSuccessMessage(language === 'fr' ? 'Taux actualisés!' : 'Rates refreshed!')
      setTimeout(() => setSuccessMessage(''), 3000)
    }, 1000)
  }

  if (isLoading) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4" />
        <div className="space-y-4">
          <div className="h-10 bg-slate-200 rounded" />
          <div className="h-10 bg-slate-200 rounded" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
            <DollarSign className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              {language === 'fr' ? 'Paramètres de Devise' : 'Currency Settings'}
            </h2>
            <p className="text-sm text-slate-500">
              {language === 'fr'
                ? 'Gérez les taux de change CAD ⇄ XOF'
                : 'Manage CAD ⇄ XOF exchange rates'}
            </p>
          </div>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          {language === 'fr' ? 'Actualiser' : 'Refresh'}
        </button>
      </div>

      {/* Current Rates Display */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">CAD → XOF</span>
          </div>
          <p className="text-2xl font-bold text-blue-900">
            1 CAD = {formData.cad_to_xof.toFixed(2)} XOF
          </p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            <span className="text-sm font-medium text-purple-900">XOF → CAD</span>
          </div>
          <p className="text-2xl font-bold text-purple-900">
            1 XOF = {formData.xof_to_cad.toFixed(4)} CAD
          </p>
        </div>
      </div>

      {/* Info Alert */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 flex gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-800">
          {language === 'fr' ? (
            <>
              <strong>Note:</strong> Les taux de change sont utilisés pour tous les calculs de prix sur la plateforme. Dernière mise à jour: {rates?.last_updated ? format(new Date(rates.last_updated), 'PPp') : 'N/A'}
            </>
          ) : (
            <>
              <strong>Note:</strong> Exchange rates are used for all pricing calculations on the platform. Last updated: {rates?.last_updated ? format(new Date(rates.last_updated), 'PPp') : 'N/A'}
            </>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* CAD to XOF Rate */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Taux CAD → XOF' : 'CAD → XOF Rate'}
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="number"
              step="0.01"
              value={formData.cad_to_xof}
              onChange={(e) => setFormData({ ...formData, cad_to_xof: parseFloat(e.target.value) })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="450.00"
            />
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {language === 'fr'
              ? 'Combien de XOF pour 1 CAD'
              : 'How many XOF for 1 CAD'}
          </p>
        </div>

        {/* XOF to CAD Rate */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Taux XOF → CAD' : 'XOF → CAD Rate'}
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="number"
              step="0.0001"
              value={formData.xof_to_cad}
              onChange={(e) => setFormData({ ...formData, xof_to_cad: parseFloat(e.target.value) })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="0.0022"
            />
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {language === 'fr'
              ? 'Combien de CAD pour 1 XOF'
              : 'How many CAD for 1 XOF'}
          </p>
        </div>

        {/* Auto Update Toggle */}
        <div className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <div>
            <p className="font-medium text-slate-900">
              {language === 'fr' ? 'Mise à jour automatique' : 'Auto Update'}
            </p>
            <p className="text-sm text-slate-500">
              {language === 'fr'
                ? 'Actualiser les taux quotidiennement depuis l\'API'
                : 'Refresh rates daily from API'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setFormData({ ...formData, auto_update: !formData.auto_update })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              formData.auto_update ? 'bg-green-500' : 'bg-slate-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.auto_update ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSaving}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all disabled:opacity-50 font-medium"
        >
          <Save className="w-5 h-5" />
          {isSaving
            ? language === 'fr' ? 'Enregistrement...' : 'Saving...'
            : language === 'fr' ? 'Enregistrer les taux' : 'Save Rates'}
        </button>
      </form>
    </div>
  )
}
