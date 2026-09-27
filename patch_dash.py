import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# Add purchase_invoices query for hotel/restaurant
old_pi_query = """      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])"""
new_pi_query = """      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('purchase_invoices').select('invoice_date, amount_usd, currency, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }).limit(10) : Promise.resolve({ data: [] })
    ])"""
content = content.replace(old_pi_query, new_pi_query)

# Change array destructuring to include `aHotelPi`
old_destruct = """const [{ data: aHrs }, { data: aHgi }, { data: aHee }, { data: aHre }, { data: aRdr }] = await Promise.all(["""
new_destruct = """const [{ data: aHrs }, { data: aHgi }, { data: aHee }, { data: aHre }, { data: aRdr }, { data: aHotelPi }] = await Promise.all(["""
content = content.replace(old_destruct, new_destruct)

old_pi_q2 = """        supabase.from('hotel_revenue_entries').select('entry_date, amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)
      ])"""
new_pi_q2 = """        supabase.from('hotel_revenue_entries').select('entry_date, amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('purchase_invoices').select('invoice_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)
      ])"""
content = content.replace(old_pi_q2, new_pi_q2)

# Adjust Total Expenses Paid formula to include purchase invoices
old_exp = """      const totalHotelExpense = totalAmcUsd + aHee.reduce((s, r) => s + (Number(r.amount_usd) || 0), 0)
      const profit = totalHotelRevenue - totalHotelExpense"""
new_exp = """      const totalHotelExpense = totalAmcUsd + aHee.reduce((s, r) => s + (Number(r.amount_usd) || 0), 0) + (aHotelPi || []).reduce((s, r) => s + (Number(r.amount_usd) || 0), 0)
      const profit = totalHotelRevenue - totalHotelExpense"""
content = content.replace(old_exp, new_exp)

# Same thing inside feed loading for Dashboard
old_feed_promise = """      const [{ data: hgi }, { data: hre }, { data: hee }] = await Promise.all(["""
new_feed_promise = """      const [{ data: hgi }, { data: hre }, { data: hee }, { data: hPi }] = await Promise.all(["""
content = content.replace(old_feed_promise, new_feed_promise)

old_feed_query = """        supabase.from('hotel_expense_entries').select('expense_date, amount_usd, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('expense_date', { ascending: false }).limit(10),
      ])"""
new_feed_query = """        supabase.from('hotel_expense_entries').select('expense_date, amount_usd, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('expense_date', { ascending: false }).limit(10),
        supabase.from('purchase_invoices').select('invoice_date, amount_usd, currency, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(10),
      ])"""
content = content.replace(old_feed_query, new_feed_query)

old_combined = """        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount_usd, currency: r.currency || 'USD' }))
      ]"""
new_combined = """        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount_usd, currency: r.currency || 'USD' })),
        ...(hPi || []).map(r => ({ date: r.invoice_date, label: r.contact?.name || r.supplier_name_freeform || 'Purchase Invoice', amount: r.amount_usd, currency: r.currency || 'USD' }))
      ]"""
content = content.replace(old_combined, new_combined)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
