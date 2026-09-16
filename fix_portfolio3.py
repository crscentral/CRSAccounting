import re

with open('src/pages/PortfolioDashboard.jsx', 'r') as f:
    code = f.read()

# Add hotelGuestInvoices fetch
old_query = """      supabase.from('sales_invoices').select('id, amount_usd').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('amount_usd').eq('company_id', companyId).eq('product', product).gte('receipt_date', range.from).lte('receipt_date', range.to),
    ])"""

new_query = """      supabase.from('sales_invoices').select('id, amount_usd').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('amount_usd').eq('company_id', companyId).eq('product', product).gte('receipt_date', range.from).lte('receipt_date', range.to),
      product === 'hotel' ? supabase.from('hotel_guest_invoices').select('invoice_amount_usd, collected_amount_usd').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: null }),
      product === 'hotel' ? supabase.from('hotel_room_stats').select('room_revenue_collected_usd').eq('company_id', companyId).eq('product', product).gte('stat_date', range.from).lte('stat_date', range.to) : Promise.resolve({ data: null }),
    ])"""
code = code.replace(old_query, new_query)

# Change destructure
old_destructure = "const [{ data: hotelSettings }, { data: hotelStats }, { data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }] = await Promise.all(["
new_destructure = "const [{ data: hotelSettings }, { data: hotelStats }, { data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }, { data: guestInv }, { data: roomStatsExt }] = await Promise.all(["
code = code.replace(old_destructure, new_destructure)

# Change calculation
old_calc = """    const invoices = (salesInv || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    const collected = (receipts || []).reduce((s, i) => s + Number(i.amount_usd), 0)"""

new_calc = """    let invoices = 0
    let collected = 0
    if (product === 'hotel') {
      invoices = (guestInv || []).reduce((s, i) => s + Number(i.invoice_amount_usd), 0)
      collected = (guestInv || []).reduce((s, i) => s + Number(i.collected_amount_usd), 0) + (roomStatsExt || []).reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
    } else {
      invoices = (salesInv || []).reduce((s, i) => s + Number(i.amount_usd), 0)
      collected = (receipts || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    }"""
code = code.replace(old_calc, new_calc)

with open('src/pages/PortfolioDashboard.jsx', 'w') as f:
    f.write(code)
