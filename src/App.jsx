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
        <Route path="/companies" element={<Companies />} />
        <Route path="/accounts" element={<ChartOfAccounts />} />
        <Route path="/contacts" element={<Contacts />} />
        <Route path="/sales-invoices" element={<SalesInvoices />} />
        <Route path="/purchase-invoices" element={<PurchaseInvoices />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/ledger" element={<Ledger />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/financial-performance" element={<FinancialPerformance />} />
        <Route path="/reports" element={<Reports />} />
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
