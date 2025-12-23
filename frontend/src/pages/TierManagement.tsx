import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Trophy, Plus, Edit, Trash2, Gift } from 'lucide-react'
import api from '@/lib/api'

interface BrokerTier {
  id: number
  name: string
  commission_percentage: string
  min_sales: number
  max_sales: number | null
  bonuses: TierBonus[]
  active_users_count: number
  is_active: boolean
}

interface DealerTier {
  id: number
  name: string
  commission_percentage: string
  min_purchases: number
  max_purchases: number | null
  bonuses: TierBonus[]
  active_users_count: number
  is_active: boolean
}

interface TierBonus {
  id: number
  name: string
  amount: string
  threshold: number
  description: string
}

export default function TierManagement() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [bonusDialogOpen, setBonusDialogOpen] = useState(false)
  const [editingTier, setEditingTier] = useState<BrokerTier | DealerTier | null>(null)
  const [tierType, setTierType] = useState<'broker' | 'dealer'>('broker')
  const [formData, setFormData] = useState<Partial<BrokerTier | DealerTier>>({})
  const [bonusFormData, setBonusFormData] = useState<Partial<TierBonus>>({})
  const queryClient = useQueryClient()

  const { data: brokerTiers } = useQuery<BrokerTier[]>({
    queryKey: ['broker-tiers'],
    queryFn: async () => {
      const response = await api.get('/api/commissions/broker-tiers/')
      return response.data
    }
  })

  const { data: dealerTiers } = useQuery<DealerTier[]>({
    queryKey: ['dealer-tiers'],
    queryFn: async () => {
      const response = await api.get('/api/commissions/dealer-tiers/')
      return response.data
    }
  })

  const createTierMutation = useMutation({
    mutationFn: async (data: Partial<BrokerTier | DealerTier>) => {
      const endpoint = tierType === 'broker' ? '/api/commissions/broker-tiers/' : '/api/commissions/dealer-tiers/'
      const response = await api.post(endpoint, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`${tierType}-tiers`] })
      setDialogOpen(false)
      setFormData({})
    }
  })

  const updateTierMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<BrokerTier | DealerTier> }) => {
      const endpoint = tierType === 'broker' ? `/api/commissions/broker-tiers/${id}/` : `/api/commissions/dealer-tiers/${id}/`
      const response = await api.patch(endpoint, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`${tierType}-tiers`] })
      setDialogOpen(false)
      setEditingTier(null)
      setFormData({})
    }
  })

  const deleteTierMutation = useMutation({
    mutationFn: async (id: number) => {
      const endpoint = tierType === 'broker' ? `/api/commissions/broker-tiers/${id}/` : `/api/commissions/dealer-tiers/${id}/`
      await api.delete(endpoint)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`${tierType}-tiers`] })
    }
  })

  const createBonusMutation = useMutation({
    mutationFn: async (data: Partial<TierBonus>) => {
      const response = await api.post('/api/commissions/bonuses/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['broker-tiers'] })
      queryClient.invalidateQueries({ queryKey: ['dealer-tiers'] })
      setBonusDialogOpen(false)
      setBonusFormData({})
    }
  })

  const handleSubmitTier = () => {
    if (editingTier) {
      updateTierMutation.mutate({ id: editingTier.id, data: formData })
    } else {
      createTierMutation.mutate(formData)
    }
  }

  const handleSubmitBonus = () => {
    createBonusMutation.mutate(bonusFormData)
  }

  const openCreateDialog = (type: 'broker' | 'dealer') => {
    setTierType(type)
    setEditingTier(null)
    setFormData({})
    setDialogOpen(true)
  }

  const openEditDialog = (tier: BrokerTier | DealerTier, type: 'broker' | 'dealer') => {
    setTierType(type)
    setEditingTier(tier)
    setFormData(tier)
    setDialogOpen(true)
  }

  const handleDeleteTier = (id: number, type: 'broker' | 'dealer') => {
    if (confirm('Delete this tier? Users will be unassigned.')) {
      setTierType(type)
      deleteTierMutation.mutate(id)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Trophy className="h-8 w-8 text-yellow-600" />
          Tier Management
        </h1>
        <p className="text-gray-600 mt-1">Manage broker and dealer commission tiers and bonuses</p>
      </div>

      <Tabs defaultValue="broker">
        <TabsList>
          <TabsTrigger value="broker">Broker Tiers</TabsTrigger>
          <TabsTrigger value="dealer">Dealer Tiers</TabsTrigger>
        </TabsList>

        <TabsContent value="broker" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Broker Commission Tiers</CardTitle>
                <Button onClick={() => openCreateDialog('broker')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Broker Tier
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {brokerTiers && brokerTiers.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Tier Name</TableHead>
                      <TableHead>Commission %</TableHead>
                      <TableHead>Sales Range</TableHead>
                      <TableHead>Active Users</TableHead>
                      <TableHead>Bonuses</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {brokerTiers.map((tier) => (
                      <TableRow key={tier.id}>
                        <TableCell className="font-medium">{tier.name}</TableCell>
                        <TableCell className="font-bold text-green-600">{tier.commission_percentage}%</TableCell>
                        <TableCell>
                          {tier.min_sales} - {tier.max_sales || '∞'}
                        </TableCell>
                        <TableCell>{tier.active_users_count}</TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {tier.bonuses.slice(0, 2).map((bonus) => (
                              <Badge key={bonus.id} variant="outline" className="text-xs">
                                ${bonus.amount}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={tier.is_active ? 'default' : 'secondary'}>
                            {tier.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline" onClick={() => openEditDialog(tier, 'broker')}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleDeleteTier(tier.id, 'broker')}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-center text-gray-500 py-8">No broker tiers found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dealer" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Dealer Commission Tiers</CardTitle>
                <Button onClick={() => openCreateDialog('dealer')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Dealer Tier
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {dealerTiers && dealerTiers.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Tier Name</TableHead>
                      <TableHead>Commission %</TableHead>
                      <TableHead>Purchase Range</TableHead>
                      <TableHead>Active Users</TableHead>
                      <TableHead>Bonuses</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dealerTiers.map((tier) => (
                      <TableRow key={tier.id}>
                        <TableCell className="font-medium">{tier.name}</TableCell>
                        <TableCell className="font-bold text-green-600">{tier.commission_percentage}%</TableCell>
                        <TableCell>
                          {tier.min_purchases} - {tier.max_purchases || '∞'}
                        </TableCell>
                        <TableCell>{tier.active_users_count}</TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {tier.bonuses.slice(0, 2).map((bonus) => (
                              <Badge key={bonus.id} variant="outline" className="text-xs">
                                ${bonus.amount}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={tier.is_active ? 'default' : 'secondary'}>
                            {tier.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline" onClick={() => openEditDialog(tier, 'dealer')}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleDeleteTier(tier.id, 'dealer')}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-center text-gray-500 py-8">No dealer tiers found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Tier Bonuses</CardTitle>
            <Dialog open={bonusDialogOpen} onOpenChange={setBonusDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Gift className="h-4 w-4 mr-2" />
                  Add Bonus
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Tier Bonus</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Bonus Name</Label>
                    <Input
                      value={bonusFormData.name || ''}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBonusFormData({ ...bonusFormData, name: e.target.value })}
                      placeholder="e.g., Quarter Milestone"
                    />
                  </div>
                  <div>
                    <Label>Amount ($)</Label>
                    <Input
                      type="number"
                      value={bonusFormData.amount || ''}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBonusFormData({ ...bonusFormData, amount: e.target.value })}
                      placeholder="e.g., 5000"
                    />
                  </div>
                  <div>
                    <Label>Threshold (Sales/Purchases)</Label>
                    <Input
                      type="number"
                      value={bonusFormData.threshold || ''}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBonusFormData({ ...bonusFormData, threshold: parseInt(e.target.value) })}
                      placeholder="e.g., 50"
                    />
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Textarea
                      value={bonusFormData.description || ''}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setBonusFormData({ ...bonusFormData, description: e.target.value })}
                      placeholder="Describe the bonus criteria..."
                    />
                  </div>
                  <Button onClick={handleSubmitBonus} disabled={createBonusMutation.isPending}>
                    Create Bonus
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">Bonuses are automatically applied when users reach tier thresholds</p>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingTier ? 'Edit' : 'Create'} {tierType === 'broker' ? 'Broker' : 'Dealer'} Tier</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Tier Name</Label>
              <Input
                value={formData.name || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Bronze, Silver, Gold"
              />
            </div>
            <div>
              <Label>Commission Percentage</Label>
              <Input
                type="number"
                step="0.01"
                value={formData.commission_percentage || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, commission_percentage: e.target.value })}
                placeholder="e.g., 5.00"
              />
            </div>
            <div>
              <Label>Minimum {tierType === 'broker' ? 'Sales' : 'Purchases'}</Label>
              <Input
                type="number"
                value={(formData as BrokerTier).min_sales || (formData as DealerTier).min_purchases || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                  const key = tierType === 'broker' ? 'min_sales' : 'min_purchases'
                  setFormData({ ...formData, [key]: parseInt(e.target.value) })
                }}
                placeholder="e.g., 0"
              />
            </div>
            <div>
              <Label>Maximum {tierType === 'broker' ? 'Sales' : 'Purchases'} (optional)</Label>
              <Input
                type="number"
                value={(formData as BrokerTier).max_sales || (formData as DealerTier).max_purchases || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                  const key = tierType === 'broker' ? 'max_sales' : 'max_purchases'
                  setFormData({ ...formData, [key]: parseInt(e.target.value) || null })
                }}
                placeholder="Leave empty for unlimited"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_active !== false}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, is_active: e.target.checked })}
                id="is_active"
                aria-label="Set tier as active"
              />
              <Label htmlFor="is_active">Active</Label>
            </div>
            <Button onClick={handleSubmitTier} disabled={createTierMutation.isPending || updateTierMutation.isPending}>
              {editingTier ? 'Update' : 'Create'} Tier
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
