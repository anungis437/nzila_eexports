import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'
import { motion } from 'framer-motion'
import { Car, Users, FileText, DollarSign } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const { t, language } = useLanguage()

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => apiClient.getDashboardStats(),
  })

  const StatCard = ({ title, value, subtitle, icon: Icon, color }: any) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm card-hover"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600 mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-slate-900 mb-1">{value}</h3>
          {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-${color}-50 flex items-center justify-center`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
    </motion.div>
  )

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="gradient-primary rounded-3xl p-8 text-white shadow-xl"
      >
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-amber-200 text-sm font-medium mb-1">
              {t('welcome')}, {user?.full_name?.split(' ')[0] || 'User'}
            </p>
            <h1 className="text-2xl md:text-3xl font-bold">
              {language === 'fr' ? 'Tableau de bord' : 'Dashboard'}
            </h1>
            <p className="text-amber-100 mt-2">
              {language === 'fr' 
                ? "Vue d'ensemble de vos activités d'exportation"
                : "Overview of your export activities"}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title={t('vehicles')}
          value={stats?.vehicles || 0}
          subtitle={language === 'fr' ? 'Disponibles' : 'Available'}
          icon={Car}
          color="amber"
        />
        <StatCard
          title={t('leads')}
          value={stats?.leads || 0}
          subtitle={language === 'fr' ? 'En attente' : 'Pending'}
          icon={Users}
          color="blue"
        />
        <StatCard
          title={t('deals')}
          value={stats?.deals || 0}
          subtitle={language === 'fr' ? 'En cours' : 'Active'}
          icon={FileText}
          color="emerald"
        />
        <StatCard
          title={t('commissions')}
          value={stats?.commissions || '$0'}
          subtitle={language === 'fr' ? 'Ce mois' : 'This month'}
          icon={DollarSign}
          color="purple"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            {t('recentActivity')}
          </h3>
          <div className="space-y-4">
            <p className="text-slate-500 text-center py-8">{t('noData')}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            {t('quickActions')}
          </h3>
          <div className="space-y-3">
            <button className="w-full text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-primary-300 hover:bg-primary-50 transition">
              <div className="font-medium text-slate-900">{t('addVehicle')}</div>
              <div className="text-sm text-slate-500">
                {language === 'fr' ? 'Ajouter un nouveau véhicule' : 'Add a new vehicle'}
              </div>
            </button>
            <button className="w-full text-left px-4 py-3 rounded-lg border border-slate-200 hover:border-primary-300 hover:bg-primary-50 transition">
              <div className="font-medium text-slate-900">{t('submitLead')}</div>
              <div className="text-sm text-slate-500">
                {language === 'fr' ? 'Créer une nouvelle demande' : 'Create a new lead'}
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
