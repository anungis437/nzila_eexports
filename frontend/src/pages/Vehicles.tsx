import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Filter, Edit2, Trash2, Car, Eye } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import VehicleFormModal from '../components/VehicleFormModal'
import VehicleDetailModal from '../components/VehicleDetailModal'
import { Vehicle } from '../types'

export default function Vehicles() {
  const { t, language, formatCurrency } = useLanguage()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | undefined>()
  const [viewingVehicle, setViewingVehicle] = useState<Vehicle | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [conditionFilter, setConditionFilter] = useState<string>('all')

  // Fetch vehicles
  const { data: vehicles = [], isLoading } = useQuery({
    queryKey: ['vehicles', statusFilter, conditionFilter],
    queryFn: async () => {
      const params: any = {}
      if (statusFilter !== 'all') params.status = statusFilter
      if (conditionFilter !== 'all') params.condition = conditionFilter
      const response = await api.getVehicles(params)
      return Array.isArray(response) ? response : response.results || []
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteVehicle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
    },
  })

  // Filter vehicles by search query
  const filteredVehicles = vehicles.filter((vehicle: Vehicle) => {
    const searchLower = searchQuery.toLowerCase()
    return (
      vehicle.make.toLowerCase().includes(searchLower) ||
      vehicle.model.toLowerCase().includes(searchLower) ||
      vehicle.vin.toLowerCase().includes(searchLower) ||
      vehicle.year.toString().includes(searchLower)
    )
  })

  const handleEdit = (vehicle: Vehicle) => {
    setEditingVehicle(vehicle)
    setIsFormOpen(true)
  }

  const handleAdd = () => {
    setEditingVehicle(undefined)
    setIsFormOpen(true)
  }

  const handleDelete = (vehicle: Vehicle) => {
    if (window.confirm(
      language === 'fr' 
        ? `Supprimer ${vehicle.year} ${vehicle.make} ${vehicle.model}?`
        : `Delete ${vehicle.year} ${vehicle.make} ${vehicle.model}?`
    )) {
      deleteMutation.mutate(vehicle.id)
    }
  }

  const getStatusColor = (status: Vehicle['status']) => {
    const colors = {
      available: 'bg-green-100 text-green-800',
      reserved: 'bg-blue-100 text-blue-800',
      sold: 'bg-purple-100 text-purple-800',
      shipped: 'bg-amber-100 text-amber-800',
      delivered: 'bg-slate-100 text-slate-800',
    }
    return colors[status] || 'bg-slate-100 text-slate-800'
  }

  const getStatusLabel = (status: Vehicle['status']) => {
    const labels = {
      available: language === 'fr' ? 'Disponible' : 'Available',
      reserved: language === 'fr' ? 'Réservé' : 'Reserved',
      sold: language === 'fr' ? 'Vendu' : 'Sold',
      shipped: language === 'fr' ? 'Expédié' : 'Shipped',
      delivered: language === 'fr' ? 'Livré' : 'Delivered',
    }
    return labels[status] || status
  }

  const getConditionLabel = (condition: Vehicle['condition']) => {
    const labels = {
      new: language === 'fr' ? 'Neuf' : 'New',
      used_excellent: language === 'fr' ? 'Usagé - Excellent' : 'Used - Excellent',
      used_good: language === 'fr' ? 'Usagé - Bon' : 'Used - Good',
      used_fair: language === 'fr' ? 'Usagé - Acceptable' : 'Used - Fair',
    }
    return labels[condition] || condition
  }

  const canManageVehicles = user?.role === 'admin' || user?.role === 'dealer'

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('vehicles')}</h1>
          <p className="text-slate-600 mt-1" role="status" aria-live="polite">
            {language === 'fr' 
              ? `${filteredVehicles.length} véhicule${filteredVehicles.length !== 1 ? 's' : ''}`
              : `${filteredVehicles.length} vehicle${filteredVehicles.length !== 1 ? 's' : ''}`}
          </p>
        </div>
        {canManageVehicles && (
          <button
            onClick={handleAdd}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all"
            aria-label={language === 'fr' ? 'Ajouter un nouveau véhicule' : 'Add new vehicle'}
          >
            <Plus className="w-5 h-5" aria-hidden="true" />
            {language === 'fr' ? 'Ajouter véhicule' : 'Add Vehicle'}
          </button>
        )}
      </div>

      {/* Filters */}
      <div 
        className="bg-white rounded-xl border border-slate-200 p-4 mb-6"
        role="search"
        aria-label={language === 'fr' ? 'Filtres de véhicules' : 'Vehicle filters'}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <label htmlFor="vehicle-search" className="sr-only">
              {language === 'fr' ? 'Rechercher des véhicules' : 'Search vehicles'}
            </label>
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" aria-hidden="true" />
            <input
              id="vehicle-search"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={language === 'fr' ? 'Rechercher...' : 'Search...'}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              aria-label={language === 'fr' ? 'Rechercher par marque, modèle, VIN ou année' : 'Search by make, model, VIN or year'}
            />
          </div>

          {/* Status Filter */}
          <div className="relative">
            <label htmlFor="status-filter" className="sr-only">
              {language === 'fr' ? 'Filtrer par statut' : 'Filter by status'}
            </label>
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" aria-hidden="true" />
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent appearance-none"
              aria-label={language === 'fr' ? 'Filtrer par statut du véhicule' : 'Filter by vehicle status'}
            >
              <option value="all">{language === 'fr' ? 'Tous les statuts' : 'All Statuses'}</option>
              <option value="available">{language === 'fr' ? 'Disponible' : 'Available'}</option>
              <option value="reserved">{language === 'fr' ? 'Réservé' : 'Reserved'}</option>
              <option value="sold">{language === 'fr' ? 'Vendu' : 'Sold'}</option>
              <option value="shipped">{language === 'fr' ? 'Expédié' : 'Shipped'}</option>
              <option value="delivered">{language === 'fr' ? 'Livré' : 'Delivered'}</option>
            </select>
          </div>

          {/* Condition Filter */}
          <div className="relative">
            <label htmlFor="condition-filter" className="sr-only">
              {language === 'fr' ? 'Filtrer par condition' : 'Filter by condition'}
            </label>
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" aria-hidden="true" />
            <select
              id="condition-filter"
              value={conditionFilter}
              onChange={(e) => setConditionFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent appearance-none"
              aria-label={language === 'fr' ? 'Filtrer par condition du véhicule' : 'Filter by vehicle condition'}
            >
              <option value="all">{language === 'fr' ? 'Toutes conditions' : 'All Conditions'}</option>
              <option value="new">{language === 'fr' ? 'Neuf' : 'New'}</option>
              <option value="used_excellent">{language === 'fr' ? 'Usagé - Excellent' : 'Used - Excellent'}</option>
              <option value="used_good">{language === 'fr' ? 'Usagé - Bon' : 'Used - Good'}</option>
              <option value="used_fair">{language === 'fr' ? 'Usagé - Acceptable' : 'Used - Fair'}</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div 
          className="bg-white rounded-xl border border-slate-200 p-12 text-center"
          role="status"
          aria-live="polite"
          aria-label={language === 'fr' ? 'Chargement des véhicules' : 'Loading vehicles'}
        >
          <div className="animate-spin w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full mx-auto mb-4" aria-hidden="true" />
          <p className="text-slate-600">{language === 'fr' ? 'Chargement...' : 'Loading...'}</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredVehicles.length === 0 && (
        <div 
          className="bg-white rounded-xl border border-slate-200 p-12 text-center"
          role="status"
          aria-live="polite"
        >
          <Car className="w-16 h-16 text-slate-300 mx-auto mb-4" aria-hidden="true" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">
            {language === 'fr' ? 'Aucun véhicule' : 'No vehicles'}
          </h3>
          <p className="text-slate-600 mb-6">
            {searchQuery || statusFilter !== 'all' || conditionFilter !== 'all'
              ? language === 'fr' ? 'Aucun véhicule ne correspond à vos critères' : 'No vehicles match your filters'
              : language === 'fr' ? 'Commencez par ajouter votre premier véhicule' : 'Start by adding your first vehicle'}
          </p>
          {canManageVehicles && !searchQuery && statusFilter === 'all' && conditionFilter === 'all' && (
            <button
              onClick={handleAdd}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all"
              aria-label={language === 'fr' ? 'Ajouter votre premier véhicule' : 'Add your first vehicle'}
            >
              <Plus className="w-5 h-5" aria-hidden="true" />
              {language === 'fr' ? 'Ajouter votre premier véhicule' : 'Add your first vehicle'}
            </button>
          )}
        </div>
      )}

      {/* Vehicle Grid */}
      {!isLoading && filteredVehicles.length > 0 && (
        <div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          role="list"
          aria-label={language === 'fr' ? 'Liste des véhicules' : 'Vehicle list'}
        >
          {filteredVehicles.map((vehicle: Vehicle) => (
            <article
              key={vehicle.id}
              className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
              role="listitem"
              aria-label={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
            >
              {/* Image */}
              <div 
                className="aspect-video bg-slate-100 relative overflow-hidden cursor-pointer"
                onClick={() => setViewingVehicle(vehicle)}
              >
                {vehicle.main_image ? (
                  <img
                    src={vehicle.main_image}
                    alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full" role="img" aria-label={language === 'fr' ? 'Aucune image' : 'No image'}>
                    <Car className="w-16 h-16 text-slate-300" aria-hidden="true" />
                  </div>
                )}
                <div className="absolute top-3 right-3">
                  <span 
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(vehicle.status)}`}
                    role="status"
                    aria-label={`${language === 'fr' ? 'Statut:' : 'Status:'} ${getStatusLabel(vehicle.status)}`}
                  >
                    {getStatusLabel(vehicle.status)}
                  </span>
                </div>
                {/* View icon overlay */}
                <div className="absolute inset-0 bg-black/0 hover:bg-black/30 transition-colors flex items-center justify-center opacity-0 hover:opacity-100">
                  <Eye className="w-12 h-12 text-white" />
                </div>
              </div>

              {/* Content */}
              <div className="p-4">
                <h3 className="text-lg font-bold text-slate-900 mb-1">
                  {vehicle.year} {vehicle.make} {vehicle.model}
                </h3>
                <p className="text-sm text-slate-600 mb-3">
                  {getConditionLabel(vehicle.condition)} • {vehicle.mileage.toLocaleString()} km
                </p>

                <div className="flex items-baseline gap-2 mb-4">
                  <span 
                    className="text-2xl font-bold text-amber-600"
                    aria-label={`${language === 'fr' ? 'Prix:' : 'Price:'} ${formatCurrency(parseFloat(vehicle.price_cad))}`}
                  >
                    {formatCurrency(parseFloat(vehicle.price_cad))}
                  </span>
                </div>

                <div className="text-xs text-slate-500 mb-4 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">VIN:</span>
                    <span className="font-mono">{vehicle.vin}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{language === 'fr' ? 'Lieu:' : 'Location:'}</span>
                    <span>{vehicle.location}</span>
                  </div>
                  {vehicle.images && vehicle.images.length > 0 && (
                    <div className="flex items-center gap-2 text-blue-600">
                      <Eye className="w-3 h-3" />
                      <span>{vehicle.images.length} {language === 'fr' ? 'images' : 'images'}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                {canManageVehicles && (
                  <div className="flex gap-2 pt-3 border-t border-slate-200">
                    <button
                      onClick={() => setViewingVehicle(vehicle)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-blue-700 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                      aria-label={`${language === 'fr' ? 'Voir' : 'View'} ${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                    >
                      <Eye className="w-4 h-4" aria-hidden="true" />
                      {language === 'fr' ? 'Voir' : 'View'}
                    </button>
                    <button
                      onClick={() => handleEdit(vehicle)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                      aria-label={`${language === 'fr' ? 'Modifier' : 'Edit'} ${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                    >
                      <Edit2 className="w-4 h-4" aria-hidden="true" />
                      {language === 'fr' ? 'Modifier' : 'Edit'}
                    </button>
                    <button
                      onClick={() => handleDelete(vehicle)}
                      disabled={deleteMutation.isPending}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                      aria-label={`${language === 'fr' ? 'Supprimer' : 'Delete'} ${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                    >
                      <Trash2 className="w-4 h-4" aria-hidden="true" />
                      {language === 'fr' ? 'Supprimer' : 'Delete'}
                    </button>
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Form Modal */}
      <VehicleFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setEditingVehicle(undefined)
        }}
        vehicle={editingVehicle}
      />

      {/* Detail Modal */}
      {viewingVehicle && (
        <VehicleDetailModal
          vehicle={viewingVehicle}
          onClose={() => setViewingVehicle(null)}
          onEdit={(vehicle) => {
            setViewingVehicle(null)
            handleEdit(vehicle)
          }}
        />
      )}
    </div>
  )
}

