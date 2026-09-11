import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Pass toggleSidebar prop
content = content.replace(
    '<ActiveCompanyBar companies={companies} activeCompany={activeCompany} switchCompany={switchCompany} activeRole={activeRole} activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />',
    '<ActiveCompanyBar toggleSidebar={() => setSidebarExpanded(e => !e)} companies={companies} activeCompany={activeCompany} switchCompany={switchCompany} activeRole={activeRole} activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />'
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
