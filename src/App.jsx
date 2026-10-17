import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './lib/AuthContext'
import { ErrorBoundary } from "./components/ErrorBoundary";
import AppShell from './components/AppShell'
import CreateFirstCompanyScreen from './components/CreateFirstCompanyScreen'
import PendingApprovalScreen from './components/PendingApprovalScreen'
import Login from './pages/Login'

function lazyWithRetry(componentImport) {
  return lazy(async () => {
    try {
      return await componentImport();
    } catch (error) {
      const msg = String(error?.message || '');
      const isChunkError =
        msg.includes('dynamically imported module') ||
        msg.includes('Failed to fetch') ||
        msg.includes('Loading chunk') ||
        msg.includes('Importing a module script failed') ||
        error?.name === 'ChunkLoadError';

      if (isChunkError) {
        const lastRetry = sessionStorage.getItem('crs_lazy_retry');
        const now = Date.now();
        if (!lastRetry || now - parseInt(lastRetry, 10) > 15000) {
          sessionStorage.setItem('crs_lazy_retry', String(now));
          if ('caches' in window) {
            try {
              await caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k))));
            } catch (e) {}
          }
          window.location.reload();
          return new Promise(() => {});
        }
      }
      throw error;
    }
  });
}

const Dashboard = lazyWithRetry(() => import('./pages/Dashboard'))
const Companies = lazyWithRetry(() => import('./pages/Companies'))
const ChartOfAccounts = lazyWithRetry(() => import('./pages/ChartOfAccounts'))
const Contacts = lazyWithRetry(() => import('./pages/Contacts'))
const SalesInvoices = lazyWithRetry(() => import('./pages/SalesInvoices'))
const PurchaseInvoices = lazyWithRetry(() => import('./pages/PurchaseInvoices'))
const Transactions = lazyWithRetry(() => import('./pages/Transactions'))
const Ledger = lazyWithRetry(() => import('./pages/Ledger'))
const Analytics = lazyWithRetry(() => import('./pages/Analytics'))
const FinancialPerformance = lazyWithRetry(() => import('./pages/FinancialPerformance'))
const Reports = lazyWithRetry(() => import('./pages/Reports'))
const Settings = lazyWithRetry(() => import('./pages/Settings'))
const RestaurantRevenue = lazyWithRetry(() => import('./pages/RestaurantRevenue'))
const RestaurantExpenses = lazyWithRetry(() => import('./pages/RestaurantExpenses'))
const CapitalTransactions = lazyWithRetry(() => import('./pages/CapitalTransactions'))
const Comparison = lazyWithRetry(() => import('./pages/Comparison'))
const HistoricalImport = lazyWithRetry(() => import('./pages/HistoricalImport'))
const PortfolioDashboard = lazyWithRetry(() => import('./pages/PortfolioDashboard'))
const HotelOccupancyStats = lazyWithRetry(() => import('./pages/HotelOccupancyStats'))
const HotelBudget = lazyWithRetry(() => import('./pages/HotelBudget'))
const HotelExpenseBudget = lazyWithRetry(() => import('./pages/HotelExpenseBudget'))
const HotelRevenue = lazyWithRetry(() => import('./pages/HotelRevenue'))
const HotelExpenses = lazyWithRetry(() => import('./pages/HotelExpenses'))
const HotelGuestInvoices = lazyWithRetry(() => import('./pages/HotelGuestInvoices'))
const DataSecurity = lazyWithRetry(() => import('./pages/DataSecurity'))
const PrivacyPolicy = lazyWithRetry(() => import('./pages/PrivacyPolicy'))

const TallyLayout = lazyWithRetry(() => import('./pages/TallyMode/TallyLayout'))
const TallyGateway = lazyWithRetry(() => import('./pages/TallyMode/TallyGateway'))
const TallyVouchers = lazyWithRetry(() => import('./pages/TallyMode/TallyVouchers'))
const TallyMasterCreate = lazyWithRetry(() => import('./pages/TallyMode/TallyMasterCreate'))
const TallyReports = lazyWithRetry(() => import('./pages/TallyMode/TallyReports'))
const TallyDashboardEmbed = lazyWithRetry(() => import('./pages/TallyMode/TallyDashboardEmbed'))

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
  if (!activeCompany) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading Company Details…</div>
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
