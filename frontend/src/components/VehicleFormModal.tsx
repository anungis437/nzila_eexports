import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { Vehicle, VehicleFormData } from '../types'

interface VehicleFormModalProps {
  isOpen: boolean
  onClose: () => void
  vehicle?: Vehicle
}

export default function VehicleFormModal({ isOpen, onClose, vehicle }: VehicleFormModalProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const isEdit = !!vehicle

  const [formData, setFormData] = useState<VehicleFormData>({
    make: '',
    model: '',
    year: new Date().getFullYear(),
    vin: '',
    condition: 'used_good',
    mileage: 0,
    color: '',
    fuel_type: '',
    transmission: '',
    price_cad: '',
    status: 'available',
    description: '',
    location: '',
  })

  const [images, setImages] = useState<Array<{ id?: number; preview: string; file?: File }>>([])
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (vehicle) {
      setFormData({
        make: vehicle.make,
        model: vehicle.model,
        year: vehicle.year,
        vin: vehicle.vin,
        condition: vehicle.condition,
        mileage: vehicle.mileage,
        color: vehicle.color,
        fuel_type: vehicle.fuel_type || '',
        transmission: vehicle.transmission || '',
        price_cad: vehicle.price_cad,
        status: vehicle.status,
        description: vehicle.description || '',
        location: vehicle.location,
      })
      
      if (vehicle.main_image) {
        setImages([{ id: 0, preview: vehicle.main_image }])
      }
      if (vehicle.images) {
        setImages([
          ...images,
          ...vehicle.images.map(img => ({ id: img.id, preview: img.image }))
        ])
      }
    }
  }, [vehicle])

  const mutation = useMutation({
    mutationFn: async (data: FormData) => {
      if (isEdit && vehicle) {
        return api.updateVehicle(vehicle.id, data)
      }
      return api.createVehicle(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      onClose()
      resetForm()
    },
    onError: (error: any) => {
      const errorData = error.response?.data
      if (errorData) {
        setErrors(errorData)
      }
    },
  })

  const resetForm = () => {
    setFormData({
      make: '',
      model: '',
      year: new Date().getFullYear(),
      vin: '',
      condition: 'used_good',
      mileage: 0,
      color: '',
      fuel_type: '',
      transmission: '',
      price_cad: '',
      status: 'available',
      description: '',
      location: '',
    })
    setImages([])
    setErrors({})
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    const formDataToSend = new FormData()
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== '' && value !== undefined) {
        formDataToSend.append(key, value.toString())
      }
    })

    // Add main image (first image)
    if (images.length > 0 && images[0].file) {
      formDataToSend.append('main_image', images[0].file)
    }

    mutation.mutate(formDataToSend)
  }

  if (!isOpen) return null

  const conditionOptions = [
    { value: 'new', label: language === 'fr' ? 'Neuf' : 'New' },
    { value: 'used_excellent', label: language === 'fr' ? 'Usagé - Excellent' : 'Used - Excellent' },
    { value: 'used_good', label: language === 'fr' ? 'Usagé - Bon' : 'Used - Good' },
    { value: 'used_fair', label: language === 'fr' ? 'Usagé - Acceptable' : 'Used - Fair' },
  ]

  const statusOptions = [
    { value: 'available', label: language === 'fr' ? 'Disponible' : 'Available' },
    { value: 'reserved', label: language === 'fr' ? 'Réservé' : 'Reserved' },
    { value: 'sold', label: language === 'fr' ? 'Vendu' : 'Sold' },
    { value: 'shipped', label: language === 'fr' ? 'Expédié' : 'Shipped' },
    { value: 'delivered', label: language === 'fr' ? 'Livré' : 'Delivered' },
  ]

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="vehicle-form-title"
    >
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <h2 id="vehicle-form-title" className="text-xl font-bold text-slate-900">
            {isEdit
              ? language === 'fr' ? 'Modifier le véhicule' : 'Edit Vehicle'
              : language === 'fr' ? 'Ajouter un véhicule' : 'Add Vehicle'}
          </h2>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-600"
            aria-label={language === 'fr' ? 'Fermer le formulaire' : 'Close form'}
          >
            <X className="w-6 h-6" aria-hidden="true" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Images - TODO: Add ImageUpload component */}
          {/* <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {language === 'fr' ? 'Photos' : 'Photos'}
            </label>
            <ImageUpload
              images={images}
              onChange={setImages}
              vehicleId={vehicle?.id}
            />
          </div> */}

          {/* Basic Info */}
          <fieldset>
            <legend className="sr-only">{language === 'fr' ? 'Informations de base' : 'Basic Information'}</legend>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="vehicle-make" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Marque' : 'Make'} *
                </label>
                <input
                  id="vehicle-make"
                  type="text"
                  required
                  aria-required="true"
                  aria-invalid={!!errors.make}
                  aria-describedby={errors.make ? "make-error" : undefined}
                  autoComplete="off"
                  value={formData.make}
                  onChange={(e) => setFormData({ ...formData, make: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder={language === 'fr' ? 'Toyota, Honda...' : 'Toyota, Honda...'}
                />
                {errors.make && <p id="make-error" className="text-red-500 text-sm mt-1" role="alert">{errors.make}</p>}
              </div>

              <div>
                <label htmlFor="vehicle-model" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Modèle' : 'Model'} *
                </label>
                <input
                  id="vehicle-model"
                  type="text"
                  required
                  aria-required="true"
                  aria-invalid={!!errors.model}
                  aria-describedby={errors.model ? "model-error" : undefined}
                  autoComplete="off"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder={language === 'fr' ? 'Corolla, Civic...' : 'Corolla, Civic...'}
                />
                {errors.model && <p id="model-error" className="text-red-500 text-sm mt-1" role="alert">{errors.model}</p>}
              </div>

              <div>
                <label htmlFor="vehicle-year" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Année' : 'Year'} *
                </label>
                <input
                  id="vehicle-year"
                  type="number"
                  required
                  aria-required="true"
                  aria-invalid={!!errors.year}
                  aria-describedby={errors.year ? "year-error" : undefined}
                  min="1900"
                  max={new Date().getFullYear() + 1}
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
                {errors.year && <p id="year-error" className="text-red-500 text-sm mt-1" role="alert">{errors.year}</p>}
              </div>

              <div>
                <label htmlFor="vehicle-vin" className="block text-sm font-medium text-slate-700 mb-1">
                  VIN *
                </label>
                <input
                  id="vehicle-vin"
                  type="text"
                  required
                  aria-required="true"
                  aria-invalid={!!errors.vin}
                  aria-describedby={errors.vin ? "vin-error" : "vin-help"}
                  maxLength={17}
                  value={formData.vin}
                  onChange={(e) => setFormData({ ...formData, vin: e.target.value.toUpperCase() })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent font-mono"
                  placeholder="1HGBH41JXMN109186"
                />
                {!errors.vin && <p id="vin-help" className="text-xs text-slate-500 mt-1 sr-only">17-character Vehicle Identification Number</p>}
                {errors.vin && <p id="vin-error" className="text-red-500 text-sm mt-1" role="alert">{errors.vin}</p>}
              </div>

              <div>
                <label htmlFor="vehicle-condition" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Condition' : 'Condition'} *
                </label>
                <select
                  id="vehicle-condition"
                  required
                  aria-required="true"
                  value={formData.condition}
                  onChange={(e) => setFormData({ ...formData, condition: e.target.value as any })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  {conditionOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="vehicle-mileage" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Kilométrage' : 'Mileage'} (km) *
                </label>
                <input
                  id="vehicle-mileage"
                  type="number"
                  required
                  aria-required="true"
                  aria-invalid={!!errors.mileage}
                  aria-describedby={errors.mileage ? "mileage-error" : undefined}
                  min="0"
                  value={formData.mileage}
                  onChange={(e) => setFormData({ ...formData, mileage: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
                {errors.mileage && <p id="mileage-error" className="text-red-500 text-sm mt-1" role="alert">{errors.mileage}</p>}
              </div>

              <div>
                <label htmlFor="vehicle-color" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Couleur' : 'Color'} *
                </label>
                <input
                  id="vehicle-color"
                  type="text"
                  required
                  aria-required="true"
                  autoComplete="off"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder={language === 'fr' ? 'Noir, Blanc...' : 'Black, White...'}
                />
              </div>

              <div>
                <label htmlFor="vehicle-fuel" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Carburant' : 'Fuel Type'}
                </label>
                <input
                  id="vehicle-fuel"
                  type="text"
                  autoComplete="off"
                  value={formData.fuel_type}
                  onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder={language === 'fr' ? 'Essence, Diesel...' : 'Gasoline, Diesel...'}
                />
              </div>

              <div>
                <label htmlFor="vehicle-transmission" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Transmission' : 'Transmission'}
                </label>
                <input
                  id="vehicle-transmission"
                  type="text"
                  autoComplete="off"
                  value={formData.transmission}
                  onChange={(e) => setFormData({ ...formData, transmission: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder={language === 'fr' ? 'Automatique, Manuelle' : 'Automatic, Manual'}
                />
              </div>

              <div>
                <label htmlFor="vehicle-price" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Prix' : 'Price'} (CAD) *
                </label>
                <input
                  id="vehicle-price"
                  type="number"
                  required
                  aria-required="true"
                  aria-invalid={!!errors.price_cad}
                  aria-describedby={errors.price_cad ? "price-error" : undefined}
                  min="0"
                  step="0.01"
                  value={formData.price_cad}
                  onChange={(e) => setFormData({ ...formData, price_cad: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder="25000.00"
                />
                {errors.price_cad && <p id="price-error" className="text-red-500 text-sm mt-1" role="alert">{errors.price_cad}</p>}
              </div>

              <div>
                <label htmlFor="vehicle-location" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Emplacement' : 'Location'} *
                </label>
                <input
                  id="vehicle-location"
                  type="text"
                  required
                  aria-required="true"
                  autoComplete="off"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  placeholder={language === 'fr' ? 'Toronto, ON' : 'Toronto, ON'}
                />
              </div>

              <div>
                <label htmlFor="vehicle-status" className="block text-sm font-medium text-slate-700 mb-1">
                  {language === 'fr' ? 'Statut' : 'Status'} *
                </label>
                <select
                  id="vehicle-status"
                  required
                  aria-required="true"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                >
                  {statusOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </fieldset>

          {/* Description */}
          <div>
            <label htmlFor="vehicle-description" className="block text-sm font-medium text-slate-700 mb-1">
              {language === 'fr' ? 'Description' : 'Description'}
            </label>
            <textarea
              id="vehicle-description"
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder={language === 'fr' 
                ? 'Décrivez les caractéristiques du véhicule...'
                : 'Describe vehicle features...'}
              aria-label={language === 'fr' ? 'Description détaillée du véhicule' : 'Detailed vehicle description'}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
              aria-label={language === 'fr' ? 'Annuler et fermer le formulaire' : 'Cancel and close form'}
            >
              {language === 'fr' ? 'Annuler' : 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all disabled:opacity-50"
              aria-busy={mutation.isPending}
              aria-label={
                mutation.isPending
                  ? language === 'fr' ? 'Enregistrement du véhicule en cours' : 'Saving vehicle'
                  : isEdit
                    ? language === 'fr' ? 'Mettre à jour le véhicule' : 'Update vehicle'
                    : language === 'fr' ? 'Ajouter le véhicule' : 'Add vehicle'
              }
            >
              {mutation.isPending
                ? language === 'fr' ? 'Enregistrement...' : 'Saving...'
                : isEdit
                  ? language === 'fr' ? 'Mettre à jour' : 'Update'
                  : language === 'fr' ? 'Ajouter' : 'Add'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
