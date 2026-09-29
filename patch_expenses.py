import re

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Update the query to fetch account details for purchase_invoices
    old_query = ".from('purchase_invoices').select('*, contact:contacts(name)')"
    new_query = ".from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)')"
    content = content.replace(old_query, new_query)

    # 2. Update byHead aggregation to include purchaseInvoices
    old_agg = """  const byHead = { 'AMC Contracts (Amortized)': amcTotalForView }
  entries.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })"""

    new_agg = """  const byHead = { 'AMC Contracts (Amortized)': amcTotalForView }
  entries.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })
  purchaseInvoices.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })"""
    
    content = content.replace(old_agg, new_agg)

    with open(filepath, 'w') as f:
        f.write(content)

patch_file('src/pages/HotelExpenses.jsx')
patch_file('src/pages/RestaurantExpenses.jsx')

# Bump sw.js
with open('public/sw.js', 'r') as f:
    sw = f.read()
sw = sw.replace('v112', 'v113')
with open('public/sw.js', 'w') as f:
    f.write(sw)
