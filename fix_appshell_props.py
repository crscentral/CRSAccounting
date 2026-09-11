import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Pass toggleSidebar prop
content = content.replace(
    '<ActiveCompanyBar\n          companies={companies} activeCompany={activeCompany}',
    '<ActiveCompanyBar\n          toggleSidebar={() => setSidebarExpanded(e => !e)}\n          companies={companies} activeCompany={activeCompany}'
)

# Receive toggleSidebar prop in ActiveCompanyBar
content = content.replace(
    'function ActiveCompanyBar({ companies, activeCompany, switchCompany, activeRole, activeProduct, availableProducts, switchProduct }) {',
    'function ActiveCompanyBar({ toggleSidebar, companies, activeCompany, switchCompany, activeRole, activeProduct, availableProducts, switchProduct }) {'
)

# Fix the button
content = content.replace(
    '<button onClick={() => setSidebarExpanded(e => !e)} className="text-white hover:text-slate-300"><Menu size={18} /></button>',
    '<button onClick={toggleSidebar} className="text-white hover:text-slate-300"><Menu size={18} /></button>'
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
