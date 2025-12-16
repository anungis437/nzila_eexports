import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  X,
  Car,
  Users,
  FileText,
  DollarSign,
  Package,
  FolderOpen,
  Command,
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import api from '../lib/api'

interface SearchResult {
  id: number
  type: 'vehicle' | 'lead' | 'deal' | 'commission' | 'shipment' | 'document'
  title: string
  subtitle: string
  metadata?: string
  url: string
}

interface GlobalSearchProps {
  isOpen: boolean
  onClose: () => void
}

export default function GlobalSearch({ isOpen, onClose }: GlobalSearchProps) {
  const { language } = useLanguage()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['all'])
  const searchInputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Search query with debouncing
  const { data: results = [], isLoading } = useQuery({
    queryKey: ['global-search', searchTerm, selectedTypes],
    queryFn: async () => {
      if (searchTerm.length < 2) return []
      const response = await api.globalSearch({
        q: searchTerm,
        types: selectedTypes.includes('all') ? undefined : selectedTypes.join(','),
      })
      return response
    },
    enabled: searchTerm.length >= 2,
  })

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [isOpen])

  // Reset state when closed
  useEffect(() => {
    if (!isOpen) {
      setSearchTerm('')
      setSelectedIndex(0)
      setSelectedTypes(['all'])
    }
  }, [isOpen])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter' && results[selectedIndex]) {
        e.preventDefault()
        handleResultClick(results[selectedIndex])
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, results, selectedIndex])

  // Scroll selected item into view
  useEffect(() => {
    if (resultsRef.current) {
      const selectedElement = resultsRef.current.querySelector(`[data-index="${selectedIndex}"]`)
      selectedElement?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [selectedIndex])

  const handleResultClick = (result: SearchResult) => {
    navigate(result.url)
    onClose()
    addToRecentSearches(result)
  }

  const addToRecentSearches = (result: SearchResult) => {
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]')
    const updated = [result, ...recent.filter((r: SearchResult) => r.id !== result.id || r.type !== result.type)].slice(0, 5)
    localStorage.setItem('recentSearches', JSON.stringify(updated))
  }

  const getResultIcon = (type: string) => {
    const iconClass = 'w-5 h-5'
    switch (type) {
      case 'vehicle':
        return <Car className={iconClass} />
      case 'lead':
        return <Users className={iconClass} />
      case 'deal':
        return <FileText className={iconClass} />
      case 'commission':
        return <DollarSign className={iconClass} />
      case 'shipment':
        return <Package className={iconClass} />
      case 'document':
        return <FolderOpen className={iconClass} />
      default:
        return <Search className={iconClass} />
    }
  }

  const getResultColor = (type: string) => {
    switch (type) {
      case 'vehicle':
        return 'from-blue-500 to-blue-600'
      case 'lead':
        return 'from-green-500 to-green-600'
      case 'deal':
        return 'from-purple-500 to-purple-600'
      case 'commission':
        return 'from-amber-500 to-amber-600'
      case 'shipment':
        return 'from-indigo-500 to-indigo-600'
      case 'document':
        return 'from-red-500 to-red-600'
      default:
        return 'from-slate-500 to-slate-600'
    }
  }

  const entityTypes = [
    { value: 'all', label: language === 'fr' ? 'Tout' : 'All' },
    { value: 'vehicle', label: language === 'fr' ? 'Véhicules' : 'Vehicles' },
    { value: 'lead', label: language === 'fr' ? 'Prospects' : 'Leads' },
    { value: 'deal', label: language === 'fr' ? 'Deals' : 'Deals' },
    { value: 'commission', label: language === 'fr' ? 'Commissions' : 'Commissions' },
    { value: 'shipment', label: language === 'fr' ? 'Expéditions' : 'Shipments' },
    { value: 'document', label: language === 'fr' ? 'Documents' : 'Documents' },
  ]

  const toggleType = (type: string) => {
    if (type === 'all') {
      setSelectedTypes(['all'])
    } else {
      const newTypes = selectedTypes.includes(type)
        ? selectedTypes.filter((t) => t !== type)
        : [...selectedTypes.filter((t) => t !== 'all'), type]
      setSelectedTypes(newTypes.length === 0 ? ['all'] : newTypes)
    }
    setSelectedIndex(0)
  }

  const groupedResults = results.reduce((acc: Record<string, SearchResult[]>, result: SearchResult) => {
    if (!acc[result.type]) acc[result.type] = []
    acc[result.type].push(result)
    return acc
  }, {})

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-20 px-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[600px] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={
                language === 'fr'
                  ? 'Rechercher des véhicules, prospects, deals...'
                  : 'Search vehicles, leads, deals...'
              }
              className="w-full pl-10 pr-10 py-3 text-lg border-0 focus:ring-0 focus:outline-none"
            />
            <button
              onClick={onClose}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-slate-100 rounded transition-colors"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          </div>

          {/* Type filters */}
          <div className="flex flex-wrap gap-2 mt-4">
            {entityTypes.map((type) => (
              <button
                key={type.value}
                onClick={() => toggleType(type.value)}
                className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${
                  selectedTypes.includes(type.value) || (type.value === 'all' && selectedTypes.includes('all'))
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <div ref={resultsRef} className="flex-1 overflow-auto">
          {searchTerm.length < 2 ? (
            <div className="p-12 text-center">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">
                {language === 'fr' ? 'Recherche globale' : 'Global Search'}
              </h3>
              <p className="text-slate-600 mb-4">
                {language === 'fr'
                  ? 'Recherchez à travers tous les véhicules, prospects, deals et plus'
                  : 'Search across all vehicles, leads, deals, and more'}
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg text-sm text-slate-600">
                <Command className="w-4 h-4" />
                <span>+</span>
                <kbd className="px-2 py-1 bg-white rounded border border-slate-300 text-xs font-mono">K</kbd>
                <span className="ml-2">{language === 'fr' ? 'pour ouvrir' : 'to open'}</span>
              </div>
            </div>
          ) : isLoading ? (
            <div className="p-8">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-4 animate-pulse">
                  <div className="w-12 h-12 bg-slate-200 rounded-lg" />
                  <div className="flex-1">
                    <div className="h-4 bg-slate-200 rounded w-2/3 mb-2" />
                    <div className="h-3 bg-slate-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : results.length === 0 ? (
            <div className="p-12 text-center">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">
                {language === 'fr' ? 'Aucun résultat trouvé' : 'No Results Found'}
              </h3>
              <p className="text-slate-600">
                {language === 'fr'
                  ? `Aucun résultat pour "${searchTerm}"`
                  : `No results found for "${searchTerm}"`}
              </p>
            </div>
          ) : (
            <div className="py-2">
              {Object.entries(groupedResults).map(([type, typeResults]) => (
                <div key={type}>
                  {/* Group header */}
                  <div className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-50">
                    {entityTypes.find((t) => t.value === type)?.label || type} ({(typeResults as SearchResult[]).length})
                  </div>

                  {/* Results */}
                  {(typeResults as SearchResult[]).map((result) => {
                    const globalIndex = results.indexOf(result)
                    return (
                      <button
                        key={`${result.type}-${result.id}`}
                        data-index={globalIndex}
                        onClick={() => handleResultClick(result)}
                        className={`w-full flex items-center gap-4 px-4 py-3 hover:bg-slate-50 transition-colors text-left ${
                          globalIndex === selectedIndex ? 'bg-blue-50' : ''
                        }`}
                      >
                        {/* Icon */}
                        <div
                          className={`w-12 h-12 rounded-lg bg-gradient-to-br ${getResultColor(
                            result.type
                          )} flex items-center justify-center text-white flex-shrink-0`}
                        >
                          {getResultIcon(result.type)}
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-slate-900 truncate">{result.title}</h4>
                          <p className="text-sm text-slate-600 truncate">{result.subtitle}</p>
                          {result.metadata && (
                            <p className="text-xs text-slate-500 truncate mt-0.5">{result.metadata}</p>
                          )}
                        </div>

                        {/* Arrow hint */}
                        {globalIndex === selectedIndex && (
                          <div className="text-slate-400">
                            <kbd className="px-2 py-1 bg-white rounded border border-slate-300 text-xs font-mono">
                              ↵
                            </kbd>
                          </div>
                        )}
                      </button>
                    )
                  })}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
          <div className="flex items-center justify-between text-xs text-slate-600">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <kbd className="px-2 py-1 bg-white rounded border border-slate-300 font-mono">↑</kbd>
                <kbd className="px-2 py-1 bg-white rounded border border-slate-300 font-mono">↓</kbd>
                <span className="ml-1">{language === 'fr' ? 'naviguer' : 'navigate'}</span>
              </div>
              <div className="flex items-center gap-1">
                <kbd className="px-2 py-1 bg-white rounded border border-slate-300 font-mono">↵</kbd>
                <span className="ml-1">{language === 'fr' ? 'sélectionner' : 'select'}</span>
              </div>
              <div className="flex items-center gap-1">
                <kbd className="px-2 py-1 bg-white rounded border border-slate-300 font-mono">esc</kbd>
                <span className="ml-1">{language === 'fr' ? 'fermer' : 'close'}</span>
              </div>
            </div>
            <div className="text-slate-500">
              {results.length} {language === 'fr' ? 'résultats' : 'results'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
