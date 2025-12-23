import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Shield, AlertCircle, CheckCircle, Package } from 'lucide-react'
import api from '@/lib/api'

interface SecurityRiskAssessment {
  id: number
  shipment: number
  assessment_date: string
  risk_level: string
  threat_factors: string
  vulnerability_assessment: string
  security_measures: string
  assessor: { id: number; username: string }
  status: string
}

interface SecurityIncident {
  id: number
  shipment: number
  incident_date: string
  incident_type: string
  severity: string
  description: string
  location: string
  reported_by: { id: number; username: string }
  investigation_status: string
  resolution: string
  resolved_at: string | null
}

interface PortVerification {
  id: number
  shipment: number
  port_name: string
  port_code: string
  verification_date: string
  security_level: string
  documentation_complete: boolean
  customs_clearance: boolean
  iso_compliant: boolean
  verified_by: { id: number; username: string }
  notes: string
}

export default function ShipmentSecurityDashboard() {
  const [activeTab, setActiveTab] = useState('risks')
  const queryClient = useQueryClient()

  const { data: risks } = useQuery<SecurityRiskAssessment[]>({
    queryKey: ['security-risks'],
    queryFn: async () => {
      const response = await api.get('/api/shipments/security-risks/')
      return response.data
    }
  })

  const { data: incidents } = useQuery<SecurityIncident[]>({
    queryKey: ['security-incidents'],
    queryFn: async () => {
      const response = await api.get('/api/shipments/security-incidents/')
      return response.data
    }
  })

  const { data: verifications } = useQuery<PortVerification[]>({
    queryKey: ['port-verifications'],
    queryFn: async () => {
      const response = await api.get('/api/shipments/port-verifications/')
      return response.data
    }
  })

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            Shipment Security Dashboard
          </h1>
          <p className="text-gray-600 mt-1">ISO 28000 Security Management</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Assessments</CardTitle>
            <AlertCircle className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{risks?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Incidents</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{incidents?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Port Verifications</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{verifications?.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="risks">Risk Assessments</TabsTrigger>
          <TabsTrigger value="incidents">Security Incidents</TabsTrigger>
          <TabsTrigger value="ports">Port Verifications</TabsTrigger>
        </TabsList>

        <TabsContent value="risks" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Security Risk Assessments</CardTitle>
                <Button>Create Assessment</Button>
              </div>
            </CardHeader>
            <CardContent>
              {risks && risks.length > 0 ? (
                <div className="space-y-3">
                  {risks.map((risk) => (
                    <div key={risk.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge>{risk.risk_level} Risk</Badge>
                            <Badge variant="outline">{risk.status}</Badge>
                          </div>
                          <p className="text-sm">Shipment #{risk.shipment}</p>
                          <p className="text-xs text-gray-600">{risk.threat_factors}</p>
                          <p className="text-xs text-gray-500">
                            Assessed by {risk.assessor.username} on {new Date(risk.assessment_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No risk assessments found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="incidents" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Security Incidents</CardTitle>
                <Button>Report Incident</Button>
              </div>
            </CardHeader>
            <CardContent>
              {incidents && incidents.length > 0 ? (
                <div className="space-y-3">
                  {incidents.map((incident) => (
                    <div key={incident.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="destructive">{incident.severity}</Badge>
                            <Badge variant="outline">{incident.incident_type}</Badge>
                          </div>
                          <p className="text-sm font-medium">{incident.description}</p>
                          <p className="text-xs text-gray-600">Location: {incident.location}</p>
                          <p className="text-xs text-gray-500">
                            Reported on {new Date(incident.incident_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No security incidents found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ports" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Port Verifications</CardTitle>
                <Button>Create Verification</Button>
              </div>
            </CardHeader>
            <CardContent>
              {verifications && verifications.length > 0 ? (
                <div className="space-y-3">
                  {verifications.map((verification) => (
                    <div key={verification.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge>{verification.port_name}</Badge>
                            <Badge variant="outline">{verification.port_code}</Badge>
                          </div>
                          <div className="flex gap-2 text-xs">
                            {verification.documentation_complete && <Badge variant="secondary">Docs Complete</Badge>}
                            {verification.customs_clearance && <Badge variant="secondary">Customs Cleared</Badge>}
                            {verification.iso_compliant && <Badge variant="secondary">ISO Compliant</Badge>}
                          </div>
                          <p className="text-xs text-gray-500">
                            Verified on {new Date(verification.verification_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No port verifications found</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
