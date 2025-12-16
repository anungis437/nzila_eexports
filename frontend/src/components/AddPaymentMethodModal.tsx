import { useState } from 'react'
import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, XCircle, Loader2, CreditCard, X } from 'lucide-react'
import api from '../lib/api'

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY || '')

interface AddPaymentMethodFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

function AddPaymentMethodForm({ onSuccess, onCancel }: AddPaymentMethodFormProps) {
  const stripe = useStripe()
  const elements = useElements()
  const queryClient = useQueryClient()
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const createPaymentMethodMutation = useMutation({
    mutationFn: (token: string) => api.createPaymentMethod({ stripe_token: token, type: 'card' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['paymentMethods'] })
    },
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
      const cardElement = elements.getElement(CardElement)
      if (!cardElement) {
        throw new Error('Card element not found')
      }

      // Create payment method with Stripe
      const { error: stripeError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
      })

      if (stripeError) {
        throw new Error(stripeError.message)
      }

      if (!paymentMethod?.id) {
        throw new Error('Failed to create payment method')
      }

      // Save to backend
      await createPaymentMethodMutation.mutateAsync(paymentMethod.id)

      setSuccess(true)
      setTimeout(() => {
        onSuccess?.()
      }, 1500)
    } catch (err: any) {
      setError(err.message || 'An error occurred while adding your payment method.')
    } finally {
      setProcessing(false)
    }
  }

  if (success) {
    return (
      <div className="text-center py-8" role="status" aria-live="polite">
        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <CheckCircle className="h-10 w-10 text-green-600" aria-hidden="true" />
        </div>
        <h3 className="text-xl font-semibold text-slate-900 mb-2">Payment Method Added!</h3>
        <p className="text-slate-600">Your payment method has been saved successfully.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label 
          htmlFor="card-element" 
          id="card-label"
          className="block text-sm font-medium text-slate-700 mb-2"
        >
          Card Details
        </label>
        <div 
          id="card-element"
          className="border border-slate-300 rounded-lg p-4 bg-white hover:border-blue-400 transition-colors"
          role="group"
          aria-labelledby="card-label"
          aria-describedby="card-help"
        >
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
        <p id="card-help" className="text-xs text-slate-500 mt-2">
          Enter your card number, expiration date (MM/YY), and security code (CVV)
        </p>
      </div>

      {error && (
        <div 
          className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3"
          role="alert"
          aria-live="assertive"
        >
          <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-900">Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={processing}
            className="flex-1 px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
            aria-label="Cancel adding payment method"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={!stripe || processing}
          className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          aria-busy={processing}
          aria-label={processing ? 'Adding payment method...' : 'Add payment method'}
        >
          {processing ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
              Adding...
            </>
          ) : (
            <>
              <CreditCard className="h-5 w-5" aria-hidden="true" />
              Add Payment Method
            </>
          )}
        </button>
      </div>

      <p className="text-xs text-center text-slate-500" role="img" aria-label="Security information">
        🔒 Your card details are secured by Stripe. We never store your card information.
      </p>
    </form>
  )
}

interface AddPaymentMethodModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function AddPaymentMethodModal({ isOpen, onClose, onSuccess }: AddPaymentMethodModalProps) {
  if (!isOpen) return null

  const handleSuccess = () => {
    onSuccess?.()
    onClose()
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="payment-modal-title"
    >
      <div className="bg-white rounded-xl max-w-md w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 transition-colors"
          aria-label="Close payment method modal"
        >
          <X className="h-5 w-5" aria-hidden="true" />
        </button>

        <div className="mb-6">
          <h2 id="payment-modal-title" className="text-2xl font-bold text-slate-900">Add Payment Method</h2>
          <p className="text-slate-600 mt-1">Add a new card to your account</p>
        </div>

        <Elements stripe={stripePromise}>
          <AddPaymentMethodForm onSuccess={handleSuccess} onCancel={onClose} />
        </Elements>
      </div>
    </div>
  )
}
