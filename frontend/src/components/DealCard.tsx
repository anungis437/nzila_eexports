import { Deal } from '../types'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import { Car, User, DollarSign, Calendar, FileText, CheckCircle, Clock, Package, Truck } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface DealCardProps {
  deal: Deal
  onClick?: () => void
}

export default function DealCard({ deal, onClick }: DealCardProps) {
  const { language, formatCurrency } = useLanguage()
  const { user } = useAuth()
  const locale = language === 'fr' ? fr : enUS
  const isBuyer = user?.role === 'buyer'

  const getStatusColor = (status: Deal['status']) => {
    const colors = {
      pending_docs: 'bg-slate-100 text-slate-800',
      docs_verified: 'bg-blue-100 text-blue-800',
      payment_pending: 'bg-amber-100 text-amber-800',
      payment_received: 'bg-green-100 text-green-800',
      ready_to_ship: 'bg-purple-100 text-purple-800',
      shipped: 'bg-indigo-100 text-indigo-800',
      completed: 'bg-emerald-100 text-emerald-800',
      cancelled: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-slate-100 text-slate-800'
  }

  const getStatusLabel = (status: Deal['status']) => {
    if (isBuyer) {
      const buyerLabels = {
        pending_docs: language === 'fr' ? 'Documents requis' : 'Documents Needed',
        docs_verified: language === 'fr' ? 'Vérification complétée' : 'Verification Complete',
        payment_pending: language === 'fr' ? 'En attente de paiement' : 'Awaiting Payment',
        payment_received: language === 'fr' ? 'Paiement confirmé' : 'Payment Confirmed',
        ready_to_ship: language === 'fr' ? 'Prêt pour expédition' : 'Ready for Shipping',
        shipped: language === 'fr' ? 'En transit' : 'In Transit',
        completed: language === 'fr' ? 'Livré' : 'Delivered',
        cancelled: language === 'fr' ? 'Annulé' : 'Cancelled',
      }
      return buyerLabels[status] || status
    }
    
    const labels = {
      pending_docs: language === 'fr' ? 'En attente docs' : 'Pending Docs',
      docs_verified: language === 'fr' ? 'Docs vérifiés' : 'Docs Verified',
      payment_pending: language === 'fr' ? 'Paiement en attente' : 'Payment Pending',
      payment_received: language === 'fr' ? 'Paiement reçu' : 'Payment Received',
      ready_to_ship: language === 'fr' ? 'Prêt à expédier' : 'Ready to Ship',
      shipped: language === 'fr' ? 'Expédié' : 'Shipped',
      completed: language === 'fr' ? 'Complété' : 'Completed',
      cancelled: language === 'fr' ? 'Annulé' : 'Cancelled',
    }
    return labels[status] || status
  }

  const getPaymentStatusIcon = (status: Deal['payment_status']) => {
    if (status === 'paid') return <CheckCircle className="w-4 h-4 text-green-600" />
    if (status === 'partial') return <Clock className="w-4 h-4 text-amber-600" />
    return <Clock className="w-4 h-4 text-slate-400" />
  }
  
  const getPaymentStatusLabel = (status: Deal['payment_status']) => {
    const labels = {
      pending: language === 'fr' ? 'En attente' : 'Pending',
      partial: language === 'fr' ? 'Partiel' : 'Partial',
      paid: language === 'fr' ? 'Payé' : 'Paid',
      refunded: language === 'fr' ? 'Remboursé' : 'Refunded',
      failed: language === 'fr' ? 'Échoué' : 'Failed',
    }
    return labels[status] || status
  }

  const getProgressPercentage = (status: Deal['status']) => {
    const progress = {
      pending_docs: 10,
      docs_verified: 25,
      payment_pending: 40,
      payment_received: 60,
      ready_to_ship: 75,
      shipped: 90,
      completed: 100,
      cancelled: 0,
    }
    return progress[status] || 0
  }

  const progress = getProgressPercentage(deal.status)

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg border border-slate-200 hover:border-amber-400 hover:shadow-lg transition-all cursor-pointer group overflow-hidden"
    >
      {/* Progress Bar */}
      <div className="h-1 bg-slate-100">
        <div
          className={`h-full transition-all duration-500 ${
            deal.status === 'completed'
              ? 'bg-gradient-to-r from-green-500 to-emerald-600'
              : deal.status === 'cancelled'
              ? 'bg-gradient-to-r from-red-500 to-red-600'
              : 'bg-gradient-to-r from-amber-500 to-amber-600'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-slate-900 group-hover:text-amber-600 transition-colors">
                {isBuyer
                  ? (language === 'fr' ? 'Achat' : 'Purchase') + ` #${deal.id}`
                  : (language === 'fr' ? 'Transaction' : 'Deal') + ` #${deal.id}`
                }
              </h3>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(deal.status)}`}>
                {getStatusLabel(deal.status)}
              </span>
            </div>
            {!isBuyer && (
              <p className="text-xs text-slate-500">
                {deal.buyer_name || `Buyer #${deal.buyer}`}
              </p>
            )}
          </div>
        </div>

        {/* Vehicle Info */}
        {deal.vehicle_details && (
          <div className="flex items-center gap-2 text-sm text-slate-700 mb-3 p-2 bg-slate-50 rounded">
            <Car className="w-4 h-4 flex-shrink-0 text-slate-400" />
            <span className="truncate">
              {deal.vehicle_details.year} {deal.vehicle_details.make} {deal.vehicle_details.model}
            </span>
          </div>
        )}

        {/* Price & Payment */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-slate-400" />
            <span className="text-lg font-bold text-slate-900">
              {formatCurrency(parseFloat(deal.agreed_price_cad))}
            </span>
          </div>
          <div className="flex items-center gap-1">
            {getPaymentStatusIcon(deal.payment_status)}
            <span className="text-xs text-slate-600 capitalize">
              {getPaymentStatusLabel(deal.payment_status)}
            </span>
          </div>
        </div>

        {/* Broker & Dealer */}
        <div className="space-y-1 mb-3">
          {deal.dealer_name && (
            <div className="flex items-center gap-2 text-xs text-slate-600">
              <User className="w-3.5 h-3.5" />
              <span className="truncate">{language === 'fr' ? 'Dealer:' : 'Dealer:'} {deal.dealer_name}</span>
            </div>
          )}
          {deal.broker_name && (
            <div className="flex items-center gap-2 text-xs text-slate-600">
              <User className="w-3.5 h-3.5" />
              <span className="truncate">{language === 'fr' ? 'Broker:' : 'Broker:'} {deal.broker_name}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <Calendar className="w-3.5 h-3.5" />
            <span>
              {formatDistanceToNow(new Date(deal.created_at), {
                addSuffix: true,
                locale,
              })}
            </span>
          </div>
          {deal.documents && deal.documents.length > 0 && (
            <div className="flex items-center gap-1 text-xs text-slate-500">
              <FileText className="w-3.5 h-3.5" />
              <span>{deal.documents.length}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
