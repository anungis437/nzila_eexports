import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { X } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Deal, DealFormData, Vehicle } from '../types'

interface DealFormModalProps {
  isOpen: boolean
  onClose: () => void
  deal?: Deal
  leadId?: number
}

export default function DealFormModal({ isOpen, onClose, deal, leadId }: DealFormModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const isEdit = !!deal

  const [formData, setFormData] = useState<DealFormData>({
    vehicle: 0,
    buyer: 0,
    broker: undefined,
    agreed_price_cad: '',
    payment_method: '',
    notes: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch available vehicles
  const { data: vehicles = [] } = useQuery({
    queryKey: ['vehicles', 'available'],
    queryFn: async () => {
      const response = await api.getVehicles({ status: 'available' })
      return Array.isArray(response) ? response : response.results || []
    },
    enabled: isOpen && !deal,
  })

  // Fetch lead details if leadId provided
  const { data: lead } = useQuery({
    queryKey: ['lead', leadId],
    queryFn: () => api.getLead(leadId!),
    enabled: isOpen && !!leadId,
  })

  useEffect(() => {
    if (deal) {
      setFormData({
        vehicle: deal.vehicle,
        buyer: deal.buyer,
        broker: deal.broker,
        agreed_price_cad: deal.agreed_price_cad,
        payment_method: deal.payment_method || '',
        notes: deal.notes || '',
      })
    } else if (lead) {
      // Pre-fill from lead
      setFormData({
        vehicle: lead.vehicle,
        buyer: lead.buyer,
        broker: lead.broker,
        agreed_price_cad: lead.vehicle_details?.price_cad || '',
        payment_method: '',
        notes: lead.notes || '',
      })
    }
  }, [deal, lead])

  const mutation = useMutation({
    mutationFn: async (data: DealFormData) => {
      const payload = {
        ...data,
        lead: leadId,
      }
      if (isEdit && deal) {
        return api.updateDeal(deal.id, payload)
      }
      return api.createDeal(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deals'] })
      queryClient.invalidateQueries({ queryKey: ['leads'] })
      onClose()
      resetForm()
    },
    onError: (error: any) => {
      const errorData = error.response?.data
      if (errorData) {
        setErrors(errorData)
      }
    },
  })

  const resetForm = () => {
    setFormData({
      vehicle: 0,
      buyer: 0,
      broker: undefined,
      agreed_price_cad: '',
      payment_method: '',
      notes: '',
    })
    setErrors({})
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    // Validation
    if (!formData.vehicle) {
      setErrors({ vehicle: language === 'fr' ? 'Véhicule requis' : 'Vehicle required' })
      return
    }
    if (!formData.buyer) {
      setErrors({ buyer: language === 'fr' ? 'Acheteur requis' : 'Buyer required' })
      return
    }
    if (!formData.agreed_price_cad || parseFloat(formData.agreed_price_cad) <= 0) {
      setErrors({ agreed_price_cad: language === 'fr' ? 'Prix invalide' : 'Invalid price' })
      return
    }

    mutation.mutate(formData)
  }

  if (!isOpen) return null

  const paymentMethodOptions = [
    { value: '', label: language === 'fr' ? 'Sélectionner...' : 'Select...' },
    { value: 'bank_transfer', label: language === 'fr' ? 'Virement bancaire' : 'Bank Transfer' },
    { value: 'wire_transfer', label: language === 'fr' ? 'Virement international' : 'Wire Transfer' },
    { value: 'cash', label: language === 'fr' ? 'Espèces' : 'Cash' },
    { value: 'check', label: language === 'fr' ? 'Chèque' : 'Check' },
    { value: 'other', label: language === 'fr' ? 'Autre' : 'Other' },
  ]

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="deal-form-title"
    >
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <h2 id="deal-form-title" className="text-xl font-bold text-slate-900">
            {isEdit
              ? language === 'fr' ? 'Modifier la transaction' : 'Edit Deal'
              : language === 'fr' ? 'Créer une transaction' : 'Create Deal'}
          </h2>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-600"
            aria-label={language === 'fr' ? 'Fermer le formulaire' : 'Close form'}
          >
            <X className="w-6 h-6" aria-hidden="true" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Vehicle Selection */}
          {!lead && (
            <div>
              <label htmlFor="deal-vehicle" className="block text-sm font-medium text-slate-700 mb-1">
                {language === 'fr' ? 'Véhicule' : 'Vehicle'} *
              </label>
              <select
                id="deal-vehicle"
                required
                aria-required="true"
                aria-invalid={!!errors.vehicle}
                aria-describedby={errors.vehicle ? "vehicle-error" : undefined}
                value={formData.vehicle}
                onChange={(e) => setFormData({ ...formData, vehicle: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                disabled={isEdit}
              >
                <option value="0">
                  {language === 'fr' ? 'Sélectionner un véhicule' : 'Select a vehicle'}
                </option>
                {vehicles.map((vehicle: Vehicle) => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.year} {vehicle.make} {vehicle.model} - ${vehicle.price_cad}
                  </option>
                ))}
              </select>
              {errors.vehicle && <p id="vehicle-error" className="text-red-500 text-sm mt-1" role="alert">{errors.vehicle}</p>}
            </div>
          )}

          {lead && (
            <div 
              className="bg-gradient-to-r from-amber-50 to-amber-100 border border-amber-200 rounded-lg p-4"
              role="status"
              aria-label={language === 'fr' ? 'Informations du prospect' : 'Lead information'}
            >
              <p className="text-sm text-amber-900 mb-1">
                {language === 'fr' ? 'Créé depuis le prospect #' : 'Creating from lead #'}{leadId}
              </p>
              {lead.vehicle_details && (
                <p className="font-semibold text-slate-900">
                  {lead.vehicle_details.year} {lead.vehicle_details.make} {lead.vehicle_details.model}
                </p>
              )}
            </div>
          )}

          {/* Buyer ID */}
          <div>
            <label htmlFor="deal-buyer" className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'ID Acheteur' : 'Buyer ID'} *
            </label>
            <input
              id="deal-buyer"
              type="number"
              required
              aria-required="true"
              aria-invalid={!!errors.buyer}
              aria-describedby={errors.buyer ? "buyer-error" : "buyer-help"}
              min="1"
              value={formData.buyer || ''}
              onChange={(e) => setFormData({ ...formData, buyer: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              disabled={isEdit || !!lead}
            />
            {!errors.buyer && <p id="buyer-help" className="text-xs text-slate-500 mt-1 sr-only">Numeric buyer identifier</p>}
            {errors.buyer && <p id="buyer-error" className="text-red-500 text-sm mt-1" role="alert">{errors.buyer}</p>}
          </div>

          {/* Broker (Optional) */}
          <div>
            <label htmlFor="deal-broker" className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Courtier' : 'Broker'} ({language === 'fr' ? 'Optionnel' : 'Optional'})
            </label>
            <input
              id="deal-broker"
              type="number"
              min="1"
              aria-describedby="broker-help"
              value={formData.broker || ''}
              onChange={(e) => setFormData({ ...formData, broker: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            />
            <p id="broker-help" className="text-xs text-slate-500 mt-1 sr-only">Optional broker identifier</p>
          </div>

          {/* Agreed Price */}
          <div>
            <label htmlFor="deal-price" className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Prix convenu' : 'Agreed Price'} (CAD) *
            </label>
            <input
              id="deal-price"
              type="number"
              required
              aria-required="true"
              aria-invalid={!!errors.agreed_price_cad}
              aria-describedby={errors.agreed_price_cad ? "price-error" : undefined}
              min="0"
              step="0.01"
              value={formData.agreed_price_cad}
              onChange={(e) => setFormData({ ...formData, agreed_price_cad: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder="25000.00"
            />
            {errors.agreed_price_cad && <p id="price-error" className="text-red-500 text-sm mt-1" role="alert">{errors.agreed_price_cad}</p>}
          </div>

          {/* Payment Method */}
          <div>
            <label htmlFor="deal-payment-method" className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Mode de paiement' : 'Payment Method'}
            </label>
            <select
              id="deal-payment-method"
              value={formData.payment_method}
              onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            >
              {paymentMethodOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="deal-notes" className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Notes' : 'Notes'}
            </label>
            <textarea
              id="deal-notes"
              rows={4}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder={language === 'fr' 
                ? 'Informations supplémentaires...'
                : 'Additional information...'}
              aria-label={language === 'fr' ? 'Notes additionnelles sur la transaction' : 'Additional deal notes'}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              aria-label={language === 'fr' ? 'Annuler et fermer le formulaire' : 'Cancel and close form'}
            >
              {language === 'fr' ? 'Annuler' : 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all disabled:opacity-50"
              aria-busy={mutation.isPending}
              aria-label={
                mutation.isPending
                  ? language === 'fr' ? 'Enregistrement de la transaction en cours' : 'Saving deal'
                  : isEdit
                    ? language === 'fr' ? 'Mettre à jour la transaction' : 'Update deal'
                    : language === 'fr' ? 'Créer la transaction' : 'Create deal'
              }
            >
              {mutation.isPending
                ? language === 'fr' ? 'Enregistrement...' : 'Saving...'
                : isEdit
                  ? language === 'fr' ? 'Mettre à jour' : 'Update'
                  : language === 'fr' ? 'Créer' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
