import { useState } from 'react'
import { Clock, XCircle, LogOut, RefreshCw } from 'lucide-react'
import { useAuth } from '../lib/AuthContext'
import logo from '../assets/crs-logo.png'

/**
 * Shown to a company's Owner when their company's approval_status is 'pending' or
 * 'rejected' -- blocks access to the rest of the app until the platform admin
 * (crscentral.rm@gmail.com) approves it via Settings -> Platform Admin.
 */
export default function PendingApprovalScreen() {
  const { user, activeCompany, signOut, refreshCompanies } = useAuth()
  const [checking, setChecking] = useState(false)
  const rejected = activeCompany?.approval_status === 'rejected'

  async function handleCheckStatus() {
    setChecking(true)
    try {
      await refreshCompanies()
    } finally {
      setTimeout(() => setChecking(false), 500)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center">
        <div className="flex flex-col items-center mb-6">
          <img src={logo} alt="CRS Accounting" className="h-14 w-14 object-contain mb-3" />
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          {rejected ? (
            <>
              <XCircle size={36} className="text-red-500 mx-auto mb-3" />
              <h2 className="font-semibold text-slate-800 mb-1">Access Not Approved</h2>
              <p className="text-sm text-slate-500">
                Your company <strong>{activeCompany?.name}</strong> was not approved for access.
                Please contact the CRS Accounting administrator for details.
              </p>
            </>
          ) : (
            <>
              <Clock size={36} className="text-gold-500 mx-auto mb-3" />
              <h2 className="font-semibold text-slate-800 mb-1">Awaiting Approval</h2>
              <p className="text-sm text-slate-500">
                Your company <strong>{activeCompany?.name}</strong> has been created and is waiting
                for approval from the CRS Accounting administrator. You'll get access as soon as
                it's approved.
              </p>
            </>
          )}

          {!rejected && (
            <button
              onClick={handleCheckStatus}
              disabled={checking}
              className="mt-5 w-full flex items-center justify-center gap-2 bg-navy-50 hover:bg-navy-100 text-navy-700 font-medium rounded-lg py-2 text-sm border border-navy-200 transition-colors"
            >
              <RefreshCw size={14} className={checking ? 'animate-spin' : ''} />
              {checking ? 'Checking Status…' : 'Check Approval Status'}
            </button>
          )}

          <p className="text-xs text-slate-400 mt-4">Signed in as {user?.email}</p>
        </div>

        <button onClick={signOut} className="w-full flex items-center justify-center gap-1.5 text-xs text-slate-400 hover:text-slate-600 mt-4">
          <LogOut size={13} /> Log Out
        </button>
      </div>
    </div>
  )
}
