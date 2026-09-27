import re

with open('src/pages/RestaurantExpenses.jsx', 'r') as f:
    content = f.read()

pie_start = '<div className="grid lg:grid-cols-2 gap-4 mb-6">'
pie_end = '<div className="flex justify-between items-end mb-3 mt-8">'

start_idx = content.find(pie_start)
if start_idx != -1:
    end_idx = content.find(pie_end, start_idx)
    if end_idx != -1:
        content = content[:start_idx] + content[end_idx:]

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)
