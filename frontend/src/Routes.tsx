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
const Favorites = lazy(() => import('./pages/Favorites.tsx'))
const Compare = lazy(() => import('./pages/Compare.tsx'))
const SavedSearches = lazy(() => import('./pages/SavedSearches.tsx'))
const Settings = lazy(() => import('./pages/Settings.tsx'))
const Payments = lazy(() => import('./pages/Payments.tsx'))
const AuditTrail = lazy(() => import('./pages/AuditTrail.tsx'))
const AdminTest = lazy(() => import('./pages/AdminTest.tsx'))
const Analytics = lazy(() => import('./pages/Analytics.tsx'))
const BrokerAnalytics = lazy(() => import('./pages/BrokerAnalytics.tsx'))
const MessagesPage = lazy(() => import('./pages/MessagesPage.tsx'))
const VehicleHistory = lazy(() => import('./pages/VehicleHistory.tsx'))
const Financing = lazy(() => import('./pages/Financing.tsx'))
const DealerVerification = lazy(() => import('./pages/DealerVerification.tsx'))
const SecurityDashboard = lazy(() => import('./pages/SecurityDashboard.tsx'))
const ComplianceDashboard = lazy(() => import('./pages/ComplianceDashboard.tsx'))
const ShipmentSecurityDashboard = lazy(() => import('./pages/ShipmentSecurityDashboard.tsx'))
const InterestRateManagement = lazy(() => import('./pages/InterestRateManagement.tsx'))
const InvoiceManagement = lazy(() => import('./pages/InvoiceManagement.tsx'))
const TransactionViewer = lazy(() => import('./pages/TransactionViewer.tsx'))
const InspectionManagement = lazy(() => import('./pages/InspectionManagement.tsx'))
const OfferManagement = lazy(() => import('./pages/OfferManagement.tsx'))
const TierManagement = lazy(() => import('./pages/TierManagement.tsx'))
const ReviewModeration = lazy(() => import('./pages/ReviewModeration.tsx'))

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
            <Route path="favorites" element={<Favorites />} />
            <Route path="compare" element={<Compare />} />
            <Route path="saved-searches" element={<SavedSearches />} />
            <Route path="messages" element={<MessagesPage />} />
            <Route path="leads" element={<Leads />} />
            <Route path="deals" element={<Deals />} />
            <Route path="commissions" element={<Commissions />} />
            <Route path="shipments" element={<Shipments />} />
            <Route path="documents" element={<Documents />} />
            <Route path="payments" element={<Payments />} />
            <Route path="audit-trail" element={<AuditTrail />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="broker-analytics" element={<BrokerAnalytics />} />
            <Route path="vehicle-history/:vehicleId" element={<VehicleHistory />} />
            <Route path="financing" element={<Financing />} />
            <Route path="dealer-verification" element={<DealerVerification />} />
            <Route path="security" element={<SecurityDashboard />} />
            <Route path="compliance" element={<ComplianceDashboard />} />
            <Route path="shipment-security" element={<ShipmentSecurityDashboard />} />
            <Route path="interest-rates" element={<InterestRateManagement />} />
            <Route path="invoices" element={<InvoiceManagement />} />
            <Route path="transactions" element={<TransactionViewer />} />
            <Route path="inspections" element={<InspectionManagement />} />
            <Route path="offers" element={<OfferManagement />} />
            <Route path="tiers" element={<TierManagement />} />
            <Route path="review-moderation" element={<ReviewModeration />} />
            <Route path="settings" element={<Settings />} />
            <Route path="admin-test" element={<AdminTest />} />
          </Route>
        </RouterRoutes>
      </Suspense>
    </ErrorBoundary>
  )
}
