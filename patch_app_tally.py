import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add import
imports = """import TallyVouchers from './pages/TallyMode/TallyVouchers'
import TallyPlaceholder from './pages/TallyMode/TallyPlaceholder'"""
content = content.replace("import TallyVouchers from './pages/TallyMode/TallyVouchers'", imports)

# Add routes
route_old = """        <Route path="vouchers" element={<TallyVouchers />} />
        <Route path="*" element={<TallyGateway />} />"""
route_new = """        <Route path="vouchers" element={<TallyVouchers />} />
        <Route path="create" element={<TallyPlaceholder />} />
        <Route path="alter" element={<TallyPlaceholder />} />
        <Route path="banking" element={<TallyPlaceholder />} />
        <Route path="balance-sheet" element={<TallyPlaceholder />} />
        <Route path="pnl" element={<TallyPlaceholder />} />
        <Route path="ratios" element={<TallyPlaceholder />} />
        <Route path="display" element={<TallyPlaceholder />} />
        <Route path="*" element={<TallyGateway />} />"""
content = content.replace(route_old, route_new)

with open('src/App.jsx', 'w') as f:
    f.write(content)
