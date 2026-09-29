import re
with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Replace "Hotel Daily Expense Entries" with "Combined Daily Expense Entries"
content = content.replace('Hotel Daily Expense Entries', 'Combined Daily Expense Entries')
content = content.replace('Hotel AMC Contracts (auto-split across 12 months)', 'Combined AMC Contracts (auto-split across 12 months)')
content = content.replace('Hotel Purchase Invoices', 'Combined Purchase Invoices')

# Find the block for Restaurant Daily Expense Entries and remove it
import re

start1 = content.find('{(restEntries.length > 0 || restAmc.length > 0) && (')
if start1 != -1:
    end1 = content.find('          )}', start1) + 12
    content = content[:start1] + content[end1:]

start2 = content.find('{restPI.length > 0 && (')
if start2 != -1:
    end2 = content.find('          )}', start2) + 12
    content = content[:start2] + content[end2:]

# Replace hotelEntries with entries
content = content.replace('hotelEntries', 'entries')
content = content.replace('hotelAmc', 'amcContracts')
content = content.replace('hotelPI', 'purchaseInvoices')
content = content.replace('hotelEntriesTotal', 'entriesTotalUsd')

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)

