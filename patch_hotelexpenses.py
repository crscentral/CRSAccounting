import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

old_state_set = """    setTotalOccupied((roomStats || []).reduce((s, r) => s + (r.rooms_occupied || 0), 0))
  }"""

new_state_set = """    setTotalOccupied((roomStats || []).reduce((s, r) => s + (r.rooms_occupied || 0), 0))
    setPurchaseInvoices(pi || [])
    setContacts(cont || [])
  }"""

content = content.replace(old_state_set, new_state_set)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
