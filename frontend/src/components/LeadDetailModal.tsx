import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Car, User, Calendar, DollarSign, Tag, MessageSquare, Clock, CheckCircle } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Lead } from '../types'
import { format } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface LeadDetailModalProps {
  isOpen: boolean
  onClose: () => void
  lead: Lead
  onEdit: () => void
}

export default function LeadDetailModal({ isOpen, onClose, lead, onEdit }: LeadDetailModalProps) {
  const { language, formatCurrency } = useLanguage()
  const queryClient = useQueryClient()
  const locale = language === 'fr' ? fr : enUS

  const convertToDealmutation = useMutation({
    mutationFn: async () => {
      // Create deal from lead
      const dealData = {
        lead: lead.id,
        vehicle: lead.vehicle,
        buyer: lead.buyer,
        dealer: lead.vehicle_details?.dealer,
        broker: lead.broker,
        agreed_price_cad: lead.vehicle_details?.price_cad,
      }
      return api.createDeal(dealData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] })
      queryClient.invalidateQueries({ queryKey: ['deals'] })
      onClose()
    },
  })

  if (!isOpen) return null

  const getStatusColor = (status: Lead['status']) => {
    const colors = {
      new: 'bg-slate-100 text-slate-800',
      contacted: 'bg-blue-100 text-blue-800',
      qualified: 'bg-green-100 text-green-800',
      negotiating: 'bg-amber-100 text-amber-800',
      converted: 'bg-purple-100 text-purple-800',
      lost: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-slate-100 text-slate-800'
  }

  const getStatusLabel = (status: Lead['status']) => {
    const labels = {
      new: language === 'fr' ? 'Nouveau' : 'New',
      contacted: language === 'fr' ? 'Contacté' : 'Contacted',
      qualified: language === 'fr' ? 'Qualifié' : 'Qualified',
      negotiating: language === 'fr' ? 'Négociation' : 'Negotiating',
      converted: language === 'fr' ? 'Converti' : 'Converted',
      lost: language === 'fr' ? 'Perdu' : 'Lost',
    }
    return labels[status] || status
  }

  const getSourceLabel = (source: Lead['source']) => {
    const labels = {
      website: language === 'fr' ? 'Site Web' : 'Website',
      referral: language === 'fr' ? 'Référence' : 'Referral',
      broker: language === 'fr' ? 'Courtier' : 'Broker',
      direct: language === 'fr' ? 'Direct' : 'Direct',
    }
    return labels[source] || source
  }

  const canConvertToDeal = lead.status === 'negotiating' || lead.status === 'qualified'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-slate-900">
              {language === 'fr' ? 'Détails du prospect' : 'Lead Details'}
            </h2>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(lead.status)}`}>
              {getStatusLabel(lead.status)}
            </span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Main Info */}
          <div className="grid grid-cols-2 gap-6">
            {/* Buyer Info */}
            <div className="bg-slate-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                <User className="w-4 h-4" />
                <span className="font-medium">{language === 'fr' ? 'Acheteur' : 'Buyer'}</span>
              </div>
              <p className="text-lg font-semibold text-slate-900">
                {lead.buyer_name || `Buyer #${lead.buyer}`}
              </p>
            </div>

            {/* Source Info */}
            <div className="bg-slate-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                <Tag className="w-4 h-4" />
                <span className="font-medium">{language === 'fr' ? 'Source' : 'Source'}</span>
              </div>
              <p className="text-lg font-semibold text-slate-900">{getSourceLabel(lead.source)}</p>
            </div>
          </div>

          {/* Vehicle Info */}
          {lead.vehicle_details && (
            <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
              <div className="flex items-center gap-2 text-sm text-amber-800 mb-3">
                <Car className="w-5 h-5" />
                <span className="font-semibold">{language === 'fr' ? 'Véhicule' : 'Vehicle'}</span>
              </div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-1">
                    {lead.vehicle_details.year} {lead.vehicle_details.make} {lead.vehicle_details.model}
                  </h3>
                  <p className="text-sm text-slate-600">
                    VIN: <span className="font-mono">{lead.vehicle_details.vin}</span>
                  </p>
                  <p className="text-sm text-slate-600">
                    {language === 'fr' ? 'Lieu:' : 'Location:'} {lead.vehicle_details.location}
                  </p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-2xl font-bold text-amber-600">
                    <DollarSign className="w-6 h-6" />
                    {formatCurrency(parseFloat(lead.vehicle_details.price_cad))}
                  </div>
                  <p className="text-xs text-slate-600 mt-1">
                    {lead.vehicle_details.status === 'available' 
                      ? (language === 'fr' ? 'Disponible' : 'Available')
                      : (language === 'fr' ? 'Non disponible' : 'Not available')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Broker Info */}
          {lead.broker_name && (
            <div className="bg-slate-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                <User className="w-4 h-4" />
                <span className="font-medium">{language === 'fr' ? 'Courtier' : 'Broker'}</span>
              </div>
              <p className="text-lg font-semibold text-slate-900">{lead.broker_name}</p>
            </div>
          )}

          {/* Timeline */}
          <div>
            <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              {language === 'fr' ? 'Chronologie' : 'Timeline'}
            </h3>
            <div className="space-y-3">
              {/* Created */}
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
                <div className="flex-1 pb-3 border-b border-slate-200">
                  <p className="font-medium text-slate-900">
                    {language === 'fr' ? 'Prospect créé' : 'Lead created'}
                  </p>
                  <p className="text-sm text-slate-600">
                    {format(new Date(lead.created_at), 'PPpp', { locale })}
                  </p>
                </div>
              </div>

              {/* Last Contacted */}
              {lead.last_contacted && (
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <MessageSquare className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1 pb-3 border-b border-slate-200">
                    <p className="font-medium text-slate-900">
                      {language === 'fr' ? 'Dernier contact' : 'Last contacted'}
                    </p>
                    <p className="text-sm text-slate-600">
                      {format(new Date(lead.last_contacted), 'PPpp', { locale })}
                    </p>
                  </div>
                </div>
              )}

              {/* Updated */}
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
                  <Calendar className="w-4 h-4 text-amber-600" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-slate-900">
                    {language === 'fr' ? 'Dernière mise à jour' : 'Last updated'}
                  </p>
                  <p className="text-sm text-slate-600">
                    {format(new Date(lead.updated_at), 'PPpp', { locale })}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {lead.notes && (
            <div className="bg-slate-50 rounded-xl p-4">
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                {language === 'fr' ? 'Notes' : 'Notes'}
              </h3>
              <p className="text-slate-700 whitespace-pre-wrap">{lead.notes}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-slate-200">
            <button
              onClick={onEdit}
              className="flex-1 px-4 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              {language === 'fr' ? 'Modifier' : 'Edit'}
            </button>
            {canConvertToDeal && (
              <button
                onClick={() => convertToDealmutation.mutate()}
                disabled={convertToDealmutation.isPending}
                className="flex-1 px-4 py-2.5 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all disabled:opacity-50"
              >
                {convertToDealmutation.isPending
                  ? (language === 'fr' ? 'Conversion...' : 'Converting...')
                  : (language === 'fr' ? 'Convertir en transaction' : 'Convert to Deal')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
