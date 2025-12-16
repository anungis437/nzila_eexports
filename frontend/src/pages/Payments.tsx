import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  CreditCard, 
  DollarSign, 
  FileText, 
  Plus,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Download,
  Send,
  Eye,
  AlertCircle
} from 'lucide-react'
import api from '../lib/api'
import { formatDistanceToNow } from 'date-fns'
import AddPaymentMethodModal from '../components/AddPaymentMethodModal'

interface Currency {
  id: number
  code: string
  name: string
  symbol: string
  is_african: boolean
  country: string
}

interface PaymentMethod {
  id: number
  type: string
  display_name: string
  card_brand?: string
  card_last4?: string
  card_exp_month?: number
  card_exp_year?: number
  bank_name?: string
  mobile_provider?: string
  is_default: boolean
  is_verified: boolean
  currency_display: Currency
}

interface Payment {
  id: number
  amount: string
  currency_display: Currency
  status: string
  status_display: string
  payment_for_display: string
  deal_display?: string
  receipt_url?: string
  created_at: string
  succeeded_at?: string
  failure_reason?: string
}

interface Invoice {
  id: number
  invoice_number: string
  total: string
  amount_paid: string
  amount_due: string
  currency_display: Currency
  status: string
  status_display: string
  due_date: string
  is_overdue: boolean
  pdf_file?: string
}

export default function Payments() {
  const [activeTab, setActiveTab] = useState<'methods' | 'payments' | 'invoices'>('methods')
  const [showAddPaymentMethod, setShowAddPaymentMethod] = useState(false)
  const queryClient = useQueryClient()

  // Fetch data
  const { data: paymentMethods = [], isLoading: loadingMethods } = useQuery({
    queryKey: ['paymentMethods'],
    queryFn: () => api.getPaymentMethods(),
  })

  const { data: payments = [], isLoading: loadingPayments } = useQuery({
    queryKey: ['payments'],
    queryFn: () => api.getPayments(),
  })

  const { data: invoices = [], isLoading: loadingInvoices } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => api.getInvoices(),
  })

  // Mutations
  const deletePaymentMethodMutation = useMutation({
    mutationFn: (id: number) => api.deletePaymentMethod(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['paymentMethods'] })
    },
  })

  const setDefaultMutation = useMutation({
    mutationFn: (id: number) => api.setDefaultPaymentMethod(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['paymentMethods'] })
    },
  })

  const handleDownloadInvoice = async (paymentId: number) => {
    try {
      const blob = await api.downloadInvoicePDF(paymentId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `invoice_${paymentId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading invoice:', error)
    }
  }

  const handleDownloadReceipt = async (paymentId: number) => {
    try {
      const blob = await api.downloadReceiptPDF(paymentId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `receipt_${paymentId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading receipt:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded':
      case 'paid':
        return 'text-green-600 bg-green-50'
      case 'pending':
      case 'processing':
        return 'text-yellow-600 bg-yellow-50'
      case 'failed':
      case 'canceled':
        return 'text-red-600 bg-red-50'
      case 'overdue':
        return 'text-orange-600 bg-orange-50'
      default:
        return 'text-slate-600 bg-slate-50'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'succeeded':
      case 'paid':
        return <CheckCircle className="h-4 w-4" />
      case 'pending':
      case 'processing':
        return <Clock className="h-4 w-4" />
      case 'failed':
      case 'canceled':
        return <XCircle className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Add Payment Method Modal */}
      <AddPaymentMethodModal
        isOpen={showAddPaymentMethod}
        onClose={() => setShowAddPaymentMethod(false)}
        onSuccess={() => setShowAddPaymentMethod(false)}
      />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Payments</h1>
          <p className="text-slate-600 mt-1">Manage your payments, methods, and invoices</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors" onClick={() => setShowAddPaymentMethod(true)}>
          <Plus className="h-5 w-5" />
          Add Payment Method
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav 
          className="-mb-px flex space-x-8" 
          role="tablist"
          aria-label="Payment sections"
          onKeyDown={(e) => {
            // Arrow key navigation
            const tabs = ['methods', 'payments', 'invoices'] as const
            const currentIndex = tabs.indexOf(activeTab)
            
            if (e.key === 'ArrowLeft' && currentIndex > 0) {
              e.preventDefault()
              setActiveTab(tabs[currentIndex - 1])
            } else if (e.key === 'ArrowRight' && currentIndex < tabs.length - 1) {
              e.preventDefault()
              setActiveTab(tabs[currentIndex + 1])
            } else if (e.key === 'Home') {
              e.preventDefault()
              setActiveTab(tabs[0])
            } else if (e.key === 'End') {
              e.preventDefault()
              setActiveTab(tabs[tabs.length - 1])
            }
          }}
        >
          <button
            onClick={() => setActiveTab('methods')}
            role="tab"
            aria-selected={activeTab === 'methods'}
            aria-controls="payment-methods-panel"
            id="payment-methods-tab"
            tabIndex={activeTab === 'methods' ? 0 : -1}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'methods'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" aria-hidden="true" />
              Payment Methods
              <span className="ml-2 py-0.5 px-2 rounded-full bg-slate-100 text-slate-600 text-xs">
                {paymentMethods.length}
              </span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('payments')}
            role="tab"
            aria-selected={activeTab === 'payments'}
            aria-controls="payment-history-panel"
            id="payment-history-tab"
            tabIndex={activeTab === 'payments' ? 0 : -1}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'payments'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" aria-hidden="true" />
              Payment History
              <span className="ml-2 py-0.5 px-2 rounded-full bg-slate-100 text-slate-600 text-xs">
                {payments.length}
              </span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('invoices')}
            role="tab"
            aria-selected={activeTab === 'invoices'}
            aria-controls="invoices-panel"
            id="invoices-tab"
            tabIndex={activeTab === 'invoices' ? 0 : -1}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'invoices'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5" aria-hidden="true" />
              Invoices
              <span className="ml-2 py-0.5 px-2 rounded-full bg-slate-100 text-slate-600 text-xs">
                {invoices.length}
              </span>
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'methods' && (
        <div 
          className="space-y-4"
          role="tabpanel"
          id="payment-methods-panel"
          aria-labelledby="payment-methods-tab"
        >
          {loadingMethods ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : paymentMethods.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="mx-auto h-12 w-12 text-slate-400" />
              <h3 className="mt-2 text-sm font-semibold text-slate-900">No payment methods</h3>
              <p className="mt-1 text-sm text-slate-500">Get started by adding a payment method.</p>
              <button className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" onClick={() => setShowAddPaymentMethod(true)}>
                <Plus className="h-5 w-5" />
                Add Payment Method
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {paymentMethods.map((method: PaymentMethod) => (
                <div
                  key={method.id}
                  className="relative bg-white border-2 rounded-lg p-6 hover:border-blue-200 transition-colors"
                  style={{
                    borderColor: method.is_default ? '#3b82f6' : undefined,
                  }}
                >
                  {method.is_default && (
                    <div className="absolute top-3 right-3">
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                        <CheckCircle className="h-3 w-3" />
                        Default
                      </span>
                    </div>
                  )}

                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                        <CreditCard className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">
                        {method.display_name}
                      </p>
                      {method.card_exp_month && method.card_exp_year && (
                        <p className="text-xs text-slate-500 mt-1">
                          Expires {method.card_exp_month}/{method.card_exp_year}
                        </p>
                      )}
                      {method.is_verified && (
                        <div className="mt-2 inline-flex items-center gap-1 text-xs text-green-600">
                          <CheckCircle className="h-3 w-3" />
                          Verified
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-2">
                    {!method.is_default && (
                      <button
                        onClick={() => setDefaultMutation.mutate(method.id)}
                        className="flex-1 px-3 py-1.5 text-sm text-blue-600 border border-blue-200 rounded hover:bg-blue-50 transition-colors"
                      >
                        Set as Default
                      </button>
                    )}
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this payment method?')) {
                          deletePaymentMethodMutation.mutate(method.id)
                        }
                      }}
                      className="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'payments' && (
        <div 
          className="space-y-4"
          role="tabpanel"
          id="payment-history-panel"
          aria-labelledby="payment-history-tab"
        >
          {loadingPayments ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : payments.length === 0 ? (
            <div className="text-center py-12">
              <DollarSign className="mx-auto h-12 w-12 text-slate-400" />
              <h3 className="mt-2 text-sm font-semibold text-slate-900">No payments</h3>
              <p className="mt-1 text-sm text-slate-500">Your payment history will appear here.</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Payment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {payments.map((payment: Payment) => (
                    <tr key={payment.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-slate-900">
                            {payment.payment_for_display}
                          </div>
                          {payment.deal_display && (
                            <div className="text-xs text-slate-500">{payment.deal_display}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-slate-900">
                          {payment.currency_display.symbol}{payment.amount}
                        </div>
                        <div className="text-xs text-slate-500">
                          {payment.currency_display.code}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(payment.status)}`}>
                          {getStatusIcon(payment.status)}
                          {payment.status_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {formatDistanceToNow(new Date(payment.created_at), { addSuffix: true })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleDownloadInvoice(payment.id)}
                            className="text-blue-600 hover:text-blue-700 p-1 hover:bg-blue-50 rounded transition-colors"
                            title="Download Invoice"
                          >
                            <FileText className="h-4 w-4" />
                          </button>
                          {payment.status === 'succeeded' && (
                            <button
                              onClick={() => handleDownloadReceipt(payment.id)}
                              className="text-green-600 hover:text-green-700 p-1 hover:bg-green-50 rounded transition-colors"
                              title="Download Receipt"
                            >
                              <Download className="h-4 w-4" />
                            </button>
                          )}
                          {payment.receipt_url && (
                            <a
                              href={payment.receipt_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-purple-600 hover:text-purple-700 p-1 hover:bg-purple-50 rounded transition-colors"
                              title="View Stripe Receipt"
                            >
                              <Eye className="h-4 w-4" />
                            </a>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'invoices' && (
        <div 
          className="space-y-4"
          role="tabpanel"
          id="invoices-panel"
          aria-labelledby="invoices-tab"
        >
          {loadingInvoices ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : invoices.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-slate-400" />
              <h3 className="mt-2 text-sm font-semibold text-slate-900">No invoices</h3>
              <p className="mt-1 text-sm text-slate-500">Your invoices will appear here.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {invoices.map((invoice: Invoice) => (
                <div
                  key={invoice.id}
                  className="bg-white border border-slate-200 rounded-lg p-6 hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
                          <FileText className="h-6 w-6 text-white" />
                        </div>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">
                          {invoice.invoice_number}
                        </h3>
                        <p className="text-sm text-slate-500 mt-1">
                          Due {new Date(invoice.due_date).toLocaleDateString()}
                        </p>
                        <div className="mt-2">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(invoice.status)}`}>
                            {getStatusIcon(invoice.status)}
                            {invoice.status_display}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold text-slate-900">
                        {invoice.currency_display.symbol}{invoice.total}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {invoice.currency_display.code}
                      </div>
                      {parseFloat(invoice.amount_paid) > 0 && (
                        <div className="text-sm text-green-600 mt-1">
                          Paid: {invoice.currency_display.symbol}{invoice.amount_paid}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-200 flex items-center gap-2">
                    <button className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 text-sm text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors">
                      <Eye className="h-4 w-4" />
                      View Invoice
                    </button>
                    {invoice.pdf_file && (
                      <a
                        href={invoice.pdf_file}
                        download
                        className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                      >
                        <Download className="h-4 w-4" />
                        Download PDF
                      </a>
                    )}
                    {invoice.status === 'sent' && (
                      <button className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
                        <Send className="h-4 w-4" />
                        Pay Now
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
