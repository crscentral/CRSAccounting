import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './lib/AuthContext'
import AppShell from './components/AppShell'
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
  const { session, loading, companies } = useAuth()
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">Loading CRS Accounting…</div>
  }
  if (!session) return <Navigate to="/login" replace />
  if (companies.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 text-center">
        <div>
          <h2 className="font-semibold text-slate-700 mb-2">No company access yet</h2>
          <p className="text-sm text-slate-500 max-w-sm">
            Your account isn't linked to a company yet. Ask your CRS Accounting Owner/Admin to invite your email
            ({/* shown via context if needed */}) from Settings → User Access & Permissions.
          </p>
        </div>
      </div>
    )
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
