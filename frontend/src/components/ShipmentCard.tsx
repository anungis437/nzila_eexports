import { Shipment } from '../types'
import { useLanguage } from '../contexts/LanguageContext'
import { Ship, MapPin, Calendar, Package, TrendingUp, Clock, CheckCircle2, AlertTriangle } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { enUS, fr } from 'date-fns/locale'

interface ShipmentCardProps {
  shipment: Shipment
  onClick?: () => void
}

export default function ShipmentCard({ shipment, onClick }: ShipmentCardProps) {
  const { language } = useLanguage()
  const locale = language === 'fr' ? fr : enUS

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-slate-100 text-slate-700 border-slate-200',
      in_transit: 'bg-blue-100 text-blue-700 border-blue-200',
      customs: 'bg-amber-100 text-amber-700 border-amber-200',
      delivered: 'bg-green-100 text-green-700 border-green-200',
      delayed: 'bg-red-100 text-red-700 border-red-200',
    }
    return colors[status] || colors.pending
  }

  const getStatusIcon = (status: string) => {
    if (status === 'delivered') return <CheckCircle2 className="w-4 h-4" />
    if (status === 'delayed') return <AlertTriangle className="w-4 h-4" />
    if (status === 'in_transit') return <Ship className="w-4 h-4" />
    if (status === 'customs') return <Package className="w-4 h-4" />
    return <Clock className="w-4 h-4" />
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      pending: { en: 'Pending', fr: 'En attente' },
      in_transit: { en: 'In Transit', fr: 'En transit' },
      customs: { en: 'At Customs', fr: 'En douane' },
      delivered: { en: 'Delivered', fr: 'Livré' },
      delayed: { en: 'Delayed', fr: 'Retardé' },
    }
    return labels[status]?.[language] || status
  }

  const getProgressPercentage = (status: string) => {
    const progress: Record<string, number> = {
      pending: 10,
      in_transit: 40,
      customs: 70,
      delivered: 100,
      delayed: 40,
    }
    return progress[status] || 0
  }

  const estimatedArrival = shipment.estimated_arrival 
    ? new Date(shipment.estimated_arrival)
    : null

  const actualArrival = shipment.actual_arrival
    ? new Date(shipment.actual_arrival)
    : null

  return (
    <div
      onClick={onClick}
      className={`bg-white border border-slate-200 rounded-xl p-5 hover:shadow-lg transition-all ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <Ship className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">
              {shipment.tracking_number}
            </h3>
            <p className="text-sm text-slate-500">
              {shipment.shipping_company}
            </p>
          </div>
        </div>
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${getStatusColor(shipment.status)}`}>
          {getStatusIcon(shipment.status)}
          {getStatusLabel(shipment.status)}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="relative h-2 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ${
              shipment.status === 'delayed' 
                ? 'bg-gradient-to-r from-red-500 to-red-600'
                : 'bg-gradient-to-r from-blue-500 to-indigo-600'
            }`}
            style={{ width: `${getProgressPercentage(shipment.status)}%` }}
          />
        </div>
      </div>

      {/* Route */}
      <div className="mb-4 pb-4 border-b border-slate-100">
        <div className="flex items-center gap-2 text-sm">
          <MapPin className="w-4 h-4 text-slate-400" />
          <div className="flex-1">
            <span className="text-slate-900 font-medium">{shipment.origin_port}</span>
            <TrendingUp className="w-3 h-3 text-slate-400 inline mx-2" />
            <span className="text-slate-900 font-medium">{shipment.destination_port}</span>
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-1 ml-6">
          {shipment.destination_country}
        </p>
      </div>

      {/* Vehicle Info */}
      {shipment.vehicle_details && (
        <div className="mb-4 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2 mb-1">
            <Package className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-500">
              {language === 'fr' ? 'Véhicule' : 'Vehicle'}
            </span>
          </div>
          <p className="text-sm font-medium text-slate-900">
            {shipment.vehicle_details.year} {shipment.vehicle_details.make} {shipment.vehicle_details.model}
          </p>
          <p className="text-xs text-slate-500">VIN: {shipment.vehicle_details.vin}</p>
        </div>
      )}

      {/* Dates */}
      <div className="space-y-2">
        {estimatedArrival && !actualArrival && (
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <Calendar className="w-3.5 h-3.5 text-amber-500" />
            <span>
              {language === 'fr' ? 'Arrivée prévue:' : 'Est. arrival:'}{' '}
              {format(estimatedArrival, 'MMM dd, yyyy', { locale })}
            </span>
          </div>
        )}
        
        {actualArrival && (
          <div className="flex items-center gap-2 text-xs text-green-600">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>
              {language === 'fr' ? 'Livré le' : 'Delivered'}{' '}
              {format(actualArrival, 'MMM dd, yyyy', { locale })}
            </span>
          </div>
        )}

        {!actualArrival && estimatedArrival && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Clock className="w-3.5 h-3.5" />
            <span>
              {formatDistanceToNow(estimatedArrival, { addSuffix: true, locale })}
            </span>
          </div>
        )}
      </div>

      {/* Deal Reference */}
      <div className="mt-4 pt-4 border-t border-slate-100">
        <p className="text-xs text-slate-500">
          {language === 'fr' ? 'Transaction' : 'Deal'} #{shipment.deal}
        </p>
      </div>
    </div>
  )
}
