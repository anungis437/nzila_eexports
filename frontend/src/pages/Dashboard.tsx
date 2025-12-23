import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'
import { motion } from 'framer-motion'
import { Car, Users, FileText, DollarSign, Package, Truck } from 'lucide-react'
import BrokerDashboard from '../components/BrokerDashboard'
import QuickLinks from '../components/QuickLinks'

export default function Dashboard() {
  const { user } = useAuth()
  const { t, language } = useLanguage()

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const data = await apiClient.getDashboardStats()
      console.log('📊 Dashboard stats:', {
        deals_count: data.deals_count,
        active_deals: data.active_deals,
        vehicles_count: data.vehicles_count,
        leads_count: data.leads_count,
        shipments_count: data.shipments_count,
        total_commissions: data.total_commissions,
        user_role: data.user_role
      })
      return data
    },
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

  const isBuyer = user?.role === 'buyer'
  const isDealer = user?.role === 'dealer'
  const isBroker = user?.role === 'broker'

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
              {isBuyer
                ? (language === 'fr'
                  ? "Vue d'ensemble de vos achats de véhicules"
                  : "Overview of your vehicle purchases")
                : (language === 'fr' 
                  ? "Vue d'ensemble de vos activités d'exportation"
                  : "Overview of your export activities")}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Broker Performance Dashboard */}
      {user?.role === 'broker' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-slate-900 mb-4">
            {language === 'fr' ? 'Performance du Courtier' : 'Broker Performance'}
          </h2>
          <BrokerDashboard />
        </motion.div>
      )}

      {/* Stats Grid */}
      <div className={`grid grid-cols-1 md:grid-cols-2 ${isBuyer ? 'lg:grid-cols-3' : 'lg:grid-cols-4'} gap-6`}>
        {/* Show vehicles only for dealers */}
        {!isBuyer && (
          <StatCard
            title={t('vehicles')}
            value={stats?.vehicles_count || 0}
            subtitle={language === 'fr' ? 'Disponibles' : 'Available'}
            icon={Car}
            color="amber"
          />
        )}
        
        {/* Leads - hidden for buyers as they don't create leads */}
        {!isBuyer && (
          <StatCard
            title={t('leads')}
            value={stats?.leads_count || 0}
            subtitle={language === 'fr' ? 'En attente' : 'Pending'}
            icon={Users}
            color="blue"
          />
        )}
        
        {/* Deals - show for everyone with different labels */}
        <StatCard
          title={isBuyer
            ? (language === 'fr' ? 'Achats' : 'Purchases')
            : t('deals')}
          value={stats?.deals_count || 0}
          subtitle={isBuyer
            ? (language === 'fr' ? 'Total' : 'Total')
            : (language === 'fr' ? 'En cours' : 'Active')}
          icon={FileText}
          color="emerald"
        />
        
        {/* Active deals/purchases */}
        <StatCard
          title={isBuyer
            ? (language === 'fr' ? 'En cours' : 'In Progress')
            : (language === 'fr' ? 'Actifs' : 'Active')}
          value={stats?.active_deals || 0}
          subtitle={isBuyer
            ? (language === 'fr' ? 'En traitement' : 'Processing')
            : (language === 'fr' ? 'Ce mois' : 'This month')}
          icon={FileText}
          color="blue"
        />
        
        {/* Shipments - show for everyone */}
        <StatCard
          title={isBuyer
            ? (language === 'fr' ? 'Livraisons' : 'Deliveries')
            : (language === 'fr' ? 'Expéditions' : 'Shipments')}
          value={stats?.shipments_count || 0}
          subtitle={language === 'fr' ? 'Total' : 'Total'}
          icon={Package}
          color="purple"
        />
        
        {/* Commissions - only for dealers/brokers */}
        {!isBuyer && (
          <StatCard
            title={t('commissions')}
            value={`$${stats?.total_commissions?.toFixed(2) || '0.00'}`}
            subtitle={language === 'fr' ? 'Total' : 'Total'}
            icon={DollarSign}
            color="emerald"
          />
        )}
      </div>

      {/* Quick Links */}
      <QuickLinks userRole={user?.role || 'buyer'} />
    </div>
  )
}
