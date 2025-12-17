import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Heart, Search, Car, MapPin, Gauge, Trash2 } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Vehicle } from '../types'
import ImageGallery from '../components/ImageGallery'

interface FavoriteWithVehicle {
  id: number
  vehicle: number
  vehicle_details: Vehicle
  created_at: string
}

export default function Favorites() {
  const { language, formatCurrency } = useLanguage()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null)

  // Fetch favorites
  const { data: favorites = [], isLoading, refetch } = useQuery<FavoriteWithVehicle[]>({
    queryKey: ['favorites'],
    queryFn: async () => {
      const response = await api.get('/favorites/')
      return response.data
    },
  })

  // Filter favorites by search
  const filteredFavorites = favorites.filter((fav) => {
    const vehicle = fav.vehicle_details
    const searchLower = searchQuery.toLowerCase()
    return (
      vehicle.make.toLowerCase().includes(searchLower) ||
      vehicle.model.toLowerCase().includes(searchLower) ||
      vehicle.year.toString().includes(searchLower)
    )
  })

  const handleRemoveFavorite = async (favoriteId: number) => {
    try {
      await api.delete(`/favorites/${favoriteId}/`)
      refetch()
    } catch (error) {
      console.error('Failed to remove favorite:', error)
    }
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

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Heart className="w-7 h-7 text-red-500 fill-current" />
            {language === 'fr' ? 'Mes Favoris' : 'My Favorites'}
          </h1>
          <p className="text-slate-600 mt-1">
            {language === 'fr' 
              ? `${filteredFavorites.length} véhicule${filteredFavorites.length !== 1 ? 's' : ''} sauvegardé${filteredFavorites.length !== 1 ? 's' : ''}`
              : `${filteredFavorites.length} saved vehicle${filteredFavorites.length !== 1 ? 's' : ''}`}
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={language === 'fr' ? 'Rechercher dans mes favoris...' : 'Search favorites...'}
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 overflow-hidden animate-pulse">
              <div className="aspect-video bg-slate-200" />
              <div className="p-4 space-y-3">
                <div className="h-6 bg-slate-200 rounded w-3/4" />
                <div className="h-4 bg-slate-200 rounded w-1/2" />
                <div className="h-4 bg-slate-200 rounded w-full" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredFavorites.length === 0 && (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
          <Heart className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-700 mb-2">
            {searchQuery 
              ? (language === 'fr' ? 'Aucun favori trouvé' : 'No favorites found')
              : (language === 'fr' ? 'Aucun favori' : 'No favorites yet')}
          </h3>
          <p className="text-slate-500">
            {searchQuery
              ? (language === 'fr' ? 'Essayez une autre recherche' : 'Try a different search')
              : (language === 'fr' ? 'Commencez à sauvegarder des véhicules' : 'Start saving vehicles you like')}
          </p>
        </div>
      )}

      {/* Favorites Grid */}
      {!isLoading && filteredFavorites.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFavorites.map((favorite) => {
            const vehicle = favorite.vehicle_details
            return (
              <div
                key={favorite.id}
                className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow group"
              >
                {/* Image */}
                <div 
                  className="relative aspect-video bg-slate-100 overflow-hidden cursor-pointer"
                  onClick={() => setSelectedVehicle(vehicle)}
                >
                  {vehicle.main_image ? (
                    <img
                      src={vehicle.main_image}
                      alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <Car className="w-16 h-16 text-slate-300" />
                    </div>
                  )}
                  {/* Remove Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (window.confirm(language === 'fr' ? 'Retirer des favoris?' : 'Remove from favorites?')) {
                        handleRemoveFavorite(favorite.id)
                      }
                    }}
                    className="absolute top-3 right-3 p-2 bg-white/90 backdrop-blur-sm rounded-full hover:bg-red-50 transition-colors group"
                    aria-label="Remove from favorites"
                  >
                    <Trash2 className="w-4 h-4 text-slate-600 group-hover:text-red-500" />
                  </button>
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
                    <span className="text-2xl font-bold text-blue-600">
                      {formatCurrency(parseFloat(vehicle.price_cad))}
                    </span>
                  </div>

                  <div className="text-xs text-slate-500 space-y-1">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3 h-3" />
                      <span>{vehicle.location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Gauge className="w-3 h-3" />
                      <span>{vehicle.mileage.toLocaleString()} km</span>
                    </div>
                  </div>

                  <button
                    onClick={() => setSelectedVehicle(vehicle)}
                    className="w-full mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                  >
                    {language === 'fr' ? 'Voir détails' : 'View Details'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Vehicle Detail Modal */}
      {selectedVehicle && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedVehicle(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-900">
                {selectedVehicle.year} {selectedVehicle.make} {selectedVehicle.model}
              </h2>
              <button
                onClick={() => setSelectedVehicle(null)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label={language === 'fr' ? 'Fermer' : 'Close'}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Image Gallery */}
              <div className="mb-6">
                <ImageGallery
                  images={selectedVehicle.images || []}
                  mainImage={selectedVehicle.main_image || undefined}
                  altText={`${selectedVehicle.make} ${selectedVehicle.model}`}
                />
              </div>

              {/* Price */}
              <div className="mb-6 pb-6 border-b border-slate-200">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {formatCurrency(parseFloat(selectedVehicle.price_cad))}
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'Année' : 'Year'}</div>
                  <div className="font-semibold text-slate-900">{selectedVehicle.year}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'Kilométrage' : 'Mileage'}</div>
                  <div className="font-semibold text-slate-900">{selectedVehicle.mileage.toLocaleString()} km</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'Couleur' : 'Color'}</div>
                  <div className="font-semibold text-slate-900">{selectedVehicle.color}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'Transmission' : 'Transmission'}</div>
                  <div className="font-semibold text-slate-900">{selectedVehicle.transmission || 'N/A'}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'Carburant' : 'Fuel'}</div>
                  <div className="font-semibold text-slate-900">{selectedVehicle.fuel_type || 'N/A'}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'Condition' : 'Condition'}</div>
                  <div className="font-semibold text-slate-900">{getConditionLabel(selectedVehicle.condition)}</div>
                </div>
              </div>

              {/* Description */}
              {selectedVehicle.description && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {language === 'fr' ? 'Description' : 'Description'}
                  </h3>
                  <p className="text-slate-700 whitespace-pre-wrap">{selectedVehicle.description}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
