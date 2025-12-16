import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Settings as SettingsIcon, User, Building, DollarSign, Shield } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import ProfileSettings from '../components/ProfileSettings'
import CompanySettings from '../components/CompanySettings'
import CurrencySettings from '../components/CurrencySettings'
import SecuritySettings from '../components/SecuritySettings'

type Tab = 'profile' | 'company' | 'currency' | 'security'

export default function Settings() {
  const { language } = useLanguage()
  const [activeTab, setActiveTab] = useState<Tab>('profile')

  const { data: user, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: api.getCurrentUser,
  })

  const tabs = [
    {
      id: 'profile' as Tab,
      label: language === 'fr' ? 'Profil' : 'Profile',
      icon: User,
      description: language === 'fr' ? 'Informations personnelles' : 'Personal information',
    },
    {
      id: 'company' as Tab,
      label: language === 'fr' ? 'Entreprise' : 'Company',
      icon: Building,
      description: language === 'fr' ? 'Détails de l\'entreprise' : 'Company details',
    },
    {
      id: 'currency' as Tab,
      label: language === 'fr' ? 'Devises' : 'Currency',
      icon: DollarSign,
      description: language === 'fr' ? 'Taux de change' : 'Exchange rates',
    },
    {
      id: 'security' as Tab,
      label: language === 'fr' ? 'Sécurité' : 'Security',
      icon: Shield,
      description: language === 'fr' ? 'Mot de passe et sécurité' : 'Password and security',
    },
  ]

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
            <SettingsIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              {language === 'fr' ? 'Paramètres' : 'Settings'}
            </h1>
            <p className="text-slate-600">
              {language === 'fr'
                ? 'Gérez vos préférences et configurations'
                : 'Manage your preferences and configurations'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Sidebar Navigation */}
        <div className="col-span-12 lg:col-span-3">
          <div className="bg-white border border-slate-200 rounded-xl p-2 space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-md'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <div className="text-left flex-1">
                    <div className={`font-medium ${isActive ? 'text-white' : 'text-slate-900'}`}>
                      {tab.label}
                    </div>
                    <div className={`text-xs ${isActive ? 'text-purple-100' : 'text-slate-500'}`}>
                      {tab.description}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          {/* User Info Card */}
          {!isLoading && user && (
            <div className="mt-4 bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-xl p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-slate-900">
                    {user.first_name} {user.last_name}
                  </div>
                  <div className="text-sm text-slate-600">{user.email}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user.role === 'admin'
                      ? 'bg-red-100 text-red-800'
                      : user.role === 'dealer'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  {user.role === 'admin'
                    ? language === 'fr' ? 'Administrateur' : 'Administrator'
                    : user.role === 'dealer'
                    ? language === 'fr' ? 'Concessionnaire' : 'Dealer'
                    : language === 'fr' ? 'Courtier' : 'Broker'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="col-span-12 lg:col-span-9">
          {isLoading ? (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                <div className="h-4 bg-slate-200 rounded w-1/2"></div>
                <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'profile' && <ProfileSettings user={user} />}
              {activeTab === 'company' && <CompanySettings />}
              {activeTab === 'currency' && <CurrencySettings />}
              {activeTab === 'security' && <SecuritySettings />}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

