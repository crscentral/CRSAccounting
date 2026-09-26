import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# Find the loadAll function to fetch guest invoices
old_load = """      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to).order('revenue_date', { ascending: false }) : Promise.resolve({ data: [] })
    ])"""
new_load = """      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to).order('revenue_date', { ascending: false }) : Promise.resolve({ data: [] }),
      supabase.from('hotel_guest_invoices').select('id, invoice_number').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
    ])"""
if old_load in content:
    content = content.replace(old_load, new_load)
else:
    print("loadAll not found")

old_destruct = "const [{ data: room }, { data: anc }, { data: accs }, { data: settings }, { data: restRev }] = await Promise.all(["
new_destruct = "const [{ data: room }, { data: anc }, { data: accs }, { data: settings }, { data: restRev }, { data: guestInvoices }] = await Promise.all(["
if old_destruct in content:
    content = content.replace(old_destruct, new_destruct)
else:
    print("destruct not found")

# Replace notes render in Ancillary Table
old_render = "{ key: 'notes', label: 'Notes', render: r => r.notes || '—' },"
new_render = """{ key: 'notes', label: 'Notes', render: r => {
      if (r.notes && r.notes.startsWith('Invoice ')) {
        const match = r.notes.match(/Invoice ([a-f0-9\\-]+):/);
        if (match && invoicesMap[match[1]]) {
          return `Invoice ${invoicesMap[match[1]]}: ${r.notes.substring(match[0].length).trim()}`;
        }
      }
      return r.notes || '—';
    } },"""
content = content.replace(old_render, new_render)

# Replace notes render in Room Table
old_room_render = "{ key: 'notes', label: 'Notes', render: r => r.notes || '—' }"
new_room_render = """{ key: 'notes', label: 'Notes', render: r => {
      if (r.notes && r.notes.startsWith('Invoice ')) {
        const match = r.notes.match(/Invoice ([a-f0-9\\-]+):/);
        if (match && invoicesMap[match[1]]) {
          return `Invoice ${invoicesMap[match[1]]}: ${r.notes.substring(match[0].length).trim()}`;
        }
      }
      return r.notes || '—';
    } }"""
content = content.replace(old_room_render, new_room_render)

# Add invoicesMap to state
old_state = "const [restRevenue, setRestRevenue] = useState([])"
new_state = "const [restRevenue, setRestRevenue] = useState([])\n  const [invoicesMap, setInvoicesMap] = useState({})"
if old_state in content:
    content = content.replace(old_state, new_state)
else:
    print("state not found")

# Set invoicesMap in loadAll
old_set = "setAncillary(anc || [])"
new_set = "setAncillary(anc || [])\n    const invMap = {};\n    (guestInvoices || []).forEach(i => {\n      if (i.invoice_number) invMap[i.id] = i.invoice_number;\n    });\n    setInvoicesMap(invMap);"
if old_set in content:
    content = content.replace(old_set, new_set)
else:
    print("set not found")

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
