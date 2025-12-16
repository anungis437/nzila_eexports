import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { X, Ship, MapPin, Calendar } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Shipment, ShipmentFormData } from '../types'

interface ShipmentFormModalProps {
  isOpen: boolean
  onClose: () => void
  shipment?: Shipment
  dealId?: number
}

export default function ShipmentFormModal({ isOpen, onClose, shipment, dealId }: ShipmentFormModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const isEdit = !!shipment

  const [formData, setFormData] = useState<ShipmentFormData>({
    deal: dealId || 0,
    tracking_number: '',
    shipping_company: '',
    origin_port: '',
    destination_port: '',
    destination_country: '',
    status: 'pending',
    estimated_departure: '',
    estimated_arrival: '',
    notes: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch deal details if dealId provided
  const { data: deal } = useQuery({
    queryKey: ['deal', dealId],
    queryFn: () => api.getDeal(dealId!),
    enabled: isOpen && !!dealId && !shipment,
  })

  useEffect(() => {
    if (shipment) {
      setFormData({
        deal: shipment.deal,
        tracking_number: shipment.tracking_number,
        shipping_company: shipment.shipping_company,
        origin_port: shipment.origin_port,
        destination_port: shipment.destination_port,
        destination_country: shipment.destination_country,
        status: shipment.status,
        estimated_departure: shipment.estimated_departure || '',
        estimated_arrival: shipment.estimated_arrival || '',
        notes: shipment.notes || '',
      })
    }
  }, [shipment])

  const mutation = useMutation({
    mutationFn: async (data: ShipmentFormData) => {
      if (isEdit && shipment) {
        return api.updateShipment(shipment.id, data)
      }
      return api.createShipment(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['deals'] })
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
      deal: dealId || 0,
      tracking_number: '',
      shipping_company: '',
      origin_port: '',
      destination_port: '',
      destination_country: '',
      status: 'pending',
      estimated_departure: '',
      estimated_arrival: '',
      notes: '',
    })
    setErrors({})
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    // Validation
    if (!formData.tracking_number) {
      setErrors({ tracking_number: language === 'fr' ? 'Numéro de suivi requis' : 'Tracking number required' })
      return
    }
    if (!formData.shipping_company) {
      setErrors({ shipping_company: language === 'fr' ? 'Compagnie requise' : 'Shipping company required' })
      return
    }
    if (!formData.origin_port) {
      setErrors({ origin_port: language === 'fr' ? 'Port d\'origine requis' : 'Origin port required' })
      return
    }
    if (!formData.destination_port) {
      setErrors({ destination_port: language === 'fr' ? 'Port de destination requis' : 'Destination port required' })
      return
    }

    mutation.mutate(formData)
  }

  if (!isOpen) return null

  const statusOptions = [
    { value: 'pending', label: language === 'fr' ? 'En attente' : 'Pending' },
    { value: 'in_transit', label: language === 'fr' ? 'En transit' : 'In Transit' },
    { value: 'customs', label: language === 'fr' ? 'En douane' : 'At Customs' },
    { value: 'delivered', label: language === 'fr' ? 'Livré' : 'Delivered' },
    { value: 'delayed', label: language === 'fr' ? 'Retardé' : 'Delayed' },
  ]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Ship className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-slate-900">
              {isEdit
                ? language === 'fr' ? 'Modifier l\'envoi' : 'Edit Shipment'
                : language === 'fr' ? 'Créer un envoi' : 'Create Shipment'}
            </h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Deal Info */}
          {deal && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-900 mb-1">
                {language === 'fr' ? 'Envoi pour la transaction #' : 'Shipment for Deal #'}{dealId}
              </p>
              {deal.vehicle_details && (
                <p className="font-semibold text-slate-900">
                  {deal.vehicle_details.year} {deal.vehicle_details.make} {deal.vehicle_details.model}
                </p>
              )}
            </div>
          )}

          {/* Tracking Number */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Numéro de suivi' : 'Tracking Number'} *
            </label>
            <input
              type="text"
              required
              value={formData.tracking_number}
              onChange={(e) => setFormData({ ...formData, tracking_number: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ABC123456789"
            />
            {errors.tracking_number && <p className="text-red-500 text-sm mt-1">{errors.tracking_number}</p>}
          </div>

          {/* Shipping Company */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Compagnie maritime' : 'Shipping Company'} *
            </label>
            <input
              type="text"
              required
              value={formData.shipping_company}
              onChange={(e) => setFormData({ ...formData, shipping_company: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Maersk, MSC, CMA CGM..."
            />
            {errors.shipping_company && <p className="text-red-500 text-sm mt-1">{errors.shipping_company}</p>}
          </div>

          {/* Ports */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  {language === 'fr' ? 'Port d\'origine' : 'Origin Port'} *
                </div>
              </label>
              <input
                type="text"
                required
                value={formData.origin_port}
                onChange={(e) => setFormData({ ...formData, origin_port: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Montreal, QC"
              />
              {errors.origin_port && <p className="text-red-500 text-sm mt-1">{errors.origin_port}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  {language === 'fr' ? 'Port de destination' : 'Destination Port'} *
                </div>
              </label>
              <input
                type="text"
                required
                value={formData.destination_port}
                onChange={(e) => setFormData({ ...formData, destination_port: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Dakar, Senegal"
              />
              {errors.destination_port && <p className="text-red-500 text-sm mt-1">{errors.destination_port}</p>}
            </div>
          </div>

          {/* Destination Country */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Pays de destination' : 'Destination Country'}
            </label>
            <input
              type="text"
              value={formData.destination_country}
              onChange={(e) => setFormData({ ...formData, destination_country: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Senegal, Benin, Togo..."
            />
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Statut' : 'Status'}
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {statusOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {language === 'fr' ? 'Départ prévu' : 'Est. Departure'}
                </div>
              </label>
              <input
                type="date"
                value={formData.estimated_departure}
                onChange={(e) => setFormData({ ...formData, estimated_departure: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {language === 'fr' ? 'Arrivée prévue' : 'Est. Arrival'}
                </div>
              </label>
              <input
                type="date"
                value={formData.estimated_arrival}
                onChange={(e) => setFormData({ ...formData, estimated_arrival: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
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
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50"
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
