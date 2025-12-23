import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Activity, Download, TrendingUp, TrendingDown, Clock } from 'lucide-react'
import api from '@/lib/api'

interface Transaction {
  id: string
  transaction_type: 'payment' | 'refund' | 'transfer' | 'commission' | 'withdrawal'
  amount: string
  currency: string
  user: string
  user_email: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  payment_method: string
  gateway: string
  timestamp: string
  response_time_ms: number
  description: string
  reference_id: string
}

interface TransactionStats {
  total_count: number
  total_amount: number
  completed_count: number
  failed_count: number
  pending_count: number
  avg_response_time_ms: number
}

export default function TransactionViewer() {
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [timeRange, setTimeRange] = useState('24h')

  const { data: transactions, isLoading } = useQuery<Transaction[]>({
    queryKey: ['transactions', timeRange, typeFilter, statusFilter, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('time_range', timeRange)
      if (typeFilter !== 'all') params.append('type', typeFilter)
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchQuery) params.append('search', searchQuery)
      const response = await api.get(`/api/payments/transactions/?${params}`)
      return response.data
    },
    refetchInterval: 30000 // Refresh every 30 seconds for real-time monitoring
  })

  const { data: stats } = useQuery<TransactionStats>({
    queryKey: ['transaction-stats', timeRange],
    queryFn: async () => {
      const response = await api.get(`/api/payments/transactions/stats/?time_range=${timeRange}`)
      return response.data
    },
    refetchInterval: 30000
  })

  const exportTransactions = async () => {
    try {
      const params = new URLSearchParams()
      params.append('time_range', timeRange)
      if (typeFilter !== 'all') params.append('type', typeFilter)
      if (statusFilter !== 'all') params.append('status', statusFilter)
      const response = await api.get(`/api/payments/transactions/export/?${params}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `transactions-${Date.now()}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to export transactions:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'processing':
      case 'pending':
        return 'secondary'
      case 'failed':
      case 'cancelled':
        return 'destructive'
      default:
        return 'default'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'payment':
        return 'text-green-600'
      case 'refund':
        return 'text-red-600'
      case 'commission':
        return 'text-blue-600'
      case 'transfer':
        return 'text-purple-600'
      case 'withdrawal':
        return 'text-orange-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Activity className="h-8 w-8 text-purple-600" />
            Transaction Viewer
          </h1>
          <p className="text-gray-600 mt-1">Real-time financial transaction monitoring</p>
        </div>
        <Button onClick={exportTransactions}>
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Total Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.total_count || 0}</p>
            <p className="text-sm text-gray-600">
              ${(stats?.total_amount || 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">{stats?.completed_count || 0}</p>
            <p className="text-sm text-gray-600">
              {stats?.total_count ? ((stats.completed_count / stats.total_count) * 100).toFixed(1) : 0}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-600" />
              Failed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">{stats?.failed_count || 0}</p>
            <p className="text-sm text-gray-600">
              {stats?.pending_count || 0} pending
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Avg Response Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.avg_response_time_ms || 0}ms</p>
            <p className="text-sm text-gray-600">Processing speed</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <Input
              placeholder="Search by ID, user, reference..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-xs"
            />
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Transaction type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="payment">Payment</SelectItem>
                <SelectItem value="refund">Refund</SelectItem>
                <SelectItem value="transfer">Transfer</SelectItem>
                <SelectItem value="commission">Commission</SelectItem>
                <SelectItem value="withdrawal">Withdrawal</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Time range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1h">Last hour</SelectItem>
                <SelectItem value="24h">Last 24 hours</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading transactions...</p>
          ) : transactions && transactions.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Gateway</TableHead>
                    <TableHead>Response Time</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell className="font-mono text-xs">{transaction.id}</TableCell>
                      <TableCell>
                        <span className={`font-medium ${getTypeColor(transaction.transaction_type)}`}>
                          {transaction.transaction_type.toUpperCase()}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{transaction.user}</p>
                          <p className="text-xs text-gray-600">{transaction.user_email}</p>
                        </div>
                      </TableCell>
                      <TableCell className="font-semibold">
                        {transaction.currency} ${parseFloat(transaction.amount).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(transaction.status)}>
                          {transaction.status.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>{transaction.gateway}</TableCell>
                      <TableCell>
                        <span className={transaction.response_time_ms > 1000 ? 'text-red-600' : 'text-green-600'}>
                          {transaction.response_time_ms}ms
                        </span>
                      </TableCell>
                      <TableCell className="text-sm">
                        {new Date(transaction.timestamp).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No transactions found</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
