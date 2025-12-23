import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, Users, Target, Award, Loader2 } from 'lucide-react'
import axios from 'axios'
import { useAuth } from '@/contexts/AuthContext'

interface BrokerTier {
  broker: string
  current_tier: string
  tier_display: string
  commission_rate: string
  deals_this_month: number
  volume_this_month: string
  total_deals: number
  total_commissions_earned: string
  country: string
  city: string
  qualified_buyers_network: number
  buyer_conversion_rate: string
  streak_days: number
}

interface DashboardData {
  tier_info: BrokerTier
  stats: {
    pending_commissions: { count: number; total: string }
    approved_commissions: { count: number; total: string }
    paid_commissions: { count: number; total: string }
    total_earnings: string
  }
}

export default function BrokerAnalytics() {
  const { user } = useAuth()

  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['broker-dashboard'],
    queryFn: async () => {
      const token = localStorage.getItem('authToken')
      const response = await axios.get('/api/commissions/commissions/dashboard/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    enabled: !!user && (user.role === 'broker' || user.role === 'admin')
  })

  if (!user || (user.role !== 'broker' && user.role !== 'admin')) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-yellow-800">Access Restricted</h2>
          <p className="text-yellow-700 mt-2">This page is only available for brokers.</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800">Error Loading Data</h2>
          <p className="text-red-700 mt-2">Failed to load broker analytics.</p>
        </div>
      </div>
    )
  }

  const tier = data?.tier_info
  const stats = data?.stats

  const getTierColor = (tierName: string) => {
    const lower = tierName.toLowerCase()
    if (lower.includes('diamond')) return 'from-purple-600 to-pink-600'
    if (lower.includes('platinum')) return 'from-slate-400 to-slate-600'
    if (lower.includes('gold')) return 'from-yellow-400 to-yellow-600'
    if (lower.includes('silver')) return 'from-gray-300 to-gray-500'
    return 'from-orange-400 to-orange-600'
  }

  const getTierIcon = (tierName: string) => {
    const lower = tierName.toLowerCase()
    if (lower.includes('diamond')) return '💎'
    if (lower.includes('platinum')) return '🏆'
    if (lower.includes('gold')) return '🥇'
    if (lower.includes('silver')) return '🥈'
    return '🥉'
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Broker Performance Analytics</h1>
        <p className="text-gray-600 mt-2">Track your tier, earnings, and network growth</p>
      </div>

      {/* Tier Header Card */}
      {tier && (
        <Card className={`mb-6 bg-gradient-to-br ${getTierColor(tier.current_tier)} text-white`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <span className="text-4xl">{getTierIcon(tier.current_tier)}</span>
                  {tier.tier_display}
                </CardTitle>
                <p className="text-white/90 mt-2">
                  Commission Rate: <span className="font-bold">{tier.commission_rate}%</span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-white/90 text-sm">Location</p>
                <p className="font-semibold text-lg">{tier.city}, {tier.country}</p>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {tier && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">This Month</CardTitle>
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{tier.deals_this_month}</div>
                <p className="text-xs text-gray-500 mt-1">Deals Closed</p>
                <p className="text-sm font-medium text-blue-600 mt-1">
                  ${parseFloat(tier.volume_this_month).toLocaleString()}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">All Time</CardTitle>
                <Award className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{tier.total_deals}</div>
                <p className="text-xs text-gray-500 mt-1">Total Deals</p>
                <p className="text-sm font-medium text-purple-600 mt-1">
                  ${parseFloat(tier.total_commissions_earned).toLocaleString()} earned
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Buyer Network</CardTitle>
                <Users className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{tier.qualified_buyers_network}</div>
                <p className="text-xs text-gray-500 mt-1">Qualified Buyers</p>
                <p className="text-sm font-medium text-green-600 mt-1">
                  {parseFloat(tier.buyer_conversion_rate).toFixed(1)}% conversion
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Streak</CardTitle>
                <Target className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{tier.streak_days}</div>
                <p className="text-xs text-gray-500 mt-1">Active Days</p>
                <p className="text-sm font-medium text-orange-600 mt-1">
                  🔥 Keep it going!
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Earnings Breakdown */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Pending</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                ${parseFloat(stats.pending_commissions.total || '0').toLocaleString()}
              </div>
              <p className="text-xs text-gray-500 mt-1">{stats.pending_commissions.count} commissions</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Approved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                ${parseFloat(stats.approved_commissions.total || '0').toLocaleString()}
              </div>
              <p className="text-xs text-gray-500 mt-1">{stats.approved_commissions.count} commissions</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Paid Out</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                ${parseFloat(stats.paid_commissions.total || '0').toLocaleString()}
              </div>
              <p className="text-xs text-gray-500 mt-1">{stats.paid_commissions.count} commissions</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Close 20+ deals this month to earn a +0.25% achievement boost</li>
            <li>• Build your qualified buyer network to improve conversion rates</li>
            <li>• Maintain your streak to maximize your commission rate</li>
            <li>• Reach the next tier for higher commission rates</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
