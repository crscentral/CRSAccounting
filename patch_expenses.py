import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# Add states for stats
code = code.replace(
    "const [expenseAccounts, setExpenseAccounts] = useState([])",
    "const [expenseAccounts, setExpenseAccounts] = useState([])\n  const [totalRooms, setTotalRooms] = useState(0)\n  const [totalOccupied, setTotalOccupied] = useState(0)"
)

# Modify loadAll to fetch stats
load_old = """    const [{ data: exp }, { data: amc }, { data: accs }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
    ])
    setEntries(exp || [])
    setAmcContracts(amc || [])
    setExpenseAccounts(accs || [])"""

load_new = """    const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: roomStats }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('rooms_occupied').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to)
    ])
    setEntries(exp || [])
    setAmcContracts(amc || [])
    setExpenseAccounts(accs || [])
    setTotalRooms(settings?.total_rooms || 0)
    setTotalOccupied((roomStats || []).reduce((s, r) => s + (r.rooms_occupied || 0), 0))"""

code = code.replace(load_old, load_new)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
