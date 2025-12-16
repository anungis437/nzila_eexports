import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import {
  X,
  Ship,
  MapPin,
  Calendar,
  Package,
  TrendingUp,
  Navigation,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Plus,
} from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { format, formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface ShipmentDetailModalProps {
  isOpen: boolean
  onClose: () => void
  shipmentId: number
}

export default function ShipmentDetailModal({
  isOpen,
  onClose,
  shipmentId,
}: ShipmentDetailModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const locale = language === 'fr' ? fr : enUS
  const [activeTab, setActiveTab] = useState<'details' | 'tracking'>('details')
  const [newUpdate, setNewUpdate] = useState({ location: '', status: '', description: '' })

  const { data: shipment, isLoading } = useQuery({
    queryKey: ['shipment', shipmentId],
    queryFn: () => api.getShipment(shipmentId),
    enabled: isOpen,
  })

  const updateStatusMutation = useMutation({
    mutationFn: (status: string) => api.updateShipment(shipmentId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId] })
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
    },
  })

  const addTrackingUpdateMutation = useMutation({
    mutationFn: (data: any) => api.addShipmentUpdate(shipmentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId] })
      setNewUpdate({ location: '', status: '', description: '' })
    },
  })

  if (!isOpen) return null

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto" />
        </div>
      </div>
    )
  }

  if (!shipment) return null

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-slate-100 text-slate-700 border-slate-200',
      in_transit: 'bg-blue-100 text-blue-700 border-blue-200',
      customs: 'bg-amber-100 text-amber-700 border-amber-200',
      delivered: 'bg-green-100 text-green-700 border-green-200',
      delayed: 'bg-red-100 text-red-700 border-red-200',
    }
    return colors[status] || colors.pending
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      pending: { en: 'Pending', fr: 'En attente' },
      in_transit: { en: 'In Transit', fr: 'En transit' },
      customs: { en: 'At Customs', fr: 'En douane' },
      delivered: { en: 'Delivered', fr: 'Livré' },
      delayed: { en: 'Delayed', fr: 'Retardé' },
    }
    return labels[status]?.[language] || status
  }

  const statusWorkflow = ['pending', 'in_transit', 'customs', 'delivered']
  const getNextStatus = () => {
    const currentIndex = statusWorkflow.indexOf(shipment.status)
    return currentIndex < statusWorkflow.length - 1 ? statusWorkflow[currentIndex + 1] : null
  }

  const nextStatus = getNextStatus()
  const canAdvance = nextStatus && shipment.status !== 'delivered' && shipment.status !== 'delayed'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Ship className="w-6 h-6 text-white" />
            <div>
              <h2 className="text-xl font-bold text-white">
                {shipment.tracking_number}
              </h2>
              <p className="text-blue-100 text-sm">{shipment.shipping_company}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-white hover:text-blue-100">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Status Badge & Progress */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold border ${getStatusColor(shipment.status)}`}>
              {shipment.status === 'delivered' && <CheckCircle2 className="w-4 h-4" />}
              {shipment.status === 'delayed' && <AlertTriangle className="w-4 h-4" />}
              {shipment.status === 'in_transit' && <Ship className="w-4 h-4" />}
              {shipment.status === 'pending' && <Clock className="w-4 h-4" />}
              {getStatusLabel(shipment.status)}
            </div>
            {canAdvance && (
              <button
                onClick={() => updateStatusMutation.mutate(nextStatus)}
                disabled={updateStatusMutation.isPending}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-sm font-semibold rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50"
              >
                {language === 'fr' ? 'Avancer vers' : 'Advance to'} {getStatusLabel(nextStatus)}
              </button>
            )}
          </div>

          {/* Progress Bar */}
          <div className="relative h-2 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500"
              style={{
                width: `${(statusWorkflow.indexOf(shipment.status) / (statusWorkflow.length - 1)) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-slate-200">
          <div className="flex px-6">
            {(['details', 'tracking'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                {tab === 'details'
                  ? language === 'fr' ? 'Détails' : 'Details'
                  : language === 'fr' ? 'Suivi' : 'Tracking'}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'details' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Route */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Navigation className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">
                    {language === 'fr' ? 'Itinéraire' : 'Route'}
                  </h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-xs text-blue-700">
                      {language === 'fr' ? 'Origine:' : 'Origin:'}
                    </span>
                    <p className="font-medium text-slate-900">{shipment.origin_port}</p>
                  </div>
                  <div className="flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <span className="text-xs text-blue-700">
                      {language === 'fr' ? 'Destination:' : 'Destination:'}
                    </span>
                    <p className="font-medium text-slate-900">{shipment.destination_port}</p>
                    <p className="text-sm text-slate-600">{shipment.destination_country}</p>
                  </div>
                </div>
              </div>

              {/* Dates */}
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Calendar className="w-5 h-5 text-amber-600" />
                  <h3 className="font-semibold text-slate-900">
                    {language === 'fr' ? 'Dates' : 'Dates'}
                  </h3>
                </div>
                <div className="space-y-2">
                  {shipment.estimated_departure && (
                    <div>
                      <span className="text-xs text-amber-700">
                        {language === 'fr' ? 'Départ prévu:' : 'Est. Departure:'}
                      </span>
                      <p className="text-sm text-slate-900">
                        {format(new Date(shipment.estimated_departure), 'MMM dd, yyyy', { locale })}
                      </p>
                    </div>
                  )}
                  {shipment.actual_departure && (
                    <div>
                      <span className="text-xs text-green-700">
                        {language === 'fr' ? 'Départ réel:' : 'Actual Departure:'}
                      </span>
                      <p className="text-sm text-slate-900">
                        {format(new Date(shipment.actual_departure), 'MMM dd, yyyy', { locale })}
                      </p>
                    </div>
                  )}
                  {shipment.estimated_arrival && (
                    <div>
                      <span className="text-xs text-amber-700">
                        {language === 'fr' ? 'Arrivée prévue:' : 'Est. Arrival:'}
                      </span>
                      <p className="text-sm text-slate-900">
                        {format(new Date(shipment.estimated_arrival), 'MMM dd, yyyy', { locale })}
                      </p>
                    </div>
                  )}
                  {shipment.actual_arrival && (
                    <div>
                      <span className="text-xs text-green-700">
                        {language === 'fr' ? 'Arrivée réelle:' : 'Actual Arrival:'}
                      </span>
                      <p className="text-sm text-slate-900">
                        {format(new Date(shipment.actual_arrival), 'MMM dd, yyyy', { locale })}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Vehicle */}
              {shipment.vehicle_details && (
                <div className="col-span-full bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Package className="w-5 h-5 text-slate-600" />
                    <h3 className="font-semibold text-slate-900">
                      {language === 'fr' ? 'Véhicule' : 'Vehicle'}
                    </h3>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Véhicule:' : 'Vehicle:'}
                      </span>
                      <p className="font-medium text-slate-900">
                        {shipment.vehicle_details.year} {shipment.vehicle_details.make} {shipment.vehicle_details.model}
                      </p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500">VIN:</span>
                      <p className="font-mono text-sm text-slate-900">{shipment.vehicle_details.vin}</p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Couleur:' : 'Color:'}
                      </span>
                      <p className="text-sm text-slate-900 capitalize">{shipment.vehicle_details.color}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Notes */}
              {shipment.notes && (
                <div className="col-span-full bg-white border border-slate-200 rounded-xl p-5">
                  <h3 className="font-semibold text-slate-900 mb-2">
                    {language === 'fr' ? 'Notes' : 'Notes'}
                  </h3>
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">{shipment.notes}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'tracking' && (
            <div>
              {/* Add Update Form */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5 mb-6">
                <h3 className="font-semibold text-slate-900 mb-4">
                  {language === 'fr' ? 'Ajouter une mise à jour' : 'Add Tracking Update'}
                </h3>
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder={language === 'fr' ? 'Emplacement' : 'Location'}
                    value={newUpdate.location}
                    onChange={(e) => setNewUpdate({ ...newUpdate, location: e.target.value })}
                    className="w-full px-4 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder={language === 'fr' ? 'Statut' : 'Status'}
                    value={newUpdate.status}
                    onChange={(e) => setNewUpdate({ ...newUpdate, status: e.target.value })}
                    className="w-full px-4 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <textarea
                    rows={2}
                    placeholder={language === 'fr' ? 'Description (optionnel)' : 'Description (optional)'}
                    value={newUpdate.description}
                    onChange={(e) => setNewUpdate({ ...newUpdate, description: e.target.value })}
                    className="w-full px-4 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={() => {
                      if (newUpdate.location && newUpdate.status) {
                        addTrackingUpdateMutation.mutate(newUpdate)
                      }
                    }}
                    disabled={!newUpdate.location || !newUpdate.status || addTrackingUpdateMutation.isPending}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50"
                  >
                    <Plus className="w-5 h-5" />
                    {language === 'fr' ? 'Ajouter' : 'Add Update'}
                  </button>
                </div>
              </div>

              {/* Tracking Updates Timeline */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">
                  {language === 'fr' ? 'Historique de suivi' : 'Tracking History'}
                </h3>
                
                {shipment.updates && shipment.updates.length > 0 ? (
                  <div className="relative space-y-6">
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />
                    
                    {shipment.updates.map((update: any) => (
                      <div key={update.id} className="relative flex gap-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center z-10">
                          <MapPin className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1 pb-6">
                          <div className="bg-white border border-slate-200 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <p className="font-semibold text-slate-900">{update.location}</p>
                                <p className="text-sm text-blue-600">{update.status}</p>
                              </div>
                              <span className="text-xs text-slate-500">
                                {formatDistanceToNow(new Date(update.created_at), { addSuffix: true, locale })}
                              </span>
                            </div>
                            {update.description && (
                              <p className="text-sm text-slate-600 mt-2">{update.description}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MapPin className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                    <p className="text-slate-500">
                      {language === 'fr' 
                        ? 'Aucune mise à jour de suivi pour le moment'
                        : 'No tracking updates yet'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Calendar className="w-4 h-4" />
            <span>
              {language === 'fr' ? 'Créé' : 'Created'} {formatDistanceToNow(new Date(shipment.created_at), { addSuffix: true, locale })}
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
          >
            {language === 'fr' ? 'Fermer' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  )
}
