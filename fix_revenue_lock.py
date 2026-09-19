import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Add Lock and Unlock icons from lucide-react
if 'Lock' not in code:
    code = code.replace("import { DollarSign", "import { Lock, Unlock, DollarSign")

# Change PageHeader props
old_header = """      <PageHeader
        title="Daily Revenue Collection"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {can(['owner', 'admin']) && (
              <button onClick={() => {
                const newVal = !isLocked
                setIsLocked(newVal)
                supabase.from('hotel_settings').upsert({ company_id: activeCompany.id, product: activeProduct, manual_revenue_locked: newVal }).then()
              }} className="flex items-center gap-1.5 border border-amber-300 bg-amber-50 text-amber-700 text-sm font-medium px-3 py-2 rounded-lg hover:bg-amber-100">
                {isLocked ? '🔒 Unlock Page' : '🔓 Lock Page'}
              </button>
            )}
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>"""

new_header = """      <PageHeader
        title={
          <div className="flex items-center gap-3">
            Daily Revenue Collection
            {can(['owner', 'admin']) && (
              <button 
                onClick={() => {
                  const newVal = !isLocked
                  setIsLocked(newVal)
                  supabase.from('hotel_settings').upsert({ company_id: activeCompany.id, product: activeProduct, manual_revenue_locked: newVal }).then()
                }} 
                className={`p-1.5 rounded-lg border transition-colors ${isLocked ? 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100' : 'bg-emerald-50 border-emerald-200 text-emerald-600 hover:bg-emerald-100'}`}
                title={isLocked ? "Page is Locked (Click to Unlock)" : "Page is Unlocked (Click to Lock)"}
              >
                {isLocked ? <Lock size={18} /> : <Unlock size={18} />}
              </button>
            )}
          </div>
        }
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400 shrink-0">
              Download Report
            </button>"""

code = code.replace(old_header, new_header)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
