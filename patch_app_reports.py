import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add import
imports = """import TallyMasterCreate from './pages/TallyMode/TallyMasterCreate'
import TallyReports from './pages/TallyMode/TallyReports'"""
content = content.replace("import TallyMasterCreate from './pages/TallyMode/TallyMasterCreate'", imports)
content = content.replace("import TallyPlaceholder from './pages/TallyMode/TallyPlaceholder'\\n", "")


# Replace routes
old_routes = """        <Route path="alter" element={<TallyPlaceholder />} />
        <Route path="banking" element={<TallyPlaceholder />} />
        <Route path="balance-sheet" element={<TallyPlaceholder />} />
        <Route path="pnl" element={<TallyPlaceholder />} />
        <Route path="ratios" element={<TallyPlaceholder />} />
        <Route path="display" element={<TallyPlaceholder />} />"""

new_routes = """        <Route path="alter" element={<TallyReports />} />
        <Route path="banking" element={<TallyReports />} />
        <Route path="balance-sheet" element={<TallyReports />} />
        <Route path="pnl" element={<TallyReports />} />
        <Route path="ratios" element={<TallyReports />} />
        <Route path="display" element={<TallyReports />} />"""

content = content.replace(old_routes, new_routes)

with open('src/App.jsx', 'w') as f:
    f.write(content)
