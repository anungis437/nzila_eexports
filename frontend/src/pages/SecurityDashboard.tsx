import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Shield, AlertTriangle, Activity, FileText, Lock, Search, Download, Filter } from 'lucide-react'
import api from '@/lib/api'

interface AuditLog {
  id: number
  user: { id: number; username: string; email: string }
  action: string
  resource_type: string
  resource_id: string
  ip_address: string
  user_agent: string
  timestamp: string
  changes: any
}

interface LoginHistory {
  id: number
  user: { id: number; username: string }
  login_time: string
  logout_time: string | null
  ip_address: string
  user_agent: string
  location: string
  device_type: string
  success: boolean
  failure_reason: string | null
}

interface SecurityEvent {
  id: number
  event_type: string
  severity: string
  user: { id: number; username: string } | null
  ip_address: string
  description: string
  details: any
  timestamp: string
  resolved: boolean
  resolved_at: string | null
  resolved_by: { id: number; username: string } | null
}

interface DataChangeLog {
  id: number
  user: { id: number; username: string }
  model_name: string
  record_id: string
  action: string
  field_name: string
  old_value: string
  new_value: string
  timestamp: string
  ip_address: string
  justification: string
}

interface APIAccessLog {
  id: number
  user: { id: number; username: string } | null
  endpoint: string
  method: string
  status_code: number
  response_time_ms: number
  ip_address: string
  user_agent: string
  timestamp: string
  request_body: any
  response_body: any
}

export default function SecurityDashboard() {
  const [activeTab, setActiveTab] = useState('audit')
  const [searchQuery, setSearchQuery] = useState('')
  const [timeRange, setTimeRange] = useState('24h')
  const [severityFilter, setSeverityFilter] = useState('all')

  // Fetch audit logs
  const { data: auditLogs, isLoading: loadingAudit } = useQuery<AuditLog[]>({
    queryKey: ['audit-logs', timeRange, searchQuery],
    queryFn: async () => {
      const response = await api.get(`/api/audit/logs/?time_range=${timeRange}&search=${searchQuery}`)
      return response.data
    }
  })

  // Fetch login history
  const { data: loginHistory, isLoading: loadingLogins } = useQuery<LoginHistory[]>({
    queryKey: ['login-history', timeRange],
    queryFn: async () => {
      const response = await api.get(`/api/audit/login-history/?time_range=${timeRange}`)
      return response.data
    }
  })

  // Fetch security events
  const { data: securityEvents, isLoading: loadingEvents } = useQuery<SecurityEvent[]>({
    queryKey: ['security-events', timeRange, severityFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ time_range: timeRange })
      if (severityFilter !== 'all') params.append('severity', severityFilter)
      const response = await api.get(`/api/audit/security-events/?${params}`)
      return response.data
    }
  })

  // Fetch data change logs
  const { data: dataChanges, isLoading: loadingChanges } = useQuery<DataChangeLog[]>({
    queryKey: ['data-changes', timeRange],
    queryFn: async () => {
      const response = await api.get(`/api/audit/data-changes/?time_range=${timeRange}`)
      return response.data
    }
  })

  // Fetch API access logs
  const { data: apiLogs, isLoading: loadingAPI } = useQuery<APIAccessLog[]>({
    queryKey: ['api-logs', timeRange],
    queryFn: async () => {
      const response = await api.get(`/api/audit/api-access/?time_range=${timeRange}`)
      return response.data
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

  const exportLogs = async (type: string) => {
    try {
      const response = await api.get(`/api/audit/export/${type}/?time_range=${timeRange}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${type}_${new Date().toISOString()}.csv`)
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
            <Shield className="h-8 w-8 text-blue-600" />
            Security Dashboard
          </h1>
          <p className="text-gray-600 mt-1">
            Comprehensive security monitoring and audit trails
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1h">Last Hour</SelectItem>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Security Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Audit Events</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{auditLogs?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Events</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{securityEvents?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {securityEvents?.filter(e => !e.resolved).length || 0} unresolved
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Login Attempts</CardTitle>
            <Lock className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loginHistory?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {loginHistory?.filter(l => !l.success).length || 0} failed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Requests</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apiLogs?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {apiLogs?.filter(l => l.status_code >= 400).length || 0} errors
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          <TabsTrigger value="logins">Login History</TabsTrigger>
          <TabsTrigger value="events">Security Events</TabsTrigger>
          <TabsTrigger value="changes">Data Changes</TabsTrigger>
          <TabsTrigger value="api">API Access</TabsTrigger>
        </TabsList>

        {/* Audit Logs Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Audit Logs</CardTitle>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search logs..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-8 w-64"
                    />
                  </div>
                  <Button variant="outline" size="sm" onClick={() => exportLogs('audit')}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loadingAudit ? (
                <p>Loading audit logs...</p>
              ) : auditLogs && auditLogs.length > 0 ? (
                <div className="space-y-2">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge>{log.action}</Badge>
                            <span className="text-sm text-gray-600">{log.resource_type}</span>
                            <span className="text-xs text-gray-400">ID: {log.resource_id}</span>
                          </div>
                          <p className="text-sm">
                            User: <strong>{log.user.username}</strong> ({log.user.email})
                          </p>
                          <p className="text-xs text-gray-500">
                            IP: {log.ip_address} • {new Date(log.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No audit logs found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Login History Tab */}
        <TabsContent value="logins" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Login History</CardTitle>
                <Button variant="outline" size="sm" onClick={() => exportLogs('logins')}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingLogins ? (
                <p>Loading login history...</p>
              ) : loginHistory && loginHistory.length > 0 ? (
                <div className="space-y-2">
                  {loginHistory.map((login) => (
                    <div key={login.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={login.success ? 'default' : 'destructive'}>
                              {login.success ? 'Success' : 'Failed'}
                            </Badge>
                            <span className="text-sm font-medium">{login.user.username}</span>
                          </div>
                          <p className="text-xs text-gray-600">
                            {login.location} • {login.device_type}
                          </p>
                          <p className="text-xs text-gray-500">
                            IP: {login.ip_address} • {new Date(login.login_time).toLocaleString()}
                          </p>
                          {!login.success && login.failure_reason && (
                            <p className="text-xs text-red-600">Reason: {login.failure_reason}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No login history found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Events Tab */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Security Events</CardTitle>
                <div className="flex gap-2">
                  <Select value={severityFilter} onValueChange={setSeverityFilter}>
                    <SelectTrigger className="w-32">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Severity</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" size="sm" onClick={() => exportLogs('events')}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loadingEvents ? (
                <p>Loading security events...</p>
              ) : securityEvents && securityEvents.length > 0 ? (
                <div className="space-y-2">
                  {securityEvents.map((event) => (
                    <div key={event.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={getSeverityColor(event.severity)}>
                              {event.severity.toUpperCase()}
                            </Badge>
                            <Badge variant="outline">{event.event_type}</Badge>
                            {event.resolved && <Badge variant="secondary">Resolved</Badge>}
                          </div>
                          <p className="text-sm font-medium">{event.description}</p>
                          {event.user && (
                            <p className="text-xs text-gray-600">User: {event.user.username}</p>
                          )}
                          <p className="text-xs text-gray-500">
                            IP: {event.ip_address} • {new Date(event.timestamp).toLocaleString()}
                          </p>
                        </div>
                        {!event.resolved && (
                          <Button size="sm" variant="outline">
                            Resolve
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No security events found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Changes Tab */}
        <TabsContent value="changes" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Data Change Logs</CardTitle>
                <Button variant="outline" size="sm" onClick={() => exportLogs('changes')}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingChanges ? (
                <p>Loading data changes...</p>
              ) : dataChanges && dataChanges.length > 0 ? (
                <div className="space-y-2">
                  {dataChanges.map((change) => (
                    <div key={change.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge>{change.action}</Badge>
                            <span className="text-sm">{change.model_name}</span>
                            <span className="text-xs text-gray-400">ID: {change.record_id}</span>
                          </div>
                          <p className="text-sm">
                            Field: <strong>{change.field_name}</strong>
                          </p>
                          <p className="text-xs text-gray-600">
                            <span className="text-red-600">{change.old_value}</span>
                            {' → '}
                            <span className="text-green-600">{change.new_value}</span>
                          </p>
                          <p className="text-xs text-gray-500">
                            By: {change.user.username} • {new Date(change.timestamp).toLocaleString()}
                          </p>
                          {change.justification && (
                            <p className="text-xs italic text-gray-600">
                              Reason: {change.justification}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No data changes found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Access Tab */}
        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>API Access Logs</CardTitle>
                <Button variant="outline" size="sm" onClick={() => exportLogs('api')}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingAPI ? (
                <p>Loading API logs...</p>
              ) : apiLogs && apiLogs.length > 0 ? (
                <div className="space-y-2">
                  {apiLogs.map((log) => (
                    <div key={log.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant={log.status_code >= 400 ? 'destructive' : 'default'}>
                              {log.method}
                            </Badge>
                            <span className="text-sm font-mono">{log.endpoint}</span>
                            <Badge variant="outline">{log.status_code}</Badge>
                          </div>
                          {log.user && (
                            <p className="text-xs text-gray-600">User: {log.user.username}</p>
                          )}
                          <p className="text-xs text-gray-500">
                            IP: {log.ip_address} • {log.response_time_ms}ms •{' '}
                            {new Date(log.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No API logs found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
