import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Search, Filter, Car, MapPin, Gauge, X, Send, CheckCircle2, MessageSquare } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import ImageGallery from '../components/ImageGallery'
import ComparisonCheckbox from '../components/ComparisonCheckbox'
import FavoriteButton from '../components/FavoriteButton'
import WhatsAppButton from '../components/WhatsAppButton'
import SaveSearchButton from '../components/SaveSearchButton'
import { PriceHistoryBadge } from '../components/PriceHistory'
import { SimilarVehicles, trackVehicleView } from '../components/SimilarVehicles'
import { SearchHistory, saveSearchToHistory } from '../components/SearchHistory'
import { VehicleHistory } from '../components/VehicleHistory'
import { FinancingCalculator } from '../components/FinancingCalculator'
import CurrencyConverter from '../components/CurrencyConverter'
import ShippingCalculator from '../components/ShippingCalculator'
import FinancingPreQualification from '../components/FinancingPreQualification'
import { useAuth } from '../contexts/AuthContext'
import { useStartConversation } from '../api/chat'
import { useNavigate } from 'react-router-dom'

interface VehicleImage {
  id: number
  image: string
  caption?: string
  is_primary?: boolean
  order: number
}

interface PriceHistoryItem {
  id: number
  old_price: string
  new_price: string
  price_difference: string
  percentage_change: string
  changed_at: string
  is_price_drop: boolean
}

interface Vehicle {
  id: number
  make: string
  model: string
  year: number
  vin: string
  condition: string
  mileage: number
  color: string
  fuel_type: string
  transmission: string
  price_cad: string
  description: string
  location: string
  main_image: string | null
  images?: VehicleImage[]
  dealer_name: string
  price_history?: PriceHistoryItem[]
}

export default function BuyerPortal() {
  const { language } = useLanguage()
  const { user } = useAuth()
  const navigate = useNavigate()
  const startConversation = useStartConversation()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedMake, setSelectedMake] = useState('')
  const [selectedYear, setSelectedYear] = useState('')
  const [selectedCondition, setSelectedCondition] = useState('')
  const [selectedFuelType, setSelectedFuelType] = useState('')
  const [selectedDrivetrain, setSelectedDrivetrain] = useState('')
  const [selectedEngineType, setSelectedEngineType] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'financing' | 'tools'>('overview')
  const [showLeadForm, setShowLeadForm] = useState(false)
  const [leadSubmitted, setLeadSubmitted] = useState(false)
  const [leadData, setLeadData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
  })

  // Handle contact dealer (start conversation)
  const handleContactDealer = async () => {
    if (!selectedVehicle || !selectedVehicle.dealer) return
    
    try {
      const conversation = await startConversation.mutateAsync({
        participant_id: selectedVehicle.dealer,
        vehicle_id: selectedVehicle.id,
        subject: `Inquiry about ${selectedVehicle.year} ${selectedVehicle.make} ${selectedVehicle.model}`,
        initial_message: `Hi, I'm interested in your ${selectedVehicle.year} ${selectedVehicle.make} ${selectedVehicle.model} (VIN: ${selectedVehicle.vin}). Can you provide more information?`,
      })
      
      // Navigate to messages page with the new conversation
      navigate('/messages')
    } catch (error) {
      console.error('Failed to start conversation:', error)
    }
  }

  // Load saved filters from localStorage
  React.useEffect(() => {
    const saved = localStorage.getItem('buyerPortalFilters')
    if (saved) {
      try {
        const filters = JSON.parse(saved)
        if (filters.make) setSelectedMake(filters.make)
        if (filters.year) setSelectedYear(filters.year)
        if (filters.condition) setSelectedCondition(filters.condition)
        if (filters.fuelType) setSelectedFuelType(filters.fuelType)
        if (filters.drivetrain) setSelectedDrivetrain(filters.drivetrain)
        if (filters.engineType) setSelectedEngineType(filters.engineType)
      } catch (e) {
        console.error('Failed to load saved filters', e)
      }
    }
  }, [])

  // Save filters to localStorage
  React.useEffect(() => {
    const filters = {
      make: selectedMake,
      year: selectedYear,
      condition: selectedCondition,
      fuelType: selectedFuelType,
      drivetrain: selectedDrivetrain,
      engineType: selectedEngineType,
    }
    localStorage.setItem('buyerPortalFilters', JSON.stringify(filters))
  }, [selectedMake, selectedYear, selectedCondition, selectedFuelType, selectedDrivetrain, selectedEngineType])

  // Track view when vehicle detail modal opens
  useEffect(() => {
    if (selectedVehicle) {
      trackVehicleView(selectedVehicle.id)
    }
  }, [selectedVehicle])

  // Save search to history when filters change or search is performed
  useEffect(() => {
    // Only save if there's actual search criteria
    if (searchTerm || selectedMake || selectedYear || selectedCondition || selectedFuelType || selectedDrivetrain || selectedEngineType) {
      // Debounce the save to avoid too many saves during typing
      const timeoutId = setTimeout(() => {
        saveSearchToHistory(searchTerm, {
          make: selectedMake,
          year: selectedYear,
          condition: selectedCondition,
          fuelType: selectedFuelType,
          drivetrain: selectedDrivetrain,
          engineType: selectedEngineType,
        });
      }, 1000); // Wait 1 second after user stops typing/changing filters

      return () => clearTimeout(timeoutId);
    }
  }, [searchTerm, selectedMake, selectedYear, selectedCondition, selectedFuelType, selectedDrivetrain, selectedEngineType])

  // Fetch available vehicles
  const { data: vehicles, isLoading } = useQuery({
    queryKey: ['publicVehicles', searchTerm, selectedMake, selectedYear, selectedCondition, selectedFuelType, selectedDrivetrain, selectedEngineType],
    queryFn: async () => {
      const params: any = { status: 'available' }
      if (searchTerm) params.search = searchTerm
      if (selectedMake) params.make = selectedMake
      if (selectedYear) params.year = selectedYear
      if (selectedCondition) params.condition = selectedCondition
      if (selectedFuelType) params.fuel_type = selectedFuelType
      if (selectedDrivetrain) params.drivetrain = selectedDrivetrain
      if (selectedEngineType) params.engine_type = selectedEngineType
      
      const response = await api.getVehicles(params)
      return response.results as Vehicle[]
    },
  })

  // Get unique makes for filter
  const makes = vehicles ? Array.from(new Set(vehicles.map((v: Vehicle) => v.make))).sort() : []

  // Lead submission mutation
  const submitLeadMutation = useMutation({
    mutationFn: async (_data: any) => {
      // This would call the leads API endpoint when authentication is set up
      // For now, simulate submission
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return { success: true, id: Math.random() }
    },
    onSuccess: () => {
      setLeadSubmitted(true)
      setTimeout(() => {
        setShowLeadForm(false)
        setLeadSubmitted(false)
        setLeadData({ name: '', email: '', phone: '', message: '' })
      }, 2000)
    },
  })

  const handleLeadSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedVehicle) return
    
    submitLeadMutation.mutate({
      vehicle_id: selectedVehicle.id,
      name: leadData.name,
      email: leadData.email,
      phone: leadData.phone,
      notes: leadData.message,
      source: 'website',
    })
  }

  const conditionLabels: Record<string, { en: string; fr: string }> = {
    new: { en: 'New', fr: 'Neuf' },
    used_excellent: { en: 'Used - Excellent', fr: 'Occasion - Excellent' },
    used_good: { en: 'Used - Good', fr: 'Occasion - Bon' },
    used_fair: { en: 'Used - Fair', fr: 'Occasion - Acceptable' },
  }

  const formatPrice = (price: string) => {
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD',
    }).format(parseFloat(price))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              {language === 'fr' ? 'Catalogue de Véhicules' : 'Vehicle Catalog'}
            </h1>
            <p className="text-xl text-blue-100">
              {language === 'fr'
                ? 'Parcourez notre sélection de véhicules canadiens de qualité'
                : 'Browse our selection of quality Canadian vehicles'}
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-3xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={
                  language === 'fr'
                    ? 'Rechercher par marque, modèle, ou emplacement...'
                    : 'Search by make, model, or location...'
                }
                className="w-full pl-12 pr-4 py-4 rounded-xl bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-lg"
              />
            </div>
            
            {/* Search History */}
            <div className="mt-3 flex justify-end">
              <SearchHistory
                onApplySearch={(item) => {
                  setSearchTerm(item.query);
                  setSelectedMake(item.filters.make || '');
                  setSelectedYear(item.filters.year || '');
                  setSelectedCondition(item.filters.condition || '');
                  setSelectedFuelType(item.filters.fuelType || '');
                  setSelectedDrivetrain(item.filters.drivetrain || '');
                  setSelectedEngineType(item.filters.engineType || '');
                }}
                language={language}
              />
            </div>
          </div>

          {/* Filter Toggle */}
          <div className="text-center mt-6">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg transition-colors"
            >
              <Filter className="w-5 h-5" />
              {language === 'fr' ? 'Filtres' : 'Filters'}
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white border-b border-slate-200 py-6">
          <div className="max-w-7xl mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Make Filter */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  {language === 'fr' ? 'Marque' : 'Make'}
                </label>
                <select
                  value={selectedMake}
                  onChange={(e) => setSelectedMake(e.target.value)}
                  aria-label={language === 'fr' ? 'Filtrer par marque' : 'Filter by make'}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{language === 'fr' ? 'Toutes' : 'All'}</option>
                  {makes.map((make) => (
                    <option key={make} value={make}>
                      {make}
                    </option>
                  ))}
                </select>
              </div>

              {/* Year Filter */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  {language === 'fr' ? 'Année' : 'Year'}
                </label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  aria-label={language === 'fr' ? 'Filtrer par année' : 'Filter by year'}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{language === 'fr' ? 'Toutes' : 'All'}</option>
                  {Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - i).map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>

              {/* Condition Filter */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  {language === 'fr' ? 'État' : 'Condition'}
                </label>
                <select
                  value={selectedCondition}
                  onChange={(e) => setSelectedCondition(e.target.value)}
                  aria-label={language === 'fr' ? 'Filtrer par état' : 'Filter by condition'}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{language === 'fr' ? 'Tous' : 'All'}</option>
                  {Object.entries(conditionLabels).map(([value, labels]) => (
                    <option key={value} value={value}>
                      {language === 'fr' ? labels.fr : labels.en}
                    </option>
                  ))}
                </select>
              </div>

              {/* Fuel Type Filter */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  {language === 'fr' ? 'Type de carburant' : 'Fuel Type'}
                </label>
                <select
                  value={selectedFuelType}
                  onChange={(e) => setSelectedFuelType(e.target.value)}
                  aria-label={language === 'fr' ? 'Filtrer par type de carburant' : 'Filter by fuel type'}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{language === 'fr' ? 'Tous' : 'All'}</option>
                  <option value="gasoline">{language === 'fr' ? 'Essence' : 'Gasoline'}</option>
                  <option value="diesel">{language === 'fr' ? 'Diesel' : 'Diesel'}</option>
                  <option value="electric">{language === 'fr' ? 'Électrique' : 'Electric'}</option>
                  <option value="hybrid">{language === 'fr' ? 'Hybride' : 'Hybrid'}</option>
                  <option value="plug-in-hybrid">{language === 'fr' ? 'Hybride rechargeable' : 'Plug-in Hybrid'}</option>
                </select>
              </div>

              {/* Engine Type Filter */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  {language === 'fr' ? 'Type de moteur' : 'Engine Type'}
                </label>
                <select
                  value={selectedEngineType}
                  onChange={(e) => setSelectedEngineType(e.target.value)}
                  aria-label={language === 'fr' ? 'Filtrer par type de moteur' : 'Filter by engine type'}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{language === 'fr' ? 'Tous' : 'All'}</option>
                  <option value="4-cylinder">{language === 'fr' ? '4 cylindres' : '4 Cylinder'}</option>
                  <option value="6-cylinder">{language === 'fr' ? '6 cylindres' : '6 Cylinder'}</option>
                  <option value="8-cylinder">{language === 'fr' ? '8 cylindres' : '8 Cylinder'}</option>
                  <option value="electric">{language === 'fr' ? 'Électrique' : 'Electric'}</option>
                  <option value="hybrid">{language === 'fr' ? 'Hybride' : 'Hybrid'}</option>
                  <option value="diesel">{language === 'fr' ? 'Diesel' : 'Diesel'}</option>
                </select>
              </div>

              {/* Drivetrain Filter */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  {language === 'fr' ? 'Traction' : 'Drivetrain'}
                </label>
                <select
                  value={selectedDrivetrain}
                  onChange={(e) => setSelectedDrivetrain(e.target.value)}
                  aria-label={language === 'fr' ? 'Filtrer par traction' : 'Filter by drivetrain'}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{language === 'fr' ? 'Tous' : 'All'}</option>
                  <option value="fwd">{language === 'fr' ? 'Traction avant (FWD)' : 'Front-Wheel Drive (FWD)'}</option>
                  <option value="rwd">{language === 'fr' ? 'Propulsion arrière (RWD)' : 'Rear-Wheel Drive (RWD)'}</option>
                  <option value="awd">{language === 'fr' ? 'Intégrale (AWD)' : 'All-Wheel Drive (AWD)'}</option>
                  <option value="4wd">{language === 'fr' ? '4 roues motrices (4WD)' : 'Four-Wheel Drive (4WD)'}</option>
                </select>
              </div>
            </div>

            {/* Clear Filters */}
            {(selectedMake || selectedYear || selectedCondition || selectedFuelType || selectedDrivetrain || selectedEngineType || searchTerm) && (
              <div className="mt-4 flex items-center justify-center gap-4">
                <button
                  onClick={() => {
                    setSelectedMake('')
                    setSelectedYear('')
                    setSelectedCondition('')
                    setSelectedFuelType('')
                    setSelectedDrivetrain('')
                    setSelectedEngineType('')
                    setSearchTerm('')
                    localStorage.removeItem('buyerPortalFilters')
                  }}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {language === 'fr' ? 'Effacer les filtres' : 'Clear filters'}
                </button>
                
                {user && (
                  <SaveSearchButton
                    currentFilters={{
                      make: selectedMake || undefined,
                      yearMin: selectedYear ? parseInt(selectedYear) : undefined,
                      condition: selectedCondition || undefined,
                    }}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Vehicle Grid */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl overflow-hidden shadow-md animate-pulse">
                <div className="h-48 bg-slate-200" />
                <div className="p-4 space-y-3">
                  <div className="h-6 bg-slate-200 rounded w-3/4" />
                  <div className="h-4 bg-slate-200 rounded w-1/2" />
                  <div className="h-4 bg-slate-200 rounded w-full" />
                </div>
              </div>
            ))}
          </div>
        ) : vehicles && vehicles.length > 0 ? (
          <>
            <div className="mb-6 text-slate-600">
              {vehicles.length} {language === 'fr' ? 'véhicule(s) disponible(s)' : 'vehicle(s) available'}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {vehicles.map((vehicle) => (
                <div
                  key={vehicle.id}
                  onClick={() => setSelectedVehicle(vehicle)}
                  className="bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all cursor-pointer group"
                >
                  {/* Image */}
                  <div className="relative h-48 bg-gradient-to-br from-slate-200 to-slate-300 overflow-hidden">
                    {vehicle.main_image ? (
                      <img
                        src={vehicle.main_image}
                        alt={`${vehicle.make} ${vehicle.model}`}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Car className="w-16 h-16 text-slate-400" />
                      </div>
                    )}
                    {/* Price Drop Badge */}
                    <PriceHistoryBadge 
                      priceHistory={vehicle.price_history}
                      currentPrice={vehicle.price_cad}
                    />
                    {/* Condition Badge */}
                    <div className="absolute top-3 left-3 px-3 py-1 bg-blue-600 text-white text-xs font-semibold rounded-full">
                      {language === 'fr'
                        ? conditionLabels[vehicle.condition]?.fr
                        : conditionLabels[vehicle.condition]?.en}
                    </div>
                    {/* Favorite and Comparison - Top Right */}
                    {user && (
                      <div className="absolute top-3 right-3 flex flex-col gap-2">
                        <div onClick={(e) => e.stopPropagation()}>
                          <FavoriteButton vehicle={vehicle} />
                        </div>
                        <div className="bg-white rounded-lg px-2 py-1">
                          <ComparisonCheckbox vehicle={vehicle} />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <h3 className="text-xl font-bold text-slate-900 mb-2">
                      {vehicle.year} {vehicle.make} {vehicle.model}
                    </h3>

                    {/* Quick Stats */}
                    <div className="space-y-2 text-sm text-slate-600 mb-4">
                      <div className="flex items-center gap-2">
                        <Gauge className="w-4 h-4" />
                        {vehicle.mileage.toLocaleString()} km
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        {vehicle.location}
                      </div>
                    </div>

                    {/* Price */}
                    <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                      <div>
                        <div className="text-2xl font-bold text-blue-600">{formatPrice(vehicle.price_cad)}</div>
                        <div className="text-xs text-slate-500">CAD</div>
                      </div>
                      <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                        {language === 'fr' ? 'Voir détails' : 'View Details'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-16">
            <Car className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">
              {language === 'fr' ? 'Aucun véhicule trouvé' : 'No vehicles found'}
            </h3>
            <p className="text-slate-500">
              {language === 'fr'
                ? 'Essayez de modifier vos critères de recherche'
                : 'Try adjusting your search criteria'}
            </p>
          </div>
        )}
      </div>

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
            <div className="sticky top-0 bg-white border-b border-slate-200">
              <div className="px-6 py-4 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-900">
                  {selectedVehicle.year} {selectedVehicle.make} {selectedVehicle.model}
                </h2>
                <button
                  onClick={() => {
                    setSelectedVehicle(null);
                    setActiveTab('overview');
                  }}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                  aria-label={language === 'fr' ? 'Fermer' : 'Close'}
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              {/* Tabs */}
              <div className="flex gap-6 px-6">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`pb-3 px-1 font-medium transition-colors border-b-2 ${
                    activeTab === 'overview'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {language === 'fr' ? 'Aperçu' : 'Overview'}
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`pb-3 px-1 font-medium transition-colors border-b-2 ${
                    activeTab === 'history'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {language === 'fr' ? 'Rapport d\'historique' : 'History Report'}
                </button>
                <button
                  onClick={() => setActiveTab('financing')}
                  className={`pb-3 px-1 font-medium transition-colors border-b-2 ${
                    activeTab === 'financing'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {language === 'fr' ? 'Financement' : 'Financing'}
                </button>
                <button
                  onClick={() => setActiveTab('tools')}
                  className={`pb-3 px-1 font-medium transition-colors border-b-2 ${
                    activeTab === 'tools'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {language === 'fr' ? 'Outils d\'achat' : 'Buyer Tools'}
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {activeTab === 'overview' ? (
                <>
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
                <div className="text-4xl font-bold text-blue-600 mb-2">{formatPrice(selectedVehicle.price_cad)}</div>
                <div className="text-slate-500">CAD</div>
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
                  <div className="text-sm text-slate-600 mb-1">{language === 'fr' ? 'État' : 'Condition'}</div>
                  <div className="font-semibold text-slate-900">
                    {language === 'fr'
                      ? conditionLabels[selectedVehicle.condition]?.fr
                      : conditionLabels[selectedVehicle.condition]?.en}
                  </div>
                </div>
              </div>

              {/* Location */}
              <div className="mb-6 flex items-center gap-2 text-slate-600">
                <MapPin className="w-5 h-5" />
                <span>{selectedVehicle.location}</span>
              </div>

              {/* Description */}
              {selectedVehicle.description && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {language === 'fr' ? 'Description' : 'Description'}
                  </h3>
                  <p className="text-slate-600 leading-relaxed">{selectedVehicle.description}</p>
                </div>
              )}

              {/* VIN */}
              <div className="mb-6 p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-600 mb-1">VIN</div>
                <div className="font-mono text-slate-900 font-semibold">{selectedVehicle.vin}</div>
              </div>

              {/* Lead Form */}
              {!showLeadForm ? (
                <div className="space-y-3">
                  {/* Contact Dealer via Chat */}
                  {user && selectedVehicle.dealer && (
                    <button
                      onClick={handleContactDealer}
                      disabled={startConversation.isPending}
                      className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      <MessageSquare className="w-5 h-5" />
                      {language === 'fr' ? 'Contacter le concessionnaire' : 'Contact Dealer'}
                    </button>
                  )}
                  
                  <button
                    onClick={() => setShowLeadForm(true)}
                    className="w-full py-4 bg-white border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold rounded-xl transition-all"
                  >
                    {language === 'fr' ? "Demander plus d'informations" : 'Request More Information'}
                  </button>
                  
                  {/* WhatsApp Button */}
                  <WhatsAppButton
                    phoneNumber="+1234567890"
                    message={`Hi! I'm interested in the ${selectedVehicle.year} ${selectedVehicle.make} ${selectedVehicle.model} (VIN: ${selectedVehicle.vin}). Can you provide more details?`}
                    size="lg"
                    className="w-full justify-center"
                  />
                </div>
              ) : leadSubmitted ? (
                <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
                  <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-green-900 mb-2">
                    {language === 'fr' ? 'Demande envoyée!' : 'Request Sent!'}
                  </h3>
                  <p className="text-green-700">
                    {language === 'fr'
                      ? 'Nous vous contacterons bientôt.'
                      : "We'll be in touch with you soon."}
                  </p>
                </div>
              ) : (
                <form onSubmit={handleLeadSubmit} className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <p className="text-sm text-blue-900">
                      {language === 'fr'
                        ? 'Remplissez le formulaire ci-dessous et nous vous contacterons sous peu.'
                        : 'Fill out the form below and we\'ll get back to you shortly.'}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      {language === 'fr' ? 'Nom complet' : 'Full Name'} *
                    </label>
                    <input
                      type="text"
                      required
                      value={leadData.name}
                      onChange={(e) => setLeadData({ ...leadData, name: e.target.value })}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder={language === 'fr' ? 'Votre nom' : 'Your name'}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      {language === 'fr' ? 'Email' : 'Email'} *
                    </label>
                    <input
                      type="email"
                      required
                      value={leadData.email}
                      onChange={(e) => setLeadData({ ...leadData, email: e.target.value })}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder={language === 'fr' ? 'votre@email.com' : 'your@email.com'}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      {language === 'fr' ? 'Téléphone' : 'Phone'}
                    </label>
                    <input
                      type="tel"
                      value={leadData.phone}
                      onChange={(e) => setLeadData({ ...leadData, phone: e.target.value })}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder={language === 'fr' ? '+221 XX XXX XX XX' : '+1 (XXX) XXX-XXXX'}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      {language === 'fr' ? 'Message' : 'Message'}
                    </label>
                    <textarea
                      value={leadData.message}
                      onChange={(e) => setLeadData({ ...leadData, message: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder={
                        language === 'fr'
                          ? 'Questions ou commentaires supplémentaires...'
                          : 'Any additional questions or comments...'
                      }
                    />
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => setShowLeadForm(false)}
                      className="flex-1 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 font-medium transition-colors"
                    >
                      {language === 'fr' ? 'Annuler' : 'Cancel'}
                    </button>
                    <button
                      type="submit"
                      disabled={submitLeadMutation.isPending}
                      className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {submitLeadMutation.isPending ? (
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          {language === 'fr' ? 'Envoyer' : 'Send'}
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
              
              {/* Similar Vehicles Section */}
              <div className="mt-8">
                <SimilarVehicles
                  referenceVehicleId={selectedVehicle.id}
                  onVehicleClick={(vehicle) => {
                    setSelectedVehicle(vehicle)
                    setShowLeadForm(false)
                    setLeadSubmitted(false)
                    setActiveTab('overview')
                    // Track view for new vehicle
                    trackVehicleView(vehicle.id)
                  }}
                />
              </div>
                </>
              ) : activeTab === 'history' ? (
                /* History Tab */
                <VehicleHistory vehicleId={selectedVehicle.id} language={language} />
              ) : activeTab === 'financing' ? (
                /* Financing Tab */
                <FinancingCalculator vehiclePrice={selectedVehicle.price} language={language} />
              ) : (
                /* Buyer Tools Tab */
                <div className="space-y-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-900">
                      {language === 'fr' 
                        ? 'Utilisez ces outils pour planifier votre achat et comprendre les coûts totaux.'
                        : 'Use these tools to plan your purchase and understand the total costs.'}
                    </p>
                  </div>

                  {/* Currency Converter */}
                  <CurrencyConverter 
                    baseAmount={parseFloat(selectedVehicle.price_cad)} 
                    baseCurrency="CAD"
                  />

                  {/* Shipping Calculator */}
                  <ShippingCalculator 
                    vehicleYear={selectedVehicle.year}
                    vehicleMake={selectedVehicle.make}
                    vehicleModel={selectedVehicle.model}
                  />

                  {/* Financing Pre-Qualification */}
                  <FinancingPreQualification 
                    vehiclePrice={parseFloat(selectedVehicle.price_cad)}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

