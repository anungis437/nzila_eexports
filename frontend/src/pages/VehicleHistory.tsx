import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  FileText,
  Calendar,
  User,
  MapPin,
  Clock,
  AlertCircle,
  ExternalLink,
  Loader2,
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../lib/api'
import { Button } from '../components/ui/button'

interface VehicleHistoryData {
  vehicle: {
    id: number
    make: string
    model: string
    year: number
    vin: string
    dealer: string
  }
  sources: {
    carfax?: any
    autocheck?: any
    transport_canada?: any
    provincial_registry?: any
  }
  timestamp: string
}

export default function VehicleHistory() {
  const { vehicleId } = useParams<{ vehicleId: string }>()
  const { language } = useLanguage()
  const [activeTab, setActiveTab] = useState<'summary' | 'carfax' | 'recalls'>('summary')

  const { data: history, isLoading, error } = useQuery({
    queryKey: ['vehicle-history', vehicleId],
    queryFn: async () => {
      const response = await api.get(`/vehicle-history/${vehicleId}/`)
      return response.data as VehicleHistoryData
    },
    enabled: !!vehicleId,
  })

  const { data: recalls } = useQuery({
    queryKey: ['vehicle-recalls', vehicleId],
    queryFn: async () => {
      const response = await api.get(`/vehicle-history/${vehicleId}/recalls/`)
      return response.data
    },
    enabled: !!vehicleId,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-slate-600">
            {language === 'fr' ? 'Chargement de l\'historique...' : 'Loading vehicle history...'}
          </p>
        </div>
      </div>
    )
  }

  if (error || !history) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">
              {language === 'fr' ? 'Erreur de chargement' : 'Loading Error'}
            </h3>
            <p className="text-red-700 text-sm">
              {language === 'fr'
                ? 'Impossible de charger l\'historique du véhicule'
                : 'Unable to load vehicle history'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  const carfax = history.sources.carfax || {}
  const transportCanada = history.sources.transport_canada || {}
  const provincial = history.sources.provincial_registry || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-8 h-8" />
          <div>
            <h1 className="text-2xl font-bold">
              {language === 'fr' ? 'Historique du véhicule' : 'Vehicle History Report'}
            </h1>
            <p className="text-primary-100">
              {history.vehicle.year} {history.vehicle.make} {history.vehicle.model}
            </p>
          </div>
        </div>
        <div className="bg-white/10 rounded-lg p-3">
          <p className="text-xs text-primary-100 mb-1">
            {language === 'fr' ? 'NIV (VIN)' : 'Vehicle Identification Number (VIN)'}
          </p>
          <p className="font-mono text-lg font-semibold">{history.vehicle.vin}</p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {carfax.accidents !== undefined ? carfax.accidents : '—'}
              </p>
              <p className="text-xs text-slate-600">
                {language === 'fr' ? 'Accidents' : 'Accidents'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {carfax.owners !== undefined ? carfax.owners : '—'}
              </p>
              <p className="text-xs text-slate-600">
                {language === 'fr' ? 'Propriétaires' : 'Owners'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {carfax.service_records !== undefined ? carfax.service_records : '—'}
              </p>
              <p className="text-xs text-slate-600">
                {language === 'fr' ? 'Entretiens' : 'Service Records'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              (transportCanada.recall_count || 0) > 0 ? 'bg-red-100' : 'bg-green-100'
            }`}>
              <AlertTriangle className={`w-5 h-5 ${
                (transportCanada.recall_count || 0) > 0 ? 'text-red-600' : 'text-green-600'
              }`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {transportCanada.recall_count || 0}
              </p>
              <p className="text-xs text-slate-600">
                {language === 'fr' ? 'Rappels' : 'Recalls'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Mock Data Warning */}
      {(carfax.status === 'mock_data' || carfax.note) && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-amber-900 mb-1">
                {language === 'fr' ? 'Données de démonstration' : 'Demo Data'}
              </h3>
              <p className="text-sm text-amber-800">
                {language === 'fr'
                  ? 'API CarFax non configurée. Les données affichées sont des exemples à des fins de démonstration. Configurez CARFAX_API_KEY pour obtenir des données réelles.'
                  : 'CarFax API not configured. Showing sample data for demonstration purposes. Configure CARFAX_API_KEY to fetch real vehicle history.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="border-b border-slate-200">
          <div className="flex gap-4 px-6">
            <button
              onClick={() => setActiveTab('summary')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'summary'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              {language === 'fr' ? 'Résumé' : 'Summary'}
            </button>
            <button
              onClick={() => setActiveTab('carfax')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'carfax'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              CarFax Report
            </button>
            <button
              onClick={() => setActiveTab('recalls')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'recalls'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              {language === 'fr' ? 'Rappels' : 'Recalls'} 
              {(transportCanada.recall_count || 0) > 0 && (
                <span className="ml-2 bg-red-100 text-red-600 text-xs px-2 py-0.5 rounded-full">
                  {transportCanada.recall_count}
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Summary Tab */}
          {activeTab === 'summary' && (
            <div className="space-y-6">
              <div className="bg-slate-50 rounded-lg p-4">
                <h3 className="font-semibold text-slate-900 mb-3">
                  {language === 'fr' ? 'Points clés' : 'Key Highlights'}
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-slate-700">
                      <strong>{language === 'fr' ? 'Titre:' : 'Title:'}</strong>{' '}
                      {carfax.title_status || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-blue-600" />
                    <span className="text-sm text-slate-700">
                      <strong>{language === 'fr' ? 'Utilisation:' : 'Usage:'}</strong>{' '}
                      {carfax.usage_type || 'Unknown'}
                    </span>
                  </div>
                  {carfax.last_odometer && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-purple-600" />
                      <span className="text-sm text-slate-700">
                        <strong>{language === 'fr' ? 'Kilométrage:' : 'Odometer:'}</strong>{' '}
                        {carfax.last_odometer.toLocaleString()} km
                      </span>
                    </div>
                  )}
                  {carfax.provinces && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-slate-600" />
                      <span className="text-sm text-slate-700">
                        <strong>{language === 'fr' ? 'Provinces:' : 'Provinces:'}</strong>{' '}
                        {carfax.provinces.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {provincial.registration_status && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-3">
                    {language === 'fr' ? 'Registre provincial' : 'Provincial Registry'}
                  </h3>
                  <div className="space-y-2">
                    <p className="text-sm text-blue-800">
                      <strong>{language === 'fr' ? 'Province:' : 'Province:'}</strong>{' '}
                      {provincial.province}
                    </p>
                    <p className="text-sm text-blue-800">
                      <strong>{language === 'fr' ? 'Statut:' : 'Status:'}</strong>{' '}
                      {provincial.registration_status}
                    </p>
                    {provincial.last_inspection_date && (
                      <p className="text-sm text-blue-800">
                        <strong>{language === 'fr' ? 'Dernière inspection:' : 'Last Inspection:'}</strong>{' '}
                        {provincial.last_inspection_date}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* CarFax Tab */}
          {activeTab === 'carfax' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">
                {language === 'fr' ? 'Rapport CarFax complet' : 'Full CarFax Report'}
              </h3>
              <pre className="bg-slate-50 rounded-lg p-4 text-xs overflow-auto">
                {JSON.stringify(carfax, null, 2)}
              </pre>
            </div>
          )}

          {/* Recalls Tab */}
          {activeTab === 'recalls' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900 mb-4">
                {language === 'fr' ? 'Rappels Transport Canada' : 'Transport Canada Recalls'}
              </h3>
              {recalls && recalls.recalls && recalls.recalls.length > 0 ? (
                <div className="space-y-3">
                  {recalls.recalls.map((recall: any, index: number) => (
                    <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <h4 className="font-semibold text-red-900 mb-1">
                            {recall.component}
                          </h4>
                          <p className="text-sm text-red-800 mb-2">
                            {recall.description}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-red-700">
                            <span>
                              <strong>{language === 'fr' ? 'N° de rappel:' : 'Recall #:'}</strong>{' '}
                              {recall.recall_number}
                            </span>
                            <span>
                              <strong>{language === 'fr' ? 'Date:' : 'Date:'}</strong>{' '}
                              {recall.date}
                            </span>
                            <span>
                              <strong>{language === 'fr' ? 'Gravité:' : 'Severity:'}</strong>{' '}
                              {recall.severity}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
                  <p className="text-green-900 font-medium">
                    {language === 'fr'
                      ? 'Aucun rappel actif trouvé'
                      : 'No active recalls found'}
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    {language === 'fr'
                      ? 'Ce véhicule n\'a pas de rappels de sécurité en cours'
                      : 'This vehicle has no outstanding safety recalls'}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Data Sources Footer */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
        <p className="text-xs text-slate-600 mb-2 font-medium">
          {language === 'fr' ? 'Sources de données:' : 'Data Sources:'}
        </p>
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1 bg-white border border-slate-200 rounded px-2 py-1 text-xs text-slate-700">
            <CheckCircle className="w-3 h-3 text-green-600" />
            CarFax Canada
          </span>
          <span className="inline-flex items-center gap-1 bg-white border border-slate-200 rounded px-2 py-1 text-xs text-slate-700">
            <CheckCircle className="w-3 h-3 text-green-600" />
            Transport Canada
          </span>
          {provincial.province && (
            <span className="inline-flex items-center gap-1 bg-white border border-slate-200 rounded px-2 py-1 text-xs text-slate-700">
              <CheckCircle className="w-3 h-3 text-green-600" />
              {provincial.province} Registry
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
