import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Add hotel_revenue_entries to loadData
old_load = r"activeProduct === 'hotel' \? supabase.from\('hotel_amc_contracts'\).select\('\*'\).eq\('company_id', activeCompany.id\).eq\('product', activeProduct\) : Promise.resolve\(\{ data: \[\] \}\),"
new_load = """activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),"""
code = code.replace(old_load, new_load)

# Add state variable
old_state_set = r"setHotelAmc\(hamc \|\| \[\]\)"
new_state_set = """setHotelAmc(hamc || [])
    const hre = arguments[0][11]?.data
    setHotelRevenueEntries(hre || [])"""
# Wait, arguments[0] doesn't work for Promise.all. I'll just change the destructured array.
