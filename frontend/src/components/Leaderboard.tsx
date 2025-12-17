import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Trophy, Medal, Award, TrendingUp } from 'lucide-react';
import axios from 'axios';

interface LeaderboardEntry {
  rank: number;
  user_id: number;
  user_name: string;
  deals: number;
  volume: string;
  tier: string;
  tier_display: string;
  commission_rate: string;
}

interface LeaderboardProps {
  userType: 'broker' | 'dealer';
}

const CANADIAN_PROVINCES = [
  { code: 'all', label: 'All Provinces' },
  { code: 'ON', label: 'Ontario' },
  { code: 'QC', label: 'Quebec' },
  { code: 'BC', label: 'British Columbia' },
  { code: 'AB', label: 'Alberta' },
  { code: 'SK', label: 'Saskatchewan' },
  { code: 'MB', label: 'Manitoba' },
  { code: 'NB', label: 'New Brunswick' },
  { code: 'NS', label: 'Nova Scotia' },
  { code: 'PE', label: 'Prince Edward Island' },
  { code: 'NL', label: 'Newfoundland and Labrador' },
  { code: 'YT', label: 'Yukon' },
  { code: 'NT', label: 'Northwest Territories' },
  { code: 'NU', label: 'Nunavut' },
];

// African countries where brokers are based (mostly CIV)
const AFRICAN_COUNTRIES = [
  { code: 'all', label: 'All Countries' },
  { code: 'CI', label: 'Côte d\'Ivoire' },
  { code: 'SN', label: 'Senegal' },
  { code: 'GH', label: 'Ghana' },
  { code: 'NG', label: 'Nigeria' },
  { code: 'BJ', label: 'Benin' },
  { code: 'TG', label: 'Togo' },
  { code: 'BF', label: 'Burkina Faso' },
  { code: 'ML', label: 'Mali' },
  { code: 'CM', label: 'Cameroon' },
  { code: 'CD', label: 'DR Congo' },
  { code: 'KE', label: 'Kenya' },
  { code: 'ZA', label: 'South Africa' },
  { code: 'MA', label: 'Morocco' },
  { code: 'TN', label: 'Tunisia' },
  { code: 'EG', label: 'Egypt' },
  { code: 'OTHER', label: 'Other' },
];

const Leaderboard: React.FC<LeaderboardProps> = ({ userType }) => {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState(userType === 'broker' ? 'month' : 'quarter');
  const [locationFilter, setLocationFilter] = useState('all'); // province for dealers, country for brokers

  useEffect(() => {
    fetchLeaderboard();
  }, [period, locationFilter]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const endpoint = userType === 'broker' 
        ? '/api/commissions/broker-tiers/leaderboard/'
        : '/api/commissions/dealer-tiers/leaderboard/';
      
      const params: any = { period };
      
      // Brokers filter by country (mostly African), dealers by province (Canadian)
      if (locationFilter && locationFilter !== 'all') {
        if (userType === 'broker') {
          params.country = locationFilter;
        } else {
          params.province = locationFilter;
        }
      }

      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      setLeaderboardData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Award className="w-6 h-6 text-amber-700" />;
    return <span className="text-lg font-bold text-gray-500">#{rank}</span>;
  };

  const getTierBadgeColor = (tier: string) => {
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

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6">
          <p className="text-red-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            {userType === 'broker' ? 'Broker' : 'Dealer'} Leaderboard
          </CardTitle>
          <div className="flex gap-3">
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={userType === 'broker' ? 'month' : 'quarter'}>
                  {userType === 'broker' ? 'This Month' : 'This Quarter'}
                </SelectItem>
                <SelectItem value="all-time">All-Time</SelectItem>
              </SelectContent>
            </Select>
            
            {/* Location filter: Countries for brokers (mostly African), Provinces for dealers (Canadian) */}
            <Select value={locationFilter} onValueChange={setLocationFilter}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder={userType === 'broker' ? 'Filter by Country' : 'Filter by Province'} />
              </SelectTrigger>
              <SelectContent>
                {userType === 'broker' ? (
                  AFRICAN_COUNTRIES.map(country => (
                    <SelectItem key={country.code} value={country.code}>
                      {country.label}
                    </SelectItem>
                  ))
                ) : (
                  CANADIAN_PROVINCES.map(prov => (
                    <SelectItem key={prov.code} value={prov.code}>
                      {prov.label}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {leaderboardData.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No rankings available yet</p>
            <p className="text-gray-400 text-sm mt-2">Complete deals to appear on the leaderboard</p>
          </div>
        ) : (
          <div className="space-y-2">
            {/* Top 3 Podium */}
            <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg">
              {leaderboardData.slice(0, 3).map((entry, index) => {
                const podiumOrder = index === 0 ? 1 : index === 1 ? 0 : 2; // Center gold, left silver, right bronze
                return (
                  <div 
                    key={entry.user_id} 
                    className={`text-center ${podiumOrder === 1 ? 'order-2' : podiumOrder === 0 ? 'order-1' : 'order-3'}`}
                  >
                    <div className="flex justify-center mb-2">
                      {getRankIcon(entry.rank)}
                    </div>
                    <p className="font-bold text-sm truncate">{entry.user_name}</p>
                    <Badge className={`${getTierBadgeColor(entry.tier)} text-white mt-1`}>
                      {entry.tier_display}
                    </Badge>
                    <p className="text-xs text-gray-600 mt-1">{entry.deals} deals</p>
                    <p className="text-xs font-semibold text-green-600">${parseFloat(entry.volume).toLocaleString()}</p>
                    <p className="text-xs text-blue-600">{entry.commission_rate}%</p>
                  </div>
                );
              })}
            </div>

            {/* Rest of Rankings */}
            <div className="space-y-1">
              {leaderboardData.slice(3).map((entry) => (
                <div 
                  key={entry.user_id}
                  className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-8 text-center">
                      {getRankIcon(entry.rank)}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{entry.user_name}</p>
                      <Badge className={`${getTierBadgeColor(entry.tier)} text-white text-xs mt-1`}>
                        {entry.tier_display}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-8 items-center">
                    <div className="text-right">
                      <p className="text-sm font-semibold">{entry.deals}</p>
                      <p className="text-xs text-gray-500">deals</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-green-600">
                        ${parseFloat(entry.volume).toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500">volume</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-blue-600">{entry.commission_rate}%</p>
                      <p className="text-xs text-gray-500">rate</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Motivational Footer */}
            {leaderboardData.length >= 10 && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg text-center">
                <p className="text-sm text-blue-800">
                  🚀 Keep closing deals to climb the ranks! Top performers earn up to{' '}
                  <span className="font-bold">{userType === 'broker' ? '5.5%' : '8.5%'}</span> commission.
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default Leaderboard;
