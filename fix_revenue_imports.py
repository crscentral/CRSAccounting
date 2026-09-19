import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Add Lock and Unlock icons from lucide-react
if 'Lock' not in code.split('\n')[2]:
    code = code.replace("import { DollarSign", "import { Lock, Unlock, DollarSign")

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
