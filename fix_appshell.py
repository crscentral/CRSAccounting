import re

def patch():
    with open('src/components/AppShell.jsx', 'r') as f:
        content = f.read()

    # Move Revenue & Occupancy right below Dashboard
    old_nav = """  { to: '/overview', label: 'All Companies', icon: LayoutGrid },
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/companies', label: 'Companies', icon: Building2 },
  { to: '/accounts', label: 'Chart of Accounts', icon: PieChart },
  { to: '/contacts', label: 'Customers & Suppliers', icon: Users },
  { to: '/sales-invoices', label: 'Sales Invoices', icon: FileCheck, products: ['basic'] },
  { to: '/purchase-invoices', label: 'Purchase Invoices', icon: FileText, products: ['basic'] },
  { to: '/hotel-stats', label: 'Revenue & Occupancy', icon: BedDouble, products: ['hotel'] },"""
    new_nav = """  { to: '/overview', label: 'All Companies', icon: LayoutGrid },
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/hotel-stats', label: 'Revenue & Occupancy', icon: BedDouble, products: ['hotel'] },
  { to: '/companies', label: 'Companies', icon: Building2 },
  { to: '/accounts', label: 'Chart of Accounts', icon: PieChart },
  { to: '/contacts', label: 'Customers & Suppliers', icon: Users },
  { to: '/sales-invoices', label: 'Sales Invoices', icon: FileCheck, products: ['basic'] },
  { to: '/purchase-invoices', label: 'Purchase Invoices', icon: FileText, products: ['basic'] },"""
    content = content.replace(old_nav, new_nav)
    
    # Make the company name bold in the sidebar
    old_company_name = """<span className={`${alwaysShowLabel ? 'block' : 'hidden lg:block'} text-sm font-medium text-slate-700 truncate`}>{activeCompany.name}</span>"""
    new_company_name = """<span className={`${alwaysShowLabel ? 'block' : 'hidden lg:block'} text-sm font-bold text-slate-800 truncate`}>{activeCompany.name}</span>"""
    content = content.replace(old_company_name, new_company_name)

    with open('src/components/AppShell.jsx', 'w') as f:
        f.write(content)
        print("Patched AppShell.jsx")

patch()
