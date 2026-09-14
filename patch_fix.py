import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# Fix the Owner Name replacement
old_html = """<div className="text-sm font-medium text-slate-700">{c.name}</div>
                      <div className="text-[11px] text-slate-400 capitalize">{c.approval_status}</div>"""
new_html = """<div className="text-sm font-medium text-slate-700">{c.name}</div>
                      <div className="text-[11px] text-slate-400 capitalize">
                        {c.approval_status} • Created by: {(() => {
                          const owner = c.members?.find(m => m.role === 'owner')
                          return owner?.profile?.email || owner?.invited_email || c.email || 'Unknown'
                        })()}
                      </div>"""
code = code.replace(old_html, new_html)

# Fix max-w-3xl for tab === 'admin'
old_max = "max-w-3xl"
# But we only want to change it for the admin tab container
# Let's find: <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 max-w-3xl">
# wait, there are multiple tabs.
code = code.replace(
    "{tab === 'admin' && isPlatformAdmin && (\n        <div className=\"bg-white rounded-xl border border-slate-200 p-4 sm:p-6 max-w-3xl\">",
    "{tab === 'admin' && isPlatformAdmin && (\n        <div className=\"bg-white rounded-xl border border-slate-200 p-4 sm:p-6 w-full\">"
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
