import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './lib/AuthContext'
import AppShell from './components/AppShell'
import CreateFirstCompanyScreen from './components/CreateFirstCompanyScreen'
import PendingApprovalScreen from './components/PendingApprovalScreen'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Companies from './pages/Companies'
import ChartOfAccounts from './pages/ChartOfAccounts'
import Contacts from './pages/Contacts'
import SalesInvoices from './pages/SalesInvoices'
import PurchaseInvoices from './pages/PurchaseInvoices'
import Transactions from './pages/Transactions'
import Ledger from './pages/Ledger'
import Analytics from './pages/Analytics'
import FinancialPerformance from './pages/FinancialPerformance'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import RestaurantRevenue from './pages/RestaurantRevenue'
import CapitalTransactions from './pages/CapitalTransactions'
import Comparison from './pages/Comparison'
import HistoricalImport from './pages/HistoricalImport'
import PortfolioDashboard from './pages/PortfolioDashboard'
import HotelOccupancyStats from './pages/HotelOccupancyStats'
import HotelBudget from './pages/HotelBudget'
import HotelRevenue from './pages/HotelRevenue'
import HotelExpenses from './pages/HotelExpenses'
import HotelGuestInvoices from './pages/HotelGuestInvoices'

function Gate({ children }) {
  const { session, loading, companies, activeCompany } = useAuth()
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading CRS Accounting…</div>
  }
  if (!session) return <Navigate to="/login" replace />
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
    <Routes>
      <Route path="/login" element={session ? <Navigate to="/" replace /> : <Login />} />
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
        <Route path="/hotel-revenue" element={<HotelRevenue />} />
        <Route path="/hotel-expenses" element={<HotelExpenses />} />
        <Route path="/hotel-guest-invoices" element={<HotelGuestInvoices />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/ledger" element={<Ledger />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/financial-performance" element={<FinancialPerformance />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/restaurant-revenue" element={<RestaurantRevenue />} />
        <Route path="/capital" element={<CapitalTransactions />} />
        <Route path="/compare" element={<Comparison />} />
        <Route path="/import" element={<HistoricalImport />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter basename="/CRSAccounting">
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
