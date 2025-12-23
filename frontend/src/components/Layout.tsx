import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useLanguage } from '../contexts/LanguageContext'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  Car,
  Users,
  FileText,
  DollarSign,
  Package,
  FolderOpen,
  Settings,
  LogOut,
  Menu,
  X,
  Globe,
  Search,
  CreditCard,
  Shield,
  MessageSquare,
  TrendingUp,
  Calculator,
  BadgeCheck,
  BarChart2,
  ChevronDown,
  ChevronRight,
  Heart,
  GitCompare,
  BookmarkCheck,
} from 'lucide-react'
import { Button } from './ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import NotificationBell from './NotificationBell'
import GlobalSearch from './GlobalSearch'
import KeyboardShortcutsModal from './KeyboardShortcutsModal'
import { useUnreadCount } from '../api/chat'

export default function Layout() {
  const { user, logout } = useAuth()
  const { language, changeLanguage, t } = useLanguage()
  const [searchOpen, setSearchOpen] = useState(false)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const { data: unreadCount } = useUnreadCount()
  
  // Collapsible sections state - Load from localStorage
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(() => {
    const saved = localStorage.getItem('collapsedNavSections')
    return saved ? new Set(JSON.parse(saved)) : new Set()
  })
  
  // Save collapsed state to localStorage
  useEffect(() => {
    localStorage.setItem('collapsedNavSections', JSON.stringify(Array.from(collapsedSections)))
  }, [collapsedSections])
  
  const toggleSection = (sectionTitle: string) => {
    setCollapsedSections(prev => {
      const next = new Set(prev)
      if (next.has(sectionTitle)) {
        next.delete(sectionTitle)
      } else {
        next.add(sectionTitle)
      }
      return next
    })
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Search shortcut: Cmd/Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
      // Help shortcut: ? (Shift + /)
      if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        // Only trigger if not in an input field
        const target = e.target as HTMLElement
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          e.preventDefault()
          setShortcutsOpen(true)
        }
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Route focus management for accessibility
  useEffect(() => {
    // Find the main h1 heading on the page and focus it after route change
    const mainHeading = document.querySelector('h1')
    if (mainHeading && mainHeading instanceof HTMLElement) {
      mainHeading.setAttribute('tabindex', '-1')
      mainHeading.focus()
      
      // Announce page change to screen readers
      const pageTitle = mainHeading.textContent || 'Page'
      const announcement = document.createElement('div')
      announcement.setAttribute('role', 'status')
      announcement.setAttribute('aria-live', 'polite')
      announcement.className = 'sr-only'
      announcement.textContent = `${language === 'fr' ? 'Navigué vers' : 'Navigated to'} ${pageTitle}`
      document.body.appendChild(announcement)
      
      // Clean up announcement after it's been read
      setTimeout(() => {
        document.body.removeChild(announcement)
      }, 1000)
    }
  }, [location.pathname, language])

  const navSections = [
    {
      title: language === 'fr' ? 'Aperçu' : 'Overview',
      items: [
        { name: t('dashboard'), path: '/dashboard', icon: LayoutDashboard, permission: 'all' },
        { name: language === 'fr' ? 'Messages' : 'Messages', path: '/messages', icon: MessageSquare, permission: 'all', badge: unreadCount?.unread_count },
      ]
    },
    {
      title: language === 'fr' ? 'Gestion' : 'Management',
      items: [
        { name: t('vehicles'), path: '/vehicles', icon: Car, permission: 'all' },
        { name: language === 'fr' ? 'Favoris' : 'Favorites', path: '/favorites', icon: Heart, permission: ['buyer'] },
        { name: language === 'fr' ? 'Comparer' : 'Compare', path: '/compare', icon: GitCompare, permission: ['buyer'] },
        { name: language === 'fr' ? 'Recherches sauvegardées' : 'Saved Searches', path: '/saved-searches', icon: BookmarkCheck, permission: ['buyer'] },
        { name: t('leads'), path: '/leads', icon: Users, permission: ['broker', 'admin'] },
        { name: t('deals'), path: '/deals', icon: FileText, permission: 'all' },
        { name: t('shipments'), path: '/shipments', icon: Package, permission: ['admin', 'dealer', 'buyer'] },
      ]
    },
    {
      title: language === 'fr' ? 'Finance' : 'Finance',
      items: [
        { name: t('commissions'), path: '/commissions', icon: DollarSign, permission: ['broker', 'dealer', 'admin'] },
        { name: language === 'fr' ? 'Financement' : 'Financing', path: '/financing', icon: Calculator, permission: 'all' },
        { name: language === 'fr' ? 'Paiements' : 'Payments', path: '/payments', icon: CreditCard, permission: 'all' },
      ]
    },
    {
      title: language === 'fr' ? 'Analytique' : 'Analytics',
      items: [
        { name: language === 'fr' ? 'Analytique Admin' : 'Admin Analytics', path: '/analytics', icon: BarChart2, permission: ['admin'] },
        { name: language === 'fr' ? 'Analytique Courtier' : 'Broker Analytics', path: '/broker-analytics', icon: TrendingUp, permission: ['broker', 'admin'] },
      ]
    },
    {
      title: language === 'fr' ? 'Sécurité & Conformité' : 'Security & Compliance',
      items: [
        { name: language === 'fr' ? 'Sécurité' : 'Security', path: '/security', icon: Shield, permission: ['admin'] },
        { name: language === 'fr' ? 'Conformité' : 'Compliance', path: '/compliance', icon: FileText, permission: ['admin'] },
        { name: language === 'fr' ? 'Sécurité des expéditions' : 'Shipment Security', path: '/shipment-security', icon: Package, permission: ['admin'] },
      ]
    },
    {
      title: language === 'fr' ? 'Opérations financières' : 'Financial Operations',
      items: [
        { name: language === 'fr' ? 'Taux d\'intérêt' : 'Interest Rates', path: '/interest-rates', icon: TrendingUp, permission: ['admin'] },
        { name: language === 'fr' ? 'Factures' : 'Invoices', path: '/invoices', icon: FileText, permission: ['admin'] },
        { name: language === 'fr' ? 'Transactions' : 'Transactions', path: '/transactions', icon: DollarSign, permission: ['admin'] },
      ]
    },
    {
      title: language === 'fr' ? 'Gestion des opérations' : 'Operations Management',
      items: [
        { name: language === 'fr' ? 'Inspections' : 'Inspections', path: '/inspections', icon: BadgeCheck, permission: ['admin'] },
        { name: language === 'fr' ? 'Offres' : 'Offers', path: '/offers', icon: DollarSign, permission: ['admin'] },
        { name: language === 'fr' ? 'Niveaux' : 'Tiers', path: '/tiers', icon: TrendingUp, permission: ['admin'] },
        { name: language === 'fr' ? 'Modération des avis' : 'Review Moderation', path: '/review-moderation', icon: MessageSquare, permission: ['admin'] },
      ]
    },
    {
      title: language === 'fr' ? 'Système' : 'System',
      items: [
        { name: language === 'fr' ? 'Documents' : 'Documents', path: '/documents', icon: FolderOpen, permission: 'all' },
        { name: language === 'fr' ? 'Vérification Concessionnaire' : 'Dealer Verification', path: '/dealer-verification', icon: BadgeCheck, permission: ['dealer', 'admin'] },
        { name: language === 'fr' ? 'Piste d\'audit' : 'Audit Trail', path: '/audit-trail', icon: Shield, permission: ['admin'] },
        { name: t('settings'), path: '/settings', icon: Settings, permission: 'all' },
      ]
    }
  ]

  const filterNavItems = (items: typeof navSections[0]['items']) => {
    return items.filter((item) => {
      if (item.permission === 'all') return true
      if (Array.isArray(item.permission)) {
        return item.permission.includes(user?.role || '')
      }
      return false
    })
  }

  const filteredSections = navSections
    .map(section => ({
      ...section,
      items: filterNavItems(section.items)
    }))
    .filter(section => section.items.length > 0)

  const NavLink = ({ item }: { item: typeof navItems[0] }) => {
    const isActive = location.pathname === item.path
    const Icon = item.icon
    return (
      <Link
        to={item.path}
        onClick={() => setMobileOpen(false)}
        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
          isActive
            ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
            : 'text-slate-600 hover:bg-slate-100'
        }`}
        aria-label={`${item.name}${isActive ? (language === 'fr' ? ' (page actuelle)' : ' (current page)') : ''}`}
        aria-current={isActive ? 'page' : undefined}
      >
        <Icon className="w-5 h-5" aria-hidden="true" />
        <span className="font-medium flex-1">{item.name}</span>
        {item.badge && item.badge > 0 && (
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            isActive ? 'bg-white text-primary-600' : 'bg-blue-600 text-white'
          }`}>
            {item.badge}
          </span>
        )}
      </Link>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-bg">
      {/* Skip to main content link for keyboard users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-lg focus:shadow-lg"
      >
        {language === 'fr' ? 'Aller au contenu principal' : 'Skip to main content'}
      </a>

      {/* Sidebar - Desktop */}
      <aside 
        className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col"
        aria-label={language === 'fr' ? 'Barre latérale de navigation' : 'Navigation sidebar'}
      >
        <div className="flex flex-col flex-1 min-h-0 bg-white border-r border-slate-200">
          {/* Logo */}
          <div className="p-6 border-b border-slate-100">
            <Link 
              to="/dashboard" 
              className="flex items-center gap-3"
              aria-label={language === 'fr' ? 'Retour au tableau de bord' : 'Back to dashboard'}
            >
              <div 
                className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/30"
                role="img"
                aria-label="Nzila Export Hub logo"
              >
                <span className="text-white font-bold text-lg" aria-hidden="true">N</span>
              </div>
              <div>
                <h1 className="font-bold text-slate-900 text-lg">Nzila</h1>
                <p className="text-xs text-slate-500">Export Hub</p>
              </div>
            </Link>
          </div>

          {/* Navigation */}
          <nav 
            className="flex-1 p-4 space-y-1 overflow-y-auto"
            aria-label={language === 'fr' ? 'Navigation principale' : 'Main navigation'}
          >
            {/* Search button */}
            <button
              onClick={() => setSearchOpen(true)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-100 transition-all duration-200 mb-4"
              aria-label={language === 'fr' ? 'Ouvrir la recherche (Commande+K)' : 'Open search (Ctrl+K)'}
            >
              <Search className="w-5 h-5" aria-hidden="true" />
              <span className="font-medium flex-1 text-left">
                {language === 'fr' ? 'Rechercher' : 'Search'}
              </span>
              <kbd 
                className="hidden xl:inline-block px-2 py-1 text-xs font-mono bg-slate-100 rounded border border-slate-300"
                aria-label={language === 'fr' ? 'Raccourci clavier: Commande K' : 'Keyboard shortcut: Command K'}
              >
                ⌘K
              </kbd>
            </button>

            {/* Sectioned Navigation */}
            {filteredSections.map((section, sectionIdx) => (
              <div key={section.title} className={sectionIdx > 0 ? 'mt-6' : ''}>
                <button
                  onClick={() => toggleSection(section.title)}
                  className="w-full flex items-center justify-between px-4 py-2 hover:bg-slate-50 rounded-lg transition-colors group"
                  aria-expanded={!collapsedSections.has(section.title) ? 'true' : 'false'}
                  aria-controls={`section-${section.title.replace(/\s+/g, '-').toLowerCase()}`}
                >
                  <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {section.title}
                  </h2>
                  {collapsedSections.has(section.title) ? (
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" aria-hidden="true" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" aria-hidden="true" />
                  )}
                </button>
                {!collapsedSections.has(section.title) && (
                  <div 
                    id={`section-${section.title.replace(/\s+/g, '-').toLowerCase()}`}
                    className="space-y-1 mt-1 overflow-hidden transition-all duration-200"
                  >
                    {section.items.map((item) => (
                      <NavLink key={item.path} item={item} />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* User Profile */}
          <div 
            className="p-4 border-t border-slate-100"
            role="region"
            aria-label={language === 'fr' ? 'Profil utilisateur' : 'User profile'}
          >
            <div className="flex items-center gap-3 mb-3">
              <div 
                className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center"
                role="img"
                aria-label={language === 'fr' ? `Avatar de ${user?.full_name}` : `${user?.full_name}'s avatar`}
              >
                <span className="text-primary-700 font-semibold text-sm" aria-hidden="true">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">{user?.full_name}</p>
                <p className="text-xs text-slate-500 capitalize">{user?.role}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <NotificationBell />
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    aria-label={language === 'fr' ? `Langue: ${language === 'fr' ? 'Français' : 'Anglais'}` : `Language: ${language === 'en' ? 'English' : 'French'}`}
                  >
                    <Globe className="w-4 h-4 mr-2" aria-hidden="true" />
                    {language.toUpperCase()}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => changeLanguage('en')}>English</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => changeLanguage('fr')}>Français</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={logout}
                aria-label={language === 'fr' ? 'Se déconnecter' : 'Log out'}
              >
                <LogOut className="w-4 h-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Header */}
      <div 
        className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200"
        role="banner"
        aria-label={language === 'fr' ? 'En-tête mobile' : 'Mobile header'}
      >
        <div className="flex items-center justify-between p-4">
          <Link 
            to="/dashboard" 
            className="flex items-center gap-2"
            aria-label={language === 'fr' ? 'Retour au tableau de bord' : 'Back to dashboard'}
          >
            <div 
              className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center"
              role="img"
              aria-label="Nzila logo"
            >
              <span className="text-white font-bold" aria-hidden="true">N</span>
            </div>
            <span className="font-bold text-slate-900">Nzila</span>
          </Link>
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setSearchOpen(true)}
              aria-label={language === 'fr' ? 'Ouvrir la recherche' : 'Open search'}
            >
              <Search className="w-6 h-6" aria-hidden="true" />
            </Button>
            <NotificationBell />
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label={mobileOpen 
                ? (language === 'fr' ? 'Fermer le menu' : 'Close menu')
                : (language === 'fr' ? 'Ouvrir le menu' : 'Open menu')
              }
              aria-expanded={mobileOpen}
              aria-controls="mobile-navigation"
            >
              {mobileOpen ? (
                <X className="w-6 h-6" aria-hidden="true" />
              ) : (
                <Menu className="w-6 h-6" aria-hidden="true" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {mobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-40 bg-black/50" 
          onClick={() => setMobileOpen(false)}
          role="presentation"
          aria-label={language === 'fr' ? 'Fermer le menu' : 'Close menu'}
        >
          <div
            id="mobile-navigation"
            className="fixed inset-y-0 left-0 w-64 bg-white"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label={language === 'fr' ? 'Menu de navigation mobile' : 'Mobile navigation menu'}
          >
            <nav 
              className="p-4 space-y-1 mt-16"
              aria-label={language === 'fr' ? 'Navigation principale' : 'Main navigation'}
            >
              {filteredSections.map((section, sectionIdx) => (
                <div key={section.title} className={sectionIdx > 0 ? 'mt-6' : ''}>
                  <button
                    onClick={() => toggleSection(section.title)}
                    className="w-full flex items-center justify-between px-4 py-2 hover:bg-slate-50 rounded-lg transition-colors group"
                    aria-expanded={!collapsedSections.has(section.title) ? 'true' : 'false'}
                    aria-controls={`mobile-section-${section.title.replace(/\s+/g, '-').toLowerCase()}`}
                  >
                    <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      {section.title}
                    </h2>
                    {collapsedSections.has(section.title) ? (
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" aria-hidden="true" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" aria-hidden="true" />
                    )}
                  </button>
                  {!collapsedSections.has(section.title) && (
                    <div 
                      id={`mobile-section-${section.title.replace(/\s+/g, '-').toLowerCase()}`}
                      className="space-y-1 mt-1 overflow-hidden transition-all duration-200"
                    >
                      {section.items.map((item) => (
                        <NavLink key={item.path} item={item} />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main 
        id="main-content"
        className="lg:pl-64"
        role="main"
        aria-label={language === 'fr' ? 'Contenu principal' : 'Main content'}
      >
        <div className="py-6 px-4 sm:px-6 lg:px-8 mt-16 lg:mt-0">
          <Outlet />
        </div>
      </main>

      {/* Global Search Modal */}
      <GlobalSearch 
        isOpen={searchOpen} 
        onClose={() => setSearchOpen(false)}
        aria-label={language === 'fr' ? 'Recherche globale' : 'Global search'}
      />

      {/* Keyboard Shortcuts Help Modal */}
      <KeyboardShortcutsModal
        isOpen={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
        language={language}
      />
    </div>
  )
}
