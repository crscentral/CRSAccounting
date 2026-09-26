import re

with open('src/pages/TallyMode/TallyGateway.jsx', 'r') as f:
    content = f.read()

content = content.replace("path: '/'", "path: '/tally-mode/dashboard'")

with open('src/pages/TallyMode/TallyGateway.jsx', 'w') as f:
    f.write(content)

with open('src/App.jsx', 'r') as f:
    content = f.read()
    
# Import Dashboard (already imported at top, so just add route)
route_old = """        <Route path="display" element={<TallyReports />} />"""
route_new = """        <Route path="display" element={<TallyReports />} />
        <Route path="dashboard" element={
          <div className="bg-[#f8f9fa] w-full h-full overflow-y-auto">
            <div className="bg-white border-b p-2 flex justify-between items-center sticky top-0 z-10 shadow-sm">
              <span className="font-bold text-navy-700">Financial Dashboard (Tally Embed)</span>
              <button onClick={() => window.location.href='#/tally-mode'} className="bg-slate-200 px-2 py-1 text-xs border border-slate-400">ESC: Gateway</button>
            </div>
            <div className="p-4"><Dashboard /></div>
          </div>
        } />"""
content = content.replace(route_old, route_new)

with open('src/App.jsx', 'w') as f:
    f.write(content)
