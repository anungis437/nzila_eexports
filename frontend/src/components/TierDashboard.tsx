import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Sparkles, TrendingUp, Award, Target, Zap } from 'lucide-react';
import axios from 'axios';

interface TierInfo {
  id: number;
  current_tier: string;
  tier_display: string;
  commission_rate: string;
  deals_this_month?: number;
  deals_this_quarter?: number;
  total_deals: number;
  total_commissions_earned: string;
  average_deal_value: string;
  streak_days?: number;
  deals_needed_next_tier?: number;
  earnings_potential?: {
    current: string;
    next_tier: string;
    increase: string;
    deals_needed: number;
  };
  base_rate?: string;
  market_bonus?: string;
  total_rate?: string;
  province?: string;
  is_rural?: boolean;
  is_first_nations?: boolean;
}

interface DashboardStats {
  tier_info: TierInfo | null;
  stats: {
    pending_commissions: { count: number; total: string | null };
    approved_commissions: { count: number; total: string | null };
    paid_commissions: { count: number; total: string | null };
    total_earnings: string;
  };
  recent_bonuses: Array<{
    id: number;
    bonus_type_display: string;
    amount_cad: string;
    status_display: string;
    created_at: string;
  }>;
}

const TierDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.get('/api/commissions/commissions/dashboard/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6">
          <p className="text-red-600">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    );
  }

  const { tier_info, stats, recent_bonuses } = dashboardData;

  if (!tier_info) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-600">Complete your first deal to activate your tier!</p>
        </CardContent>
      </Card>
    );
  }

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      starter: 'bg-gray-500',
      bronze: 'bg-amber-700',
      silver: 'bg-gray-400',
      gold: 'bg-yellow-500',
      platinum: 'bg-cyan-500',
      diamond: 'bg-purple-600',
      standard: 'bg-blue-500',
      preferred: 'bg-green-500',
      elite: 'bg-purple-500',
      premier: 'bg-pink-500'
    };
    return colors[tier.toLowerCase()] || 'bg-gray-500';
  };

  const getTierIcon = (tier: string) => {
    if (tier.toLowerCase().includes('diamond') || tier.toLowerCase().includes('premier')) {
      return '👑';
    } else if (tier.toLowerCase().includes('platinum') || tier.toLowerCase().includes('elite')) {
      return '💎';
    } else if (tier.toLowerCase().includes('gold')) {
      return '🏆';
    } else if (tier.toLowerCase().includes('silver') || tier.toLowerCase().includes('preferred')) {
      return '⭐';
    } else if (tier.toLowerCase().includes('bronze')) {
      return '🥉';
    }
    return '🎯';
  };

  const isBroker = 'deals_this_month' in tier_info;
  const currentDeals = isBroker ? tier_info.deals_this_month! : tier_info.deals_this_quarter!;
  const periodLabel = isBroker ? 'This Month' : 'This Quarter';

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="bg-gradient-to-br from-blue-600 to-purple-700 text-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-3xl font-bold flex items-center gap-2">
                <span className="text-4xl">{getTierIcon(tier_info.current_tier)}</span>
                {tier_info.tier_display}
              </CardTitle>
              <p className="text-blue-100 mt-2">
                Your Commission Rate: <span className="text-2xl font-bold">{tier_info.commission_rate}%</span>
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-100">Total Earnings</p>
              <p className="text-3xl font-bold">${parseFloat(stats.total_earnings).toLocaleString()}</p>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Current Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              {periodLabel}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Deals Closed</span>
                  <span className="font-semibold">{currentDeals}</span>
                </div>
                {tier_info.deals_needed_next_tier !== undefined && tier_info.deals_needed_next_tier > 0 && (
                  <>
                    <Progress 
                      value={(currentDeals / (currentDeals + tier_info.deals_needed_next_tier)) * 100} 
                      className="h-2"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {tier_info.deals_needed_next_tier} more deals to next tier
                    </p>
                  </>
                )}
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Average Deal Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${parseFloat(tier_info.average_deal_value).toLocaleString()}
                </p>
              </div>
              {isBroker && tier_info.streak_days && tier_info.streak_days > 0 && (
                <div className="pt-3 border-t">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-orange-500" />
                    <span className="text-sm font-medium">{tier_info.streak_days} Day Streak!</span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Earnings Potential */}
        {isBroker && tier_info.earnings_potential && tier_info.deals_needed_next_tier! > 0 && (
          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Target className="w-5 h-5 text-green-600" />
                Next Tier Bonus
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Potential Monthly Increase</p>
                  <p className="text-2xl font-bold text-green-600">
                    +${parseFloat(tier_info.earnings_potential.increase).toLocaleString()}
                  </p>
                </div>
                <div className="pt-3 border-t border-green-200">
                  <p className="text-xs text-gray-600">Close {tier_info.earnings_potential.deals_needed} more deals</p>
                  <p className="text-sm font-medium mt-1">
                    Unlock {tier_info.earnings_potential.next_tier ? 
                      `$${parseFloat(tier_info.earnings_potential.next_tier).toLocaleString()}/month` : 
                      'next tier'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Canadian Dealer Bonuses */}
        {!isBroker && (
          <Card className="border-purple-200 bg-purple-50">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Award className="w-5 h-5 text-purple-600" />
                Your Bonuses
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Base Rate</span>
                  <span className="font-semibold">{tier_info.base_rate}%</span>
                </div>
                {tier_info.market_bonus && parseFloat(tier_info.market_bonus) > 0 && (
                  <>
                    {tier_info.province && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">🍁 {tier_info.province} Bonus</span>
                        <span className="font-semibold text-green-600">+0.5%</span>
                      </div>
                    )}
                    {tier_info.is_rural && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">🏡 Rural Bonus</span>
                        <span className="font-semibold text-green-600">+1.0%</span>
                      </div>
                    )}
                    {tier_info.is_first_nations && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">🪶 First Nations</span>
                        <span className="font-semibold text-green-600">+1.5%</span>
                      </div>
                    )}
                  </>
                )}
                <div className="pt-2 border-t border-purple-200">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Total Rate</span>
                    <span className="text-xl font-bold text-purple-600">{tier_info.total_rate}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Commission Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-yellow-600" />
              Commission Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Pending</span>
                <div className="text-right">
                  <p className="font-semibold">
                    ${stats.pending_commissions.total ? 
                      parseFloat(stats.pending_commissions.total).toLocaleString() : '0'}
                  </p>
                  <p className="text-xs text-gray-500">{stats.pending_commissions.count} deals</p>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Approved</span>
                <div className="text-right">
                  <p className="font-semibold text-green-600">
                    ${stats.approved_commissions.total ? 
                      parseFloat(stats.approved_commissions.total).toLocaleString() : '0'}
                  </p>
                  <p className="text-xs text-gray-500">{stats.approved_commissions.count} deals</p>
                </div>
              </div>
              <div className="flex justify-between items-center pt-2 border-t">
                <span className="text-sm font-medium">Paid YTD</span>
                <div className="text-right">
                  <p className="font-bold text-blue-600">
                    ${stats.paid_commissions.total ? 
                      parseFloat(stats.paid_commissions.total).toLocaleString() : '0'}
                  </p>
                  <p className="text-xs text-gray-500">{stats.paid_commissions.count} deals</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Bonuses */}
      {recent_bonuses.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Bonuses 🎁</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recent_bonuses.map(bonus => (
                <div key={bonus.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{bonus.bonus_type_display}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(bonus.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-green-600">${parseFloat(bonus.amount_cad).toLocaleString()}</p>
                    <Badge variant={bonus.status_display === 'Paid' ? 'default' : 'secondary'}>
                      {bonus.status_display}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* All-Time Stats */}
      <Card className="bg-gradient-to-r from-gray-50 to-gray-100">
        <CardHeader>
          <CardTitle className="text-lg">All-Time Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Deals</p>
              <p className="text-2xl font-bold">{tier_info.total_deals}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Commissions</p>
              <p className="text-2xl font-bold text-green-600">
                ${parseFloat(tier_info.total_commissions_earned).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Current Rate</p>
              <p className="text-2xl font-bold text-blue-600">{tier_info.commission_rate}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TierDashboard;
