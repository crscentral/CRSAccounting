import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add import
imports = """import TallyReports from './pages/TallyMode/TallyReports'
import TallyDashboardEmbed from './pages/TallyMode/TallyDashboardEmbed'"""
content = content.replace("import TallyReports from './pages/TallyMode/TallyReports'", imports)

# Replace the messy inline route
old_route = """        <Route path="dashboard" element={
          <div className="bg-[#f8f9fa] w-full h-full overflow-y-auto">
            <div className="bg-white border-b p-2 flex justify-between items-center sticky top-0 z-10 shadow-sm">
              <span className="font-bold text-navy-700">Financial Dashboard (Tally Embed)</span>
              <button onClick={() => window.location.href='#/tally-mode'} className="bg-slate-200 px-2 py-1 text-xs border border-slate-400">ESC: Gateway</button>
            </div>
            <div className="p-4"><Dashboard /></div>
          </div>
        } />"""
new_route = """        <Route path="dashboard" element={<TallyDashboardEmbed />} />"""
content = content.replace(old_route, new_route)

with open('src/App.jsx', 'w') as f:
    f.write(content)
