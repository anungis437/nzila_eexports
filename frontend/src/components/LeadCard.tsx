import { Lead } from '../types'
import { useLanguage } from '../contexts/LanguageContext'
import { Car, User, Calendar, DollarSign, Tag } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface LeadCardProps {
  lead: Lead
  onClick: () => void
}

export default function LeadCard({ lead, onClick }: LeadCardProps) {
  const { language, formatCurrency } = useLanguage()
  const locale = language === 'fr' ? fr : enUS

  const getSourceColor = (source: Lead['source']) => {
    const colors = {
      website: 'bg-blue-100 text-blue-800',
      referral: 'bg-green-100 text-green-800',
      broker: 'bg-purple-100 text-purple-800',
      direct: 'bg-amber-100 text-amber-800',
    }
    return colors[source] || 'bg-slate-100 text-slate-800'
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

  const getLeadScore = (lead: Lead) => {
    let score = 50 // Base score
    
    // Newer leads get higher scores
    const daysSinceCreation = Math.floor(
      (Date.now() - new Date(lead.created_at).getTime()) / (1000 * 60 * 60 * 24)
    )
    if (daysSinceCreation < 1) score += 30
    else if (daysSinceCreation < 3) score += 20
    else if (daysSinceCreation < 7) score += 10
    
    // Source-based scoring
    if (lead.source === 'referral') score += 15
    else if (lead.source === 'broker') score += 10
    
    // Status-based scoring
    if (lead.status === 'negotiating') score += 20
    else if (lead.status === 'qualified') score += 15
    else if (lead.status === 'contacted') score += 10
    
    return Math.min(score, 100)
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-amber-600'
    return 'text-slate-600'
  }

  const score = getLeadScore(lead)

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg p-4 border border-slate-200 hover:border-amber-400 hover:shadow-md transition-all cursor-pointer group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900 text-sm mb-1 group-hover:text-amber-600 transition-colors">
            {lead.buyer_name || `Buyer #${lead.buyer}`}
          </h3>
          <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${getSourceColor(lead.source)}`}>
            {getSourceLabel(lead.source)}
          </span>
        </div>
        <div className={`text-right ${getScoreColor(score)}`}>
          <div className="text-lg font-bold">{score}</div>
          <div className="text-xs">{language === 'fr' ? 'Score' : 'Score'}</div>
        </div>
      </div>

      {/* Vehicle Info */}
      {lead.vehicle_details && (
        <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
          <Car className="w-4 h-4 flex-shrink-0" />
          <span className="truncate">
            {lead.vehicle_details.year} {lead.vehicle_details.make} {lead.vehicle_details.model}
          </span>
        </div>
      )}

      {/* Price */}
      {lead.vehicle_details && (
        <div className="flex items-center gap-2 text-sm font-medium text-slate-900 mb-2">
          <DollarSign className="w-4 h-4 flex-shrink-0" />
          <span>{formatCurrency(parseFloat(lead.vehicle_details.price_cad))}</span>
        </div>
      )}

      {/* Broker */}
      {lead.broker_name && (
        <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
          <User className="w-3.5 h-3.5 flex-shrink-0" />
          <span className="truncate">{lead.broker_name}</span>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100">
        <div className="flex items-center gap-1 text-xs text-slate-500">
          <Calendar className="w-3.5 h-3.5" />
          <span>
            {formatDistanceToNow(new Date(lead.created_at), {
              addSuffix: true,
              locale,
            })}
          </span>
        </div>
        {lead.notes && (
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <Tag className="w-3.5 h-3.5" />
            <span>{language === 'fr' ? 'Note' : 'Note'}</span>
          </div>
        )}
      </div>
    </div>
  )
}
