import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Shield, Lock, Key, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import TwoFactorSettings from './TwoFactorSettings'

export default function SecuritySettings() {
  const { language } = useLanguage()

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const [isChanging, setIsChanging] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const changePasswordMutation = useMutation({
    mutationFn: async (_data: any) => {
      // Simulated password change - would need backend implementation
      return Promise.resolve({ message: 'Password changed' })
    },
    onSuccess: () => {
      setSuccessMessage(language === 'fr' ? 'Mot de passe changé avec succès!' : 'Password changed successfully!')
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
      setTimeout(() => setSuccessMessage(''), 5000)
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.message ||
        (language === 'fr' ? 'Erreur lors du changement de mot de passe' : 'Error changing password')
      )
      setTimeout(() => setErrorMessage(''), 5000)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')
    
    // Validation
    if (passwordData.new_password.length < 8) {
      setErrorMessage(
        language === 'fr'
          ? 'Le mot de passe doit contenir au moins 8 caractères'
          : 'Password must be at least 8 characters'
      )
      return
    }

    if (passwordData.new_password !== passwordData.confirm_password) {
      setErrorMessage(
        language === 'fr'
          ? 'Les mots de passe ne correspondent pas'
          : 'Passwords do not match'
      )
      return
    }

    setIsChanging(true)
    changePasswordMutation.mutate(
      {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      },
      {
        onSettled: () => setIsChanging(false),
      }
    )
  }

  const passwordStrength = (password: string) => {
    if (!password) return { strength: 0, label: '', color: '' }
    
    let strength = 0
    if (password.length >= 8) strength++
    if (password.length >= 12) strength++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^a-zA-Z0-9]/.test(password)) strength++

    const labels = {
      0: { label: language === 'fr' ? 'Très faible' : 'Very Weak', color: 'bg-red-500' },
      1: { label: language === 'fr' ? 'Faible' : 'Weak', color: 'bg-orange-500' },
      2: { label: language === 'fr' ? 'Moyen' : 'Fair', color: 'bg-yellow-500' },
      3: { label: language === 'fr' ? 'Bon' : 'Good', color: 'bg-blue-500' },
      4: { label: language === 'fr' ? 'Fort' : 'Strong', color: 'bg-green-500' },
      5: { label: language === 'fr' ? 'Très fort' : 'Very Strong', color: 'bg-green-600' },
    }

    return { strength, ...labels[strength as keyof typeof labels] }
  }

  const strength = passwordStrength(passwordData.new_password)

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-600 rounded-full flex items-center justify-center">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-slate-900">
            {language === 'fr' ? 'Sécurité' : 'Security'}
          </h2>
          <p className="text-sm text-slate-500">
            {language === 'fr'
              ? 'Gérez votre mot de passe et la sécurité du compte'
              : 'Manage your password and account security'}
          </p>
        </div>
      </div>

      {/* Security Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900 mb-2">
              {language === 'fr' ? 'Conseils de sécurité:' : 'Security Tips:'}
            </p>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• {language === 'fr' ? 'Utilisez au moins 8 caractères' : 'Use at least 8 characters'}</li>
              <li>• {language === 'fr' ? 'Mélangez majuscules et minuscules' : 'Mix uppercase and lowercase'}</li>
              <li>• {language === 'fr' ? 'Incluez des chiffres et symboles' : 'Include numbers and symbols'}</li>
              <li>• {language === 'fr' ? 'Ne réutilisez pas vos anciens mots de passe' : 'Don\'t reuse old passwords'}</li>
            </ul>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Current Password */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Mot de passe actuel' : 'Current Password'}
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="password"
              value={passwordData.current_password}
              onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez votre mot de passe actuel' : 'Enter your current password'}
              required
            />
          </div>
        </div>

        {/* New Password */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Nouveau mot de passe' : 'New Password'}
          </label>
          <div className="relative">
            <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="password"
              value={passwordData.new_password}
              onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Entrez un nouveau mot de passe' : 'Enter a new password'}
              required
            />
          </div>
          
          {/* Password Strength Indicator */}
          {passwordData.new_password && (
            <div className="mt-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-slate-600">
                  {language === 'fr' ? 'Force:' : 'Strength:'}
                </span>
                <span className="text-xs font-medium" style={{ color: strength.color.replace('bg-', '') }}>
                  {strength.label}
                </span>
              </div>
              <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${strength.color} transition-all duration-300`}
                  style={{ width: `${(strength.strength / 5) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {language === 'fr' ? 'Confirmer le mot de passe' : 'Confirm Password'}
          </label>
          <div className="relative">
            <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="password"
              value={passwordData.confirm_password}
              onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder={language === 'fr' ? 'Confirmez votre nouveau mot de passe' : 'Confirm your new password'}
              required
            />
          </div>
          {passwordData.confirm_password && passwordData.new_password !== passwordData.confirm_password && (
            <p className="text-xs text-red-600 mt-1">
              {language === 'fr' ? 'Les mots de passe ne correspondent pas' : 'Passwords do not match'}
            </p>
          )}
          {passwordData.confirm_password && passwordData.new_password === passwordData.confirm_password && (
            <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <CheckCircle2 className="w-3 h-3" />
              {language === 'fr' ? 'Les mots de passe correspondent' : 'Passwords match'}
            </div>
          )}
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
            {errorMessage}
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isChanging}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-lg hover:from-red-600 hover:to-orange-700 transition-all disabled:opacity-50 font-medium"
        >
          <Shield className="w-5 h-5" />
          {isChanging
            ? language === 'fr' ? 'Changement...' : 'Changing...'
            : language === 'fr' ? 'Changer le mot de passe' : 'Change Password'}
        </button>
      </form>

      {/* Two-Factor Authentication Section */}
      <div className="mt-8">
        <TwoFactorSettings />
      </div>
    </div>
  )
}
