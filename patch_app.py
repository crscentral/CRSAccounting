import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add imports
imports = """import HotelGuestInvoices from './pages/HotelGuestInvoices'
import TallyLayout from './pages/TallyMode/TallyLayout'
import TallyGateway from './pages/TallyMode/TallyGateway'
import TallyVouchers from './pages/TallyMode/TallyVouchers'"""
content = content.replace("import HotelGuestInvoices from './pages/HotelGuestInvoices'", imports)

# Add route
route_old = """      <Route element={<Gate><AppShell /></Gate>}>"""
route_new = """      <Route path="/tally-mode" element={<Gate><TallyLayout /></Gate>}>
        <Route index element={<TallyGateway />} />
        <Route path="vouchers" element={<TallyVouchers />} />
        <Route path="*" element={<TallyGateway />} />
      </Route>
      <Route element={<Gate><AppShell /></Gate>}>"""
content = content.replace(route_old, route_new)

with open('src/App.jsx', 'w') as f:
    f.write(content)
