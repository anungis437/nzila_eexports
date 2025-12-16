import { Commission } from '../types'
import { useLanguage } from '../contexts/LanguageContext'
import { DollarSign, User, Calendar, CheckCircle2, Clock, XCircle, AlertCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface CommissionCardProps {
  commission: Commission
  onClick?: () => void
}

export default function CommissionCard({ commission, onClick }: CommissionCardProps) {
  const { language } = useLanguage()
  const locale = language === 'fr' ? fr : enUS

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-amber-100 text-amber-700 border-amber-200',
      approved: 'bg-blue-100 text-blue-700 border-blue-200',
      paid: 'bg-green-100 text-green-700 border-green-200',
      cancelled: 'bg-red-100 text-red-700 border-red-200',
    }
    return colors[status] || colors.pending
  }

  const getStatusIcon = (status: string) => {
    if (status === 'paid') return <CheckCircle2 className="w-4 h-4" />
    if (status === 'approved') return <Clock className="w-4 h-4" />
    if (status === 'cancelled') return <XCircle className="w-4 h-4" />
    return <AlertCircle className="w-4 h-4" />
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      pending: { en: 'Pending', fr: 'En attente' },
      approved: { en: 'Approved', fr: 'Approuvé' },
      paid: { en: 'Paid', fr: 'Payé' },
      cancelled: { en: 'Cancelled', fr: 'Annulé' },
    }
    return labels[status]?.[language] || status
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      broker: { en: 'Broker Commission', fr: 'Commission courtier' },
      dealer: { en: 'Dealer Commission', fr: 'Commission revendeur' },
    }
    return labels[type]?.[language] || type
  }

  return (
    <div
      onClick={onClick}
      className={`bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-all ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
            <DollarSign className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">
              {getTypeLabel(commission.commission_type)}
            </h3>
            <p className="text-sm text-slate-500">
              {language === 'fr' ? 'Transaction #' : 'Deal #'}{commission.deal_id}
            </p>
          </div>
        </div>
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${getStatusColor(commission.status)}`}>
          {getStatusIcon(commission.status)}
          {getStatusLabel(commission.status)}
        </div>
      </div>

      {/* Amount */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-3xl font-bold text-green-600">
            ${parseFloat(commission.amount_cad).toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className="text-sm text-slate-500">CAD</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-700 font-medium">
            {parseFloat(commission.percentage).toFixed(1)}%
          </span>
          <span>{language === 'fr' ? 'du prix convenu' : 'of agreed price'}</span>
        </div>
      </div>

      {/* Recipient Info */}
      <div className="flex items-center gap-2 mb-3 pb-3 border-b border-slate-100">
        <User className="w-4 h-4 text-slate-400" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-slate-600 truncate">
            {commission.recipient?.username || commission.recipient?.email || language === 'fr' ? 'Bénéficiaire' : 'Recipient'}
          </p>
        </div>
      </div>

      {/* Timestamps */}
      <div className="space-y-1.5">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Calendar className="w-3.5 h-3.5" />
          <span>
            {language === 'fr' ? 'Créé' : 'Created'}{' '}
            {formatDistanceToNow(new Date(commission.created_at), { addSuffix: true, locale })}
          </span>
        </div>
        
        {commission.approved_at && (
          <div className="flex items-center gap-2 text-xs text-blue-600">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>
              {language === 'fr' ? 'Approuvé' : 'Approved'}{' '}
              {formatDistanceToNow(new Date(commission.approved_at), { addSuffix: true, locale })}
            </span>
          </div>
        )}
        
        {commission.paid_at && (
          <div className="flex items-center gap-2 text-xs text-green-600">
            <DollarSign className="w-3.5 h-3.5" />
            <span>
              {language === 'fr' ? 'Payé' : 'Paid'}{' '}
              {formatDistanceToNow(new Date(commission.paid_at), { addSuffix: true, locale })}
            </span>
          </div>
        )}
      </div>

      {/* Notes Preview */}
      {commission.notes && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <p className="text-xs text-slate-600 line-clamp-2">{commission.notes}</p>
        </div>
      )}
    </div>
  )
}
