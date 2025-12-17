import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  TrendingUp, TrendingDown, DollarSign, ShoppingCart, Package,
  Activity, Filter
} from 'lucide-react';
import api from '../lib/api';

interface AnalyticsDashboardProps {
  language: 'en' | 'fr';
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ language }) => {
  const [timeRange, setTimeRange] = useState(30);

  // Fetch dashboard summary
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analytics-summary', timeRange],
    queryFn: async () => {
      const response = await api.get(`/analytics-dashboard/dashboard-summary/?days=${timeRange}`);
      return response.data;
    }
  });

  // Fetch revenue trends
  const { data: revenueTrends } = useQuery({
    queryKey: ['revenue-trends', timeRange],
    queryFn: async () => {
      const response = await api.get(`/analytics-dashboard/revenue-trends/?period=day&days=${timeRange}`);
      return response.data;
    }
  });

  // Fetch deal pipeline
  const { data: dealPipeline } = useQuery({
    queryKey: ['deal-pipeline'],
    queryFn: async () => {
      const response = await api.get('/analytics-dashboard/deal-pipeline/');
      return response.data;
    }
  });

  // Fetch conversion funnel
  const { data: conversionFunnel } = useQuery({
    queryKey: ['conversion-funnel', timeRange],
    queryFn: async () => {
      const response = await api.get(`/analytics-dashboard/conversion-funnel/?days=${timeRange}`);
      return response.data;
    }
  });

  // Fetch buyer behavior
  const { data: buyerBehavior } = useQuery({
    queryKey: ['buyer-behavior', timeRange],
    queryFn: async () => {
      const response = await api.get(`/analytics-dashboard/buyer-behavior/?days=${timeRange}`);
      return response.data;
    }
  });

  // Fetch inventory insights
  const { data: inventoryInsights } = useQuery({
    queryKey: ['inventory-insights', timeRange],
    queryFn: async () => {
      const response = await api.get(`/analytics-dashboard/inventory-insights/?days=${timeRange}`);
      return response.data;
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat(language === 'fr' ? 'fr-CA' : 'en-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {language === 'fr' ? 'Tableau de bord analytique' : 'Analytics Dashboard'}
            </h1>
            <p className="text-gray-600 mt-1">
              {language === 'fr' ? 'Vue d\'ensemble de votre entreprise' : 'Overview of your business performance'}
            </p>
          </div>
          
          {/* Time Range Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              aria-label={language === 'fr' ? 'Sélectionner la période' : 'Select time range'}
            >
              <option value={7}>{language === 'fr' ? '7 derniers jours' : 'Last 7 days'}</option>
              <option value={30}>{language === 'fr' ? '30 derniers jours' : 'Last 30 days'}</option>
              <option value={90}>{language === 'fr' ? '90 derniers jours' : 'Last 90 days'}</option>
              <option value={365}>{language === 'fr' ? 'Cette année' : 'This year'}</option>
            </select>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* Total Revenue */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
              <div className={`flex items-center gap-1 ${
                summary.metrics.revenue_growth >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {summary.metrics.revenue_growth >= 0 ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span className="text-sm font-medium">{Math.abs(summary.metrics.revenue_growth).toFixed(1)}%</span>
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{formatCurrency(summary.metrics.total_revenue)}</h3>
            <p className="text-sm text-gray-600 mt-1">
              {language === 'fr' ? 'Revenus totaux' : 'Total Revenue'}
            </p>
          </div>

          {/* Total Deals */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <ShoppingCart className="w-6 h-6 text-green-600" />
              </div>
              <div className={`flex items-center gap-1 ${
                summary.metrics.deals_growth >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {summary.metrics.deals_growth >= 0 ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span className="text-sm font-medium">{Math.abs(summary.metrics.deals_growth).toFixed(1)}%</span>
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{summary.metrics.total_deals}</h3>
            <p className="text-sm text-gray-600 mt-1">
              {language === 'fr' ? 'Transactions totales' : 'Total Deals'}
            </p>
          </div>

          {/* Conversion Rate */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{summary.metrics.conversion_rate}%</h3>
            <p className="text-sm text-gray-600 mt-1">
              {language === 'fr' ? 'Taux de conversion' : 'Conversion Rate'}
            </p>
          </div>

          {/* Available Inventory */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-orange-100 rounded-lg">
                <Package className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{summary.metrics.available_vehicles}</h3>
            <p className="text-sm text-gray-600 mt-1">
              {language === 'fr' ? 'Inventaire disponible' : 'Available Inventory'}
            </p>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Revenue Trends */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Tendances des revenus' : 'Revenue Trends'}
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueTrends?.data || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="period" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString(language === 'fr' ? 'fr-CA' : 'en-CA', { month: 'short', day: 'numeric' })}
                />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip 
                  formatter={(value: number | undefined) => value !== undefined ? formatCurrency(value) : 'N/A'}
                  labelFormatter={(label) => new Date(label).toLocaleDateString(language === 'fr' ? 'fr-CA' : 'en-CA')}
                />
                <Legend />
                <Line type="monotone" dataKey="total_revenue" stroke="#3b82f6" strokeWidth={2} name={language === 'fr' ? 'Revenus' : 'Revenue'} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Deal Pipeline */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Pipeline de transactions' : 'Deal Pipeline'}
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dealPipeline?.pipeline || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#10b981" name={language === 'fr' ? 'Nombre' : 'Count'} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Conversion Funnel */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Entonnoir de conversion' : 'Conversion Funnel'}
            </h3>
            {conversionFunnel && (
              <div className="space-y-4">
                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {language === 'fr' ? 'Véhicules listés' : 'Vehicles Listed'}
                    </span>
                    <span className="text-lg font-bold text-gray-900">{conversionFunnel.funnel.vehicles_listed}</span>
                  </div>
                  <div className="w-full h-3 bg-blue-200 rounded-full">
                    <div className="h-3 bg-blue-600 rounded-full" style={{ width: '100%' }}></div>
                  </div>
                </div>

                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {language === 'fr' ? 'Transactions créées' : 'Deals Created'}
                    </span>
                    <span className="text-lg font-bold text-gray-900">
                      {conversionFunnel.funnel.deals_created} ({conversionFunnel.conversion_rates.vehicle_to_deal}%)
                    </span>
                  </div>
                  <div className="w-full h-3 bg-green-200 rounded-full">
                    <div 
                      className="h-3 bg-green-600 rounded-full" 
                      style={{ width: `${conversionFunnel.conversion_rates.vehicle_to_deal}%` }}
                    ></div>
                  </div>
                </div>

                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {language === 'fr' ? 'Transactions complétées' : 'Deals Completed'}
                    </span>
                    <span className="text-lg font-bold text-gray-900">
                      {conversionFunnel.funnel.deals_completed} ({conversionFunnel.conversion_rates.deal_to_completed}%)
                    </span>
                  </div>
                  <div className="w-full h-3 bg-purple-200 rounded-full">
                    <div 
                      className="h-3 bg-purple-600 rounded-full" 
                      style={{ width: `${conversionFunnel.conversion_rates.deal_to_completed}%` }}
                    ></div>
                  </div>
                </div>

                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {language === 'fr' ? 'Expéditions créées' : 'Shipments Created'}
                    </span>
                    <span className="text-lg font-bold text-gray-900">
                      {conversionFunnel.funnel.shipments_created} ({conversionFunnel.conversion_rates.deal_to_shipment}%)
                    </span>
                  </div>
                  <div className="w-full h-3 bg-orange-200 rounded-full">
                    <div 
                      className="h-3 bg-orange-600 rounded-full" 
                      style={{ width: `${conversionFunnel.conversion_rates.deal_to_shipment}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Popular Makes */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Marques populaires' : 'Popular Makes'}
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={buyerBehavior?.popular_makes.slice(0, 6) || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ make, percent }: any) => `${make} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="make"
                >
                  {buyerBehavior?.popular_makes.slice(0, 6).map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Inventory Insights */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Aperçu de l\'inventaire' : 'Inventory Insights'}
            </h3>
            {inventoryInsights && (
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">
                    {language === 'fr' ? 'Jours moyens pour vendre' : 'Avg Days to Sell'}
                  </span>
                  <span className="font-semibold text-gray-900">{inventoryInsights.avg_days_to_sell}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">
                    {language === 'fr' ? 'Taux de rotation' : 'Turnover Rate'}
                  </span>
                  <span className="font-semibold text-gray-900">{inventoryInsights.turnover_rate}%</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-600">
                    {language === 'fr' ? 'Inventaire total' : 'Total Inventory'}
                  </span>
                  <span className="font-semibold text-gray-900">{inventoryInsights.total_inventory}</span>
                </div>
              </div>
            )}
          </div>

          {/* Price Ranges */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Gammes de prix' : 'Price Ranges'}
            </h3>
            {buyerBehavior && (
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">&lt; $10,000</span>
                  <span className="font-semibold text-gray-900">{buyerBehavior.price_ranges.under_10k}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">$10,000 - $20,000</span>
                  <span className="font-semibold text-gray-900">{buyerBehavior.price_ranges['10k_20k']}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">$20,000 - $30,000</span>
                  <span className="font-semibold text-gray-900">{buyerBehavior.price_ranges['20k_30k']}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm text-gray-600">$30,000 - $50,000</span>
                  <span className="font-semibold text-gray-900">{buyerBehavior.price_ranges['30k_50k']}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-600">&gt; $50,000</span>
                  <span className="font-semibold text-gray-900">{buyerBehavior.price_ranges.over_50k}</span>
                </div>
              </div>
            )}
          </div>

          {/* Top Models */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {language === 'fr' ? 'Modèles les plus populaires' : 'Top Models'}
            </h3>
            {buyerBehavior && (
              <div className="space-y-2">
                {buyerBehavior.popular_models.slice(0, 5).map((model: any, index: number) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b">
                    <span className="text-sm text-gray-700">{model.make} {model.model}</span>
                    <span className="font-semibold text-gray-900">{model.count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
