import { useQuery } from '@tanstack/react-query'
import {
  DollarSign,
  FileText,
  Car,
  Ship,
  TrendingUp,
  Users,
} from 'lucide-react'
import StatCard from '../components/StatCard'
import RevenueChart from '../components/RevenueChart'
import DealPipelineChart from '../components/DealPipelineChart'
import RecentActivity from '../components/RecentActivity'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'

export default function Analytics() {
  const { language } = useLanguage()

  // Fetch analytics data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['analytics', 'stats'],
    queryFn: api.getAnalyticsStats,
  })

  const { data: revenueData, isLoading: revenueLoading } = useQuery({
    queryKey: ['analytics', 'revenue'],
    queryFn: api.getRevenueChart,
  })

  const { data: pipelineData, isLoading: pipelineLoading } = useQuery({
    queryKey: ['analytics', 'pipeline'],
    queryFn: api.getPipelineChart,
  })

  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ['analytics', 'activities'],
    queryFn: api.getRecentActivities,
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
          {language === 'fr' ? 'Tableau de Bord Analytique' : 'Analytics Dashboard'}
        </h1>
        <p className="text-slate-600">
          {language === 'fr'
            ? 'Aperçu complet de vos performances et métriques'
            : 'Complete overview of your performance and metrics'}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        <StatCard
          title={language === 'fr' ? 'Revenus Totaux' : 'Total Revenue'}
          value={`$${stats?.totalRevenue.toLocaleString() || '0'}`}
          change={{ value: stats?.revenueChange || 0, trend: (stats?.revenueChange || 0) > 0 ? 'up' : 'down' }}
          icon={DollarSign}
          color="green"
          loading={statsLoading}
        />
        <StatCard
          title={language === 'fr' ? 'Transactions Actives' : 'Active Deals'}
          value={stats?.activeDeals || 0}
          change={{ value: stats?.dealsChange || 0, trend: (stats?.dealsChange || 0) > 0 ? 'up' : 'down' }}
          icon={FileText}
          color="blue"
          loading={statsLoading}
        />
        <StatCard
          title={language === 'fr' ? 'Véhicules Vendus' : 'Vehicles Sold'}
          value={stats?.vehiclesSold || 0}
          change={{ value: stats?.vehiclesChange || 0, trend: (stats?.vehiclesChange || 0) > 0 ? 'up' : 'down' }}
          icon={Car}
          color="purple"
          loading={statsLoading}
        />
        <StatCard
          title={language === 'fr' ? 'En Transit' : 'In Transit'}
          value={stats?.shipmentsInTransit || 0}
          change={{ value: stats?.shipmentsChange || 0, trend: (stats?.shipmentsChange || 0) > 0 ? 'up' : 'down' }}
          icon={Ship}
          color="indigo"
          loading={statsLoading}
        />
        <StatCard
          title={language === 'fr' ? 'Commissions' : 'Commissions'}
          value={`$${stats?.totalCommissions.toLocaleString() || '0'}`}
          change={{ value: stats?.commissionsChange || 0, trend: (stats?.commissionsChange || 0) > 0 ? 'up' : 'down' }}
          icon={TrendingUp}
          color="amber"
          loading={statsLoading}
        />
        <StatCard
          title={language === 'fr' ? 'Nouveaux Leads' : 'New Leads'}
          value={stats?.newLeads || 0}
          change={{ value: stats?.leadsChange || 0, trend: (stats?.leadsChange || 0) > 0 ? 'up' : 'down' }}
          icon={Users}
          color="green"
          loading={statsLoading}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <RevenueChart data={revenueData || []} loading={revenueLoading} />
        <DealPipelineChart data={pipelineData || []} loading={pipelineLoading} />
      </div>

      {/* Recent Activity */}
      <RecentActivity activities={activities || []} loading={activitiesLoading} />

      {/* Quick Links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
        <a
          href="/vehicles"
          className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-6 hover:shadow-lg transition-all group"
        >
          <div className="flex items-center gap-3 mb-2">
            <Car className="w-6 h-6 text-blue-600" />
            <h3 className="font-semibold text-slate-900">
              {language === 'fr' ? 'Véhicules' : 'Vehicles'}
            </h3>
          </div>
          <p className="text-sm text-slate-600 group-hover:text-slate-900">
            {language === 'fr' ? 'Gérer l\'inventaire' : 'Manage inventory'} →
          </p>
        </a>

        <a
          href="/deals"
          className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-6 hover:shadow-lg transition-all group"
        >
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-6 h-6 text-purple-600" />
            <h3 className="font-semibold text-slate-900">
              {language === 'fr' ? 'Transactions' : 'Deals'}
            </h3>
          </div>
          <p className="text-sm text-slate-600 group-hover:text-slate-900">
            {language === 'fr' ? 'Voir les transactions' : 'View deals'} →
          </p>
        </a>

        <a
          href="/shipments"
          className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-xl p-6 hover:shadow-lg transition-all group"
        >
          <div className="flex items-center gap-3 mb-2">
            <Ship className="w-6 h-6 text-indigo-600" />
            <h3 className="font-semibold text-slate-900">
              {language === 'fr' ? 'Expéditions' : 'Shipments'}
            </h3>
          </div>
          <p className="text-sm text-slate-600 group-hover:text-slate-900">
            {language === 'fr' ? 'Suivre les expéditions' : 'Track shipments'} →
          </p>
        </a>

        <a
          href="/commissions"
          className="bg-gradient-to-br from-amber-50 to-amber-100 border border-amber-200 rounded-xl p-6 hover:shadow-lg transition-all group"
        >
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-6 h-6 text-amber-600" />
            <h3 className="font-semibold text-slate-900">
              {language === 'fr' ? 'Commissions' : 'Commissions'}
            </h3>
          </div>
          <p className="text-sm text-slate-600 group-hover:text-slate-900">
            {language === 'fr' ? 'Gérer les paiements' : 'Manage payments'} →
          </p>
        </a>
      </div>
    </div>
  )
}
