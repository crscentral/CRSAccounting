import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add import
imports = """import TallyPlaceholder from './pages/TallyMode/TallyPlaceholder'
import TallyMasterCreate from './pages/TallyMode/TallyMasterCreate'"""
content = content.replace("import TallyPlaceholder from './pages/TallyMode/TallyPlaceholder'", imports)

# Add route
route_old = """        <Route path="create" element={<TallyPlaceholder />} />"""
route_new = """        <Route path="create" element={<TallyMasterCreate />} />"""
content = content.replace(route_old, route_new)

with open('src/App.jsx', 'w') as f:
    f.write(content)
