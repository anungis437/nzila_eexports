import { Routes as RouterRoutes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { useAuth } from './contexts/AuthContext'
import ErrorBoundary from './components/ErrorBoundary'

// Lazy load components for code splitting
const Layout = lazy(() => import('./components/Layout.tsx'))
const Login = lazy(() => import('./pages/Login.tsx'))
const Dashboard = lazy(() => import('./pages/Dashboard.tsx'))
const Vehicles = lazy(() => import('./pages/Vehicles.tsx'))
const Leads = lazy(() => import('./pages/Leads.tsx'))
const Deals = lazy(() => import('./pages/Deals.tsx'))
const Commissions = lazy(() => import('./pages/Commissions.tsx'))
const Shipments = lazy(() => import('./pages/Shipments.tsx'))
const Documents = lazy(() => import('./pages/Documents.tsx'))
const BuyerPortal = lazy(() => import('./pages/BuyerPortal.tsx'))
const Settings = lazy(() => import('./pages/Settings.tsx'))
const Payments = lazy(() => import('./pages/Payments.tsx'))
const AuditTrail = lazy(() => import('./pages/AuditTrail.tsx'))

// Loading component for lazy routes
function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <LoadingFallback />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }

  return <>{children}</>
}

export default function Routes() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<LoadingFallback />}>
        <RouterRoutes>
          <Route path="/login" element={<Login />} />
          <Route path="/buyer-portal" element={<BuyerPortal />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="vehicles" element={<Vehicles />} />
            <Route path="leads" element={<Leads />} />
            <Route path="deals" element={<Deals />} />
            <Route path="commissions" element={<Commissions />} />
            <Route path="shipments" element={<Shipments />} />
            <Route path="documents" element={<Documents />} />
            <Route path="payments" element={<Payments />} />
            <Route path="audit-trail" element={<AuditTrail />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </RouterRoutes>
      </Suspense>
    </ErrorBoundary>
  )
}
