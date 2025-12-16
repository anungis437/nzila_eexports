import { createContext, useContext, useState, ReactNode } from 'react'
import { formatCurrency, XOF_RATE } from '../lib/utils'

type Language = 'en' | 'fr'

interface Translations {
  [key: string]: {
    en: string
    fr: string
  }
}

const translations: Translations = {
  // Navigation
  dashboard: { en: 'Dashboard', fr: 'Tableau de bord' },
  vehicles: { en: 'Vehicles', fr: 'Véhicules' },
  leads: { en: 'Leads', fr: 'Demandes' },
  deals: { en: 'Deals', fr: 'Transactions' },
  commissions: { en: 'Commissions', fr: 'Commissions' },
  shipments: { en: 'Shipments', fr: 'Expéditions' },
  settings: { en: 'Settings', fr: 'Paramètres' },
  logout: { en: 'Logout', fr: 'Déconnexion' },
  
  // Common
  search: { en: 'Search', fr: 'Rechercher' },
  filter: { en: 'Filter', fr: 'Filtrer' },
  add: { en: 'Add', fr: 'Ajouter' },
  edit: { en: 'Edit', fr: 'Modifier' },
  delete: { en: 'Delete', fr: 'Supprimer' },
  save: { en: 'Save', fr: 'Enregistrer' },
  cancel: { en: 'Cancel', fr: 'Annuler' },
  submit: { en: 'Submit', fr: 'Soumettre' },
  loading: { en: 'Loading...', fr: 'Chargement...' },
  noData: { en: 'No data available', fr: 'Aucune donnée disponible' },
  status: { en: 'Status', fr: 'Statut' },
  actions: { en: 'Actions', fr: 'Actions' },
  view: { en: 'View', fr: 'Voir' },
  export: { en: 'Export', fr: 'Exporter' },
  
  // Vehicles
  addVehicle: { en: 'Add Vehicle', fr: 'Ajouter un véhicule' },
  vehicleCatalog: { en: 'Vehicle Catalog', fr: 'Catalogue de véhicules' },
  vin: { en: 'VIN', fr: 'NIV' },
  make: { en: 'Make', fr: 'Marque' },
  model: { en: 'Model', fr: 'Modèle' },
  year: { en: 'Year', fr: 'Année' },
  mileage: { en: 'Mileage', fr: 'Kilométrage' },
  condition: { en: 'Condition', fr: 'État' },
  price: { en: 'Price', fr: 'Prix' },
  location: { en: 'Location', fr: 'Emplacement' },
  photos: { en: 'Photos', fr: 'Photos' },
  
  // Status
  available: { en: 'Available', fr: 'Disponible' },
  reserved: { en: 'Reserved', fr: 'Réservé' },
  inTransit: { en: 'In Transit', fr: 'En transit' },
  sold: { en: 'Sold', fr: 'Vendu' },
  pending: { en: 'Pending', fr: 'En attente' },
  matched: { en: 'Matched', fr: 'Associé' },
  accepted: { en: 'Accepted', fr: 'Accepté' },
  rejected: { en: 'Rejected', fr: 'Rejeté' },
  completed: { en: 'Completed', fr: 'Terminé' },
  
  // Leads
  submitLead: { en: 'Submit Lead', fr: 'Soumettre une demande' },
  buyerName: { en: 'Buyer Name', fr: 'Nom de l\'acheteur' },
  buyerPhone: { en: 'Buyer Phone', fr: 'Téléphone de l\'acheteur' },
  preferredMake: { en: 'Preferred Make', fr: 'Marque préférée' },
  budget: { en: 'Budget', fr: 'Budget' },
  
  // Deals
  dealDetails: { en: 'Deal Details', fr: 'Détails de la transaction' },
  askingPrice: { en: 'Asking Price', fr: 'Prix demandé' },
  offeredPrice: { en: 'Offered Price', fr: 'Prix offert' },
  
  // Welcome
  welcome: { en: 'Welcome', fr: 'Bienvenue' },
  quickActions: { en: 'Quick Actions', fr: 'Actions rapides' },
  recentActivity: { en: 'Recent Activity', fr: 'Activité récente' },
}

interface LanguageContextType {
  language: Language
  changeLanguage: (lang: Language) => void
  t: (key: string) => string
  formatCurrency: (amount: number, currency?: 'CAD' | 'XOF') => string
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en')

  const changeLanguage = (lang: Language) => {
    setLanguage(lang)
    localStorage.setItem('language', lang)
  }

  const t = (key: string): string => {
    return translations[key]?.[language] || key
  }

  const formatCurrencyWithLang = (amount: number, currency: 'CAD' | 'XOF' = 'CAD'): string => {
    return formatCurrency(amount, currency)
  }

  return (
    <LanguageContext.Provider
      value={{
        language,
        changeLanguage,
        t,
        formatCurrency: formatCurrencyWithLang,
      }}
    >
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

export { XOF_RATE }
