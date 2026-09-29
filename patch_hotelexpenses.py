import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

state_target = "const [entries, setEntries] = useState([]);"
state_replacement = "const [entries, setEntries] = useState([]);\n  const [totalRevenue, setTotalRevenue] = useState(0);"
content = content.replace(state_target, state_replacement)

load_all_target = """const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: roomStats }, { data: pi }, { data: cont }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype, type').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('rooms_occupied').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
      supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')
    ])
    setEntries(exp || [])"""

load_all_replacement = """const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: roomStats }, { data: pi }, { data: cont }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype, type').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('rooms_occupied, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
      supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name'),
      supabase.from('hotel_revenue_entries').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      supabase.from('restaurant_daily_revenue').select('total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
    ])
    
    let rev = 0;
    (roomStats || []).forEach(r => rev += Number(r.room_revenue_usd) || 0);
    (hre || []).forEach(r => rev += Number(r.amount_usd) || 0);
    (rdr || []).forEach(r => {
       const total = Number(r.total_amount_usd) || ((Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0))
       if (total > 0) rev += total;
    });
    setTotalRevenue(rev);
    
    setEntries(exp || [])"""

content = content.replace(load_all_target, load_all_replacement)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
