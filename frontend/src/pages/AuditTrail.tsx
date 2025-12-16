import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Shield,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Users,
  FileText,
  Lock,
  RefreshCw,
  Server
} from 'lucide-react'
import api from '../lib/api'
import { formatDistanceToNow } from 'date-fns'

export default function AuditTrail() {
  const [activeTab, setActiveTab] = useState<'overview' | 'logs' | 'security' | 'logins' | 'api'>('overview')
  const [timeRange, setTimeRange] = useState(7)

  // Fetch data
  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['audit-stats', timeRange],
    queryFn: () => api.getAuditStats(timeRange),
  })

  const { data: auditLogs = { results: [] }, isLoading: loadingLogs } = useQuery({
    queryKey: ['audit-logs', timeRange],
    queryFn: () => api.getAuditLogs({ days: timeRange }),
  })

  const { data: securityEvents = { results: [] }, isLoading: loadingSecurity } = useQuery({
    queryKey: ['security-events'],
    queryFn: () => api.getSecurityEvents(),
  })

  const { data: loginHistory = { results: [] }, isLoading: loadingLogins } = useQuery({
    queryKey: ['login-history'],
    queryFn: () => api.getLoginHistory(),
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'error':
        return 'bg-orange-100 text-orange-800'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800'
      case 'info':
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical':
        return 'bg-red-600 text-white'
      case 'high':
        return 'bg-orange-600 text-white'
      case 'medium':
        return 'bg-yellow-600 text-white'
      case 'low':
      default:
        return 'bg-green-600 text-white'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            Audit Trail
          </h1>
          <p className="text-slate-600 mt-1">Security monitoring and activity tracking</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      {!loadingStats && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Actions</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.total_actions?.toLocaleString() || 0}
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Logins</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.total_logins?.toLocaleString() || 0}
                </p>
                <p className="text-xs text-red-600 mt-1">
                  {stats.failed_logins || 0} failed
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                <Users className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Security Events</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.security_events?.toLocaleString() || 0}
                </p>
                <p className="text-xs text-orange-600 mt-1">
                  {stats.unresolved_security_events || 0} unresolved
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">API Calls</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.api_calls?.toLocaleString() || 0}
                </p>
                <p className="text-xs text-slate-600 mt-1">
                  {Math.round(stats.avg_response_time || 0)}ms avg
                </p>
              </div>
              <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                <Server className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'logs', label: 'Activity Logs', icon: FileText },
            { id: 'security', label: 'Security Events', icon: Shield },
            { id: 'logins', label: 'Login History', icon: Lock },
            { id: 'api', label: 'API Access', icon: Server },
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <Icon className="h-5 w-5" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Security Events */}
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Recent Security Events
            </h3>
            <div className="space-y-3">
              {securityEvents.results?.slice(0, 5).map((event: any) => (
                <div key={event.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(event.risk_level)}`}>
                    {event.risk_level_display}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900">{event.event_type_display}</p>
                    <p className="text-xs text-slate-600 mt-1 truncate">{event.description}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-600" />
              Recent Activity
            </h3>
            <div className="space-y-3">
              {auditLogs.results?.slice(0, 5).map((log: any) => (
                <div key={log.id} className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    {log.severity === 'error' || log.severity === 'critical' ? (
                      <XCircle className="h-5 w-5 text-red-600" />
                    ) : (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900">{log.action_display}</p>
                    <p className="text-xs text-slate-600 mt-1">{log.description}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(log.severity)}`}>
                        {log.severity_display}
                      </span>
                      <span className="text-xs text-slate-500">
                        {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          {loadingLogs ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Action</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Description</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">IP</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {auditLogs.results?.map((log: any) => (
                    <tr key={log.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                        {log.user_display?.email || 'System'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                        {log.action_display}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600 max-w-md truncate">
                        {log.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(log.severity)}`}>
                          {log.severity_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-mono">
                        {log.ip_address}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-4">
          {loadingSecurity ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : (
            securityEvents.results?.map((event: any) => (
              <div
                key={event.id}
                className="bg-white border-2 rounded-lg p-6 hover:border-red-300 transition-colors"
                style={{ borderColor: event.resolved ? '#e2e8f0' : '#fecaca' }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      event.risk_level === 'critical' || event.risk_level === 'high'
                        ? 'bg-red-100'
                        : event.risk_level === 'medium'
                        ? 'bg-yellow-100'
                        : 'bg-green-100'
                    }`}>
                      <AlertTriangle className={`h-6 w-6 ${
                        event.risk_level === 'critical' || event.risk_level === 'high'
                          ? 'text-red-600'
                          : event.risk_level === 'medium'
                          ? 'text-yellow-600'
                          : 'text-green-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-slate-900">
                          {event.event_type_display}
                        </h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(event.risk_level)}`}>
                          {event.risk_level_display}
                        </span>
                        {event.resolved && (
                          <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                            Resolved
                          </span>
                        )}
                        {event.blocked && (
                          <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                            Blocked
                          </span>
                        )}
                      </div>
                      <p className="text-slate-700 mb-3">{event.description}</p>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-slate-500">IP Address:</span>
                          <span className="ml-2 font-mono text-slate-900">{event.ip_address}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Time:</span>
                          <span className="ml-2 text-slate-900">
                            {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                          </span>
                        </div>
                        {event.action_taken && (
                          <div className="col-span-2">
                            <span className="text-slate-500">Action Taken:</span>
                            <span className="ml-2 text-slate-900">{event.action_taken}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'logins' && (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          {loadingLogins ? (
            <div className="flex justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">IP Address</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">2FA</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Duration</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {loginHistory.results?.map((login: any) => (
                    <tr key={login.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {formatDistanceToNow(new Date(login.login_timestamp), { addSuffix: true })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                        {login.user_display?.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          login.status === 'success'
                            ? 'bg-green-100 text-green-800'
                            : login.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {login.status_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-mono">
                        {login.ip_address}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {login.two_factor_used ? (
                          <span className="flex items-center gap-1 text-green-600">
                            <CheckCircle className="h-4 w-4" />
                            {login.two_factor_method}
                          </span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                        {login.session_duration || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'api' && (
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">API Performance Monitoring</h3>
          <p className="text-slate-600">
            API access logs and performance metrics are available for administrators.
          </p>
        </div>
      )}
    </div>
  )
}
