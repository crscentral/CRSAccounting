import re

with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    content = f.read()

old_filter = """  const todayRows = rows.filter(r => r.invoice_date === today)
  const mtdRows = rows.filter(r => r.invoice_date >= mtd.from && r.invoice_date <= mtd.to)
  const ytdRows = rows // already scoped to YTD in the query"""
new_filter = """  const todayRows = rows.filter(r => r.invoice_date === today)
  const mtdRows = rows.filter(r => r.invoice_date >= mtd.from && r.invoice_date <= mtd.to)
  const ytdRows = rows.filter(r => r.invoice_date >= ytd.from && r.invoice_date <= ytd.to)
  const cpRows = rows.filter(r => r.invoice_date >= cp.range.from && (cp.range.to === '9999-12-31' || r.invoice_date <= cp.range.to))"""
content = content.replace(old_filter, new_filter)

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(content)
