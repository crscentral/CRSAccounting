import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Fix the Promise.all destructuring array
old_destructure = "const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }] = await Promise.all(["
new_destructure = "const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all(["
code = code.replace(old_destructure, new_destructure)

# Fix the Promise.all array to actually include the hotel_revenue_entries query
old_promise = "activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),\n    ])"
new_promise = "activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),\n      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),\n    ])"
code = code.replace(old_promise, new_promise)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
