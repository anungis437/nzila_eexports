import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CheckCircle, Calendar, ClipboardCheck, Plus, Eye } from 'lucide-react'
import api from '@/lib/api'

interface Inspector {
  id: number
  user: string
  name: string
  email: string
  phone: string
  certifications: string[]
  availability_status: 'available' | 'busy' | 'unavailable'
  rating: number
  completed_inspections: number
  specializations: string[]
}

interface InspectionSlot {
  id: number
  inspector: string
  date: string
  start_time: string
  end_time: string
  status: 'available' | 'booked' | 'completed' | 'cancelled'
  vehicle: string | null
  location: string
}

interface InspectionReport {
  id: number
  vehicle: string
  inspector: string
  inspection_date: string
  status: 'pending' | 'in_progress' | 'completed' | 'approved' | 'rejected'
  overall_condition: 'excellent' | 'good' | 'fair' | 'poor'
  findings: string
  recommendations: string
  images_count: number
  approved_by: string | null
  approved_at: string | null
}

interface InspectorReview {
  id: number
  inspector: string
  reviewer: string
  rating: number
  comment: string
  inspection: number
  created_at: string
}

export default function InspectionManagement() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedReport, setSelectedReport] = useState<InspectionReport | null>(null)
  const queryClient = useQueryClient()

  const { data: inspectors } = useQuery<Inspector[]>({
    queryKey: ['inspectors'],
    queryFn: async () => {
      const response = await api.get('/api/inspections/inspectors/')
      return response.data
    }
  })

  const { data: slots } = useQuery<InspectionSlot[]>({
    queryKey: ['inspection-slots'],
    queryFn: async () => {
      const response = await api.get('/api/inspections/slots/')
      return response.data
    }
  })

  const { data: reports } = useQuery<InspectionReport[]>({
    queryKey: ['inspection-reports'],
    queryFn: async () => {
      const response = await api.get('/api/inspections/reports/')
      return response.data
    }
  })

  const { data: reviews } = useQuery<InspectorReview[]>({
    queryKey: ['inspector-reviews'],
    queryFn: async () => {
      const response = await api.get('/api/inspections/reviews/')
      return response.data
    }
  })

  const approveReportMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.patch(`/api/inspections/reports/${id}/approve/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inspection-reports'] })
    }
  })

  const getAvailabilityColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'default'
      case 'busy':
        return 'secondary'
      case 'unavailable':
        return 'destructive'
      default:
        return 'default'
    }
  }

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case 'excellent':
        return 'default'
      case 'good':
        return 'secondary'
      case 'fair':
        return 'secondary'
      case 'poor':
        return 'destructive'
      default:
        return 'default'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'approved':
        return 'default'
      case 'in_progress':
        return 'secondary'
      case 'pending':
        return 'outline'
      case 'rejected':
        return 'destructive'
      default:
        return 'default'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <ClipboardCheck className="h-8 w-8 text-indigo-600" />
          Inspection Management
        </h1>
        <p className="text-gray-600 mt-1">Manage inspectors, slots, reports, and reviews</p>
      </div>

      <Tabs defaultValue="inspectors">
        <TabsList>
          <TabsTrigger value="inspectors">Inspectors</TabsTrigger>
          <TabsTrigger value="slots">Inspection Slots</TabsTrigger>
          <TabsTrigger value="reports">Reports & Reviews</TabsTrigger>
        </TabsList>

        <TabsContent value="inspectors" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Inspector Directory</CardTitle>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Inspector
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {inspectors && inspectors.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Contact</TableHead>
                      <TableHead>Certifications</TableHead>
                      <TableHead>Availability</TableHead>
                      <TableHead>Rating</TableHead>
                      <TableHead>Completed</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {inspectors.map((inspector) => (
                      <TableRow key={inspector.id}>
                        <TableCell className="font-medium">{inspector.name}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <p>{inspector.email}</p>
                            <p className="text-gray-600">{inspector.phone}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {inspector.certifications.slice(0, 3).map((cert, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {cert}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={getAvailabilityColor(inspector.availability_status)}>
                            {inspector.availability_status.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <span className="font-semibold">{inspector.rating.toFixed(1)}</span>
                            <span className="text-gray-600">/5.0</span>
                          </div>
                        </TableCell>
                        <TableCell>{inspector.completed_inspections}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-center text-gray-500 py-8">No inspectors found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="slots" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Inspection Slots</CardTitle>
                <Button>
                  <Calendar className="h-4 w-4 mr-2" />
                  Schedule Slot
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {slots && slots.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Inspector</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Time</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Vehicle</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {slots.map((slot) => (
                      <TableRow key={slot.id}>
                        <TableCell className="font-medium">{slot.inspector}</TableCell>
                        <TableCell>{new Date(slot.date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          {slot.start_time} - {slot.end_time}
                        </TableCell>
                        <TableCell>{slot.location}</TableCell>
                        <TableCell>{slot.vehicle || '-'}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(slot.status)}>
                            {slot.status.toUpperCase()}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-center text-gray-500 py-8">No slots found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Inspection Reports</CardTitle>
            </CardHeader>
            <CardContent>
              {reports && reports.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vehicle</TableHead>
                      <TableHead>Inspector</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Condition</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reports.map((report) => (
                      <TableRow key={report.id}>
                        <TableCell className="font-medium">{report.vehicle}</TableCell>
                        <TableCell>{report.inspector}</TableCell>
                        <TableCell>{new Date(report.inspection_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Badge variant={getConditionColor(report.overall_condition)}>
                            {report.overall_condition.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(report.status)}>
                            {report.status.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setSelectedReport(report)
                                setDialogOpen(true)
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {report.status === 'completed' && !report.approved_at && (
                              <Button
                                size="sm"
                                onClick={() => approveReportMutation.mutate(report.id)}
                              >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Approve
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-center text-gray-500 py-8">No reports found</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Inspector Reviews</CardTitle>
            </CardHeader>
            <CardContent>
              {reviews && reviews.length > 0 ? (
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <div key={review.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{review.inspector}</p>
                          <p className="text-sm text-gray-600">by {review.reviewer}</p>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="font-bold">{review.rating}</span>
                          <span className="text-gray-600">/5</span>
                        </div>
                      </div>
                      <p className="text-sm mt-2">{review.comment}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(review.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No reviews found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Inspection Report Details</DialogTitle>
          </DialogHeader>
          {selectedReport && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Vehicle</Label>
                  <p className="font-medium">{selectedReport.vehicle}</p>
                </div>
                <div>
                  <Label>Inspector</Label>
                  <p className="font-medium">{selectedReport.inspector}</p>
                </div>
                <div>
                  <Label>Inspection Date</Label>
                  <p>{new Date(selectedReport.inspection_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <Label>Overall Condition</Label>
                  <Badge variant={getConditionColor(selectedReport.overall_condition)}>
                    {selectedReport.overall_condition.toUpperCase()}
                  </Badge>
                </div>
              </div>
              <div>
                <Label>Findings</Label>
                <p className="text-sm mt-1">{selectedReport.findings}</p>
              </div>
              <div>
                <Label>Recommendations</Label>
                <p className="text-sm mt-1">{selectedReport.recommendations}</p>
              </div>
              {selectedReport.approved_at && (
                <div>
                  <Label>Approved By</Label>
                  <p className="text-sm mt-1">
                    {selectedReport.approved_by} on {new Date(selectedReport.approved_at).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
