import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Upload,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Download,
  Trash2,
  Eye,
  Filter,
  Search,
  HelpCircle,
  CreditCard,
  Smartphone,
  AlertCircle,
  CheckSquare,
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import { useAuth } from '../contexts/AuthContext'
import api from '../lib/api'
import { Button } from '../components/ui/button'

interface Document {
  id: number
  deal: number
  document_type: string
  file: string
  status: 'pending' | 'verified' | 'rejected'
  uploaded_by: number
  verified_by?: number
  notes: string
  uploaded_at: string
  verified_at?: string
}

interface DocumentsProps {
  dealId?: number
  showUpload?: boolean
}

export default function Documents({ dealId, showUpload = true }: DocumentsProps) {
  const { language } = useLanguage()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [viewDocument, setViewDocument] = useState<Document | null>(null)
  const [showHelp, setShowHelp] = useState(true)
  
  const isBuyer = user?.role === 'buyer'

  // Fetch documents
  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents', dealId, selectedType, selectedStatus],
    queryFn: async () => {
      const params: any = {}
      if (dealId) params.deal = dealId
      if (selectedType !== 'all') params.document_type = selectedType
      if (selectedStatus !== 'all') params.status = selectedStatus
      return await api.getDocuments(params)
    },
  })

  // Document types with buyer-friendly descriptions
  const documentTypes = [
    { 
      value: 'id', 
      label: language === 'fr' ? 'Pièce d\'identité' : 'ID Document',
      description: language === 'fr' 
        ? 'Passeport, carte d\'identité nationale, ou permis de conduire' 
        : 'Passport, national ID card, or driver\'s license',
      icon: FileText,
      required: true
    },
    { 
      value: 'payment_proof', 
      label: language === 'fr' ? 'Preuve de paiement' : 'Payment Proof',
      description: language === 'fr'
        ? 'Reçu de virement bancaire, capture d\'écran mobile money (M-Pesa, Orange Money, etc.), ou confirmation de paiement'
        : 'Bank transfer receipt, mobile money screenshot (M-Pesa, Orange Money, etc.), or payment confirmation',
      icon: CreditCard,
      required: true
    },
    { 
      value: 'title', 
      label: language === 'fr' ? 'Documents du véhicule' : 'Vehicle Documents',
      description: language === 'fr'
        ? 'Fourni par le vendeur - titre du véhicule et certificat d\'inspection'
        : 'Provided by seller - vehicle title and inspection certificate',
      icon: FileText,
      required: false
    },
    { 
      value: 'export_permit', 
      label: language === 'fr' ? 'Permis d\'exportation' : 'Export Permit',
      description: language === 'fr'
        ? 'Nous vous aiderons à l\'obtenir - téléchargez quand disponible'
        : 'We\'ll help you obtain this - upload when available',
      icon: FileText,
      required: false
    },
    { 
      value: 'customs', 
      label: language === 'fr' ? 'Déclaration en douane' : 'Customs Declaration',
      description: language === 'fr'
        ? 'Nécessaire pour le dédouanement dans votre pays'
        : 'Required for customs clearance in your country',
      icon: FileText,
      required: false
    },
    { 
      value: 'other', 
      label: language === 'fr' ? 'Autre document' : 'Other Document',
      description: language === 'fr'
        ? 'Tout autre document demandé par notre équipe'
        : 'Any other document requested by our team',
      icon: FileText,
      required: false
    },
  ]

  // Status options
  const statusOptions = [
    { value: 'pending', label: language === 'fr' ? 'En attente' : 'Pending', color: 'text-yellow-600 bg-yellow-50' },
    { value: 'verified', label: language === 'fr' ? 'Vérifié' : 'Verified', color: 'text-green-600 bg-green-50' },
    { value: 'rejected', label: language === 'fr' ? 'Rejeté' : 'Rejected', color: 'text-red-600 bg-red-50' },
  ]

  // Get status badge
  const getStatusBadge = (status: string) => {
    const option = statusOptions.find((s) => s.value === status)
    if (!option) return null
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${option.color}`}>
        {option.label}
      </span>
    )
  }

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-yellow-600" />
    }
  }

  // Filter documents by search
  const filteredDocuments = documents.filter((doc: Document) => {
    const searchLower = searchTerm.toLowerCase()
    const typeLabel = documentTypes.find((t) => t.value === doc.document_type)?.label || ''
    return (
      typeLabel.toLowerCase().includes(searchLower) ||
      doc.notes.toLowerCase().includes(searchLower)
    )
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.deleteDocument(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  // Verify mutation
  const verifyMutation = useMutation({
    mutationFn: async ({ id, status, notes }: { id: number; status: string; notes?: string }) => {
      await api.verifyDocument(id, { status, notes })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setViewDocument(null)
    },
  })

  const handleDelete = (id: number) => {
    if (confirm(language === 'fr' ? 'Supprimer ce document ?' : 'Delete this document?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleVerify = (id: number, status: 'verified' | 'rejected') => {
    verifyMutation.mutate({ id, status })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            {isBuyer 
              ? (language === 'fr' ? 'Mes Documents' : 'My Documents')
              : (language === 'fr' ? 'Documents' : 'Documents')}
          </h2>
          <p className="text-slate-600 mt-1">
            {isBuyer
              ? (language === 'fr'
                ? 'Téléchargez vos documents pour finaliser votre achat'
                : 'Upload your documents to finalize your purchase')
              : (language === 'fr'
                ? 'Gérez les documents du deal'
                : 'Manage deal documents')}
          </p>
        </div>
        {showUpload && (
          <Button onClick={() => setUploadModalOpen(true)} size="lg">
            <Upload className="w-5 h-5 mr-2" />
            {language === 'fr' ? 'Télécharger un document' : 'Upload Document'}
          </Button>
        )}
      </div>

      {/* Buyer Help Section - Simplified Process */}
      {isBuyer && showHelp && filteredDocuments.length === 0 && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                <HelpCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  {language === 'fr' ? 'Commençons simplement' : 'Let\'s Get Started Simply'}
                </h3>
                <p className="text-sm text-slate-600">
                  {language === 'fr' 
                    ? 'Seulement 2 documents nécessaires pour commencer'
                    : 'Only 2 documents needed to get started'}
                </p>
              </div>
            </div>
            <button 
              onClick={() => setShowHelp(false)}
              className="text-slate-400 hover:text-slate-600"
            >
              ✕
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Required Document 1: ID */}
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckSquare className="w-4 h-4 text-green-600" />
                </div>
                <h4 className="font-semibold text-slate-900">
                  {language === 'fr' ? '1. Pièce d\'identité' : '1. Your ID'}
                </h4>
              </div>
              <p className="text-sm text-slate-600 mb-3">
                {language === 'fr'
                  ? 'Photo claire de votre passeport, carte d\'identité, ou permis de conduire'
                  : 'Clear photo of your passport, ID card, or driver\'s license'}
              </p>
              <div className="flex items-start gap-2 text-xs text-slate-500">
                <Smartphone className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>
                  {language === 'fr'
                    ? 'Utilisez votre téléphone - une photo claire suffit'
                    : 'Use your phone - a clear photo is enough'}
                </span>
              </div>
            </div>

            {/* Required Document 2: Payment Proof */}
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckSquare className="w-4 h-4 text-green-600" />
                </div>
                <h4 className="font-semibold text-slate-900">
                  {language === 'fr' ? '2. Preuve de paiement' : '2. Payment Proof'}
                </h4>
              </div>
              <p className="text-sm text-slate-600 mb-3">
                {language === 'fr'
                  ? 'Reçu de virement ou capture d\'écran de mobile money'
                  : 'Bank receipt or mobile money screenshot'}
              </p>
              <div className="flex items-start gap-2 text-xs text-slate-500 mb-2">
                <CreditCard className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>
                  {language === 'fr'
                    ? 'M-Pesa, Orange Money, MTN, Airtel - tous acceptés'
                    : 'M-Pesa, Orange Money, MTN, Airtel - all accepted'}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-800">
                <strong>{language === 'fr' ? 'Astuce:' : 'Tip:'}</strong>{' '}
                {language === 'fr'
                  ? 'C\'est tout ce dont vous avez besoin pour l\'instant ! Nous gérons le reste du processus pour vous.'
                  : 'That\'s all you need for now! We handle the rest of the process for you.'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder={language === 'fr' ? 'Rechercher...' : 'Search...'}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Type filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
            >
              <option value="all">{language === 'fr' ? 'Tous les types' : 'All Types'}</option>
              {documentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Status filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
            >
              <option value="all">{language === 'fr' ? 'Tous les statuts' : 'All Statuses'}</option>
              {statusOptions.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Documents List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 animate-pulse">
              <div className="h-20 bg-slate-200 rounded mb-4" />
              <div className="h-4 bg-slate-200 rounded mb-2" />
              <div className="h-3 bg-slate-200 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-slate-300 p-12 text-center">
          <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-10 h-10 text-blue-500" />
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-2">
            {isBuyer
              ? (language === 'fr' ? 'Prêt à commencer ?' : 'Ready to Get Started?')
              : (language === 'fr' ? 'Aucun document' : 'No Documents')}
          </h3>
          <p className="text-slate-600 mb-6 max-w-md mx-auto">
            {isBuyer
              ? (language === 'fr'
                ? 'Téléchargez votre pièce d\'identité et preuve de paiement pour finaliser votre achat. C\'est simple et rapide !'
                : 'Upload your ID and payment proof to finalize your purchase. It\'s simple and quick!')
              : (language === 'fr'
                ? 'Aucun document trouvé pour ce deal'
                : 'No documents found for this deal')}
          </p>
          {showUpload && (
            <Button onClick={() => setUploadModalOpen(true)} size="lg" className="mx-auto">
              <Upload className="w-5 h-5 mr-2" />
              {isBuyer
                ? (language === 'fr' ? 'Télécharger mes documents' : 'Upload My Documents')
                : (language === 'fr' ? 'Télécharger le premier document' : 'Upload First Document')}
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((doc: Document) => {
            const docType = documentTypes.find((t) => t.value === doc.document_type)
            const DocIcon = docType?.icon || FileText
            
            return (
              <div
                key={doc.id}
                className={`bg-white rounded-lg shadow-sm border-2 p-6 hover:shadow-md transition-all ${
                  doc.status === 'verified' 
                    ? 'border-green-200 bg-green-50/30' 
                    : doc.status === 'rejected'
                    ? 'border-red-200 bg-red-50/30'
                    : 'border-slate-200'
                }`}
              >
                {/* Document icon and status */}
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    doc.status === 'verified' 
                      ? 'bg-green-100' 
                      : doc.status === 'rejected'
                      ? 'bg-red-100'
                      : 'bg-blue-100'
                  }`}>
                    <DocIcon className={`w-6 h-6 ${
                      doc.status === 'verified' 
                        ? 'text-green-600' 
                        : doc.status === 'rejected'
                        ? 'text-red-600'
                        : 'text-blue-600'
                    }`} />
                  </div>
                  {getStatusIcon(doc.status)}
                </div>

                {/* Document info */}
                <h3 className="font-semibold text-slate-900 mb-1">
                  {docType?.label || doc.document_type}
                </h3>
                
                {/* Buyer-friendly description */}
                {isBuyer && docType?.description && (
                  <p className="text-xs text-slate-500 mb-3">
                    {docType.description}
                  </p>
                )}
                
                <div className="flex items-center gap-2 mb-3">
                  {getStatusBadge(doc.status)}
                </div>

                {/* Buyer-friendly status message */}
                {isBuyer && (
                  <div className="mb-3 p-2 rounded-lg bg-slate-50 border border-slate-200">
                    <p className="text-xs text-slate-700">
                      {doc.status === 'verified' && (
                        <>{language === 'fr' ? '✅ Document approuvé' : '✅ Document approved'}</>
                      )}
                      {doc.status === 'pending' && (
                        <>{language === 'fr' ? '⏳ En cours de vérification (1-2 jours)' : '⏳ Under review (1-2 days)'}</>
                      )}
                      {doc.status === 'rejected' && (
                        <>{language === 'fr' ? '❌ Veuillez télécharger à nouveau' : '❌ Please re-upload'}</>
                      )}
                    </p>
                  </div>
                )}

                {/* Date */}
                <p className="text-xs text-slate-500 mb-4">
                  {language === 'fr' ? 'Téléchargé' : 'Uploaded'}{' '}
                  {new Date(doc.uploaded_at).toLocaleDateString()}
                </p>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setViewDocument(doc)}
                    className="flex-1"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    {language === 'fr' ? 'Voir' : 'View'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(doc.file, '_blank')}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                  {/* Only show delete for pending docs or non-buyers */}
                  {(!isBuyer || doc.status === 'pending' || doc.status === 'rejected') && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(doc.id)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Upload Modal */}
      {uploadModalOpen && (
        <UploadModal
          dealId={dealId}
          onClose={() => setUploadModalOpen(false)}
          onSuccess={() => {
            setUploadModalOpen(false)
            queryClient.invalidateQueries({ queryKey: ['documents'] })
          }}
        />
      )}

      {/* View Document Modal */}
      {viewDocument && (
        <ViewDocumentModal
          document={viewDocument}
          onClose={() => setViewDocument(null)}
          onVerify={handleVerify}
          verifying={verifyMutation.isPending}
        />
      )}
    </div>
  )
}

// Upload Modal Component
function UploadModal({
  dealId,
  onClose,
  onSuccess,
}: {
  dealId?: number
  onClose: () => void
  onSuccess: () => void
}) {
  const { language } = useLanguage()
  const [documentType, setDocumentType] = useState('title')
  const [file, setFile] = useState<File | null>(null)
  const [notes, setNotes] = useState('')
  const [selectedDeal, setSelectedDeal] = useState(dealId || 0)

  const { data: deals = [] } = useQuery({
    queryKey: ['deals'],
    queryFn: async () => await api.getDeals(),
    enabled: !dealId,
  })

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      return await api.uploadDocument(formData)
    },
    onSuccess: () => {
      onSuccess()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !selectedDeal) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('document_type', documentType)
    formData.append('deal', selectedDeal.toString())
    formData.append('notes', notes)

    uploadMutation.mutate(formData)
  }

  const documentTypes = [
    { value: 'title', label: language === 'fr' ? 'Titre de véhicule' : 'Vehicle Title' },
    { value: 'id', label: language === 'fr' ? 'Pièce d\'identité' : 'ID Document' },
    { value: 'payment_proof', label: language === 'fr' ? 'Preuve de paiement' : 'Payment Proof' },
    { value: 'export_permit', label: language === 'fr' ? 'Permis d\'exportation' : 'Export Permit' },
    { value: 'customs', label: language === 'fr' ? 'Déclaration en douane' : 'Customs Declaration' },
    { value: 'other', label: language === 'fr' ? 'Autre' : 'Other' },
  ]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-xl font-bold text-slate-900">
            {language === 'fr' ? 'Télécharger un document' : 'Upload Document'}
          </h3>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {!dealId && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                {language === 'fr' ? 'Deal' : 'Deal'}
              </label>
              <select
                value={selectedDeal}
                onChange={(e) => setSelectedDeal(Number(e.target.value))}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value={0}>{language === 'fr' ? 'Sélectionner un deal' : 'Select a deal'}</option>
                {deals.map((deal: any) => (
                  <option key={deal.id} value={deal.id}>
                    Deal #{deal.id} - {deal.vehicle?.make} {deal.vehicle?.model}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {language === 'fr' ? 'Type de document' : 'Document Type'}
            </label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              {documentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {language === 'fr' ? 'Fichier' : 'File'}
            </label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              required
            />
            <p className="text-xs text-slate-500 mt-1">
              {language === 'fr'
                ? 'PDF, JPG, PNG, DOC, DOCX (max 10MB)'
                : 'PDF, JPG, PNG, DOC, DOCX (max 10MB)'}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              {language === 'fr' ? 'Notes (optionnel)' : 'Notes (optional)'}
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder={language === 'fr' ? 'Ajouter des notes...' : 'Add notes...'}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              {language === 'fr' ? 'Annuler' : 'Cancel'}
            </Button>
            <Button type="submit" disabled={uploadMutation.isPending || !file}>
              {uploadMutation.isPending ? (
                language === 'fr' ? 'Téléchargement...' : 'Uploading...'
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  {language === 'fr' ? 'Télécharger' : 'Upload'}
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

// View Document Modal Component
function ViewDocumentModal({
  document,
  onClose,
  onVerify,
  verifying,
}: {
  document: Document
  onClose: () => void
  onVerify: (id: number, status: 'verified' | 'rejected') => void
  verifying: boolean
}) {
  const { language } = useLanguage()

  const documentTypes = [
    { value: 'title', label: language === 'fr' ? 'Titre de véhicule' : 'Vehicle Title' },
    { value: 'id', label: language === 'fr' ? 'Pièce d\'identité' : 'ID Document' },
    { value: 'payment_proof', label: language === 'fr' ? 'Preuve de paiement' : 'Payment Proof' },
    { value: 'export_permit', label: language === 'fr' ? 'Permis d\'exportation' : 'Export Permit' },
    { value: 'customs', label: language === 'fr' ? 'Déclaration en douane' : 'Customs Declaration' },
    { value: 'other', label: language === 'fr' ? 'Autre' : 'Other' },
  ]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xl font-bold text-slate-900">
            {documentTypes.find((t) => t.value === document.document_type)?.label || document.document_type}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {/* Document preview iframe */}
          <div className="bg-slate-100 rounded-lg h-96 mb-6 flex items-center justify-center">
            {document.file.toLowerCase().endsWith('.pdf') ? (
              <iframe src={document.file} className="w-full h-full rounded-lg" />
            ) : (
              <img src={document.file} alt="Document" className="max-w-full max-h-full object-contain rounded-lg" />
            )}
          </div>

          {/* Document details */}
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">
                {language === 'fr' ? 'Statut' : 'Status'}
              </label>
              <p className="mt-1">
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    document.status === 'verified'
                      ? 'text-green-600 bg-green-50'
                      : document.status === 'rejected'
                      ? 'text-red-600 bg-red-50'
                      : 'text-yellow-600 bg-yellow-50'
                  }`}
                >
                  {document.status === 'verified'
                    ? language === 'fr'
                      ? 'Vérifié'
                      : 'Verified'
                    : document.status === 'rejected'
                    ? language === 'fr'
                      ? 'Rejeté'
                      : 'Rejected'
                    : language === 'fr'
                    ? 'En attente'
                    : 'Pending'}
                </span>
              </p>
            </div>

            {document.notes && (
              <div>
                <label className="text-sm font-medium text-slate-700">
                  {language === 'fr' ? 'Notes' : 'Notes'}
                </label>
                <p className="mt-1 text-slate-600">{document.notes}</p>
              </div>
            )}

            <div>
              <label className="text-sm font-medium text-slate-700">
                {language === 'fr' ? 'Téléchargé le' : 'Uploaded on'}
              </label>
              <p className="mt-1 text-slate-600">{new Date(document.uploaded_at).toLocaleString()}</p>
            </div>

            {document.verified_at && (
              <div>
                <label className="text-sm font-medium text-slate-700">
                  {language === 'fr' ? 'Vérifié le' : 'Verified on'}
                </label>
                <p className="mt-1 text-slate-600">{new Date(document.verified_at).toLocaleString()}</p>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        {document.status === 'pending' && (
          <div className="p-6 border-t border-slate-200 flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => onVerify(document.id, 'rejected')}
              disabled={verifying}
              className="text-red-600 hover:bg-red-50"
            >
              <XCircle className="w-4 h-4 mr-2" />
              {language === 'fr' ? 'Rejeter' : 'Reject'}
            </Button>
            <Button onClick={() => onVerify(document.id, 'verified')} disabled={verifying}>
              <CheckCircle className="w-4 h-4 mr-2" />
              {language === 'fr' ? 'Vérifier' : 'Verify'}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
