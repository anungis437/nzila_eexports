import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Shield, 
  Smartphone, 
  Key,
  CheckCircle,
  XCircle,
  Loader2,
  Copy,
  Lock
} from 'lucide-react'
import api from '../lib/api'

export default function TwoFactorSettings() {
  const queryClient = useQueryClient()
  const [showTOTPSetup, setShowTOTPSetup] = useState(false)
  const [showSMSSetup, setShowSMSSetup] = useState(false)
  const [totpCode, setTotpCode] = useState('')
  const [smsCode, setSmsCode] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [disablePassword, setDisablePassword] = useState('')
  const [qrData, setQrData] = useState<any>(null)

  // Fetch 2FA status
  const { data: status, isLoading } = useQuery({
    queryKey: ['2fa-status'],
    queryFn: () => api.get2FAStatus(),
  })

  // Enable TOTP
  const enableTOTPMutation = useMutation({
    mutationFn: () => api.enableTOTP(),
    onSuccess: (data) => {
      setQrData(data)
      setShowTOTPSetup(true)
    },
  })

  // Verify TOTP
  const verifyTOTPMutation = useMutation({
    mutationFn: (code: string) => api.verifyTOTP(code),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['2fa-status'] })
      setShowTOTPSetup(false)
      setTotpCode('')
      setQrData(null)
    },
  })

  // Disable 2FA
  const disable2FAMutation = useMutation({
    mutationFn: (password: string) => api.disable2FA(password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['2fa-status'] })
      setDisablePassword('')
    },
  })

  // Send SMS
  const sendSMSMutation = useMutation({
    mutationFn: (phone: string) => api.sendSMSCode(phone),
  })

  // Verify SMS
  const verifySMSMutation = useMutation({
    mutationFn: (code: string) => api.verifySMSCode(code),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['2fa-status'] })
      setShowSMSSetup(false)
      setSmsCode('')
      setPhoneNumber('')
    },
  })

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Shield className="h-6 w-6 text-blue-600" />
          Two-Factor Authentication
        </h2>
        <p className="text-slate-600 mt-1">
          Add an extra layer of security to your account
        </p>
      </div>

      {/* Status Card */}
      <div className="bg-white border border-slate-200 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
              status?.two_factor_enabled ? 'bg-green-100' : 'bg-slate-100'
            }`}>
              {status?.two_factor_enabled ? (
                <CheckCircle className="h-6 w-6 text-green-600" />
              ) : (
                <Shield className="h-6 w-6 text-slate-400" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">
                {status?.two_factor_enabled ? '2FA Enabled' : '2FA Disabled'}
              </h3>
              <p className="text-sm text-slate-600">
                {status?.two_factor_enabled 
                  ? 'Your account is protected with 2FA'
                  : 'Enable 2FA to secure your account'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* TOTP (Authenticator App) */}
      <div className="bg-white border border-slate-200 rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Key className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Authenticator App</h3>
              <p className="text-sm text-slate-600 mt-1">
                Use an app like Google Authenticator or Authy
              </p>
              {status?.methods?.totp && (
                <div className="mt-2 inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                  <CheckCircle className="h-3 w-3" />
                  Enabled
                </div>
              )}
            </div>
          </div>
        </div>

        {!showTOTPSetup && !status?.methods?.totp && (
          <button
            onClick={() => enableTOTPMutation.mutate()}
            disabled={enableTOTPMutation.isPending}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {enableTOTPMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Setting up...
              </>
            ) : (
              <>
                <Key className="h-4 w-4" />
                Enable Authenticator App
              </>
            )}
          </button>
        )}

        {showTOTPSetup && qrData && (
          <div className="space-y-4 mt-4 p-4 bg-slate-50 rounded-lg">
            <div className="text-center">
              <div className="inline-block p-4 bg-white rounded-lg border-2 border-slate-200">
                <img src={qrData.qr_code} alt="QR Code" className="w-48 h-48" />
              </div>
              <p className="text-sm text-slate-600 mt-3">
                Scan this QR code with your authenticator app
              </p>
            </div>

            <div className="bg-white p-3 rounded border border-slate-200">
              <div className="flex items-center justify-between gap-2">
                <div className="flex-1">
                  <p className="text-xs text-slate-500 mb-1">Manual Entry Key:</p>
                  <code className="text-sm text-slate-900 font-mono break-all">
                    {qrData.secret}
                  </code>
                </div>
                <button
                  onClick={() => copyToClipboard(qrData.secret)}
                  className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition-colors"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Enter the 6-digit code from your app
              </label>
              <input
                type="text"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg text-center text-2xl tracking-widest font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                maxLength={6}
              />
            </div>

            {verifyTOTPMutation.isError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-900">Verification Failed</p>
                  <p className="text-sm text-red-700 mt-1">Invalid code. Please try again.</p>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => {
                  setShowTOTPSetup(false)
                  setQrData(null)
                  setTotpCode('')
                }}
                className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => verifyTOTPMutation.mutate(totpCode)}
                disabled={totpCode.length !== 6 || verifyTOTPMutation.isPending}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {verifyTOTPMutation.isPending ? 'Verifying...' : 'Verify & Enable'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* SMS Verification */}
      <div className="bg-white border border-slate-200 rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
              <Smartphone className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">SMS Verification</h3>
              <p className="text-sm text-slate-600 mt-1">
                Receive codes via text message
              </p>
              {status?.phone_verified && (
                <div className="mt-2 inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                  <CheckCircle className="h-3 w-3" />
                  Phone Verified
                </div>
              )}
            </div>
          </div>
        </div>

        {!showSMSSetup && !status?.phone_verified && (
          <button
            onClick={() => setShowSMSSetup(true)}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
          >
            <Smartphone className="h-4 w-4" />
            Setup SMS Verification
          </button>
        )}

        {showSMSSetup && (
          <div className="space-y-4 mt-4 p-4 bg-slate-50 rounded-lg">
            {!sendSMSMutation.isSuccess ? (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="+1234567890"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Include country code (e.g., +1 for US)
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setShowSMSSetup(false)
                      setPhoneNumber('')
                    }}
                    className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => sendSMSMutation.mutate(phoneNumber)}
                    disabled={!phoneNumber || sendSMSMutation.isPending}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    {sendSMSMutation.isPending ? 'Sending...' : 'Send Code'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-900">Code Sent!</p>
                    <p className="text-sm text-green-700 mt-1">
                      Check your phone for the verification code
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Enter verification code
                  </label>
                  <input
                    type="text"
                    value={smsCode}
                    onChange={(e) => setSmsCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="000000"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg text-center text-2xl tracking-widest font-mono focus:outline-none focus:ring-2 focus:ring-green-500"
                    maxLength={6}
                  />
                </div>

                <button
                  onClick={() => verifySMSMutation.mutate(smsCode)}
                  disabled={smsCode.length !== 6 || verifySMSMutation.isPending}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {verifySMSMutation.isPending ? 'Verifying...' : 'Verify Phone'}
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Disable 2FA */}
      {status?.two_factor_enabled && (
        <div className="bg-white border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
              <Lock className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Disable 2FA</h3>
              <p className="text-sm text-slate-600 mt-1">
                Remove two-factor authentication from your account
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Enter your password to confirm
              </label>
              <input
                type="password"
                value={disablePassword}
                onChange={(e) => setDisablePassword(e.target.value)}
                placeholder="Password"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>

            <button
              onClick={() => disable2FAMutation.mutate(disablePassword)}
              disabled={!disablePassword || disable2FAMutation.isPending}
              className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {disable2FAMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Disabling...
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4" />
                  Disable Two-Factor Authentication
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
