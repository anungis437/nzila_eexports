import { LucideIcon } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

interface StatCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    trend: 'up' | 'down'
  }
  icon: LucideIcon
  color: 'blue' | 'green' | 'amber' | 'purple' | 'red' | 'indigo'
  loading?: boolean
}

export default function StatCard({ title, value, change, icon: Icon, color, loading }: StatCardProps) {
  const { language } = useLanguage()

  const colorClasses = {
    blue: {
      bg: 'from-blue-50 to-blue-100',
      border: 'border-blue-200',
      icon: 'text-blue-600',
      text: 'text-blue-900',
      change: 'text-blue-700',
    },
    green: {
      bg: 'from-green-50 to-green-100',
      border: 'border-green-200',
      icon: 'text-green-600',
      text: 'text-green-900',
      change: 'text-green-700',
    },
    amber: {
      bg: 'from-amber-50 to-amber-100',
      border: 'border-amber-200',
      icon: 'text-amber-600',
      text: 'text-amber-900',
      change: 'text-amber-700',
    },
    purple: {
      bg: 'from-purple-50 to-purple-100',
      border: 'border-purple-200',
      icon: 'text-purple-600',
      text: 'text-purple-900',
      change: 'text-purple-700',
    },
    red: {
      bg: 'from-red-50 to-red-100',
      border: 'border-red-200',
      icon: 'text-red-600',
      text: 'text-red-900',
      change: 'text-red-700',
    },
    indigo: {
      bg: 'from-indigo-50 to-indigo-100',
      border: 'border-indigo-200',
      icon: 'text-indigo-600',
      text: 'text-indigo-900',
      change: 'text-indigo-700',
    },
  }

  const classes = colorClasses[color]

  if (loading) {
    return (
      <div className={`bg-gradient-to-br ${classes.bg} border ${classes.border} rounded-xl p-6 animate-pulse`}>
        <div className="h-4 bg-slate-200 rounded w-1/2 mb-4" />
        <div className="h-8 bg-slate-200 rounded w-3/4" />
      </div>
    )
  }

  return (
    <div className={`bg-gradient-to-br ${classes.bg} border ${classes.border} rounded-xl p-6 transition-all hover:shadow-lg`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <p className={`text-sm font-medium ${classes.change}`}>{title}</p>
        </div>
        <div className={`w-12 h-12 rounded-full bg-white/50 flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${classes.icon}`} />
        </div>
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <p className={`text-3xl font-bold ${classes.text}`}>{value}</p>
        </div>
        
        {change && (
          <div className="flex items-center gap-1">
            <span className={`text-xs font-medium ${change.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {change.trend === 'up' ? '↑' : '↓'} {Math.abs(change.value)}%
            </span>
          </div>
        )}
      </div>
      
      {change && (
        <p className="text-xs text-slate-500 mt-2">
          {language === 'fr' ? 'vs mois dernier' : 'vs last month'}
        </p>
      )}
    </div>
  )
}
