import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Building, MapPin, Globe, Mail, Phone, Save } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'

export default function CompanySettings() {
  const { language } = useLanguage()
  const queryClient = useQueryClient()

  const { data: settings, isLoading } = useQuery({
    queryKey: ['companySettings'],
    queryFn: api.getCompanySettings,
  })

  const [formData, setFormData] = useState({
    company_name: settings?.company_name || 'Nzila Export Hub',
    address: settings?.address || '',
    city: settings?.city || '',
    country: settings?.country || 'Canada',
    postal_code: settings?.postal_code || '',
    email: settings?.email || '',
    phone: settings?.phone || '',
    website: settings?.website || '',
  })

  const [isSaving, setIsSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const updateSettingsMutation = useMutation({
    mutationFn: (data: any) => api.updateCompanySettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companySettings'] })
      setSuccessMessage(language === 'fr' ? 'Paramètres mis à jour avec succès!' : 'Settings updated successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    updateSettingsMutation.mutate(formData, {
      onSettled: () => setIsSaving(false),
    })
  }

  if (isLoading) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4" />
        <div className="space-y-4">
          <div className="h-10 bg-slate-200 rounded" />
          <div className="h-10 bg-slate-200 rounded" />
          <div className="h-10 bg-slate-200 rounded" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
          <Building className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-900">
            {language === 'fr' ? 'Paramètres de l\'Entreprise' : 'Company Settings'}
          </h2>
          <p className="text-sm text-slate-500">
            {language === 'fr'
              ? 'Gérez les informations de votre entreprise'
              : 'Manage your company information'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Company Name */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Nom de l\'Entreprise' : 'Company Name'}
          </label>
          <div className="relative">
            <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez le nom de l\'entreprise' : 'Enter company name'}
            />
          </div>
        </div>

        {/* Address */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Adresse' : 'Address'}
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez l\'adresse' : 'Enter address'}
            />
          </div>
        </div>

        {/* City & Postal Code */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {language === 'fr' ? 'Ville' : 'City'}
            </label>
            <input
              type="text"
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Ville' : 'City'}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {language === 'fr' ? 'Code Postal' : 'Postal Code'}
            </label>
            <input
              type="text"
              value={formData.postal_code}
              onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Code postal' : 'Postal code'}
            />
          </div>
        </div>

        {/* Country */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Pays' : 'Country'}
          </label>
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <select
              value={formData.country}
              onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="Canada">Canada</option>
              <option value="USA">United States</option>
              <option value="Senegal">Senegal</option>
              <option value="France">France</option>
            </select>
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Email de l\'Entreprise' : 'Company Email'}
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'contact@entreprise.com' : 'contact@company.com'}
            />
          </div>
        </div>

        {/* Phone */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Téléphone' : 'Phone'}
          </label>
          <div className="relative">
            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="+1 (555) 123-4567"
            />
          </div>
        </div>

        {/* Website */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Site Web' : 'Website'}
          </label>
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="url"
              value={formData.website}
              onChange={(e) => setFormData({ ...formData, website: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="https://www.example.com"
            />
          </div>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSaving}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg hover:from-purple-600 hover:to-indigo-700 transition-all disabled:opacity-50 font-medium"
        >
          <Save className="w-5 h-5" />
          {isSaving
            ? language === 'fr' ? 'Enregistrement...' : 'Saving...'
            : language === 'fr' ? 'Enregistrer les modifications' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
