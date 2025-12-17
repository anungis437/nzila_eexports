import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { DollarSign, Search, Filter, TrendingUp, CheckCircle2, Clock, Percent } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import { Commission } from '../types'
import CommissionCard from '../components/CommissionCard'
import CommissionDetailModal from '../components/CommissionDetailModal'
import TierDashboard from '../components/TierDashboard'
import Leaderboard from '../components/Leaderboard'

export default function Commissions() {
  const { language } = useLanguage()
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [selectedCommissionId, setSelectedCommissionId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState('tier-dashboard')

  const { data: commissions = [], isLoading } = useQuery({
    queryKey: ['commissions', statusFilter, typeFilter],
    queryFn: async () => {
      const params: any = {}
      if (statusFilter !== 'all') params.status = statusFilter
      if (typeFilter !== 'all') params.commission_type = typeFilter
      const response = await api.getCommissions(params)
      return Array.isArray(response) ? response : response.results || []
    },
  })

  // Determine if user is broker or dealer
  const userType = user?.role === 'seller_broker' ? 'broker' : 'dealer'

  // Filter by search term
  const filteredCommissions = commissions.filter((commission: Commission) => {
    const searchLower = searchTerm.toLowerCase()
    const recipientMatch = commission.recipient?.username?.toLowerCase().includes(searchLower) ||
                          commission.recipient?.email?.toLowerCase().includes(searchLower)
    const dealMatch = commission.deal_id?.toString().includes(searchLower)
    return recipientMatch || dealMatch || commission.id.toString().includes(searchLower)
  })

  // Calculate statistics
  const stats = {
    total: commissions.length,
    pending: commissions.filter((c: Commission) => c.status === 'pending').length,
    approved: commissions.filter((c: Commission) => c.status === 'approved').length,
    paid: commissions.filter((c: Commission) => c.status === 'paid').length,
    totalAmount: commissions
      .filter((c: Commission) => c.status !== 'cancelled')
      .reduce((sum: number, c: Commission) => sum + parseFloat(c.amount_cad), 0),
    paidAmount: commissions
      .filter((c: Commission) => c.status === 'paid')
      .reduce((sum: number, c: Commission) => sum + parseFloat(c.amount_cad), 0),
  }

  const statusOptions = [
    { value: 'all', label: language === 'fr' ? 'Tous' : 'All' },
    { value: 'pending', label: language === 'fr' ? 'En attente' : 'Pending' },
    { value: 'approved', label: language === 'fr' ? 'Approuvé' : 'Approved' },
    { value: 'paid', label: language === 'fr' ? 'Payé' : 'Paid' },
    { value: 'cancelled', label: language === 'fr' ? 'Annulé' : 'Cancelled' },
  ]

  const typeOptions = [
    { value: 'all', label: language === 'fr' ? 'Tous les types' : 'All Types' },
    { value: 'broker', label: language === 'fr' ? 'Courtier' : 'Broker' },
    { value: 'dealer', label: language === 'fr' ? 'Revendeur' : 'Dealer' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-500 bg-clip-text text-transparent">
            {language === 'fr' ? 'Centre de Commissions' : 'Commission Center'}
          </h1>
          <p className="text-slate-600 mt-2">
            {language === 'fr'
              ? 'Suivez vos performances, gains et classement'
              : 'Track your performance, earnings, and rankings'}
          </p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[500px]">
            <TabsTrigger value="tier-dashboard">
              {language === 'fr' ? 'Tableau de Bord' : 'My Dashboard'}
            </TabsTrigger>
            <TabsTrigger value="leaderboard">
              {language === 'fr' ? 'Classement' : 'Leaderboard'}
            </TabsTrigger>
            <TabsTrigger value="commissions">
              {language === 'fr' ? 'Historique' : 'History'}
            </TabsTrigger>
          </TabsList>

          {/* Tier Dashboard Tab */}
          <TabsContent value="tier-dashboard">
            <TierDashboard />
          </TabsContent>

          {/* Leaderboard Tab */}
          <TabsContent value="leaderboard">
            <Leaderboard userType={userType} />
          </TabsContent>

          {/* Commissions History Tab */}
          <TabsContent value="commissions">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DollarSign className="w-5 h-5 text-blue-600" />
                  </div>
                  <span className="text-sm text-slate-600">
                    {language === 'fr' ? 'Total' : 'Total'}
                  </span>
                </div>
                <p className="text-3xl font-bold text-slate-900">{stats.total}</p>
                <p className="text-xs text-slate-500 mt-1">
                  ${stats.totalAmount.toLocaleString('en-CA', { minimumFractionDigits: 0 })}
                </p>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <Clock className="w-5 h-5 text-amber-600" />
                  </div>
                  <span className="text-sm text-slate-600">
                    {language === 'fr' ? 'En attente' : 'Pending'}
                  </span>
                </div>
                <p className="text-3xl font-bold text-slate-900">{stats.pending}</p>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <CheckCircle2 className="w-5 h-5 text-blue-600" />
                  </div>
                  <span className="text-sm text-slate-600">
                    {language === 'fr' ? 'Approuvé' : 'Approved'}
                  </span>
                </div>
                <p className="text-3xl font-bold text-slate-900">{stats.approved}</p>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  </div>
                  <span className="text-sm text-green-900">
                    {language === 'fr' ? 'Payé' : 'Paid'}
                  </span>
                </div>
                <p className="text-3xl font-bold text-green-900">{stats.paid}</p>
                <p className="text-xs text-green-700 mt-1">
                  ${stats.paidAmount.toLocaleString('en-CA', { minimumFractionDigits: 0 })}
                </p>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6">
              <div className="flex flex-col md:flex-row gap-4">
                {/* Search */}
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder={
                      language === 'fr'
                        ? 'Rechercher par bénéficiaire, transaction...'
                        : 'Search by recipient, deal...'
                    }
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                {/* Status Filter */}
                <div className="flex items-center gap-2">
                  <Filter className="w-5 h-5 text-slate-400" />
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {statusOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Type Filter */}
                <div className="flex items-center gap-2">
                  <Percent className="w-5 h-5 text-slate-400" />
                  <select
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                    className="px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {typeOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Commissions Grid */}
            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500" />
              </div>
            ) : filteredCommissions.length === 0 ? (
              <div className="bg-white border-2 border-dashed border-slate-300 rounded-2xl p-12 text-center">
                <DollarSign className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  {language === 'fr' ? 'Aucune commission trouvée' : 'No commissions found'}
                </h3>
                <p className="text-slate-500">
                  {language === 'fr'
                    ? 'Les commissions sont créées automatiquement lors de la finalisation des transactions'
                    : 'Commissions are automatically created when deals are completed'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCommissions.map((commission: Commission) => (
                  <CommissionCard
                    key={commission.id}
                    commission={commission}
                    onClick={() => setSelectedCommissionId(commission.id)}
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Detail Modal */}
      {selectedCommissionId && (
        <CommissionDetailModal
          isOpen={!!selectedCommissionId}
          onClose={() => setSelectedCommissionId(null)}
          commissionId={selectedCommissionId}
        />
      )}
    </div>
  )
}
