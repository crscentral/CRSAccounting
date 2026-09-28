import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

old_footer = """        <button
          onClick={signOut}
          className="flex items-center gap-3 px-3 lg:px-5 py-3 text-sm text-slate-500 hover:text-red-600 border-t border-slate-100"
        >
          <LogOut size={18} />
          <span className="hidden lg:inline">Log Out</span>
        </button>"""

new_footer = """        <div className="mt-auto border-t border-slate-100 flex flex-col">
          <button
            onClick={signOut}
            className="flex items-center gap-3 px-3 lg:px-5 py-3 text-sm text-slate-500 hover:text-red-600"
          >
            <LogOut size={18} />
            <span className="hidden lg:inline">Log Out</span>
          </button>
          <div className="hidden lg:flex flex-col gap-1 px-3 lg:px-5 py-4 text-[10px] text-slate-400 text-center bg-slate-50/50 border-t border-slate-100">
            <div className="flex justify-center gap-3">
              <NavLink to="/data-security" className="hover:text-slate-600 transition-colors">Data Security</NavLink>
              <NavLink to="/privacy" className="hover:text-slate-600 transition-colors">Privacy Policy</NavLink>
            </div>
            <div className="mt-2 text-[9px] leading-tight">
              CRS Accounting is owned by<br/>
              <span className="font-medium text-slate-500">CRS Central - A Unit of CRS Chauhan Private Limited.</span>
            </div>
          </div>
        </div>"""

content = content.replace(old_footer, new_footer)

old_mobile_footer = """            <button onClick={signOut} className="flex items-center gap-3 px-5 py-4 text-sm text-slate-500 border-t border-slate-100">
              <LogOut size={18} /> Log Out
            </button>"""

new_mobile_footer = """            <div className="mt-auto border-t border-slate-100 flex flex-col">
              <button onClick={signOut} className="flex items-center gap-3 px-5 py-4 text-sm text-slate-500">
                <LogOut size={18} /> Log Out
              </button>
              <div className="flex flex-col gap-1 px-5 py-4 text-[10px] text-slate-400 text-center bg-slate-50/50 border-t border-slate-100">
                <div className="flex justify-center gap-3">
                  <NavLink to="/data-security" onClick={() => setDrawerOpen(false)} className="hover:text-slate-600 transition-colors">Data Security</NavLink>
                  <NavLink to="/privacy" onClick={() => setDrawerOpen(false)} className="hover:text-slate-600 transition-colors">Privacy Policy</NavLink>
                </div>
                <div className="mt-2 text-[9px] leading-tight">
                  CRS Accounting is owned by<br/>
                  <span className="font-medium text-slate-500">CRS Central - A Unit of CRS Chauhan Private Limited.</span>
                </div>
              </div>
            </div>"""

content = content.replace(old_mobile_footer, new_mobile_footer)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
