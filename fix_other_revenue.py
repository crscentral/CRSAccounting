import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "<span>Other Revenue (Extra Bed, Early Check-in, Late Check-out, Breakfast, Transportation, SPA, etc.)</span>",
    "<span>Other Revenue</span>"
)

content = content.replace(
    "rows={ancillary}",
    "data={ancOther}"
)

# wait, does DataTable use `rows` or `data`?
# In HotelRevenue it was `rows={ancillary}` and `rows={roomStats}`, but `data={restRevenue}`!
# Wait, `DataTable` usually expects `data={...}`. Let's check `DataTable.jsx`.

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)

