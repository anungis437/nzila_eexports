import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import {
  X,
  DollarSign,
  User,
  Calendar,
  CheckCircle2,
  XCircle,
  FileText,
  AlertCircle,
  Clock,
  Package,
  TrendingUp,
} from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface CommissionDetailModalProps {
  isOpen: boolean
  onClose: () => void
  commissionId: number
}

export default function CommissionDetailModal({
  isOpen,
  onClose,
  commissionId,
}: CommissionDetailModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const locale = language === 'fr' ? fr : enUS
  const [notes, setNotes] = useState('')

  const { data: commission, isLoading } = useQuery({
    queryKey: ['commission', commissionId],
    queryFn: () => api.getCommission(commissionId),
    enabled: isOpen,
  })

  const approveMutation = useMutation({
    mutationFn: () => api.approveCommission(commissionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['commission', commissionId] })
      queryClient.invalidateQueries({ queryKey: ['commissions'] })
    },
  })

  const markPaidMutation = useMutation({
    mutationFn: (paymentNotes: string) =>
      api.markCommissionPaid(commissionId, { notes: paymentNotes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['commission', commissionId] })
      queryClient.invalidateQueries({ queryKey: ['commissions'] })
      setNotes('')
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => api.cancelCommission(commissionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['commission', commissionId] })
      queryClient.invalidateQueries({ queryKey: ['commissions'] })
    },
  })

  if (!isOpen) return null

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto" />
        </div>
      </div>
    )
  }

  if (!commission) return null

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-amber-100 text-amber-700 border-amber-200',
      approved: 'bg-blue-100 text-blue-700 border-blue-200',
      paid: 'bg-green-100 text-green-700 border-green-200',
      cancelled: 'bg-red-100 text-red-700 border-red-200',
    }
    return colors[status] || colors.pending
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      pending: { en: 'Pending Approval', fr: 'En attente d\'approbation' },
      approved: { en: 'Approved - Awaiting Payment', fr: 'Approuvé - En attente de paiement' },
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

  const canApprove = commission.status === 'pending'
  const canMarkPaid = commission.status === 'approved'
  const canCancel = ['pending', 'approved'].includes(commission.status)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <DollarSign className="w-6 h-6 text-white" />
            <div>
              <h2 className="text-xl font-bold text-white">
                {language === 'fr' ? 'Détails de la commission' : 'Commission Details'}
              </h2>
              <p className="text-green-100 text-sm">
                {getTypeLabel(commission.commission_type)} #{commission.id}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-white hover:text-green-100">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Status Badge */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold border ${getStatusColor(commission.status)}`}>
            {commission.status === 'paid' && <CheckCircle2 className="w-4 h-4" />}
            {commission.status === 'approved' && <Clock className="w-4 h-4" />}
            {commission.status === 'pending' && <AlertCircle className="w-4 h-4" />}
            {commission.status === 'cancelled' && <XCircle className="w-4 h-4" />}
            {getStatusLabel(commission.status)}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Amount Card */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <h3 className="font-semibold text-slate-900">
                  {language === 'fr' ? 'Montant de la commission' : 'Commission Amount'}
                </h3>
              </div>
              <div className="flex items-baseline gap-2 mb-2">
                <span className="text-4xl font-bold text-green-600">
                  ${parseFloat(commission.amount_cad).toLocaleString('en-CA', { minimumFractionDigits: 2 })}
                </span>
                <span className="text-lg text-slate-600">CAD</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
                  {parseFloat(commission.percentage).toFixed(1)}%
                </span>
                <span className="text-sm text-slate-600">
                  {language === 'fr' ? 'du prix de la transaction' : 'of deal price'}
                </span>
              </div>
            </div>

            {/* Recipient Info */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <User className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-slate-900">
                  {language === 'fr' ? 'Bénéficiaire' : 'Recipient'}
                </h3>
              </div>
              {commission.recipient && (
                <div className="space-y-2">
                  <div>
                    <span className="text-xs text-slate-500">
                      {language === 'fr' ? 'Nom:' : 'Name:'}
                    </span>
                    <p className="font-medium text-slate-900">
                      {commission.recipient.first_name} {commission.recipient.last_name}
                    </p>
                  </div>
                  <div>
                    <span className="text-xs text-slate-500">Email:</span>
                    <p className="text-slate-900">{commission.recipient.email}</p>
                  </div>
                  {commission.recipient.company && (
                    <div>
                      <span className="text-xs text-slate-500">
                        {language === 'fr' ? 'Entreprise:' : 'Company:'}
                      </span>
                      <p className="text-slate-900">{commission.recipient.company}</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Deal Reference */}
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <Package className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-slate-900">
                  {language === 'fr' ? 'Transaction associée' : 'Related Deal'}
                </h3>
              </div>
              <p className="text-slate-900">
                {language === 'fr' ? 'Transaction' : 'Deal'} #{commission.deal_id}
              </p>
            </div>

            {/* Timeline */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Calendar className="w-5 h-5 text-slate-600" />
                <h3 className="font-semibold text-slate-900">
                  {language === 'fr' ? 'Chronologie' : 'Timeline'}
                </h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">
                      {language === 'fr' ? 'Commission créée' : 'Commission created'}
                    </p>
                    <p className="text-xs text-slate-500">
                      {formatDistanceToNow(new Date(commission.created_at), { addSuffix: true, locale })}
                    </p>
                  </div>
                </div>
                {commission.approved_at && (
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5" />
                    <div>
                      <p className="text-sm font-medium text-slate-900">
                        {language === 'fr' ? 'Approuvée' : 'Approved'}
                      </p>
                      <p className="text-xs text-slate-500">
                        {formatDistanceToNow(new Date(commission.approved_at), { addSuffix: true, locale })}
                      </p>
                    </div>
                  </div>
                )}
                {commission.paid_at && (
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5" />
                    <div>
                      <p className="text-sm font-medium text-slate-900">
                        {language === 'fr' ? 'Payée' : 'Paid'}
                      </p>
                      <p className="text-xs text-slate-500">
                        {formatDistanceToNow(new Date(commission.paid_at), { addSuffix: true, locale })}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Notes */}
            {commission.notes && (
              <div className="bg-white border border-slate-200 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-5 h-5 text-slate-600" />
                  <h3 className="font-semibold text-slate-900">
                    {language === 'fr' ? 'Notes' : 'Notes'}
                  </h3>
                </div>
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{commission.notes}</p>
              </div>
            )}

            {/* Mark as Paid Form (for approved status) */}
            {canMarkPaid && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5">
                <h3 className="font-semibold text-slate-900 mb-3">
                  {language === 'fr' ? 'Marquer comme payée' : 'Mark as Paid'}
                </h3>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={language === 'fr' ? 'Notes de paiement (optionnel)...' : 'Payment notes (optional)...'}
                  rows={3}
                  className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent mb-3"
                />
                <button
                  onClick={() => markPaidMutation.mutate(notes)}
                  disabled={markPaidMutation.isPending}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all disabled:opacity-50"
                >
                  <CheckCircle2 className="w-5 h-5" />
                  {markPaidMutation.isPending
                    ? language === 'fr' ? 'Traitement...' : 'Processing...'
                    : language === 'fr' ? 'Confirmer le paiement' : 'Confirm Payment'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <div className="flex gap-2">
            {canCancel && (
              <button
                onClick={() => {
                  if (window.confirm(language === 'fr' 
                    ? 'Êtes-vous sûr de vouloir annuler cette commission?' 
                    : 'Are you sure you want to cancel this commission?')) {
                    cancelMutation.mutate()
                  }
                }}
                disabled={cancelMutation.isPending}
                className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                {language === 'fr' ? 'Annuler' : 'Cancel'}
              </button>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              {language === 'fr' ? 'Fermer' : 'Close'}
            </button>
            {canApprove && (
              <button
                onClick={() => approveMutation.mutate()}
                disabled={approveMutation.isPending}
                className="px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all disabled:opacity-50"
              >
                {approveMutation.isPending
                  ? language === 'fr' ? 'Approbation...' : 'Approving...'
                  : language === 'fr' ? 'Approuver' : 'Approve'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
