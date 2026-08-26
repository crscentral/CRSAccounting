import { useState } from 'react'
import { Building2, LogOut } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { CURRENCY_LIST } from '../lib/currencies'
import logo from '../assets/crs-logo.png'

/**
 * Shown to any authenticated user who isn't yet a member of any company. This is the
 * self-service onboarding path: anyone who signs up (a friend, a client you're selling
 * this software to, etc.) lands here and can create their OWN company, becoming its
 * Owner with zero visibility into any other company's data (enforced by the same RLS
 * rules that protect every company in the system). They can then invite their own
 * team from their own Settings page, completely independently.
 */
export default function CreateFirstCompanyScreen() {
  const { user, signOut, refreshCompanies, switchCompany } = useAuth()
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ name: '', base_currency: 'USD', fiscal_year_start_month: 1 })
  const [error, setError] = useState('')

  function update(field, value) { setForm(f => ({ ...f, [field]: value })) }

  async function handleCreate(e) {
    e.preventDefault()
    setError('')
    if (!form.name.trim()) { setError('Company name is required.'); return }
    setCreating(true)
    try {
      const { data: newCompanyId, error: rpcError } = await supabase.rpc('create_company_with_owner', {
        p_name: form.name.trim(),
        p_base_currency: form.base_currency,
        p_fiscal_year_start_month: form.fiscal_year_start_month,
      })
      if (rpcError) throw rpcError
      await refreshCompanies()
      switchCompany(newCompanyId)
    } catch (err) {
      setError(err.message || 'Something went wrong creating your company.')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <img src={logo} alt="CRS Accounting" className="h-14 w-14 object-contain mb-3" />
          <h1 className="text-xl font-bold text-navy-700">Welcome to CRS Accounting</h1>
          <p className="text-xs text-slate-400 mt-1">Signed in as {user?.email}</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-2 mb-1">
            <Building2 size={18} className="text-navy-600" />
            <h2 className="font-semibold text-slate-800">Create Your Company</h2>
          </div>
          <p className="text-xs text-slate-500 mb-4">
            Set up your own company's books. You'll be the Owner, fully independent from any other
            company on this platform — you can invite your own accountants and team afterward from Settings.
          </p>

          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="text-xs font-medium text-slate-500">Company Name *</label>
              <input required value={form.name} onChange={e => update('name', e.target.value)}
                className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Acme Hospitality Group" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-500">Base Currency</label>
                <select value={form.base_currency} onChange={e => update('base_currency', e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                  {CURRENCY_LIST.slice(0, 20).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">Fiscal Year Start</label>
                <select value={form.fiscal_year_start_month} onChange={e => update('fiscal_year_start_month', Number(e.target.value))}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                  {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                </select>
              </div>
            </div>

            {error && <p className="text-xs text-red-600">{error}</p>}

            <button disabled={creating} type="submit"
              className="w-full bg-navy-600 hover:bg-navy-700 text-white font-medium rounded-lg py-2.5 text-sm disabled:opacity-60">
              {creating ? 'Creating…' : 'Create My Company'}
            </button>
          </form>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-slate-400">
            Trying to join an existing company instead? Ask that company's Owner or Admin to invite
            <span className="font-medium text-slate-500"> {user?.email} </span>
            from their Settings → User Access & Permissions page.
          </p>
        </div>

        <button onClick={signOut} className="w-full flex items-center justify-center gap-1.5 text-xs text-slate-400 hover:text-slate-600 mt-4">
          <LogOut size={13} /> Log Out
        </button>
      </div>
    </div>
  )
}
