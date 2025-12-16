import React, { Component, ReactNode } from 'react'
import * as Sentry from '@sentry/react'
import { AlertCircle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

/**
 * Error Boundary Component
 * Catches React errors and displays fallback UI instead of crashing the app
 * Logs errors to Sentry for monitoring
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error to Sentry
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack,
        },
      },
    })

    // Update state with error details
    this.setState({
      error,
      errorInfo,
    })

    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
            <div className="flex items-center justify-center w-16 h-16 mx-auto bg-red-100 rounded-full mb-4">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>

            <h1 className="text-2xl font-bold text-center text-slate-900 mb-2">
              Oops! Something went wrong
            </h1>

            <p className="text-slate-600 text-center mb-6">
              We're sorry for the inconvenience. An unexpected error has occurred.
              {import.meta.env.DEV && this.state.error && (
                <>
                  <br />
                  <span className="text-sm text-red-600 mt-2 block">
                    {this.state.error.toString()}
                  </span>
                </>
              )}
            </p>

            <div className="space-y-3">
              <button
                onClick={this.handleReset}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </button>

              <button
                onClick={() => (window.location.href = '/')}
                className="w-full px-4 py-3 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors font-medium"
              >
                Go to Homepage
              </button>
            </div>

            {import.meta.env.DEV && this.state.errorInfo && (
              <details className="mt-6 text-xs text-slate-500">
                <summary className="cursor-pointer font-medium">
                  Error Details (Dev Only)
                </summary>
                <pre className="mt-2 p-3 bg-slate-50 rounded overflow-auto max-h-40">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
