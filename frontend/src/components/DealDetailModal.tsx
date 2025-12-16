import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import {
  X,
  Package,
  Calendar,
  DollarSign,
  User,
  FileText,
  TrendingUp,
  Download,
  Upload,
  CheckCircle2,
  Clock,
  AlertCircle,
} from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { formatDistanceToNow } from 'date-fns'

interface DealDetailModalProps {
  isOpen: boolean
  onClose: () => void
  dealId: number
}

export default function DealDetailModal({ isOpen, onClose, dealId }: DealDetailModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'details' | 'documents' | 'timeline'>('details')

  const { data: deal, isLoading } = useQuery({
    queryKey: ['deal', dealId],
    queryFn: () => api.getDeal(dealId),
    enabled: isOpen,
  })

  const updateStatusMutation = useMutation({
    mutationFn: (status: string) => api.updateDeal(dealId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deal', dealId] })
      queryClient.invalidateQueries({ queryKey: ['deals'] })
    },
  })

  if (!isOpen) return null

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending_docs: 'bg-slate-100 text-slate-700',
      docs_verified: 'bg-blue-100 text-blue-700',
      payment_pending: 'bg-amber-100 text-amber-700',
      payment_received: 'bg-green-100 text-green-700',
      ready_to_ship: 'bg-purple-100 text-purple-700',
      shipped: 'bg-indigo-100 text-indigo-700',
      completed: 'bg-emerald-100 text-emerald-700',
      cancelled: 'bg-red-100 text-red-700',
    }
    return colors[status] || colors.pending_docs
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      pending_docs: { en: 'Pending Documents', fr: 'Documents en attente' },
      docs_verified: { en: 'Documents Verified', fr: 'Documents vérifiés' },
      payment_pending: { en: 'Payment Pending', fr: 'Paiement en attente' },
      payment_received: { en: 'Payment Received', fr: 'Paiement reçu' },
      ready_to_ship: { en: 'Ready to Ship', fr: 'Prêt à expédier' },
      shipped: { en: 'Shipped', fr: 'Expédié' },
      completed: { en: 'Completed', fr: 'Terminé' },
      cancelled: { en: 'Cancelled', fr: 'Annulé' },
    }
    return labels[status]?.[language] || status
  }

  const getPaymentStatusIcon = (status: string) => {
    if (status === 'paid') return <CheckCircle2 className="w-4 h-4 text-green-500" />
    if (status === 'partial') return <Clock className="w-4 h-4 text-amber-500" />
    return <AlertCircle className="w-4 h-4 text-slate-400" />
  }

  const statusWorkflow = [
    'pending_docs',
    'docs_verified',
    'payment_pending',
    'payment_received',
    'ready_to_ship',
    'shipped',
    'completed',
  ]

  const getNextStatus = () => {
    if (!deal) return null
    const currentIndex = statusWorkflow.indexOf(deal.status)
    return currentIndex < statusWorkflow.length - 1 ? statusWorkflow[currentIndex + 1] : null
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto" />
        </div>
      </div>
    )
  }

  if (!deal) return null

  const nextStatus = getNextStatus()

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Package className="w-6 h-6 text-white" />
            <div>
              <h2 className="text-xl font-bold text-white">
                {language === 'fr' ? 'Transaction' : 'Deal'} #{deal.id}
              </h2>
              <p className="text-amber-100 text-sm">
                {deal.vehicle_details
                  ? `${deal.vehicle_details.year} ${deal.vehicle_details.make} ${deal.vehicle_details.model}`
                  : 'Vehicle Details Unavailable'}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-white hover:text-amber-100">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Status Badge & Progress */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <span className={`px-3 py-1.5 rounded-full text-xs font-semibold ${getStatusColor(deal.status)}`}>
              {getStatusLabel(deal.status)}
            </span>
            <div className="flex items-center gap-2">
              {getPaymentStatusIcon(deal.payment_status)}
              <span className="text-sm text-slate-600">
                {deal.payment_status === 'paid'
                  ? language === 'fr' ? 'Payé' : 'Paid'
                  : deal.payment_status === 'partial'
                  ? language === 'fr' ? 'Partiel' : 'Partial'
                  : language === 'fr' ? 'En attente' : 'Pending'}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="relative h-2 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-amber-500 to-amber-600 transition-all duration-500"
              style={{
                width: `${(statusWorkflow.indexOf(deal.status) / (statusWorkflow.length - 1)) * 100}%`,
              }}
            />
          </div>

          {/* Next Action */}
          {nextStatus && deal.status !== 'completed' && deal.status !== 'cancelled' && (
            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                {language === 'fr' ? 'Prochaine étape:' : 'Next step:'} {getStatusLabel(nextStatus)}
              </span>
              <button
                onClick={() => updateStatusMutation.mutate(nextStatus)}
                disabled={updateStatusMutation.isPending}
                className="px-4 py-1.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white text-xs font-semibold rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all disabled:opacity-50"
              >
                {language === 'fr' ? 'Avancer' : 'Advance'}
              </button>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-slate-200">
          <div className="flex px-6">
            {(['details', 'documents', 'timeline'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-amber-500 text-amber-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                {tab === 'details'
                  ? language === 'fr' ? 'Détails' : 'Details'
                  : tab === 'documents'
                  ? language === 'fr' ? 'Documents' : 'Documents'
                  : language === 'fr' ? 'Chronologie' : 'Timeline'}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'details' && (
            <div className="grid grid-cols-2 gap-6">
              {/* Financial Info */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-slate-900">
                    {language === 'fr' ? 'Informations financières' : 'Financial Information'}
                  </h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">
                      {language === 'fr' ? 'Prix convenu:' : 'Agreed Price:'}
                    </span>
                    <span className="font-semibold text-slate-900">
                      ${parseFloat(deal.agreed_price_cad).toLocaleString('en-CA', { minimumFractionDigits: 2 })} CAD
                    </span>
                  </div>
                  {deal.payment_method && (
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-600">
                        {language === 'fr' ? 'Mode de paiement:' : 'Payment Method:'}
                      </span>
                      <span className="text-slate-900 capitalize">{deal.payment_method.replace('_', ' ')}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">
                      {language === 'fr' ? 'Commission:' : 'Commission:'}
                    </span>
                    <span className="font-semibold text-green-600">
                      ${parseFloat(deal.commission_cad || '0').toLocaleString('en-CA', { minimumFractionDigits: 2 })} CAD
                    </span>
                  </div>
                </div>
              </div>

              {/* Parties Involved */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <User className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">
                    {language === 'fr' ? 'Parties impliquées' : 'Parties Involved'}
                  </h3>
                </div>
                <div className="space-y-2">
                  {deal.dealer_name && (
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Revendeur:' : 'Dealer:'}
                      </span>
                      <p className="font-medium text-slate-900">{deal.dealer_name}</p>
                    </div>
                  )}
                  {deal.buyer_name && (
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Acheteur:' : 'Buyer:'}
                      </span>
                      <p className="font-medium text-slate-900">{deal.buyer_name}</p>
                    </div>
                  )}
                  {deal.broker_name && (
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Courtier:' : 'Broker:'}
                      </span>
                      <p className="font-medium text-slate-900">{deal.broker_name}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Vehicle Info */}
              {deal.vehicle_details && (
                <div className="col-span-2 bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Package className="w-5 h-5 text-amber-600" />
                    <h3 className="font-semibold text-slate-900">
                      {language === 'fr' ? 'Détails du véhicule' : 'Vehicle Details'}
                    </h3>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <span className="text-xs text-slate-500">VIN:</span>
                      <p className="font-mono text-sm text-slate-900">{deal.vehicle_details.vin}</p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Kilométrage:' : 'Mileage:'}
                      </span>
                      <p className="text-sm text-slate-900">
                        {deal.vehicle_details.mileage?.toLocaleString()} {deal.vehicle_details.mileage_unit || 'km'}
                      </p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Couleur:' : 'Color:'}
                      </span>
                      <p className="text-sm text-slate-900 capitalize">{deal.vehicle_details.color}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Notes */}
              {deal.notes && (
                <div className="col-span-2 bg-slate-50 border border-slate-200 rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-slate-600" />
                    <h3 className="font-semibold text-slate-900">
                      {language === 'fr' ? 'Notes' : 'Notes'}
                    </h3>
                  </div>
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">{deal.notes}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'documents' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-slate-900">
                  {language === 'fr' ? 'Documents de transaction' : 'Deal Documents'}
                </h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all">
                  <Upload className="w-4 h-4" />
                  {language === 'fr' ? 'Téléverser' : 'Upload'}
                </button>
              </div>

              {/* Document List Placeholder */}
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg hover:border-amber-300 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-slate-400" />
                      <div>
                        <p className="font-medium text-slate-900">Document_{i}.pdf</p>
                        <p className="text-xs text-slate-500">
                          {language === 'fr' ? 'Téléversé il y a' : 'Uploaded'} 2{language === 'fr' ? 'j' : 'd'}
                        </p>
                      </div>
                    </div>
                    <button className="text-amber-600 hover:text-amber-700">
                      <Download className="w-5 h-5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'timeline' && (
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-6">
                {language === 'fr' ? 'Historique de la transaction' : 'Deal Timeline'}
              </h3>
              
              <div className="relative space-y-6">
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200" />

                {/* Timeline Items */}
                <div className="relative flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center z-10">
                    <CheckCircle2 className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 pb-6">
                    <p className="font-semibold text-slate-900">
                      {language === 'fr' ? 'Transaction créée' : 'Deal Created'}
                    </p>
                    <p className="text-sm text-slate-500">
                      {formatDistanceToNow(new Date(deal.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>

                <div className="relative flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center z-10">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-slate-900">
                      {language === 'fr' ? 'Statut actuel:' : 'Current Status:'} {getStatusLabel(deal.status)}
                    </p>
                    <p className="text-sm text-slate-500">
                      {formatDistanceToNow(new Date(deal.updated_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Calendar className="w-4 h-4" />
            <span>
              {language === 'fr' ? 'Créé' : 'Created'} {formatDistanceToNow(new Date(deal.created_at), { addSuffix: true })}
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
