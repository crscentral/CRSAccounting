import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

code = code.replace(
    'const [inviteRole, setInviteRole] = useState(\'viewer\')',
    'const [inviteRole, setInviteRole] = useState(\'viewer\')\n  const [inviteProducts, setInviteProducts] = useState([\'basic\', \'hotel\', \'restaurant\'])'
)

code = code.replace(
    'company_id: activeCompany.id, invited_email: inviteEmail.trim().toLowerCase(), role: inviteRole,',
    'company_id: activeCompany.id, invited_email: inviteEmail.trim().toLowerCase(), role: inviteRole, products: inviteProducts,'
)

new_ui = """              <div className="flex flex-col sm:flex-row gap-2 mb-2">
                <input value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="email@example.com" type="email"
                  className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
                <select value={inviteRole} onChange={e => setInviteRole(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
                  {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
                <button onClick={inviteMember} disabled={inviting || inviteProducts.length === 0} className="flex items-center justify-center gap-1.5 bg-navy-600 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-60">
                  <Plus size={16} /> {inviting ? 'Sending…' : 'Invite'}
                </button>
              </div>
              
              <div className="mb-5 text-sm text-slate-700 bg-slate-50 p-3 border border-slate-200 rounded-lg">
                <div className="font-semibold mb-2">Access Granted:</div>
                <div className="flex flex-col sm:flex-row gap-4">
                  <label className="flex items-center gap-1.5 cursor-pointer">
                    <input type="checkbox" className="rounded text-navy-600 border-slate-300"
                           checked={inviteProducts.includes('basic')}
                           onChange={(e) => setInviteProducts(prev => e.target.checked ? [...prev, 'basic'] : prev.filter(p => p !== 'basic'))} />
                    CRS Basic Accounting
                  </label>
                  <label className="flex items-center gap-1.5 cursor-pointer">
                    <input type="checkbox" className="rounded text-navy-600 border-slate-300"
                           checked={inviteProducts.includes('hotel')}
                           onChange={(e) => setInviteProducts(prev => e.target.checked ? [...prev, 'hotel'] : prev.filter(p => p !== 'hotel'))} />
                    CRS Hotel Accounting
                  </label>
                  <label className="flex items-center gap-1.5 cursor-pointer">
                    <input type="checkbox" className="rounded text-navy-600 border-slate-300"
                           checked={inviteProducts.includes('restaurant')}
                           onChange={(e) => setInviteProducts(prev => e.target.checked ? [...prev, 'restaurant'] : prev.filter(p => p !== 'restaurant'))} />
                    CRS Restaurant Accounting
                  </label>
                </div>
              </div>"""

code = re.sub(
    r'              <div className="flex flex-col sm:flex-row gap-2 mb-5">.*?              </div>',
    new_ui,
    code,
    flags=re.DOTALL
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
