with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

import re

# Find the start and end of ActiveCompanyBar
start_idx = content.find("function ActiveCompanyBar(")
if start_idx != -1:
    end_idx = content.find("function ProductSwitcher(", start_idx)
    
    new_acb = """function ActiveCompanyBar({ toggleSidebar, companies, activeCompany, switchCompany, activeRole, activeProduct, availableProducts, switchProduct }) {
  const [open, setOpen] = useState(false)
  if (!activeCompany) return null

  return (
    <div className="hidden md:block sticky top-0 z-20 bg-navy-700 w-full">
      <div className="w-full shrink-0" style={{ height: 'env(safe-area-inset-top)' }} />
      <div className="flex items-center justify-between px-6 lg:px-8 h-11 text-white text-sm shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={toggleSidebar} className="text-white hover:text-slate-300"><Menu size={18} /></button>
        </div>
        <div className="relative">
          <button
            onClick={() => companies.length > 1 && setOpen(o => !o)}
            className="flex items-center gap-2 font-medium"
          >
            <Building2 size={15} className="text-gold-300 shrink-0" />
            <span>Viewing: <span className="font-semibold">{activeCompany.name}</span></span>
            {companies.length > 1 && <ChevronDown size={14} className="text-navy-200" />}
          </button>
          {open && (
            <div className="absolute z-30 top-full left-0 mt-1 w-64 bg-white border border-slate-200 rounded-lg shadow-lg text-slate-700">
              {companies.map(({ company }) => (
                <button
                  key={company.id}
                  onClick={() => { switchCompany(company.id); setOpen(false) }}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-navy-50 truncate ${company.id === activeCompany.id ? 'font-semibold text-navy-700' : ''}`}
                >
                  {company.name}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center gap-3">
          <NavLink to="/tally-mode" className="text-[11px] text-navy-200 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors font-medium tracking-wide">Switch to Tally View</NavLink>
          <ProductSwitcher activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />
          {activeRole && (
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/10 capitalize">{activeRole}</span>
          )}
        </div>
      </div>
    </div>
  )
}

"""
    content = content[:start_idx] + new_acb + content[end_idx:]

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
