import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { X } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Lead, LeadFormData, Vehicle } from '../types'

interface LeadFormModalProps {
  isOpen: boolean
  onClose: () => void
  lead?: Lead
}

export default function LeadFormModal({ isOpen, onClose, lead }: LeadFormModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const isEdit = !!lead

  const [formData, setFormData] = useState<LeadFormData>({
    vehicle: 0,
    buyer: 0,
    broker: undefined,
    status: 'new',
    source: 'website',
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
    enabled: isOpen,
  })

  useEffect(() => {
    if (lead) {
      setFormData({
        vehicle: lead.vehicle,
        buyer: lead.buyer,
        broker: lead.broker,
        status: lead.status,
        source: lead.source,
        notes: lead.notes || '',
      })
    }
  }, [lead])

  const mutation = useMutation({
    mutationFn: async (data: LeadFormData) => {
      if (isEdit && lead) {
        return api.updateLead(lead.id, data)
      }
      return api.createLead(data)
    },
    onSuccess: () => {
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
      status: 'new',
      source: 'website',
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

    mutation.mutate(formData)
  }

  if (!isOpen) return null

  const statusOptions = [
    { value: 'new', label: language === 'fr' ? 'Nouveau' : 'New' },
    { value: 'contacted', label: language === 'fr' ? 'Contacté' : 'Contacted' },
    { value: 'qualified', label: language === 'fr' ? 'Qualifié' : 'Qualified' },
    { value: 'negotiating', label: language === 'fr' ? 'Négociation' : 'Negotiating' },
    { value: 'converted', label: language === 'fr' ? 'Converti' : 'Converted' },
    { value: 'lost', label: language === 'fr' ? 'Perdu' : 'Lost' },
  ]

  const sourceOptions = [
    { value: 'website', label: language === 'fr' ? 'Site Web' : 'Website' },
    { value: 'referral', label: language === 'fr' ? 'Référence' : 'Referral' },
    { value: 'broker', label: language === 'fr' ? 'Courtier' : 'Broker' },
    { value: 'direct', label: language === 'fr' ? 'Direct' : 'Direct' },
  ]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">
            {isEdit
              ? language === 'fr' ? 'Modifier le prospect' : 'Edit Lead'
              : language === 'fr' ? 'Ajouter un prospect' : 'Add Lead'}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Vehicle Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Véhicule' : 'Vehicle'} *
            </label>
            <select
              required
              value={formData.vehicle}
              onChange={(e) => setFormData({ ...formData, vehicle: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            >
              <option value="0">
                {language === 'fr' ? 'Sélectionner un véhicule' : 'Select a vehicle'}
              </option>
              {vehicles.map((vehicle: Vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.year} {vehicle.make} {vehicle.model} - {vehicle.vin}
                </option>
              ))}
            </select>
            {errors.vehicle && <p className="text-red-500 text-sm mt-1">{errors.vehicle}</p>}
          </div>

          {/* Buyer Input (for now, just ID until we have user selection) */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'ID Acheteur' : 'Buyer ID'} *
            </label>
            <input
              type="number"
              required
              min="1"
              value={formData.buyer || ''}
              onChange={(e) => setFormData({ ...formData, buyer: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Ex: 1' : 'e.g. 1'}
            />
            {errors.buyer && <p className="text-red-500 text-sm mt-1">{errors.buyer}</p>}
            <p className="text-xs text-slate-500 mt-1">
              {language === 'fr' 
                ? 'Entrez l\'ID de l\'acheteur (temporaire - la sélection sera ajoutée)'
                : 'Enter buyer ID (temporary - selection will be added)'}
            </p>
          </div>

          {/* Broker (Optional) */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Courtier' : 'Broker'} ({language === 'fr' ? 'Optionnel' : 'Optional'})
            </label>
            <input
              type="number"
              min="1"
              value={formData.broker || ''}
              onChange={(e) => setFormData({ ...formData, broker: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'ID du courtier' : 'Broker ID'}
            />
          </div>

          {/* Status & Source */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                {language === 'fr' ? 'Statut' : 'Status'} *
              </label>
              <select
                required
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as Lead['status'] })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              >
                {statusOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                {language === 'fr' ? 'Source' : 'Source'} *
              </label>
              <select
                required
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value as Lead['source'] })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              >
                {sourceOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Notes' : 'Notes'}
            </label>
            <textarea
              rows={4}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder={language === 'fr' 
                ? 'Informations supplémentaires...'
                : 'Additional information...'}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              {language === 'fr' ? 'Annuler' : 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all disabled:opacity-50"
            >
              {mutation.isPending
                ? language === 'fr' ? 'Enregistrement...' : 'Saving...'
                : isEdit
                  ? language === 'fr' ? 'Mettre à jour' : 'Update'
                  : language === 'fr' ? 'Ajouter' : 'Add'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
