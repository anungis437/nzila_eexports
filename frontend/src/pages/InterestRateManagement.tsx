import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, Plus, Edit, Trash2 } from 'lucide-react'
import api from '@/lib/api'

interface InterestRate {
  id: number
  province: string
  tier: string
  rate: string
  min_credit_score: number
  max_credit_score: number
  is_active: boolean
  effective_date: string
  created_at: string
}

const PROVINCES = [
  { code: 'ON', name: 'Ontario' },
  { code: 'QC', name: 'Quebec' },
  { code: 'BC', name: 'British Columbia' },
  { code: 'AB', name: 'Alberta' },
  { code: 'MB', name: 'Manitoba' },
  { code: 'SK', name: 'Saskatchewan' },
  { code: 'NS', name: 'Nova Scotia' },
  { code: 'NB', name: 'New Brunswick' },
  { code: 'NL', name: 'Newfoundland and Labrador' },
  { code: 'PE', name: 'Prince Edward Island' },
  { code: 'NT', name: 'Northwest Territories' },
  { code: 'YT', name: 'Yukon' },
  { code: 'NU', name: 'Nunavut' }
]

const CREDIT_TIERS = [
  { name: 'Excellent', min: 750, max: 850 },
  { name: 'Good', min: 680, max: 749 },
  { name: 'Fair', min: 620, max: 679 },
  { name: 'Poor', min: 550, max: 619 },
  { name: 'Very Poor', min: 300, max: 549 }
]

export default function InterestRateManagement() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRate, setEditingRate] = useState<InterestRate | null>(null)
  const [formData, setFormData] = useState<Partial<InterestRate>>({})
  const queryClient = useQueryClient()

  const { data: rates, isLoading } = useQuery<InterestRate[]>({
    queryKey: ['interest-rates'],
    queryFn: async () => {
      const response = await api.get('/api/commissions/interest-rates/')
      return response.data
    }
  })

  const createMutation = useMutation({
    mutationFn: async (data: Partial<InterestRate>) => {
      const response = await api.post('/api/commissions/interest-rates/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interest-rates'] })
      setDialogOpen(false)
      setFormData({})
    }
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<InterestRate> }) => {
      const response = await api.patch(`/api/commissions/interest-rates/${id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interest-rates'] })
      setDialogOpen(false)
      setEditingRate(null)
      setFormData({})
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/api/commissions/interest-rates/${id}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interest-rates'] })
    }
  })

  const handleSubmit = () => {
    if (editingRate) {
      updateMutation.mutate({ id: editingRate.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const openCreateDialog = () => {
    setEditingRate(null)
    setFormData({})
    setDialogOpen(true)
  }

  const openEditDialog = (rate: InterestRate) => {
    setEditingRate(rate)
    setFormData(rate)
    setDialogOpen(true)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <TrendingUp className="h-8 w-8 text-green-600" />
            Interest Rate Management
          </h1>
          <p className="text-gray-600 mt-1">Manage financing interest rates by province and credit tier</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreateDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Add Interest Rate
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{editingRate ? 'Edit Interest Rate' : 'Create Interest Rate'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Province</Label>
                <Select
                  value={formData.province}
                  onValueChange={(value) => setFormData({ ...formData, province: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select province" />
                  </SelectTrigger>
                  <SelectContent>
                    {PROVINCES.map((prov) => (
                      <SelectItem key={prov.code} value={prov.code}>
                        {prov.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Credit Tier</Label>
                <Select
                  value={formData.tier}
                  onValueChange={(value) => {
                    const tier = CREDIT_TIERS.find(t => t.name === value)
                    setFormData({
                      ...formData,
                      tier: value,
                      min_credit_score: tier?.min,
                      max_credit_score: tier?.max
                    })
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select tier" />
                  </SelectTrigger>
                  <SelectContent>
                    {CREDIT_TIERS.map((tier) => (
                      <SelectItem key={tier.name} value={tier.name}>
                        {tier.name} ({tier.min}-{tier.max})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Interest Rate (%)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.rate || ''}
                  onChange={(e) => setFormData({ ...formData, rate: e.target.value })}
                  placeholder="e.g., 5.99"
                />
              </div>

              <div>
                <Label>Effective Date</Label>
                <Input
                  type="date"
                  value={formData.effective_date || ''}
                  onChange={(e) => setFormData({ ...formData, effective_date: e.target.value })}
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_active !== false}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  id="is_active"
                  aria-label="Set rate as active"
                />
                <Label htmlFor="is_active">Active</Label>
              </div>

              <Button onClick={handleSubmit} disabled={createMutation.isPending || updateMutation.isPending}>
                {editingRate ? 'Update' : 'Create'} Rate
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Interest Rates</CardTitle>
          <CardDescription>Current interest rates for vehicle financing across Canada</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading interest rates...</p>
          ) : rates && rates.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Province</TableHead>
                  <TableHead>Tier</TableHead>
                  <TableHead>Credit Score Range</TableHead>
                  <TableHead>Rate (%)</TableHead>
                  <TableHead>Effective Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rates.map((rate) => (
                  <TableRow key={rate.id}>
                    <TableCell>{rate.province}</TableCell>
                    <TableCell>{rate.tier}</TableCell>
                    <TableCell>
                      {rate.min_credit_score} - {rate.max_credit_score}
                    </TableCell>
                    <TableCell className="font-semibold">{rate.rate}%</TableCell>
                    <TableCell>{new Date(rate.effective_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Badge variant={rate.is_active ? 'default' : 'secondary'}>
                        {rate.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => openEditDialog(rate)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            if (confirm('Delete this interest rate?')) {
                              deleteMutation.mutate(rate.id)
                            }
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-center text-gray-500 py-8">No interest rates found. Create your first rate!</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Current Rate Structure</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {PROVINCES.map((province) => {
              const provinceRates = rates?.filter(r => r.province === province.code && r.is_active) || []
              if (provinceRates.length === 0) return null

              return (
                <div key={province.code} className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-2">{province.name}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                    {CREDIT_TIERS.map((tier) => {
                      const rate = provinceRates.find(r => r.tier === tier.name)
                      return (
                        <div key={tier.name} className="text-center">
                          <p className="text-xs text-gray-600">{tier.name}</p>
                          <p className="text-lg font-bold">{rate ? `${rate.rate}%` : 'N/A'}</p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
