import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Shield, AlertTriangle, FileText, Users, Download, Check } from 'lucide-react'
import api from '@/lib/api'

interface DataBreachLog {
  id: number
  breach_date: string
  discovery_date: string
  severity: string
  description: string
  affected_users_count: number
  attack_vector: string
  data_compromised: string
  status: string
  remediation_steps: string
  notification_sent: boolean
  notification_sent_date: string | null
  compliance_status: string
  created_at: string
  updated_at: string
}

interface ConsentHistory {
  id: number
  user: { id: number; username: string; email: string }
  consent_type: string
  granted: boolean
  timestamp: string
  ip_address: string
  user_agent: string
  consent_version: string
  expiry_date: string | null
}

interface DataRetentionPolicy {
  id: number
  data_type: string
  retention_period_days: number
  legal_basis: string
  deletion_method: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface PrivacyImpactAssessment {
  id: number
  title: string
  description: string
  data_processed: string
  processing_purpose: string
  legal_basis: string
  risk_level: string
  mitigation_measures: string
  assessment_date: string
  reviewer: { id: number; username: string }
  status: string
  created_at: string
}

export default function ComplianceDashboard() {
  const [activeTab, setActiveTab] = useState('breaches')
  const [timeRange, setTimeRange] = useState('30d')
  const [newBreach, setNewBreach] = useState<Partial<DataBreachLog>>({})
  const [breachDialogOpen, setBreachDialogOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch data breach logs
  const { data: breaches, isLoading: loadingBreaches } = useQuery<DataBreachLog[]>({
    queryKey: ['data-breaches', timeRange],
    queryFn: async () => {
      const response = await api.get(`/api/accounts/compliance/breaches/?time_range=${timeRange}`)
      return response.data
    }
  })

  // Fetch consent history
  const { data: consents, isLoading: loadingConsents } = useQuery<ConsentHistory[]>({
    queryKey: ['consent-history', timeRange],
    queryFn: async () => {
      const response = await api.get(`/api/accounts/compliance/consents/?time_range=${timeRange}`)
      return response.data
    }
  })

  // Fetch retention policies
  const { data: policies, isLoading: loadingPolicies } = useQuery<DataRetentionPolicy[]>({
    queryKey: ['retention-policies'],
    queryFn: async () => {
      const response = await api.get('/api/accounts/compliance/retention-policies/')
      return response.data
    }
  })

  // Fetch PIAs
  const { data: pias, isLoading: loadingPIAs } = useQuery<PrivacyImpactAssessment[]>({
    queryKey: ['privacy-assessments'],
    queryFn: async () => {
      const response = await api.get('/api/accounts/compliance/privacy-assessments/')
      return response.data
    }
  })

  // Create breach mutation
  const createBreachMutation = useMutation({
    mutationFn: async (breach: Partial<DataBreachLog>) => {
      const response = await api.post('/api/accounts/compliance/breaches/', breach)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-breaches'] })
      setBreachDialogOpen(false)
      setNewBreach({})
    }
  })

  // Update breach status mutation
  const updateBreachMutation = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }) => {
      const response = await api.patch(`/api/accounts/compliance/breaches/${id}/`, { status })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-breaches'] })
    }
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive'
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'secondary'
    }
  }

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'default'
      case 'in_progress': return 'secondary'
      case 'non_compliant': return 'destructive'
      default: return 'secondary'
    }
  }

  const exportReport = async (type: string) => {
    try {
      const response = await api.get(`/api/accounts/compliance/export/${type}/`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${type}_report_${new Date().toISOString()}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8 text-green-600" />
            Compliance Dashboard
          </h1>
          <p className="text-gray-600 mt-1">
            PIPEDA & Law 25 Compliance Management
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
              <SelectItem value="1y">Last Year</SelectItem>
              <SelectItem value="all">All Time</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Compliance Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Breaches</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{breaches?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {breaches?.filter(b => b.status !== 'resolved').length || 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Consent Records</CardTitle>
            <Users className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{consents?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {consents?.filter(c => c.granted).length || 0} granted
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Retention Policies</CardTitle>
            <FileText className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{policies?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {policies?.filter(p => p.is_active).length || 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Privacy Assessments</CardTitle>
            <Shield className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pias?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {pias?.filter(p => p.status === 'approved').length || 0} approved
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="breaches">Data Breaches</TabsTrigger>
          <TabsTrigger value="consents">Consent History</TabsTrigger>
          <TabsTrigger value="policies">Retention Policies</TabsTrigger>
          <TabsTrigger value="pias">Privacy Assessments</TabsTrigger>
        </TabsList>

        {/* Data Breaches Tab */}
        <TabsContent value="breaches" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Data Breach Logs</CardTitle>
                  <CardDescription>Track and manage PIPEDA-required breach notifications</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Dialog open={breachDialogOpen} onOpenChange={setBreachDialogOpen}>
                    <DialogTrigger asChild>
                      <Button>Report Breach</Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Report Data Breach</DialogTitle>
                        <DialogDescription>
                          Document a security incident involving personal data
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label>Breach Date</Label>
                          <Input
                            type="date"
                            value={newBreach.breach_date || ''}
                            onChange={(e) => setNewBreach({ ...newBreach, breach_date: e.target.value })}
                          />
                        </div>
                        <div>
                          <Label>Discovery Date</Label>
                          <Input
                            type="date"
                            value={newBreach.discovery_date || ''}
                            onChange={(e) => setNewBreach({ ...newBreach, discovery_date: e.target.value })}
                          />
                        </div>
                        <div>
                          <Label>Severity</Label>
                          <Select
                            value={newBreach.severity}
                            onValueChange={(value) => setNewBreach({ ...newBreach, severity: value })}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select severity" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="critical">Critical</SelectItem>
                              <SelectItem value="high">High</SelectItem>
                              <SelectItem value="medium">Medium</SelectItem>
                              <SelectItem value="low">Low</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Description</Label>
                          <Textarea
                            value={newBreach.description || ''}
                            onChange={(e) => setNewBreach({ ...newBreach, description: e.target.value })}
                            placeholder="Describe the breach incident..."
                          />
                        </div>
                        <div>
                          <Label>Affected Users Count</Label>
                          <Input
                            type="number"
                            value={newBreach.affected_users_count || ''}
                            onChange={(e) => setNewBreach({ ...newBreach, affected_users_count: parseInt(e.target.value) })}
                          />
                        </div>
                        <div>
                          <Label>Attack Vector</Label>
                          <Input
                            value={newBreach.attack_vector || ''}
                            onChange={(e) => setNewBreach({ ...newBreach, attack_vector: e.target.value })}
                            placeholder="e.g., SQL Injection, Phishing, etc."
                          />
                        </div>
                        <div>
                          <Label>Data Compromised</Label>
                          <Textarea
                            value={newBreach.data_compromised || ''}
                            onChange={(e) => setNewBreach({ ...newBreach, data_compromised: e.target.value })}
                            placeholder="List types of data affected..."
                          />
                        </div>
                        <Button
                          onClick={() => createBreachMutation.mutate(newBreach)}
                          disabled={createBreachMutation.isPending}
                        >
                          {createBreachMutation.isPending ? 'Reporting...' : 'Report Breach'}
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                  <Button variant="outline" onClick={() => exportReport('breaches')}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loadingBreaches ? (
                <p>Loading breach logs...</p>
              ) : breaches && breaches.length > 0 ? (
                <div className="space-y-3">
                  {breaches.map((breach) => (
                    <div key={breach.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={getSeverityColor(breach.severity)}>
                              {breach.severity.toUpperCase()}
                            </Badge>
                            <Badge variant={getComplianceColor(breach.compliance_status)}>
                              {breach.compliance_status.replace('_', ' ')}
                            </Badge>
                            <Badge variant="outline">{breach.status}</Badge>
                          </div>
                          <p className="text-sm font-medium">{breach.description}</p>
                          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                            <p>Breach Date: {new Date(breach.breach_date).toLocaleDateString()}</p>
                            <p>Discovery: {new Date(breach.discovery_date).toLocaleDateString()}</p>
                            <p>Affected Users: {breach.affected_users_count}</p>
                            <p>Attack Vector: {breach.attack_vector}</p>
                          </div>
                          {breach.notification_sent && (
                            <p className="text-xs text-green-600 flex items-center gap-1">
                              <Check className="h-3 w-3" />
                              Notifications sent on {new Date(breach.notification_sent_date!).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        {breach.status !== 'resolved' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateBreachMutation.mutate({ id: breach.id, status: 'resolved' })}
                          >
                            Mark Resolved
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No data breaches recorded</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Consent History Tab */}
        <TabsContent value="consents" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Consent History</CardTitle>
                  <CardDescription>Law 25 consent tracking and management</CardDescription>
                </div>
                <Button variant="outline" onClick={() => exportReport('consents')}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingConsents ? (
                <p>Loading consent history...</p>
              ) : consents && consents.length > 0 ? (
                <div className="space-y-2">
                  {consents.map((consent) => (
                    <div key={consent.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={consent.granted ? 'default' : 'destructive'}>
                              {consent.granted ? 'Granted' : 'Revoked'}
                            </Badge>
                            <span className="text-sm font-medium">{consent.consent_type}</span>
                          </div>
                          <p className="text-sm">User: {consent.user.username} ({consent.user.email})</p>
                          <p className="text-xs text-gray-500">
                            Version: {consent.consent_version} • IP: {consent.ip_address}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(consent.timestamp).toLocaleString()}
                          </p>
                          {consent.expiry_date && (
                            <p className="text-xs text-orange-600">
                              Expires: {new Date(consent.expiry_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No consent records found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Retention Policies Tab */}
        <TabsContent value="policies" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Data Retention Policies</CardTitle>
                  <CardDescription>Manage data lifecycle and deletion schedules</CardDescription>
                </div>
                <Button>Create Policy</Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingPolicies ? (
                <p>Loading retention policies...</p>
              ) : policies && policies.length > 0 ? (
                <div className="space-y-2">
                  {policies.map((policy) => (
                    <div key={policy.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={policy.is_active ? 'default' : 'secondary'}>
                              {policy.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                            <span className="text-sm font-medium">{policy.data_type}</span>
                          </div>
                          <p className="text-sm text-gray-600">
                            Retention: {policy.retention_period_days} days
                          </p>
                          <p className="text-xs text-gray-500">
                            Legal Basis: {policy.legal_basis}
                          </p>
                          <p className="text-xs text-gray-500">
                            Deletion Method: {policy.deletion_method}
                          </p>
                        </div>
                        <Button size="sm" variant="outline">Edit</Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No retention policies found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Assessments Tab */}
        <TabsContent value="pias" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Privacy Impact Assessments</CardTitle>
                  <CardDescription>PIA documentation and risk assessment</CardDescription>
                </div>
                <Button>Create PIA</Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingPIAs ? (
                <p>Loading privacy assessments...</p>
              ) : pias && pias.length > 0 ? (
                <div className="space-y-3">
                  {pias.map((pia) => (
                    <div key={pia.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={getSeverityColor(pia.risk_level)}>
                              {pia.risk_level} Risk
                            </Badge>
                            <Badge variant="outline">{pia.status}</Badge>
                          </div>
                          <p className="text-sm font-medium">{pia.title}</p>
                          <p className="text-sm text-gray-600">{pia.description}</p>
                          <div className="text-xs text-gray-500">
                            <p>Purpose: {pia.processing_purpose}</p>
                            <p>Legal Basis: {pia.legal_basis}</p>
                            <p>Reviewed by: {pia.reviewer.username}</p>
                            <p>Date: {new Date(pia.assessment_date).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <Button size="sm" variant="outline">View Details</Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No privacy assessments found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
