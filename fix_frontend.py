import re

# Fix FinancialPerformance.jsx
with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

content = content.replace("a.code === '4016'", "a.name === 'Breakfast Revenue'")
content = content.replace("a.code === '4011'", "a.name === 'Beverage Sales'") # Wait, in Restaurant 4011 was Beverage Sales! In Hotel it was Early Check-in.
content = content.replace("a.code === '4020'", "a.name === 'Beverage Revenue' || a.name === 'F&B Revenue'")
content = content.replace("a.code === '4021'", "a.name === 'Other F&B Revenue'")
content = content.replace("code === '4010'", "name === 'Room Revenue'")

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)

# Fix HotelBudget.jsx
with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace("a.code === '4010'", "a.name === 'Room Revenue'")

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

# Fix Ledger.jsx
with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

content = content.replace("a.code === '4010'", "a.name === 'Room Revenue' || a.name === 'Sales Revenue'")

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)
