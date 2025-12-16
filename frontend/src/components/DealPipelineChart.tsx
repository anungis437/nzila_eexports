import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useLanguage } from '../contexts/LanguageContext'

interface PipelineData {
  status: string
  count: number
  color: string
}

interface DealPipelineChartProps {
  data: PipelineData[]
  loading?: boolean
}

export default function DealPipelineChart({ data, loading }: DealPipelineChartProps) {
  const { language } = useLanguage()

  const getStatusLabel = (status: string) => {
    const labels: Record<string, { en: string; fr: string }> = {
      pending_docs: { en: 'Pending Docs', fr: 'Docs en attente' },
      docs_verified: { en: 'Docs Verified', fr: 'Docs vérifiés' },
      payment_pending: { en: 'Payment Pending', fr: 'Paiement en attente' },
      payment_received: { en: 'Payment Received', fr: 'Paiement reçu' },
      ready_to_ship: { en: 'Ready to Ship', fr: 'Prêt à expédier' },
      shipped: { en: 'Shipped', fr: 'Expédié' },
      completed: { en: 'Completed', fr: 'Complété' },
    }
    return labels[status]?.[language] || status
  }

  const chartData = data.map(item => ({
    ...item,
    displayName: getStatusLabel(item.status)
  }))

  if (loading) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 h-[400px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900">
          {language === 'fr' ? 'Pipeline de Transactions' : 'Deal Pipeline'}
        </h3>
        <p className="text-sm text-slate-500">
          {language === 'fr' ? 'Distribution par statut' : 'Distribution by status'}
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="displayName" 
            stroke="#64748b"
            style={{ fontSize: '11px' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '12px'
            }}
            formatter={(value?: number) => [value || 0, language === 'fr' ? 'Transactions' : 'Deals']}
          />
          <Bar 
            dataKey="count" 
            radius={[8, 8, 0, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
