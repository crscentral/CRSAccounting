import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './lib/AuthContext'
import { ErrorBoundary } from "./components/ErrorBoundary";
import AppShell from './components/AppShell'
import CreateFirstCompanyScreen from './components/CreateFirstCompanyScreen'
import PendingApprovalScreen from './components/PendingApprovalScreen'
import Login from './pages/Login'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Companies = lazy(() => import('./pages/Companies'))
const ChartOfAccounts = lazy(() => import('./pages/ChartOfAccounts'))
const Contacts = lazy(() => import('./pages/Contacts'))
const SalesInvoices = lazy(() => import('./pages/SalesInvoices'))
const PurchaseInvoices = lazy(() => import('./pages/PurchaseInvoices'))
const Transactions = lazy(() => import('./pages/Transactions'))
const Ledger = lazy(() => import('./pages/Ledger'))
const Analytics = lazy(() => import('./pages/Analytics'))
const FinancialPerformance = lazy(() => import('./pages/FinancialPerformance'))
const Reports = lazy(() => import('./pages/Reports'))
const Settings = lazy(() => import('./pages/Settings'))
const RestaurantRevenue = lazy(() => import('./pages/RestaurantRevenue'))
const RestaurantExpenses = lazy(() => import('./pages/RestaurantExpenses'))
const CapitalTransactions = lazy(() => import('./pages/CapitalTransactions'))
const Comparison = lazy(() => import('./pages/Comparison'))
const HistoricalImport = lazy(() => import('./pages/HistoricalImport'))
const PortfolioDashboard = lazy(() => import('./pages/PortfolioDashboard'))
const HotelOccupancyStats = lazy(() => import('./pages/HotelOccupancyStats'))
const HotelBudget = lazy(() => import('./pages/HotelBudget'))
const HotelExpenseBudget = lazy(() => import('./pages/HotelExpenseBudget'))
const HotelRevenue = lazy(() => import('./pages/HotelRevenue'))
const HotelExpenses = lazy(() => import('./pages/HotelExpenses'))
const HotelGuestInvoices = lazy(() => import('./pages/HotelGuestInvoices'))
const DataSecurity = lazy(() => import('./pages/DataSecurity'))
const PrivacyPolicy = lazy(() => import('./pages/PrivacyPolicy'))

const TallyLayout = lazy(() => import('./pages/TallyMode/TallyLayout'))
const TallyGateway = lazy(() => import('./pages/TallyMode/TallyGateway'))
const TallyVouchers = lazy(() => import('./pages/TallyMode/TallyVouchers'))
const TallyMasterCreate = lazy(() => import('./pages/TallyMode/TallyMasterCreate'))
const TallyReports = lazy(() => import('./pages/TallyMode/TallyReports'))
const TallyDashboardEmbed = lazy(() => import('./pages/TallyMode/TallyDashboardEmbed'))

function PageLoader() {
  return (
    <div className="min-h-[250px] flex items-center justify-center text-slate-400 text-sm">
      <div className="animate-pulse">Loading…</div>
    </div>
  )
}

function Gate({ children }) {
  const { session, loading, loadingCompanies, companies, activeCompany } = useAuth()
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading CRS Accounting…</div>
  }
  if (!session) return <Navigate to="/login" replace />
  if (loadingCompanies) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading Companies…</div>
  }
  if (companies.length === 0) {
    return <CreateFirstCompanyScreen />
  }
  if (activeCompany?.approval_status === 'pending' || activeCompany?.approval_status === 'rejected') {
    return <PendingApprovalScreen />
  }
  return children
}

function AppRoutes() {
  const { session } = useAuth()
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={session ? <Navigate to="/" replace /> : <Login />} />
        <Route path="/tally-mode" element={<Gate><TallyLayout /></Gate>}>
          <Route index element={<TallyGateway />} />
          <Route path="vouchers" element={<TallyVouchers />} />
          <Route path="create" element={<TallyMasterCreate />} />
          <Route path="alter" element={<TallyReports />} />
          <Route path="banking" element={<TallyReports />} />
          <Route path="balance-sheet" element={<TallyReports />} />
          <Route path="pnl" element={<TallyReports />} />
          <Route path="ratios" element={<TallyReports />} />
          <Route path="display" element={<TallyReports />} />
          <Route path="dashboard" element={<TallyDashboardEmbed />} />
          <Route path="*" element={<TallyGateway />} />
        </Route>
        <Route element={<Gate><AppShell /></Gate>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/overview" element={<PortfolioDashboard />} />
          <Route path="/companies" element={<Companies />} />
          <Route path="/accounts" element={<ChartOfAccounts />} />
          <Route path="/contacts" element={<Contacts />} />
          <Route path="/sales-invoices" element={<SalesInvoices />} />
          <Route path="/purchase-invoices" element={<PurchaseInvoices />} />
          <Route path="/hotel-stats" element={<HotelOccupancyStats />} />
          <Route path="/hotel-budget" element={<HotelBudget />} />
          <Route path="/hotel-expense-budget" element={<HotelExpenseBudget />} />
          <Route path="/restaurant-budget" element={<HotelBudget />} />
          <Route path="/restaurant-expense-budget" element={<HotelExpenseBudget />} />
          <Route path="/hotel-revenue" element={<HotelRevenue />} />
          <Route path="/hotel-expenses" element={<HotelExpenses />} />
          <Route path="/hotel-guest-invoices" element={<HotelGuestInvoices />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/ledger" element={<Ledger />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/financial-performance" element={<FinancialPerformance />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/restaurant-revenue" element={<RestaurantRevenue />} />
          <Route path="/restaurant-expenses" element={<RestaurantExpenses />} />
          <Route path="/capital" element={<CapitalTransactions />} />
          <Route path="/compare" element={<Comparison />} />
          <Route path="/import" element={<HistoricalImport />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/data-security" element={<DataSecurity />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}

export default function App() {
  return (
    <BrowserRouter basename="/">
      <ErrorBoundary>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
          </ErrorBoundary>
    </BrowserRouter>
  )
}
