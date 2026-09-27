import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# I will just replace all instances of `\n    (sales || []).forEach` with `\n    ;(sales || []).forEach`
# and `\n    (receipts || []).forEach` with `\n    ;(receipts || []).forEach`
# and `\n    (hotelGuestInvoices || []).forEach` with `\n    ;(hotelGuestInvoices || []).forEach`

content = content.replace("\n    (sales || []).forEach", "\n    ;(sales || []).forEach")
content = content.replace("\n    (receipts || []).forEach", "\n    ;(receipts || []).forEach")
content = content.replace("\n    (hotelGuestInvoices || []).forEach", "\n    ;(hotelGuestInvoices || []).forEach")
content = content.replace("\n    (hotelRoomStats || []).forEach", "\n    ;(hotelRoomStats || []).forEach")
content = content.replace("\n    (hotelRevenueEntries || []).forEach", "\n    ;(hotelRevenueEntries || []).forEach")

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)
