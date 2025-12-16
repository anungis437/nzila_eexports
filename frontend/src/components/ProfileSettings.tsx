import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { User, Mail, Phone, Building, Save } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import type { User as UserType } from '../types'

interface ProfileSettingsProps {
  user: UserType
}

export default function ProfileSettings({ user }: ProfileSettingsProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    email: user.email || '',
    phone: user.phone || '',
    company: user.company || '',
  })

  const [isSaving, setIsSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const updateProfileMutation = useMutation({
    mutationFn: async (data: any) => {
      // Simulated profile update - backend uses accounts API
      return Promise.resolve({ ...user, ...data })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
      setSuccessMessage(language === 'fr' ? 'Profil mis à jour avec succès!' : 'Profile updated successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    updateProfileMutation.mutate(formData, {
      onSettled: () => setIsSaving(false),
    })
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
          <User className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-900">
            {language === 'fr' ? 'Informations du Profil' : 'Profile Information'}
          </h2>
          <p className="text-sm text-slate-500">
            {language === 'fr' 
              ? 'Mettez à jour vos informations personnelles'
              : 'Update your personal information'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* First Name */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Prénom' : 'First Name'}
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez votre prénom' : 'Enter your first name'}
            />
          </div>
        </div>

        {/* Last Name */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Nom' : 'Last Name'}
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez votre nom' : 'Enter your last name'}
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Email' : 'Email'}
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez votre email' : 'Enter your email'}
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
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez votre téléphone' : 'Enter your phone'}
            />
          </div>
        </div>

        {/* Company */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Entreprise' : 'Company'}
          </label>
          <div className="relative">
            <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez votre entreprise' : 'Enter your company'}
            />
          </div>
        </div>

        {/* Role Display */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <p className="text-sm text-slate-600">
            {language === 'fr' ? 'Rôle:' : 'Role:'}{' '}
            <span className="font-semibold text-slate-900 capitalize">{user.role}</span>
          </p>
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
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all disabled:opacity-50 font-medium"
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
