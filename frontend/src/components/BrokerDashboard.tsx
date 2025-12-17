import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Users, DollarSign, BarChart3, Loader2 } from 'lucide-react';
import axios from 'axios';

interface DashboardStats {
  leads_count: number;
  deals_count: number;
  total_commissions: number;
  active_deals: number;
  closed_deals: number;
  conversion_rate: number;
}

export default function BrokerDashboard() {
  const { data: stats, isLoading, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/analytics/stats/');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        Failed to load broker performance metrics
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-gray-600 text-sm font-medium">Total Leads</h3>
          <div className="bg-blue-100 p-2 rounded-lg">
            <Users className="h-5 w-5 text-blue-600" />
          </div>
        </div>
        <p className="text-2xl font-bold text-gray-900">{stats.leads_count}</p>
        <p className="text-xs text-gray-500 mt-1">Leads created</p>
      </div>

      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-gray-600 text-sm font-medium">Conversion Rate</h3>
          <div className="bg-green-100 p-2 rounded-lg">
            <TrendingUp className="h-5 w-5 text-green-600" />
          </div>
        </div>
        <p className="text-2xl font-bold text-gray-900">{stats.conversion_rate}%</p>
        <p className="text-xs text-gray-500 mt-1">Leads to deals</p>
      </div>

      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-gray-600 text-sm font-medium">Total Commissions</h3>
          <div className="bg-yellow-100 p-2 rounded-lg">
            <DollarSign className="h-5 w-5 text-yellow-600" />
          </div>
        </div>
        <p className="text-2xl font-bold text-gray-900">${stats.total_commissions.toFixed(2)}</p>
        <p className="text-xs text-gray-500 mt-1">CAD earned</p>
      </div>

      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-gray-600 text-sm font-medium">Deal Status</h3>
          <div className="bg-purple-100 p-2 rounded-lg">
            <BarChart3 className="h-5 w-5 text-purple-600" />
          </div>
        </div>
        <p className="text-2xl font-bold text-gray-900">{stats.active_deals} / {stats.closed_deals}</p>
        <p className="text-xs text-gray-500 mt-1">Active / Closed</p>
      </div>
    </div>
  );
}
