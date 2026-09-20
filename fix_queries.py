import os

files = [
    'src/pages/HotelRevenue.jsx',
    'src/pages/FinancialPerformance.jsx'
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    content = content.replace("other_amount_usd, total_amount_usd, collected_usd", "other_amount_usd, collected_usd")
    content = content.replace("other_amount_usd, total_amount_usd", "other_amount_usd")
    
    with open(filepath, 'w') as f:
        f.write(content)

