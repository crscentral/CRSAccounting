import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_order = "const order = { 'Room Revenue': 1, 'Front Office': 1, 'F&B Service': 2 };"
new_order = "const order = { 'Room Revenue': 1, 'Front Office': 1, 'Sales': 1, 'F&B Revenue': 1, 'F&B Service': 2 };"
content = content.replace(old_order, new_order)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
