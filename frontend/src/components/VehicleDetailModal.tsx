import { X, Edit2, Trash2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Vehicle } from '../types'
import ImageGallery from './ImageGallery'
import ImageUpload from './ImageUpload'
import api from '../lib/api'
import { useState } from 'react'

interface VehicleDetailModalProps {
  vehicle: Vehicle
  onClose: () => void
  onEdit: (vehicle: Vehicle) => void
}

export default function VehicleDetailModal({ vehicle, onClose, onEdit }: VehicleDetailModalProps) {
  const queryClient = useQueryClient()
  const [showUpload, setShowUpload] = useState(false)

  const deleteImageMutation = useMutation({
    mutationFn: async (imageId: number) => {
      await api.delete(`/vehicles/${vehicle.id}/images/${imageId}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      queryClient.invalidateQueries({ queryKey: ['vehicle', vehicle.id] })
    },
  })

  const handleDeleteImage = (imageId: number) => {
    if (window.confirm('Delete this image?')) {
      deleteImageMutation.mutate(imageId)
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-2xl font-bold text-gray-900">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onEdit(vehicle)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Edit vehicle"
            >
              <Edit2 className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Image Gallery */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Images</h3>
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                {showUpload ? 'Hide Upload' : 'Upload Images'}
              </button>
            </div>

            {showUpload && (
              <div className="mb-6">
                <ImageUpload
                  vehicleId={vehicle.id}
                  onUploadComplete={() => {
                    setShowUpload(false)
                  }}
                />
              </div>
            )}

            <ImageGallery
              images={vehicle.images || []}
              mainImage={vehicle.main_image || undefined}
              altText={`${vehicle.make} ${vehicle.model}`}
            />

            {/* Image Management */}
            {vehicle.images && vehicle.images.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Manage Images</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                  {vehicle.images.map((image) => (
                    <div key={image.id} className="relative group">
                      <img
                        src={image.image}
                        alt={image.caption || 'Vehicle image'}
                        className="w-full h-24 object-cover rounded-lg"
                      />
                      {image.is_primary && (
                        <div className="absolute top-1 left-1 bg-blue-600 text-white text-xs px-2 py-0.5 rounded">
                          Primary
                        </div>
                      )}
                      <button
                        onClick={() => handleDeleteImage(image.id)}
                        className="absolute top-1 right-1 bg-red-600 hover:bg-red-700 text-white p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        aria-label="Delete image"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                      {image.caption && (
                        <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-1 truncate">
                          {image.caption}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Vehicle Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Vehicle Details</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">VIN</div>
                <div className="font-medium text-gray-900">{vehicle.vin}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Status</div>
                <div className="font-medium text-gray-900">{vehicle.status}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Condition</div>
                <div className="font-medium text-gray-900">{vehicle.condition}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Mileage</div>
                <div className="font-medium text-gray-900">{vehicle.mileage.toLocaleString()} km</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Color</div>
                <div className="font-medium text-gray-900">{vehicle.color}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Transmission</div>
                <div className="font-medium text-gray-900">{vehicle.transmission || 'N/A'}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Fuel Type</div>
                <div className="font-medium text-gray-900">{vehicle.fuel_type || 'N/A'}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Location</div>
                <div className="font-medium text-gray-900">{vehicle.location}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Price (CAD)</div>
                <div className="font-medium text-gray-900">${parseFloat(vehicle.price_cad).toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Description */}
          {vehicle.description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{vehicle.description}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
