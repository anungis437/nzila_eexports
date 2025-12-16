import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Ship,
  Plus,
  Search,
  Filter,
  Grid3x3,
  List,
  TrendingUp,
  Package,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react'
import ShipmentCard from '../components/ShipmentCard'
import ShipmentFormModal from '../components/ShipmentFormModal'
import ShipmentDetailModal from '../components/ShipmentDetailModal'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import type { Shipment } from '../types'

export default function Shipments() {
  const { language } = useLanguage()
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [selectedShipmentId, setSelectedShipmentId] = useState<number | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data: shipments = [], isLoading } = useQuery({
    queryKey: ['shipments'],
    queryFn: api.getShipments,
  })

  // Calculate stats
  const stats = {
    total: shipments.length,
    in_transit: shipments.filter((s: Shipment) => s.status === 'in_transit').length,
    customs: shipments.filter((s: Shipment) => s.status === 'customs').length,
    delivered: shipments.filter((s: Shipment) => s.status === 'delivered').length,
    delayed: shipments.filter((s: Shipment) => s.status === 'delayed').length,
  }

  // Filter shipments
  const filteredShipments = shipments.filter((shipment: Shipment) => {
    const matchesSearch =
      shipment.tracking_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      shipment.shipping_company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      shipment.destination_country?.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === 'all' || shipment.status === statusFilter

    return matchesSearch && matchesStatus
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            {language === 'fr' ? 'Expéditions' : 'Shipments'}
          </h1>
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg shadow-blue-500/25"
          >
            <Plus className="w-5 h-5" />
            {language === 'fr' ? 'Nouvelle expédition' : 'New Shipment'}
          </button>
        </div>
        <p className="text-slate-600">
          {language === 'fr' 
            ? 'Suivez et gérez vos expéditions de véhicules'
            : 'Track and manage your vehicle shipments'}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-600">
              {language === 'fr' ? 'Total' : 'Total'}
            </span>
            <Ship className="w-5 h-5 text-slate-500" />
          </div>
          <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-600">
              {language === 'fr' ? 'En transit' : 'In Transit'}
            </span>
            <TrendingUp className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-blue-900">{stats.in_transit}</p>
        </div>

        <div className="bg-gradient-to-br from-amber-50 to-amber-100 border border-amber-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-amber-600">
              {language === 'fr' ? 'En douane' : 'At Customs'}
            </span>
            <Package className="w-5 h-5 text-amber-500" />
          </div>
          <p className="text-2xl font-bold text-amber-900">{stats.customs}</p>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-600">
              {language === 'fr' ? 'Livrés' : 'Delivered'}
            </span>
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold text-green-900">{stats.delivered}</p>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-red-600">
              {language === 'fr' ? 'Retardés' : 'Delayed'}
            </span>
            <AlertTriangle className="w-5 h-5 text-red-500" />
          </div>
          <p className="text-2xl font-bold text-red-900">{stats.delayed}</p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6 flex flex-wrap items-center gap-4">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder={
                language === 'fr'
                  ? 'Rechercher par numéro, compagnie...'
                  : 'Search by tracking number, company...'
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">{language === 'fr' ? 'Tous les statuts' : 'All Statuses'}</option>
            <option value="pending">{language === 'fr' ? 'En attente' : 'Pending'}</option>
            <option value="in_transit">{language === 'fr' ? 'En transit' : 'In Transit'}</option>
            <option value="customs">{language === 'fr' ? 'En douane' : 'At Customs'}</option>
            <option value="delivered">{language === 'fr' ? 'Livrés' : 'Delivered'}</option>
            <option value="delayed">{language === 'fr' ? 'Retardés' : 'Delayed'}</option>
          </select>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded transition-colors ${
              viewMode === 'grid'
                ? 'bg-white text-blue-600 shadow'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Grid3x3 className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded transition-colors ${
              viewMode === 'list'
                ? 'bg-white text-blue-600 shadow'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Shipments List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
        </div>
      ) : filteredShipments.length === 0 ? (
        <div className="text-center py-12">
          <Ship className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            {language === 'fr' ? 'Aucune expédition trouvée' : 'No shipments found'}
          </h3>
          <p className="text-slate-500 mb-6">
            {searchTerm || statusFilter !== 'all'
              ? language === 'fr'
                ? 'Essayez de modifier vos filtres'
                : 'Try adjusting your filters'
              : language === 'fr'
              ? 'Commencez par créer votre première expédition'
              : 'Get started by creating your first shipment'}
          </p>
          {!searchTerm && statusFilter === 'all' && (
            <button
              onClick={() => setIsFormOpen(true)}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all"
            >
              <Plus className="w-5 h-5" />
              {language === 'fr' ? 'Nouvelle expédition' : 'New Shipment'}
            </button>
          )}
        </div>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          }
        >
          {filteredShipments.map((shipment: Shipment) => (
            <div
              key={shipment.id}
              onClick={() => setSelectedShipmentId(shipment.id)}
              className="cursor-pointer transform transition-transform hover:scale-[1.02]"
            >
              <ShipmentCard shipment={shipment} />
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      <ShipmentFormModal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
      />

      {selectedShipmentId && (
        <ShipmentDetailModal
          isOpen={true}
          onClose={() => setSelectedShipmentId(null)}
          shipmentId={selectedShipmentId}
        />
      )}
    </div>
  )
}
