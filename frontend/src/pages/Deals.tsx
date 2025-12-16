import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Plus,
  Search,
  Filter,
  Grid3x3,
  List,
  Package,
  DollarSign,
  TrendingUp,
  CheckCircle2,
} from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Deal } from '../types'
import DealCard from '../components/DealCard'
import DealFormModal from '../components/DealFormModal'
import DealDetailModal from '../components/DealDetailModal'

export default function Deals() {
  const { language } = useLanguage()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [paymentFilter, setPaymentFilter] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [selectedDealId, setSelectedDealId] = useState<number | null>(null)

  const { data: deals = [], isLoading } = useQuery({
    queryKey: ['deals', statusFilter, paymentFilter],
    queryFn: async () => {
      const params: any = {}
      if (statusFilter !== 'all') params.status = statusFilter
      if (paymentFilter !== 'all') params.payment_status = paymentFilter
      const response = await api.getDeals(params)
      return Array.isArray(response) ? response : response.results || []
    },
  })

  // Filter deals by search term
  const filteredDeals = deals.filter((deal: Deal) => {
    const searchLower = searchTerm.toLowerCase()
    const vehicleMatch = deal.vehicle_details
      ? `${deal.vehicle_details.year} ${deal.vehicle_details.make} ${deal.vehicle_details.model}`
          .toLowerCase()
          .includes(searchLower)
      : false
    const buyerMatch = deal.buyer_name?.toLowerCase().includes(searchLower) || false
    const dealerMatch = deal.dealer_name?.toLowerCase().includes(searchLower) || false
    return vehicleMatch || buyerMatch || dealerMatch || deal.id.toString().includes(searchLower)
  })

  // Calculate statistics
  const stats = {
    total: deals.length,
    active: deals.filter(
      (d: Deal) => !['completed', 'cancelled'].includes(d.status)
    ).length,
    completed: deals.filter((d: Deal) => d.status === 'completed').length,
    totalValue: deals
      .filter((d: Deal) => d.status !== 'cancelled')
      .reduce((sum: number, d: Deal) => sum + parseFloat(d.agreed_price_cad), 0),
  }

  const statusOptions = [
    { value: 'all', label: language === 'fr' ? 'Tous' : 'All' },
    { value: 'pending_docs', label: language === 'fr' ? 'Docs en attente' : 'Pending Docs' },
    { value: 'docs_verified', label: language === 'fr' ? 'Docs vérifiés' : 'Docs Verified' },
    { value: 'payment_pending', label: language === 'fr' ? 'Paiement en attente' : 'Payment Pending' },
    { value: 'payment_received', label: language === 'fr' ? 'Paiement reçu' : 'Payment Received' },
    { value: 'ready_to_ship', label: language === 'fr' ? 'Prêt à expédier' : 'Ready to Ship' },
    { value: 'shipped', label: language === 'fr' ? 'Expédié' : 'Shipped' },
    { value: 'completed', label: language === 'fr' ? 'Terminé' : 'Completed' },
    { value: 'cancelled', label: language === 'fr' ? 'Annulé' : 'Cancelled' },
  ]

  const paymentOptions = [
    { value: 'all', label: language === 'fr' ? 'Tous' : 'All' },
    { value: 'pending', label: language === 'fr' ? 'En attente' : 'Pending' },
    { value: 'partial', label: language === 'fr' ? 'Partiel' : 'Partial' },
    { value: 'paid', label: language === 'fr' ? 'Payé' : 'Paid' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-600 to-amber-500 bg-clip-text text-transparent">
                {language === 'fr' ? 'Transactions' : 'Deals'}
              </h1>
              <p className="text-slate-600 mt-1">
                {language === 'fr'
                  ? 'Gérez vos ventes et suivez les paiements'
                  : 'Manage your sales and track payments'}
              </p>
            </div>
            <button
              onClick={() => setIsFormOpen(true)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl hover:from-amber-600 hover:to-amber-700 transition-all shadow-lg hover:shadow-xl"
              aria-label={language === 'fr' ? 'Créer une nouvelle transaction' : 'Create new deal'}
            >
              <Plus className="w-5 h-5" aria-hidden="true" />
              {language === 'fr' ? 'Nouvelle transaction' : 'New Deal'}
            </button>
          </div>

          {/* Stats Cards */}
          <div 
            className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"
            role="region"
            aria-label={language === 'fr' ? 'Statistiques des transactions' : 'Deal statistics'}
          >
            <div 
              className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-shadow"
              role="article"
              aria-label={`${language === 'fr' ? 'Total des transactions:' : 'Total deals:'} ${stats.total}`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-100 rounded-lg" aria-hidden="true">
                  <Package className="w-5 h-5 text-blue-600" />
                </div>
                <span className="text-sm text-slate-600">
                  {language === 'fr' ? 'Total' : 'Total Deals'}
                </span>
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats.total}</p>
            </div>

            <div 
              className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-shadow"
              role="article"
              aria-label={`${language === 'fr' ? 'Transactions en cours:' : 'Active deals:'} ${stats.active}`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-amber-100 rounded-lg" aria-hidden="true">
                  <TrendingUp className="w-5 h-5 text-amber-600" />
                </div>
                <span className="text-sm text-slate-600">
                  {language === 'fr' ? 'En cours' : 'Active'}
                </span>
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats.active}</p>
            </div>

            <div 
              className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-shadow"
              role="article"
              aria-label={`${language === 'fr' ? 'Transactions terminées:' : 'Completed deals:'} ${stats.completed}`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-green-100 rounded-lg" aria-hidden="true">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                </div>
                <span className="text-sm text-slate-600">
                  {language === 'fr' ? 'Terminées' : 'Completed'}
                </span>
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats.completed}</p>
            </div>

            <div 
              className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5 hover:shadow-lg transition-shadow"
              role="article"
              aria-label={`${language === 'fr' ? 'Valeur totale:' : 'Total value:'} ${stats.totalValue.toLocaleString('en-CA')} dollars canadiens`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-green-100 rounded-lg" aria-hidden="true">
                  <DollarSign className="w-5 h-5 text-green-600" />
                </div>
                <span className="text-sm text-green-900">
                  {language === 'fr' ? 'Valeur totale' : 'Total Value'}
                </span>
              </div>
              <p className="text-3xl font-bold text-green-900">
                ${stats.totalValue.toLocaleString('en-CA', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
              </p>
            </div>
          </div>

          {/* Filters */}
          <div 
            className="bg-white border border-slate-200 rounded-xl p-4"
            role="search"
            aria-label={language === 'fr' ? 'Filtres de transactions' : 'Deal filters'}
          >
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <label htmlFor="deal-search" className="sr-only">
                  {language === 'fr' 
                    ? 'Rechercher des transactions' 
                    : 'Search deals'}
                </label>
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" aria-hidden="true" />
                <input
                  id="deal-search"
                  type="text"
                  placeholder={
                    language === 'fr'
                      ? 'Rechercher par véhicule, acheteur, revendeur...'
                      : 'Search by vehicle, buyer, dealer...'
                  }
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  aria-label={language === 'fr' 
                    ? 'Rechercher par véhicule, acheteur ou revendeur' 
                    : 'Search by vehicle, buyer, or dealer'}
                />
              </div>

              {/* Status Filter */}
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-slate-400" aria-hidden="true" />
                <label htmlFor="status-filter" className="sr-only">
                  {language === 'fr' ? 'Filtrer par statut' : 'Filter by status'}
                </label>
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  aria-label={language === 'fr' ? 'Filtrer par statut de transaction' : 'Filter by deal status'}
                >
                  {statusOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Payment Filter */}
              <label htmlFor="payment-filter" className="sr-only">
                {language === 'fr' ? 'Filtrer par statut de paiement' : 'Filter by payment status'}
              </label>
              <select
                id="payment-filter"
                value={paymentFilter}
                onChange={(e) => setPaymentFilter(e.target.value)}
                className="px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                aria-label={language === 'fr' ? 'Filtrer par statut de paiement' : 'Filter by payment status'}
              >
                {paymentOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>

              {/* View Toggle */}
              <div 
                className="flex items-center gap-1 bg-slate-100 rounded-lg p-1"
                role="group"
                aria-label={language === 'fr' ? 'Mode d\'affichage' : 'View mode'}
              >
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-white text-amber-600 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                  aria-label={language === 'fr' ? 'Vue en grille' : 'Grid view'}
                  aria-pressed={viewMode === 'grid'}
                >
                  <Grid3x3 className="w-5 h-5" aria-hidden="true" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list'
                      ? 'bg-white text-amber-600 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                  aria-label={language === 'fr' ? 'Vue en liste' : 'List view'}
                  aria-pressed={viewMode === 'list'}
                >
                  <List className="w-5 h-5" aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Deals Grid/List */}
        {isLoading ? (
          <div 
            className="flex items-center justify-center py-20"
            role="status"
            aria-live="polite"
            aria-label={language === 'fr' ? 'Chargement des transactions' : 'Loading deals'}
          >
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500" aria-hidden="true" />
            <span className="sr-only">{language === 'fr' ? 'Chargement...' : 'Loading...'}</span>
          </div>
        ) : filteredDeals.length === 0 ? (
          <div 
            className="bg-white border-2 border-dashed border-slate-300 rounded-2xl p-12 text-center"
            role="status"
            aria-live="polite"
          >
            <Package className="w-16 h-16 text-slate-300 mx-auto mb-4" aria-hidden="true" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              {language === 'fr' ? 'Aucune transaction trouvée' : 'No deals found'}
            </h3>
            <p className="text-slate-500 mb-6">
              {language === 'fr'
                ? 'Commencez à créer des transactions pour gérer vos ventes'
                : 'Start creating deals to manage your sales'}
            </p>
            <button
              onClick={() => setIsFormOpen(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl hover:from-amber-600 hover:to-amber-700 transition-all"
              aria-label={language === 'fr' ? 'Créer ma première transaction' : 'Create my first deal'}
            >
              <Plus className="w-5 h-5" aria-hidden="true" />
              {language === 'fr' ? 'Créer ma première transaction' : 'Create my first deal'}
            </button>
          </div>
        ) : (
          <div
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
            }
            role="list"
            aria-label={language === 'fr' ? `${filteredDeals.length} transactions` : `${filteredDeals.length} deals`}
          >
            {filteredDeals.map((deal: Deal) => (
              <div
                key={deal.id}
                onClick={() => setSelectedDealId(deal.id)}
                className="cursor-pointer"
                role="listitem"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    setSelectedDealId(deal.id)
                  }
                }}
                aria-label={`${language === 'fr' ? 'Transaction' : 'Deal'} ${deal.id} - ${deal.vehicle_details ? `${deal.vehicle_details.year} ${deal.vehicle_details.make} ${deal.vehicle_details.model}` : language === 'fr' ? 'Véhicule inconnu' : 'Unknown vehicle'}`}
              >
                <DealCard deal={deal} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <DealFormModal isOpen={isFormOpen} onClose={() => setIsFormOpen(false)} />
      {selectedDealId && (
        <DealDetailModal
          isOpen={!!selectedDealId}
          onClose={() => setSelectedDealId(null)}
          dealId={selectedDealId}
        />
      )}
    </div>
  )
}
