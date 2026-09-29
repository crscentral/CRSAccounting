import re
with open('src/pages/HotelExpenses.jsx', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "const entries = entries.filter" in line: continue
    if "const restEntries =" in line: continue
    if "const amcContracts = amcContracts.filter" in line: continue
    if "const restAmc =" in line: continue
    if "const purchaseInvoices = purchaseInvoices.filter" in line: continue
    if "const restPI =" in line: continue
    if "const entriesTotalUsd = entries.reduce" in line and "hotelEntriesTotal" not in line: 
        # wait, we have two entriesTotalUsd definitions?
        pass
    if "const restEntriesTotal" in line: continue
    new_lines.append(line)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.writelines(new_lines)
