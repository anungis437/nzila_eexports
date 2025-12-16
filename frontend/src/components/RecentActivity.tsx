import { formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'
import { 
  Car, 
  Users, 
  FileText, 
  DollarSign, 
  Ship, 
  CheckCircle2,
  Clock,
  TrendingUp,
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

interface Activity {
  id: number
  type: 'vehicle' | 'lead' | 'deal' | 'commission' | 'shipment'
  action: string
  description: string
  timestamp: string
  user?: string
}

interface RecentActivityProps {
  activities: Activity[]
  loading?: boolean
}

export default function RecentActivity({ activities, loading }: RecentActivityProps) {
  const { language } = useLanguage()
  const locale = language === 'fr' ? fr : enUS

  const getActivityIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      vehicle: <Car className="w-5 h-5 text-blue-600" />,
      lead: <Users className="w-5 h-5 text-green-600" />,
      deal: <FileText className="w-5 h-5 text-purple-600" />,
      commission: <DollarSign className="w-5 h-5 text-amber-600" />,
      shipment: <Ship className="w-5 h-5 text-indigo-600" />,
    }
    return icons[type] || <Clock className="w-5 h-5 text-slate-600" />
  }

  const getActivityColor = (type: string) => {
    const colors: Record<string, string> = {
      vehicle: 'bg-blue-100',
      lead: 'bg-green-100',
      deal: 'bg-purple-100',
      commission: 'bg-amber-100',
      shipment: 'bg-indigo-100',
    }
    return colors[type] || 'bg-slate-100'
  }

  const getActionBadge = (action: string) => {
    const badges: Record<string, { color: string; label: { en: string; fr: string } }> = {
      created: { 
        color: 'bg-green-100 text-green-700',
        label: { en: 'Created', fr: 'Créé' }
      },
      updated: { 
        color: 'bg-blue-100 text-blue-700',
        label: { en: 'Updated', fr: 'Mis à jour' }
      },
      completed: { 
        color: 'bg-purple-100 text-purple-700',
        label: { en: 'Completed', fr: 'Complété' }
      },
      approved: { 
        color: 'bg-indigo-100 text-indigo-700',
        label: { en: 'Approved', fr: 'Approuvé' }
      },
      shipped: { 
        color: 'bg-amber-100 text-amber-700',
        label: { en: 'Shipped', fr: 'Expédié' }
      },
    }
    const badge = badges[action] || { 
      color: 'bg-slate-100 text-slate-700',
      label: { en: action, fr: action }
    }
    return (
      <span className={`text-xs font-medium px-2 py-1 rounded-full ${badge.color}`}>
        {badge.label[language]}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-6">
          {language === 'fr' ? 'Activité Récente' : 'Recent Activity'}
        </h3>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex gap-4 animate-pulse">
              <div className="w-10 h-10 bg-slate-200 rounded-full" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-slate-200 rounded w-3/4" />
                <div className="h-3 bg-slate-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900">
          {language === 'fr' ? 'Activité Récente' : 'Recent Activity'}
        </h3>
        <TrendingUp className="w-5 h-5 text-slate-400" />
      </div>
      
      {activities.length === 0 ? (
        <div className="text-center py-8">
          <Clock className="w-12 h-12 text-slate-300 mx-auto mb-2" />
          <p className="text-slate-500">
            {language === 'fr' ? 'Aucune activité récente' : 'No recent activity'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex gap-4 pb-4 border-b border-slate-100 last:border-0 last:pb-0">
              <div className={`w-10 h-10 rounded-full ${getActivityColor(activity.type)} flex items-center justify-center flex-shrink-0`}>
                {getActivityIcon(activity.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {getActionBadge(activity.action)}
                  {activity.user && (
                    <span className="text-xs text-slate-500">
                      {language === 'fr' ? 'par' : 'by'} {activity.user}
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-900 mb-1">{activity.description}</p>
                <span className="text-xs text-slate-500">
                  {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true, locale })}
                </span>
              </div>
              
              <div className="flex-shrink-0">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>
            </div>
          ))}
        </div>
      )}
      
      {activities.length > 0 && (
        <button className="w-full mt-4 py-2 text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors">
          {language === 'fr' ? 'Voir toutes les activités' : 'View all activities'} →
        </button>
      )}
    </div>
  )
}
