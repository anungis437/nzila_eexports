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
import { MessageSquare, Check, X, Flag, ThumbsUp, ThumbsDown, Eye } from 'lucide-react'
import api from '@/lib/api'

interface Review {
  id: number
  vehicle: string
  vehicle_details: {
    make: string
    model: string
    year: number
  }
  dealer: string
  reviewer: string
  reviewer_email: string
  rating: number
  title: string
  comment: string
  status: 'pending' | 'approved' | 'rejected' | 'flagged'
  created_at: string
  moderated_by: string | null
  moderated_at: string | null
  moderation_reason: string | null
  helpfulness_upvotes: number
  helpfulness_downvotes: number
}

interface HelpfulnessVote {
  id: number
  review: number
  user: string
  vote: 'up' | 'down'
  created_at: string
}

export default function ReviewModeration() {
  const [statusFilter, setStatusFilter] = useState('pending')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedReview, setSelectedReview] = useState<Review | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  const [moderationReason, setModerationReason] = useState('')
  const queryClient = useQueryClient()

  const { data: reviews, isLoading } = useQuery<Review[]>({
    queryKey: ['reviews-moderation', statusFilter, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchQuery) params.append('search', searchQuery)
      const response = await api.get(`/api/reviews/?${params}`)
      return response.data
    }
  })

  const { data: helpfulnessVotes } = useQuery<HelpfulnessVote[]>({
    queryKey: ['helpfulness-votes', selectedReview?.id],
    queryFn: async () => {
      if (!selectedReview) return []
      const response = await api.get(`/api/reviews/${selectedReview.id}/helpfulness/`)
      return response.data
    },
    enabled: !!selectedReview
  })

  const approveMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.patch(`/api/reviews/${id}/approve/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews-moderation'] })
    }
  })

  const rejectMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      await api.patch(`/api/reviews/${id}/reject/`, { reason })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews-moderation'] })
      setViewDialogOpen(false)
      setModerationReason('')
    }
  })

  const flagMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      await api.post(`/api/reviews/${id}/flag/`, { reason })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews-moderation'] })
    }
  })

  const handleApprove = (id: number) => {
    if (confirm('Approve this review? It will be visible to all users.')) {
      approveMutation.mutate(id)
    }
  }

  const handleReject = () => {
    if (selectedReview && moderationReason) {
      rejectMutation.mutate({ id: selectedReview.id, reason: moderationReason })
    }
  }

  const handleFlag = (id: number) => {
    const reason = prompt('Enter reason for flagging:')
    if (reason) {
      flagMutation.mutate({ id, reason })
    }
  }

  const viewReview = (review: Review) => {
    setSelectedReview(review)
    setModerationReason('')
    setViewDialogOpen(true)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'default'
      case 'pending':
        return 'secondary'
      case 'flagged':
        return 'outline'
      case 'rejected':
        return 'destructive'
      default:
        return 'default'
    }
  }

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return 'text-green-600'
    if (rating >= 3) return 'text-yellow-600'
    return 'text-red-600'
  }

  const stats = {
    total: reviews?.length || 0,
    pending: reviews?.filter(r => r.status === 'pending').length || 0,
    approved: reviews?.filter(r => r.status === 'approved').length || 0,
    flagged: reviews?.filter(r => r.status === 'flagged').length || 0
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <MessageSquare className="h-8 w-8 text-blue-600" />
          Review Moderation
        </h1>
        <p className="text-gray-600 mt-1">Moderate dealer and vehicle reviews</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Reviews</CardTitle>
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
            <CardTitle className="text-sm">Approved</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Flagged</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">{stats.flagged}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <Input
              placeholder="Search reviews..."
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
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="flagged">Flagged</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading reviews...</p>
          ) : reviews && reviews.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vehicle</TableHead>
                  <TableHead>Dealer</TableHead>
                  <TableHead>Reviewer</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Helpfulness</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reviews.map((review) => (
                  <TableRow key={review.id}>
                    <TableCell>
                      <div className="font-medium">
                        {review.vehicle_details.year} {review.vehicle_details.make} {review.vehicle_details.model}
                      </div>
                    </TableCell>
                    <TableCell>{review.dealer}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{review.reviewer}</p>
                        <p className="text-sm text-gray-600">{review.reviewer_email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className={`font-bold ${getRatingColor(review.rating)}`}>
                        {review.rating}/5
                      </span>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{review.title}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="flex items-center gap-1">
                          <ThumbsUp className="h-3 w-3 text-green-600" />
                          {review.helpfulness_upvotes}
                        </span>
                        <span className="flex items-center gap-1">
                          <ThumbsDown className="h-3 w-3 text-red-600" />
                          {review.helpfulness_downvotes}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(review.status)}>
                        {review.status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>{new Date(review.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => viewReview(review)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        {review.status === 'pending' && (
                          <>
                            <Button
                              size="sm"
                              variant="default"
                              onClick={() => handleApprove(review.id)}
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => viewReview(review)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                        {review.status !== 'flagged' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleFlag(review.id)}
                          >
                            <Flag className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-center text-gray-500 py-8">No reviews found</p>
          )}
        </CardContent>
      </Card>

      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Review Details</DialogTitle>
          </DialogHeader>
          {selectedReview && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Vehicle</Label>
                  <p className="font-medium">
                    {selectedReview.vehicle_details.year} {selectedReview.vehicle_details.make}{' '}
                    {selectedReview.vehicle_details.model}
                  </p>
                </div>
                <div>
                  <Label>Dealer</Label>
                  <p className="font-medium">{selectedReview.dealer}</p>
                </div>
                <div>
                  <Label>Reviewer</Label>
                  <p className="font-medium">{selectedReview.reviewer}</p>
                  <p className="text-sm text-gray-600">{selectedReview.reviewer_email}</p>
                </div>
                <div>
                  <Label>Rating</Label>
                  <p className={`text-2xl font-bold ${getRatingColor(selectedReview.rating)}`}>
                    {selectedReview.rating}/5
                  </p>
                </div>
              </div>

              <div>
                <Label>Title</Label>
                <p className="font-medium mt-1">{selectedReview.title}</p>
              </div>

              <div>
                <Label>Comment</Label>
                <p className="text-sm mt-1">{selectedReview.comment}</p>
              </div>

              <div>
                <Label>Helpfulness Votes</Label>
                <div className="flex gap-4 mt-1">
                  <span className="flex items-center gap-2">
                    <ThumbsUp className="h-4 w-4 text-green-600" />
                    {selectedReview.helpfulness_upvotes} helpful
                  </span>
                  <span className="flex items-center gap-2">
                    <ThumbsDown className="h-4 w-4 text-red-600" />
                    {selectedReview.helpfulness_downvotes} not helpful
                  </span>
                </div>
              </div>

              <div>
                <Label>Status</Label>
                <Badge variant={getStatusColor(selectedReview.status)}>
                  {selectedReview.status.toUpperCase()}
                </Badge>
              </div>

              {selectedReview.moderated_by && (
                <div>
                  <Label>Moderation Info</Label>
                  <p className="text-sm mt-1">
                    Moderated by {selectedReview.moderated_by} on{' '}
                    {new Date(selectedReview.moderated_at!).toLocaleDateString()}
                  </p>
                  {selectedReview.moderation_reason && (
                    <p className="text-sm text-gray-600 mt-1">Reason: {selectedReview.moderation_reason}</p>
                  )}
                </div>
              )}

              {selectedReview.status === 'pending' && (
                <div className="space-y-4 border-t pt-4">
                  <div>
                    <Label>Moderation Actions</Label>
                    <div className="flex gap-2 mt-2">
                      <Button onClick={() => handleApprove(selectedReview.id)}>
                        <Check className="h-4 w-4 mr-2" />
                        Approve
                      </Button>
                      <Button variant="destructive" onClick={() => {}}>
                        <X className="h-4 w-4 mr-2" />
                        Reject
                      </Button>
                      <Button variant="outline" onClick={() => handleFlag(selectedReview.id)}>
                        <Flag className="h-4 w-4 mr-2" />
                        Flag for Review
                      </Button>
                    </div>
                  </div>

                  <div>
                    <Label>Rejection Reason (if rejecting)</Label>
                    <Textarea
                      value={moderationReason}
                      onChange={(e) => setModerationReason(e.target.value)}
                      placeholder="Explain why this review is being rejected..."
                    />
                    <Button
                      className="mt-2"
                      variant="destructive"
                      onClick={handleReject}
                      disabled={!moderationReason}
                    >
                      Confirm Rejection
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
