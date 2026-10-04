with open("src/pages/Dashboard.jsx", "r") as f:
    content = f.read()

replacement = """
      // Filtered lists for the active period
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).in('product', prodFilter).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).in('product', prodFilter).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).in('product', prodFilter).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', prodFilter) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).in('product', prodFilter).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).in('product', prodFilter).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      
      // All-time lists for YTD and All-Time cards
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd, manual_room_revenue_collected_usd, invoiced_room_revenue_collected').eq('company_id', activeCompany.id).in('product', prodFilter) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('invoice_date, invoice_amount_usd, collected_amount_usd').eq('company_id', activeCompany.id).in('product', prodFilter) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('expense_date, amount_usd').eq('company_id', activeCompany.id).in('product', prodFilter) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('entry_date, amount_usd, collected_usd').eq('company_id', activeCompany.id).in('product', prodFilter) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('purchase_invoices').select('invoice_date, amount_usd, status').eq('company_id', activeCompany.id).in('product', prodFilter) : Promise.resolve({ data: [] }),
"""

import re
content = re.sub(
    r"\s+\['hotel', 'restaurant'\]\.includes\(activeProduct\) \? supabase\.from\('hotel_room_stats'\)\.select\('\*'\)[\s\S]*?\['hotel', 'restaurant'\]\.includes\(activeProduct\) \? supabase\.from\('purchase_invoices'\)\.select\('invoice_date, amount_usd, status'\)[\s\S]*?Promise\.resolve\(\{ data: \[\] \}\),",
    replacement,
    content,
    count=1
)

with open("src/pages/Dashboard.jsx", "w") as f:
    f.write(content)
