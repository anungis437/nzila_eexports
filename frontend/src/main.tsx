import React from 'react'
import ReactDOM from 'react-dom/client'
import * as Sentry from '@sentry/react'
import App from './App.tsx'
import './index.css'

// Initialize Sentry for error tracking
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: ENVIRONMENT,
    // Send default PII data (IP addresses, user info)
    sendDefaultPii: true,
    // Enable structured logging
    enableLogs: true,
    // Performance monitoring
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
      // Send console logs to Sentry
      Sentry.consoleLoggingIntegration({ levels: ['log', 'warn', 'error'] }),
    ],
    // Performance monitoring sample rate (10% of transactions)
    tracesSampleRate: 0.1,
    // Session replay sample rate
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  })
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
