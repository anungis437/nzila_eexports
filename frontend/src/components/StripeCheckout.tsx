import { useState } from 'react'
import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle, XCircle, Loader2, CreditCard } from 'lucide-react'
import api from '../lib/api'

// Initialize Stripe (replace with your actual publishable key from environment)
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY || '')

interface CheckoutFormProps {
  amount: number
  currency: string
  dealId?: number
  shipmentId?: number
  paymentFor: 'deposit' | 'final_payment' | 'full_payment' | 'shipping_fee'
  onSuccess?: () => void
  onCancel?: () => void
}

function CheckoutForm({ amount, currency, dealId, shipmentId, paymentFor, onSuccess, onCancel }: CheckoutFormProps) {
  const stripe = useStripe()
  const elements = useElements()
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const createPaymentIntentMutation = useMutation({
    mutationFn: (data: any) => api.createPaymentIntent(data),
  })

  const confirmPaymentMutation = useMutation({
    mutationFn: (intentId: string) => api.confirmPayment({ payment_intent_id: intentId }),
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!stripe || !elements) {
      setError('Stripe has not loaded yet. Please try again.')
      return
    }

    setProcessing(true)
    setError(null)

    try {
      // Step 1: Create payment intent on the backend
      const intentResponse = await createPaymentIntentMutation.mutateAsync({
        amount: amount,
        currency: currency,
        payment_for: paymentFor,
        deal_id: dealId,
        shipment_id: shipmentId,
      })

      const clientSecret = intentResponse.client_secret

      if (!clientSecret) {
        throw new Error('Failed to create payment intent')
      }

      // Step 2: Confirm payment with Stripe
      const cardElement = elements.getElement(CardElement)
      if (!cardElement) {
        throw new Error('Card element not found')
      }

      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
        },
      })

      if (stripeError) {
        throw new Error(stripeError.message)
      }

      // Step 3: Confirm with backend
      if (paymentIntent?.id) {
        await confirmPaymentMutation.mutateAsync(paymentIntent.id)
      }

      setSuccess(true)
      setTimeout(() => {
        onSuccess?.()
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'An error occurred while processing your payment.')
    } finally {
      setProcessing(false)
    }
  }

  if (success) {
    return (
      <div className="text-center py-8">
        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <CheckCircle className="h-10 w-10 text-green-600" />
        </div>
        <h3 className="text-xl font-semibold text-slate-900 mb-2">Payment Successful!</h3>
        <p className="text-slate-600">Your payment has been processed successfully.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Payment Summary */}
      <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-slate-600">Amount</span>
          <span className="text-2xl font-bold text-slate-900">
            {currency} {amount.toFixed(2)}
          </span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-600">Payment Type</span>
          <span className="text-slate-900 capitalize">{paymentFor.replace('_', ' ')}</span>
        </div>
      </div>

      {/* Card Input */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Card Details
        </label>
        <div className="border border-slate-300 rounded-lg p-4 bg-white hover:border-blue-400 transition-colors">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#1e293b',
                  '::placeholder': {
                    color: '#94a3b8',
                  },
                },
                invalid: {
                  color: '#ef4444',
                },
              },
            }}
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-900">Payment Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={processing}
            className="flex-1 px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={!stripe || processing}
          className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {processing ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <CreditCard className="h-5 w-5" />
              Pay {currency} {amount.toFixed(2)}
            </>
          )}
        </button>
      </div>

      {/* Security Notice */}
      <p className="text-xs text-center text-slate-500">
        🔒 Your payment is secured by Stripe. We never store your card details.
      </p>
    </form>
  )
}

export default function StripeCheckout(props: CheckoutFormProps) {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm {...props} />
    </Elements>
  )
}
