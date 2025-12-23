import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BadgeCheck, 
  Shield, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Upload,
  Award,
  Loader2,
  AlertCircle
} from 'lucide-react'
import axios from 'axios'
import { useAuth } from '@/contexts/AuthContext'
import { useState } from 'react'

interface DealerLicense {
  id: number
  license_type: string
  license_type_display: string
  license_number: string
  issuing_authority: string
  province: string
  issue_date: string
  expiry_date: string
  status: string
  status_display: string
  is_expired: boolean
  expires_soon: boolean
  days_until_expiry: number
  document?: string
}

interface DealerVerification {
  id: number
  status: string
  status_display: string
  badge: string
  badge_display: string
  trust_score: number
  business_name: string
  business_number: string
  years_in_business: number
  has_insurance: boolean
  insurance_provider?: string
  total_sales: number
  average_rating: string
  total_reviews: number
  license_verified: boolean
  insurance_verified: boolean
  business_verified: boolean
  identity_verified: boolean
  address_verified: boolean
  verification_percentage: number
}

export default function DealerVerification() {
  const { user } = useAuth()

  const { data: verification, isLoading: loadingVerification } = useQuery<DealerVerification>({
    queryKey: ['dealer-verification'],
    queryFn: async () => {
      const token = localStorage.getItem('authToken')
      const response = await axios.get('/api/accounts/verification/dealer-verification/my_verification/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    enabled: !!user && (user.role === 'dealer' || user.role === 'admin')
  })

  const { data: licenses, isLoading: loadingLicenses } = useQuery<DealerLicense[]>({
    queryKey: ['dealer-licenses'],
    queryFn: async () => {
      const token = localStorage.getItem('authToken')
      const response = await axios.get('/api/accounts/verification/dealer-licenses/my_licenses/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    enabled: !!user && (user.role === 'dealer' || user.role === 'admin')
  })

  if (!user || (user.role !== 'dealer' && user.role !== 'admin')) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-yellow-800">Access Restricted</h2>
          <p className="text-yellow-700 mt-2">This page is only available for dealers.</p>
        </div>
      </div>
    )
  }

  if (loadingVerification || loadingLicenses) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    )
  }

  const getBadgeIcon = (badge: string) => {
    if (badge === 'gold') return '🥇'
    if (badge === 'silver') return '🥈'
    if (badge === 'bronze') return '🥉'
    return '⚪'
  }

  const getBadgeColor = (badge: string) => {
    if (badge === 'gold') return 'from-yellow-400 to-yellow-600'
    if (badge === 'silver') return 'from-gray-300 to-gray-500'
    if (badge === 'bronze') return 'from-orange-400 to-orange-600'
    return 'from-gray-200 to-gray-400'
  }

  const getStatusIcon = (status: string) => {
    if (status === 'verified') return <CheckCircle2 className="h-5 w-5 text-green-600" />
    if (status === 'pending') return <Clock className="h-5 w-5 text-yellow-600" />
    if (status === 'rejected') return <XCircle className="h-5 w-5 text-red-600" />
    return <AlertCircle className="h-5 w-5 text-gray-400" />
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <BadgeCheck className="h-8 w-8 text-blue-600" />
          Dealer Verification & Badges
        </h1>
        <p className="text-gray-600 mt-2">
          Build trust with buyers through official verification and licensing
        </p>
      </div>

      {/* Verification Status Card */}
      {verification && (
        <Card className={`mb-6 bg-gradient-to-br ${getBadgeColor(verification.badge)} text-white`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-3xl font-bold flex items-center gap-2">
                  <span className="text-4xl">{getBadgeIcon(verification.badge)}</span>
                  {verification.badge_display}
                </CardTitle>
                <p className="text-white/90 mt-2">
                  Trust Score: <span className="font-bold text-2xl">{verification.trust_score}/100</span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-white/90 text-sm">Status</p>
                <p className="font-semibold text-lg">{verification.status_display}</p>
                <div className="mt-2">
                  <div className="bg-white/20 rounded-full h-2 w-48">
                    <div 
                      className="bg-white rounded-full h-2 transition-all"
                      style={{ width: `${verification.verification_percentage}%` }}
                    />
                  </div>
                  <p className="text-xs text-white/80 mt-1">
                    {verification.verification_percentage}% Complete
                  </p>
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {/* Verification Criteria */}
      {verification && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          <Card>
            <CardContent className="p-4 text-center">
              <Shield className={`h-8 w-8 mx-auto mb-2 ${verification.license_verified ? 'text-green-600' : 'text-gray-400'}`} />
              <p className="text-sm font-medium">License</p>
              {verification.license_verified ? (
                <CheckCircle2 className="h-4 w-4 text-green-600 mx-auto mt-1" />
              ) : (
                <XCircle className="h-4 w-4 text-gray-400 mx-auto mt-1" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Shield className={`h-8 w-8 mx-auto mb-2 ${verification.insurance_verified ? 'text-green-600' : 'text-gray-400'}`} />
              <p className="text-sm font-medium">Insurance</p>
              {verification.insurance_verified ? (
                <CheckCircle2 className="h-4 w-4 text-green-600 mx-auto mt-1" />
              ) : (
                <XCircle className="h-4 w-4 text-gray-400 mx-auto mt-1" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <FileText className={`h-8 w-8 mx-auto mb-2 ${verification.business_verified ? 'text-green-600' : 'text-gray-400'}`} />
              <p className="text-sm font-medium">Business</p>
              {verification.business_verified ? (
                <CheckCircle2 className="h-4 w-4 text-green-600 mx-auto mt-1" />
              ) : (
                <XCircle className="h-4 w-4 text-gray-400 mx-auto mt-1" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <BadgeCheck className={`h-8 w-8 mx-auto mb-2 ${verification.identity_verified ? 'text-green-600' : 'text-gray-400'}`} />
              <p className="text-sm font-medium">Identity</p>
              {verification.identity_verified ? (
                <CheckCircle2 className="h-4 w-4 text-green-600 mx-auto mt-1" />
              ) : (
                <XCircle className="h-4 w-4 text-gray-400 mx-auto mt-1" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Award className={`h-8 w-8 mx-auto mb-2 ${verification.address_verified ? 'text-green-600' : 'text-gray-400'}`} />
              <p className="text-sm font-medium">Address</p>
              {verification.address_verified ? (
                <CheckCircle2 className="h-4 w-4 text-green-600 mx-auto mt-1" />
              ) : (
                <XCircle className="h-4 w-4 text-gray-400 mx-auto mt-1" />
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Business Information */}
      {verification && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>Business Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Business Name</p>
                <p className="font-semibold">{verification.business_name || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Business Number</p>
                <p className="font-semibold">{verification.business_number || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Years in Business</p>
                <p className="font-semibold">{verification.years_in_business} years</p>
              </div>
              {verification.has_insurance && verification.insurance_provider && (
                <div>
                  <p className="text-sm text-gray-600">Insurance Provider</p>
                  <p className="font-semibold">{verification.insurance_provider}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Total Sales</p>
                <p className="font-semibold text-2xl">{verification.total_sales}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Average Rating</p>
                <p className="font-semibold text-2xl flex items-center gap-1">
                  {parseFloat(verification.average_rating).toFixed(1)} ⭐
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Reviews</p>
                <p className="font-semibold">{verification.total_reviews}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Licenses */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Your Licenses & Certifications</CardTitle>
            <Button size="sm">
              <Upload className="mr-2 h-4 w-4" />
              Submit New License
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {licenses && licenses.length > 0 ? (
            <div className="space-y-4">
              {licenses.map((license) => (
                <div key={license.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(license.status)}
                      <div>
                        <p className="font-semibold">{license.license_type_display}</p>
                        <p className="text-sm text-gray-600">
                          {license.license_number} • {license.province}
                        </p>
                        <p className="text-xs text-gray-500">
                          Expires: {new Date(license.expiry_date).toLocaleDateString()}
                          {license.expires_soon && !license.is_expired && (
                            <span className="ml-2 text-orange-600 font-medium">
                              ⚠️ Expires in {license.days_until_expiry} days
                            </span>
                          )}
                          {license.is_expired && (
                            <span className="ml-2 text-red-600 font-medium">
                              ❌ Expired
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Badge 
                    variant={
                      license.status === 'verified' ? 'default' :
                      license.status === 'pending' ? 'secondary' :
                      'destructive'
                    }
                  >
                    {license.status_display}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No licenses submitted yet</p>
              <p className="text-sm text-gray-400 mt-1">
                Submit your OMVIC, AMVIC, or other provincial licenses to get verified
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Badge Benefits */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Badge Benefits</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg">
              <p className="font-semibold text-yellow-600 mb-2">🥇 Gold Badge</p>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• All 5 verifications complete</li>
                <li>• Premium search placement</li>
                <li>• "Verified Dealer" badge</li>
                <li>• Highest buyer trust</li>
              </ul>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="font-semibold text-gray-600 mb-2">🥈 Silver Badge</p>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• 3+ verifications complete</li>
                <li>• Enhanced search visibility</li>
                <li>• "Verified" badge</li>
                <li>• High buyer trust</li>
              </ul>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="font-semibold text-orange-600 mb-2">🥉 Bronze Badge</p>
              <ul className="text-sm space-y-1 text-gray-600">
                <li>• 2 verifications complete</li>
                <li>• Standard search placement</li>
                <li>• "Registered" badge</li>
                <li>• Basic buyer trust</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
