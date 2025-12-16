import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, LayoutGrid, LayoutList, Search, Filter } from 'lucide-react'
import api from '../lib/api'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import KanbanBoard from '../components/KanbanBoard'
import LeadFormModal from '../components/LeadFormModal'
import LeadDetailModal from '../components/LeadDetailModal'
import { Lead } from '../types'

export default function Leads() {
  const { t, language } = useLanguage()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [editingLead, setEditingLead] = useState<Lead | undefined>()
  const [selectedLead, setSelectedLead] = useState<Lead | undefined>()
  const [searchQuery, setSearchQuery] = useState('')
  const [sourceFilter, setSourceFilter] = useState<string>('all')

  // Fetch leads
  const { data: leads = [], isLoading } = useQuery({
    queryKey: ['leads', sourceFilter],
    queryFn: async () => {
      const params: any = {}
      if (sourceFilter !== 'all') params.source = sourceFilter
      const response = await api.getLeads(params)
      return Array.isArray(response) ? response : response.results || []
    },
  })

  // Update lead status (drag & drop)
  const updateStatusMutation = useMutation({
    mutationFn: ({ leadId, newStatus }: { leadId: number; newStatus: Lead['status'] }) =>
      api.updateLead(leadId, { status: newStatus }),
    onMutate: async ({ leadId, newStatus }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['leads'] })
      const previousLeads = queryClient.getQueryData(['leads'])
      
      queryClient.setQueryData(['leads'], (old: Lead[] = []) =>
        old.map(lead => lead.id === leadId ? { ...lead, status: newStatus } : lead)
      )
      
      return { previousLeads }
    },
    onError: (_err, _variables, context) => {
      // Rollback on error
      if (context?.previousLeads) {
        queryClient.setQueryData(['leads'], context.previousLeads)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] })
    },
  })

  // Filter leads by search query
  const filteredLeads = leads.filter((lead: Lead) => {
    const searchLower = searchQuery.toLowerCase()
    return (
      lead.buyer_name?.toLowerCase().includes(searchLower) ||
      lead.vehicle_details?.make?.toLowerCase().includes(searchLower) ||
      lead.vehicle_details?.model?.toLowerCase().includes(searchLower) ||
      lead.vehicle_details?.vin?.toLowerCase().includes(searchLower)
    )
  })

  const handleLeadClick = (lead: Lead) => {
    setSelectedLead(lead)
    setIsDetailOpen(true)
  }

  const handleEdit = (lead: Lead) => {
    setEditingLead(lead)
    setIsFormOpen(true)
    setIsDetailOpen(false)
  }

  const handleAdd = () => {
    setEditingLead(undefined)
    setIsFormOpen(true)
  }

  const handleStatusChange = (leadId: number, newStatus: Lead['status']) => {
    updateStatusMutation.mutate({ leadId, newStatus })
  }

  const canManageLeads = user?.role === 'admin' || user?.role === 'dealer' || user?.role === 'broker'

  // Lead statistics
  const stats = {
    total: filteredLeads.length,
    new: filteredLeads.filter((l: Lead) => l.status === 'new').length,
    qualified: filteredLeads.filter((l: Lead) => l.status === 'qualified').length,
    negotiating: filteredLeads.filter((l: Lead) => l.status === 'negotiating').length,
    converted: filteredLeads.filter((l: Lead) => l.status === 'converted').length,
  }

  return (
    <div className="max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('leads')}</h1>
          <div className="flex items-center gap-4 mt-2 text-sm">
            <span className="text-slate-600">
              {language === 'fr' ? 'Total:' : 'Total:'} <span className="font-semibold">{stats.total}</span>
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-blue-600">
              {language === 'fr' ? 'Nouveau:' : 'New:'} <span className="font-semibold">{stats.new}</span>
            </span>
            <span className="text-green-600">
              {language === 'fr' ? 'Qualifié:' : 'Qualified:'} <span className="font-semibold">{stats.qualified}</span>
            </span>
            <span className="text-amber-600">
              {language === 'fr' ? 'Négociation:' : 'Negotiating:'} <span className="font-semibold">{stats.negotiating}</span>
            </span>
            <span className="text-purple-600">
              {language === 'fr' ? 'Converti:' : 'Converted:'} <span className="font-semibold">{stats.converted}</span>
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* View Mode Toggle */}
          <div className="flex bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('kanban')}
              className={`px-3 py-1.5 rounded transition-colors ${
                viewMode === 'kanban' ? 'bg-white shadow-sm text-amber-600' : 'text-slate-600'
              }`}
            >
              <LayoutGrid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded transition-colors ${
                viewMode === 'list' ? 'bg-white shadow-sm text-amber-600' : 'text-slate-600'
              }`}
            >
              <LayoutList className="w-5 h-5" />
            </button>
          </div>

          {canManageLeads && (
            <button
              onClick={handleAdd}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all"
            >
              <Plus className="w-5 h-5" />
              {language === 'fr' ? 'Ajouter prospect' : 'Add Lead'}
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={language === 'fr' ? 'Rechercher acheteur, véhicule...' : 'Search buyer, vehicle...'}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            />
          </div>

          {/* Source Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent appearance-none"
            >
              <option value="all">{language === 'fr' ? 'Toutes les sources' : 'All Sources'}</option>
              <option value="website">{language === 'fr' ? 'Site Web' : 'Website'}</option>
              <option value="referral">{language === 'fr' ? 'Référence' : 'Referral'}</option>
              <option value="broker">{language === 'fr' ? 'Courtier' : 'Broker'}</option>
              <option value="direct">{language === 'fr' ? 'Direct' : 'Direct'}</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-slate-600">{language === 'fr' ? 'Chargement...' : 'Loading...'}</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredLeads.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <LayoutGrid className="w-8 h-8 text-slate-400" />
          </div>
          <h3 className="text-lg font-medium text-slate-900 mb-2">
            {language === 'fr' ? 'Aucun prospect' : 'No leads'}
          </h3>
          <p className="text-slate-600 mb-6">
            {searchQuery || sourceFilter !== 'all'
              ? language === 'fr' ? 'Aucun prospect ne correspond à vos critères' : 'No leads match your filters'
              : language === 'fr' ? 'Commencez par ajouter votre premier prospect' : 'Start by adding your first lead'}
          </p>
          {canManageLeads && !searchQuery && sourceFilter === 'all' && (
            <button
              onClick={handleAdd}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all"
            >
              <Plus className="w-5 h-5" />
              {language === 'fr' ? 'Ajouter votre premier prospect' : 'Add your first lead'}
            </button>
          )}
        </div>
      )}

      {/* Kanban View */}
      {!isLoading && filteredLeads.length > 0 && viewMode === 'kanban' && (
        <KanbanBoard
          leads={filteredLeads}
          onStatusChange={handleStatusChange}
          onLeadClick={handleLeadClick}
        />
      )}

      {/* List View (Future Enhancement) */}
      {!isLoading && filteredLeads.length > 0 && viewMode === 'list' && (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
          <p className="text-slate-600">
            {language === 'fr' ? 'Vue liste - Bientôt disponible' : 'List view - Coming soon'}
          </p>
        </div>
      )}

      {/* Modals */}
      <LeadFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setEditingLead(undefined)
        }}
        lead={editingLead}
      />

      {selectedLead && (
        <LeadDetailModal
          isOpen={isDetailOpen}
          onClose={() => {
            setIsDetailOpen(false)
            setSelectedLead(undefined)
          }}
          lead={selectedLead}
          onEdit={() => handleEdit(selectedLead)}
        />
      )}
    </div>
  )
}

