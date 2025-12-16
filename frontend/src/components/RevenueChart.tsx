import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useLanguage } from '../contexts/LanguageContext'

interface RevenueData {
  month: string
  revenue: number
  deals: number
}

interface RevenueChartProps {
  data: RevenueData[]
  loading?: boolean
}

export default function RevenueChart({ data, loading }: RevenueChartProps) {
  const { language } = useLanguage()

  if (loading) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 h-[400px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900">
          {language === 'fr' ? 'Revenus et Transactions' : 'Revenue & Deals'}
        </h3>
        <p className="text-sm text-slate-500">
          {language === 'fr' ? 'Derniers 6 mois' : 'Last 6 months'}
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="month" 
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            yAxisId="left"
            stroke="#3b82f6"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            stroke="#8b5cf6"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '12px'
            }}
            formatter={(value?: number, name?: string) => {
              if (!value || !name) return ['', ''];
              if (name === 'revenue') {
                return [`$${value.toLocaleString()}`, language === 'fr' ? 'Revenus' : 'Revenue']
              }
              return [value, language === 'fr' ? 'Transactions' : 'Deals']
            }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => {
              if (value === 'revenue') return language === 'fr' ? 'Revenus (CAD)' : 'Revenue (CAD)'
              if (value === 'deals') return language === 'fr' ? 'Transactions' : 'Deals'
              return value
            }}
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="revenue" 
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={{ fill: '#3b82f6', r: 5 }}
            activeDot={{ r: 7 }}
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="deals" 
            stroke="#8b5cf6" 
            strokeWidth={3}
            dot={{ fill: '#8b5cf6', r: 5 }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
