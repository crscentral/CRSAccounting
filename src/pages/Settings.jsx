import { useEffect, useState } from 'react'
import { User, Shield, Bell, Users, Plus, Trash2, ShieldCheck, Check, X } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'

const ROLES = ['owner', 'admin', 'accountant', 'viewer']

export default function Settings() {
  const { user, activeCompany, activeRole, can, refreshCompanies } = useAuth()
  const [tab, setTab] = useState('profile')
  const [fullName, setFullName] = useState('')
  const [fyMonth, setFyMonth] = useState(1)
  const [favorites, setFavorites] = useState(['USD', 'THB', 'INR'])
  const [members, setMembers] = useState([])
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('viewer')
  const [pendingCompanies, setPendingCompanies] = useState([])
  const isPlatformAdmin = user?.email === 'crscentral.rm@gmail.com'

  useEffect(() => {
    if (activeCompany) {
      setFyMonth(activeCompany.fiscal_year_start_month)
      loadMembers()
      loadSettings()
    }
  }, [activeCompany])

  async function loadSettings() {
    const { data } = await supabase.from('company_settings').select('*').eq('company_id', activeCompany.id).maybeSingle()
    if (data) setFavorites(data.favorite_currencies)
  }

  async function loadMembers() {
    const { data } = await supabase.from('company_members').select('*, profile:user_profiles(full_name, email)').eq('company_id', activeCompany.id)
    setMembers(data || [])
  }

  useEffect(() => {
    if (tab === 'admin' && isPlatformAdmin) loadPendingCompanies()
  }, [tab])

  async function loadPendingCompanies() {
    const { data } = await supabase.from('companies').select('*').eq('approval_status', 'pending').order('created_at')
    setPendingCompanies(data || [])
  }

  async function decideCompany(companyId, approve) {
    const { error } = await supabase.rpc('approve_company', { p_company_id: companyId, p_approve: approve })
    if (error) { alert(error.message); return }
    loadPendingCompanies()
  }

  async function saveProfile() {
    await supabase.from('user_profiles').update({ full_name: fullName }).eq('id', user.id)
  }

  async function saveCompanySettings() {
    await supabase.from('companies').update({ fiscal_year_start_month: fyMonth }).eq('id', activeCompany.id)
    await supabase.from('company_settings').upsert({ company_id: activeCompany.id, favorite_currencies: favorites }, { onConflict: 'company_id' })
    refreshCompanies()
  }

  async function inviteMember() {
    if (!inviteEmail) return
    // Creates a pending invite (no user_id yet). The invited person must sign up with
    // this exact email in CRS Accounting; a database trigger then auto-attaches them
    // to this company with the assigned role on their first sign-up.
    const { error } = await supabase.from('company_members').insert({
      company_id: activeCompany.id, invited_email: inviteEmail.trim().toLowerCase(), role: inviteRole,
    })
    if (error) { alert(error.message); return }
    setInviteEmail('')
    loadMembers()
  }

  function toggleFavorite(code) {
    setFavorites(f => f.includes(code) ? f.filter(c => c !== code) : [...f, code])
  }

  if (!activeCompany) return null

  const cards = [
    { key: 'profile', label: 'Profile', desc: 'Manage your account information', icon: User },
    { key: 'security', label: 'Security', desc: 'Password and authentication', icon: Shield },
    { key: 'notifications', label: 'Notifications', desc: 'Email and app notifications', icon: Bell },
    { key: 'access', label: 'User Access & Permissions', desc: 'Invite users and set their access permissions', icon: Users },
    ...(isPlatformAdmin ? [{ key: 'admin', label: 'Platform Admin', desc: 'Approve new companies signing up', icon: ShieldCheck }] : []),
  ]

  return (
    <div>
      <PageHeader title="Settings" subtitle="Manage your account and application preferences" />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cards.map(c => (
          <button key={c.key} onClick={() => setTab(c.key)}
            className={`text-left rounded-xl border p-5 ${tab === c.key ? 'border-navy-400 bg-navy-50' : 'border-slate-200 bg-white'}`}>
            <c.icon size={18} className="text-navy-600 mb-2" />
            <div className="font-semibold text-slate-800 text-sm">{c.label}</div>
            <div className="text-xs text-slate-400 mt-1">{c.desc}</div>
          </button>
        ))}
      </div>

      {tab === 'profile' && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 max-w-lg">
          <h3 className="font-semibold text-slate-700 mb-4">User Profile</h3>
          <div className="flex items-center gap-3 mb-4">
            <div className="h-14 w-14 rounded-full bg-navy-100 text-navy-700 flex items-center justify-center font-bold text-xl">
              {(fullName || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div>
              <div className="font-semibold text-slate-800">{fullName || user?.email}</div>
              <div className="text-xs text-slate-400">{user?.email}</div>
              <div className="text-xs text-navy-600 capitalize">{activeRole} role</div>
            </div>
          </div>
          <label className="text-xs font-medium text-slate-500">Full Name</label>
          <input value={fullName} onChange={e => setFullName(e.target.value)} placeholder={user?.email}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm mb-4" />
          <button onClick={saveProfile} className="bg-navy-800 text-white text-sm font-medium px-4 py-2 rounded-lg">Save Changes</button>
        </div>
      )}

      {tab === 'security' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 max-w-lg text-sm text-slate-500">
          Password changes are handled via Supabase Auth's secure reset flow. Use "Forgot password" on the login screen to receive a reset link by email.
        </div>
      )}

      {tab === 'notifications' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 max-w-lg text-sm text-slate-500">
          Email notification preferences (overdue invoice alerts, daily FX rate updates) — coming soon.
        </div>
      )}

      {tab === 'access' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 max-w-2xl">
            <h3 className="font-semibold text-slate-700 mb-4">Fiscal Year & Currency Defaults</h3>
            <div className="grid sm:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-xs font-medium text-slate-500">Fiscal Year Start Month (default YTD)</label>
                <select value={fyMonth} onChange={e => setFyMonth(Number(e.target.value))}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                  {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                </select>
              </div>
            </div>
            <label className="text-xs font-medium text-slate-500">Favorite Currencies (shown at top of every switcher)</label>
            <div className="flex flex-wrap gap-2 mt-2 mb-4">
              {CURRENCY_LIST.slice(0, 20).map(c => (
                <button key={c.code} onClick={() => toggleFavorite(c.code)}
                  className={`px-2.5 py-1 rounded-full text-xs font-medium border ${favorites.includes(c.code) ? 'bg-navy-600 text-white border-navy-600' : 'bg-white border-slate-200 text-slate-600'}`}>
                  {c.code}
                </button>
              ))}
            </div>
            {can(['owner', 'admin']) && (
              <button onClick={saveCompanySettings} className="bg-navy-800 text-white text-sm font-medium px-4 py-2 rounded-lg">Save</button>
            )}
          </div>

          {can(['owner', 'admin']) && (
            <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
              <h3 className="font-semibold text-slate-700 mb-4">Invite a User</h3>
              <p className="text-xs text-slate-500 mb-4 bg-slate-50 border border-slate-100 rounded-lg p-3">
                Use this to add someone to <strong>this company</strong> (e.g. your accountant, a teammate). They'll only see this company's data, scoped by the role you pick.
                <br /><br />
                <strong>Selling or handing this software to someone else entirely?</strong> Don't invite them here — just share the site link. When they sign up, they'll get their own "Create Your Company" screen and become Owner of a completely separate, isolated company — invisible to you and everyone else, with no invite needed.
              </p>
              <div className="flex flex-col sm:flex-row gap-2 mb-5">
                <input value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="email@example.com" type="email"
                  className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                <select value={inviteRole} onChange={e => setInviteRole(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
                  {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
                <button onClick={inviteMember} className="flex items-center justify-center gap-1.5 bg-navy-600 text-white text-sm font-medium px-4 py-2 rounded-lg">
                  <Plus size={16} /> Invite
                </button>
              </div>

              <h4 className="text-sm font-semibold text-slate-600 mb-2">Current Members</h4>
              <div className="space-y-2">
                {members.map(m => (
                  <div key={m.id} className="flex items-center justify-between text-sm border-b border-slate-50 py-2">
                    <div>
                      <div className="text-slate-700">{m.profile?.email || m.invited_email}</div>
                      <div className="text-xs text-slate-400 capitalize">{m.role}{!m.profile && ' • invited, pending sign-up'}</div>
                    </div>
                    <button className="text-slate-300 hover:text-red-500"><Trash2 size={15} /></button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      {tab === 'admin' && isPlatformAdmin && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 max-w-2xl">
          <h3 className="font-semibold text-slate-700 mb-1">Pending Company Approvals</h3>
          <p className="text-xs text-slate-500 mb-4">
            New companies created via self-service sign-up wait here until you approve them.
          </p>
          {pendingCompanies.length === 0 ? (
            <p className="text-sm text-slate-400">No companies awaiting approval.</p>
          ) : (
            <div className="space-y-2">
              {pendingCompanies.map(c => (
                <div key={c.id} className="flex items-center justify-between border border-slate-100 rounded-lg px-3 py-2.5">
                  <div>
                    <div className="text-sm font-medium text-slate-700">{c.name}</div>
                    <div className="text-xs text-slate-400">{c.base_currency} • created {new Date(c.created_at).toLocaleDateString()}</div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => decideCompany(c.id, true)} className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium px-3 py-1.5 rounded-lg"><Check size={13} /> Approve</button>
                    <button onClick={() => decideCompany(c.id, false)} className="flex items-center gap-1 border border-red-200 text-red-600 text-xs font-medium px-3 py-1.5 rounded-lg"><X size={13} /> Reject</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
