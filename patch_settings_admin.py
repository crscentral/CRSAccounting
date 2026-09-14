import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# Add states
states_search = "const [allCompanies, setAllCompanies] = useState([])"
states_replace = "const [allCompanies, setAllCompanies] = useState([])\n  const [allUsers, setAllUsers] = useState([])\n  const [loadingUsers, setLoadingUsers] = useState(false)"
code = code.replace(states_search, states_replace)

# Modify loadAllCompaniesProducts query
query_search = ".select('id, name, approval_status, company_products(product)')"
query_replace = ".select('id, name, email, approval_status, company_products(product), members:company_members(role, invited_email, profile:user_profiles(email, full_name))')"
code = code.replace(query_search, query_replace)

# Add loadAllUsers function and call it
effect_search = "if (tab === 'admin') {"
effect_replace = "if (tab === 'admin') {\n      loadAllUsers()"
code = code.replace(effect_search, effect_replace)

load_users_func = """
  async function loadAllUsers() {
    setLoadingUsers(true)
    const { data, error } = await supabase
      .from('user_profiles')
      .select('*')
      .order('created_at', { ascending: false })
    if (!error && data) setAllUsers(data)
    setLoadingUsers(false)
  }
"""
code = code.replace("async function loadAllCompaniesProducts() {", load_users_func + "\n  async function loadAllCompaniesProducts() {")

# Modify rendering in Company Products to show Owner Email
company_render_search = """<h4 className="text-sm font-semibold text-slate-800">{c.name}</h4>
                      <span className="text-xs text-slate-400 capitalize">{c.approval_status}</span>"""
company_render_replace = """<h4 className="text-sm font-semibold text-slate-800">{c.name}</h4>
                      <span className="text-xs text-slate-400 capitalize">
                        {c.approval_status} • Created by: {(() => {
                          const owner = c.members?.find(m => m.role === 'owner')
                          return owner?.profile?.email || owner?.invited_email || c.email || 'Unknown'
                        })()}
                      </span>"""
code = code.replace(company_render_search, company_render_replace)

# Add "Global Users" section at the bottom of the tab === 'admin'
admin_end_search = """          )}
        </div>
      )}
    </div>"""
admin_end_replace = """          )}

          <div className="mt-8">
            <h3 className="font-semibold text-slate-800 text-base mb-1">Global Users List</h3>
            <p className="text-xs text-slate-500 mb-4">
              All registered user accounts across the entire application. Use this to distinguish people from companies.
            </p>
            {loadingUsers ? (
              <p className="text-sm text-slate-400 py-4">Loading users…</p>
            ) : (
              <div className="space-y-2">
                {allUsers.map(u => (
                  <div key={u.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border border-slate-100 rounded-lg px-3 py-2.5">
                    <div>
                      <div className="text-sm font-medium text-slate-700">{u.full_name || 'No Name'}</div>
                      <div className="text-xs text-slate-500">{u.email}</div>
                    </div>
                    <div className="text-xs text-slate-400">
                      Joined {new Date(u.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
                {allUsers.length === 0 && <p className="text-sm text-slate-500 py-2">No users found.</p>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>"""
code = code.replace(admin_end_search, admin_end_replace)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
