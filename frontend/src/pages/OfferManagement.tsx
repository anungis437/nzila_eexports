import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { DollarSign, Check, X, MessageSquare, Eye } from 'lucide-react'
import api from '@/lib/api'

interface VehicleOffer {
  id: number
  vehicle: string
  vehicle_details: {
    make: string
    model: string
    year: number
    price: string
  }
  buyer: string
  buyer_email: string
  offer_amount: string
  currency: string
  status: 'pending' | 'accepted' | 'rejected' | 'countered' | 'expired'
  message: string
  created_at: string
  expires_at: string
  counter_offer_amount: string | null
  counter_offer_message: string | null
}

interface OfferHistory {
  id: number
  offer: number
  action: string
  amount: string
  message: string
  created_by: string
  created_at: string
}

export default function OfferManagement() {
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedOffer, setSelectedOffer] = useState<VehicleOffer | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  const [counterDialogOpen, setCounterDialogOpen] = useState(false)
  const [counterAmount, setCounterAmount] = useState('')
  const [counterMessage, setCounterMessage] = useState('')
  const queryClient = useQueryClient()

  const { data: offers, isLoading } = useQuery<VehicleOffer[]>({
    queryKey: ['vehicle-offers', statusFilter, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchQuery) params.append('search', searchQuery)
      const response = await api.get(`/api/vehicles/offers/?${params}`)
      return response.data
    }
  })

  const { data: history, isLoading: historyLoading } = useQuery<OfferHistory[]>({
    queryKey: ['offer-history', selectedOffer?.id],
    queryFn: async () => {
      if (!selectedOffer) return []
      const response = await api.get(`/api/vehicles/offers/${selectedOffer.id}/history/`)
      return response.data
    },
    enabled: !!selectedOffer
  })

  const acceptMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.patch(`/api/vehicles/offers/${id}/accept/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle-offers'] })
    }
  })

  const rejectMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.patch(`/api/vehicles/offers/${id}/reject/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle-offers'] })
    }
  })

  const counterMutation = useMutation({
    mutationFn: async ({ id, amount, message }: { id: number; amount: string; message: string }) => {
      await api.post(`/api/vehicles/offers/${id}/counter/`, {
        counter_amount: amount,
        counter_message: message
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle-offers'] })
      setCounterDialogOpen(false)
      setCounterAmount('')
      setCounterMessage('')
    }
  })

  const handleAccept = (id: number) => {
    if (confirm('Accept this offer? This will mark the vehicle as sold.')) {
      acceptMutation.mutate(id)
    }
  }

  const handleReject = (id: number) => {
    if (confirm('Reject this offer? The buyer will be notified.')) {
      rejectMutation.mutate(id)
    }
  }

  const handleCounter = () => {
    if (selectedOffer && counterAmount) {
      counterMutation.mutate({
        id: selectedOffer.id,
        amount: counterAmount,
        message: counterMessage
      })
    }
  }

  const viewOffer = (offer: VehicleOffer) => {
    setSelectedOffer(offer)
    setViewDialogOpen(true)
  }

  const openCounterDialog = (offer: VehicleOffer) => {
    setSelectedOffer(offer)
    setCounterAmount('')
    setCounterMessage('')
    setCounterDialogOpen(true)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'default'
      case 'pending':
        return 'secondary'
      case 'countered':
        return 'outline'
      case 'rejected':
      case 'expired':
        return 'destructive'
      default:
        return 'default'
    }
  }

  const stats = {
    total: offers?.length || 0,
    pending: offers?.filter(o => o.status === 'pending').length || 0,
    accepted: offers?.filter(o => o.status === 'accepted').length || 0,
    rejected: offers?.filter(o => o.status === 'rejected').length || 0
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <DollarSign className="h-8 w-8 text-green-600" />
          Offer Management
        </h1>
        <p className="text-gray-600 mt-1">Review and manage vehicle purchase offers</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Offers</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.total}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Accepted</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{stats.accepted}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Rejected</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <Input
              placeholder="Search by vehicle, buyer..."
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
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="accepted">Accepted</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="countered">Countered</SelectItem>
                <SelectItem value="expired">Expired</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading offers...</p>
          ) : offers && offers.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vehicle</TableHead>
                  <TableHead>Buyer</TableHead>
                  <TableHead>Asking Price</TableHead>
                  <TableHead>Offer Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {offers.map((offer) => (
                  <TableRow key={offer.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">
                          {offer.vehicle_details.year} {offer.vehicle_details.make} {offer.vehicle_details.model}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{offer.buyer}</p>
                        <p className="text-sm text-gray-600">{offer.buyer_email}</p>
                      </div>
                    </TableCell>
                    <TableCell className="font-semibold">
                      {offer.currency} ${parseFloat(offer.vehicle_details.price).toLocaleString()}
                    </TableCell>
                    <TableCell className="font-bold text-green-600">
                      {offer.currency} ${parseFloat(offer.offer_amount).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(offer.status)}>
                        {offer.status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>{new Date(offer.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => viewOffer(offer)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        {offer.status === 'pending' && (
                          <>
                            <Button
                              size="sm"
                              variant="default"
                              onClick={() => handleAccept(offer.id)}
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openCounterDialog(offer)}
                            >
                              <MessageSquare className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleReject(offer.id)}
                            >
                              <X className="h-4 w-4" />
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
            <p className="text-center text-gray-500 py-8">No offers found</p>
          )}
        </CardContent>
      </Card>

      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Offer Details</DialogTitle>
          </DialogHeader>
          {selectedOffer && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Vehicle</Label>
                  <p className="font-medium">
                    {selectedOffer.vehicle_details.year} {selectedOffer.vehicle_details.make}{' '}
                    {selectedOffer.vehicle_details.model}
                  </p>
                </div>
                <div>
                  <Label>Status</Label>
                  <Badge variant={getStatusColor(selectedOffer.status)}>
                    {selectedOffer.status.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <Label>Buyer</Label>
                  <p className="font-medium">{selectedOffer.buyer}</p>
                  <p className="text-sm text-gray-600">{selectedOffer.buyer_email}</p>
                </div>
                <div>
                  <Label>Asking Price</Label>
                  <p className="text-2xl font-bold">
                    {selectedOffer.currency} ${parseFloat(selectedOffer.vehicle_details.price).toLocaleString()}
                  </p>
                </div>
                <div>
                  <Label>Offer Amount</Label>
                  <p className="text-2xl font-bold text-green-600">
                    {selectedOffer.currency} ${parseFloat(selectedOffer.offer_amount).toLocaleString()}
                  </p>
                </div>
                {selectedOffer.counter_offer_amount && (
                  <div>
                    <Label>Counter Offer</Label>
                    <p className="text-2xl font-bold text-blue-600">
                      {selectedOffer.currency} ${parseFloat(selectedOffer.counter_offer_amount).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>

              {selectedOffer.message && (
                <div>
                  <Label>Buyer Message</Label>
                  <p className="text-sm mt-1">{selectedOffer.message}</p>
                </div>
              )}

              {selectedOffer.counter_offer_message && (
                <div>
                  <Label>Counter Offer Message</Label>
                  <p className="text-sm mt-1">{selectedOffer.counter_offer_message}</p>
                </div>
              )}

              <div>
                <Label>Negotiation History</Label>
                {historyLoading ? (
                  <p className="text-sm text-gray-500">Loading history...</p>
                ) : history && history.length > 0 ? (
                  <div className="mt-2 space-y-2">
                    {history.map((item) => (
                      <div key={item.id} className="border rounded p-3 text-sm">
                        <div className="flex justify-between items-start">
                          <span className="font-medium">{item.action}</span>
                          <span className="text-gray-600">{new Date(item.created_at).toLocaleString()}</span>
                        </div>
                        {item.amount && <p className="font-semibold">${parseFloat(item.amount).toLocaleString()}</p>}
                        {item.message && <p className="text-gray-700 mt-1">{item.message}</p>}
                        <p className="text-xs text-gray-500 mt-1">by {item.created_by}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 mt-2">No history available</p>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={counterDialogOpen} onOpenChange={setCounterDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Counter Offer</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Counter Amount</Label>
              <Input
                type="number"
                value={counterAmount}
                onChange={(e) => setCounterAmount(e.target.value)}
                placeholder="Enter counter offer amount"
              />
            </div>
            <div>
              <Label>Message (Optional)</Label>
              <Textarea
                value={counterMessage}
                onChange={(e) => setCounterMessage(e.target.value)}
                placeholder="Add a message to your counter offer..."
              />
            </div>
            <Button onClick={handleCounter} disabled={!counterAmount || counterMutation.isPending}>
              Send Counter Offer
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
