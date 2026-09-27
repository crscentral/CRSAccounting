import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# 1. Desktop Sidebar
old_aside = """      <aside className={`hidden md:flex md:flex-col border-r border-slate-200 bg-white shrink-0 transition-all duration-300 ${sidebarExpanded ? 'w-20 lg:w-64' : 'w-0 overflow-hidden border-r-0'}`}>
        <div className="h-16 flex items-center gap-2 px-3 lg:px-5 border-b border-slate-100">"""
new_aside = """      <aside className={`hidden md:flex md:flex-col border-r border-slate-200 bg-white shrink-0 transition-all duration-300 ${sidebarExpanded ? 'w-20 lg:w-64' : 'w-0 overflow-hidden border-r-0'}`}>
        <div className="w-full shrink-0" style={{ height: 'env(safe-area-inset-top)' }} />
        <div className="h-16 flex items-center gap-2 px-3 lg:px-5 border-b border-slate-100 shrink-0">"""
content = content.replace(old_aside, new_aside)

# 2. Mobile Drawer Sidebar
old_drawer = """          <div className="absolute left-0 top-0 bottom-0 w-72 bg-white shadow-xl flex flex-col">
            <div className="h-16 flex items-center justify-between px-4 border-b border-slate-100">"""
new_drawer = """          <div className="absolute left-0 top-0 bottom-0 w-72 bg-white shadow-xl flex flex-col">
            <div className="w-full shrink-0" style={{ height: 'env(safe-area-inset-top)' }} />
            <div className="h-16 flex items-center justify-between px-4 border-b border-slate-100 shrink-0">"""
content = content.replace(old_drawer, new_drawer)

# 3. Mobile Header
old_mobile_header = """        <header className="md:hidden h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4 sticky top-0 z-30">
          <button onClick={() => setDrawerOpen(true)}><Menu size={22} className="text-navy-700" /></button>
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-2">
              <img src={logo} alt="" className="h-6 w-6 object-contain" />
              <span className="font-semibold text-navy-700 text-sm">{activeCompany?.name || 'CRS Accounting'}</span>
            </div>
            {availableProducts.length > 0 && (
              <span className="text-[10px] text-slate-400 -mt-0.5">{PRODUCT_LABELS[activeProduct]}</span>
            )}
          </div>
          <div className="w-6" />
        </header>"""
new_mobile_header = """        <header className="md:hidden bg-white border-b border-slate-200 sticky top-0 z-30 flex flex-col">
          <div className="w-full shrink-0" style={{ height: 'env(safe-area-inset-top)' }} />
          <div className="h-14 flex items-center justify-between px-4 shrink-0">
            <button onClick={() => setDrawerOpen(true)}><Menu size={22} className="text-navy-700" /></button>
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2">
                <img src={logo} alt="" className="h-6 w-6 object-contain" />
                <span className="font-semibold text-navy-700 text-sm">{activeCompany?.name || 'CRS Accounting'}</span>
              </div>
              {availableProducts.length > 0 && (
                <span className="text-[10px] text-slate-400 -mt-0.5">{PRODUCT_LABELS[activeProduct]}</span>
              )}
            </div>
            <div className="w-6" />
          </div>
        </header>"""
content = content.replace(old_mobile_header, new_mobile_header)

# 4. ActiveCompanyBar (Desktop Header)
old_acb = """  return (
    <div className="hidden md:flex items-center justify-between px-6 lg:px-8 h-11 bg-navy-700 text-white text-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <button onClick={toggleSidebar} className="text-white hover:text-slate-300"><Menu size={18} /></button>
      </div>"""
new_acb = """  return (
    <div className="hidden md:block sticky top-0 z-20 bg-navy-700 w-full">
      <div className="w-full shrink-0" style={{ height: 'env(safe-area-inset-top)' }} />
      <div className="flex items-center justify-between px-6 lg:px-8 h-11 text-white text-sm shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={toggleSidebar} className="text-white hover:text-slate-300"><Menu size={18} /></button>
      </div>"""
content = content.replace(old_acb, new_acb)

# 5. Make sure the div is properly closed for ActiveCompanyBar!
# Wait! ActiveCompanyBar was `div` then `div`... wait.
# Let's check how ActiveCompanyBar currently ends to see if the tag matches.
