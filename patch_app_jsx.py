import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add imports
imports = """import DataSecurity from './pages/DataSecurity'
import PrivacyPolicy from './pages/PrivacyPolicy'
"""
content = content.replace(
    "import HotelGuestInvoices from './pages/HotelGuestInvoices'",
    "import HotelGuestInvoices from './pages/HotelGuestInvoices'\n" + imports
)

# Add routes
routes = """        <Route path="/data-security" element={<DataSecurity />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
"""
content = content.replace(
    '<Route path="/settings" element={<Settings />} />',
    '<Route path="/settings" element={<Settings />} />\n' + routes
)

with open('src/App.jsx', 'w') as f:
    f.write(content)
