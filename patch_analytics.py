import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# Replace all occurrences of array methods on potentially null arrays
replacements = [
    ('sales.reduce', '(sales || []).reduce'),
    ('receipts.reduce', '(receipts || []).reduce'),
    ('purchases.reduce', '(purchases || []).reduce'),
    ('sales.filter', '(sales || []).filter'),
    ('sales.forEach', '(sales || []).forEach'),
    ('receipts.forEach', '(receipts || []).forEach'),
    ('hotelRoomStats.reduce', '(hotelRoomStats || []).reduce'),
    ('hotelGuestInvoices.reduce', '(hotelGuestInvoices || []).reduce'),
    ('hotelRevenueEntries.reduce', '(hotelRevenueEntries || []).reduce'),
    ('restaurantRevenue.reduce', '(restaurantRevenue || []).reduce'),
    ('hotelAmc.reduce', '(hotelAmc || []).reduce'),
    ('hotelExpenseEntries.reduce', '(hotelExpenseEntries || []).reduce'),
    ('hotelGuestInvoices.filter', '(hotelGuestInvoices || []).filter'),
    ('hotelGuestInvoices.forEach', '(hotelGuestInvoices || []).forEach'),
    ('hotelRoomStats.forEach', '(hotelRoomStats || []).forEach'),
    ('hotelRevenueEntries.forEach', '(hotelRevenueEntries || []).forEach'),
    ('hotelGuestInvoices.length', '(hotelGuestInvoices || []).length'),
    ('hotelRoomStats.length', '(hotelRoomStats || []).length'),
    ('hotelRevenueEntries.length', '(hotelRevenueEntries || []).length'),
    ('hotelExpenseEntries.length', '(hotelExpenseEntries || []).length'),
    ('sales.length', '(sales || []).length'),
    ('purchases.length', '(purchases || []).length'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)

