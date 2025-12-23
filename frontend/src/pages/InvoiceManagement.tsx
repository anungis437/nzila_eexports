import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { FileText, Download, Mail, Eye } from 'lucide-react'
import api from '@/lib/api'

interface Invoice {
  id: number
  invoice_number: string
  customer: string
  customer_email: string
  amount: string
  currency: string
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'
  due_date: string
  issued_date: string
  paid_date: string | null
  items: InvoiceItem[]
  notes: string
}

interface InvoiceItem {
  id: number
  description: string
  quantity: number
  unit_price: string
  total: string
}

export default function InvoiceManagement() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [timeRange, setTimeRange] = useState('30d')
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: invoices, isLoading } = useQuery<Invoice[]>({
    queryKey: ['invoices', timeRange, statusFilter, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (timeRange !== 'all') params.append('time_range', timeRange)
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchQuery) params.append('search', searchQuery)
      const response = await api.get(`/api/payments/invoices/?${params}`)
      return response.data
    }
  })

  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }) => {
      const response = await api.patch(`/api/payments/invoices/${id}/`, { status })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
    }
  })

  const sendReminderMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.post(`/api/payments/invoices/${id}/send-reminder/`)
    }
  })

  const downloadPDF = async (id: number) => {
    try {
      const response = await api.get(`/api/payments/invoices/${id}/pdf/`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `invoice-${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to download PDF:', error)
    }
  }

  const viewInvoice = (invoice: Invoice) => {
    setSelectedInvoice(invoice)
    setViewDialogOpen(true)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'default'
      case 'sent':
        return 'secondary'
      case 'overdue':
        return 'destructive'
      case 'draft':
        return 'outline'
      case 'cancelled':
        return 'secondary'
      default:
        return 'default'
    }
  }

  const stats = {
    total: invoices?.length || 0,
    paid: invoices?.filter((i: Invoice) => i.status === 'paid').length || 0,
    overdue: invoices?.filter((i: Invoice) => i.status === 'overdue').length || 0,
    totalAmount: invoices?.reduce((sum: number, i: Invoice) => sum + parseFloat(i.amount), 0) || 0
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <FileText className="h-8 w-8 text-blue-600" />
          Invoice Management
        </h1>
        <p className="text-gray-600 mt-1">View and manage customer invoices</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Invoices</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.total}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Paid</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{stats.paid}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Overdue</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">{stats.overdue}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Amount</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">${stats.totalAmount.toLocaleString()}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <Input
              placeholder="Search by invoice #, customer..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-xs"
            />
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="overdue">Overdue</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Time range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
                <SelectItem value="1y">Last year</SelectItem>
                <SelectItem value="all">All time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading invoices...</p>
          ) : invoices && invoices.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice #</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((invoice: Invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell className="font-mono">{invoice.invoice_number}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{invoice.customer}</p>
                        <p className="text-sm text-gray-600">{invoice.customer_email}</p>
                      </div>
                    </TableCell>
                    <TableCell className="font-semibold">
                      {invoice.currency} ${parseFloat(invoice.amount).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(invoice.status)}>
                        {invoice.status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(invoice.due_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => viewInvoice(invoice)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => downloadPDF(invoice.id)}>
                          <Download className="h-4 w-4" />
                        </Button>
                        {invoice.status !== 'paid' && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => sendReminderMutation.mutate(invoice.id)}
                            >
                              <Mail className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => updateStatusMutation.mutate({ id: invoice.id, status: 'paid' })}
                            >
                              Mark Paid
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-center text-gray-500 py-8">No invoices found</p>
          )}
        </CardContent>
      </Card>

      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Invoice Details</DialogTitle>
          </DialogHeader>
          {selectedInvoice && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Invoice Number</p>
                  <p className="font-mono font-semibold">{selectedInvoice.invoice_number}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <Badge variant={getStatusColor(selectedInvoice.status)}>
                    {selectedInvoice.status.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Customer</p>
                  <p className="font-medium">{selectedInvoice.customer}</p>
                  <p className="text-sm">{selectedInvoice.customer_email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Amount</p>
                  <p className="text-2xl font-bold">
                    {selectedInvoice.currency} ${parseFloat(selectedInvoice.amount).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Issued Date</p>
                  <p>{new Date(selectedInvoice.issued_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Due Date</p>
                  <p>{new Date(selectedInvoice.due_date).toLocaleDateString()}</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-2">Items</p>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Description</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Unit Price</TableHead>
                      <TableHead>Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedInvoice.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.description}</TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>${parseFloat(item.unit_price).toLocaleString()}</TableCell>
                        <TableCell>${parseFloat(item.total).toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {selectedInvoice.notes && (
                <div>
                  <p className="text-sm text-gray-600">Notes</p>
                  <p className="text-sm mt-1">{selectedInvoice.notes}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
