import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "{ key: 'total_amount_usd', label: 'Total F&B Rev', render: r => cp.fmt(r.total_amount_usd) },",
    "{ key: 'total_amount_usd', label: 'Total F&B Rev', render: r => cp.fmt(r.total_amount_usd || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))) },"
)
content = content.replace(
    "{ key: 'pending_collection', label: 'Pending Collection', render: r => <span className=\"font-semibold text-red-500\">{cp.fmt((r.total_amount_usd || 0) - (r.collected_usd || 0))}</span> },",
    "{ key: 'pending_collection', label: 'Pending Collection', render: r => { const total = r.total_amount_usd || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return <span className=\"font-semibold text-red-500\">{cp.fmt(total - (r.collected_usd || 0))}</span> } },"
)
with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
