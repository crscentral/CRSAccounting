import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

content = content.replace("data={restRevenue}", "rows={restRevenue}")
content = content.replace("data={ancRoom}", "rows={ancRoom}")
content = content.replace("data={ancFB}", "rows={ancFB}")
content = content.replace("data={ancOther}", "rows={ancOther}")
content = content.replace('emptyState="No F&B revenue entries in this range."', 'emptyMessage="No F&B revenue entries in this range."')
content = content.replace('emptyState="No postings."', 'emptyMessage="No postings."')

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)

