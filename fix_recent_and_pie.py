import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Fix Recent Transactions
old_recent = "setRecentTx(combined)"
new_recent = """if (activeProduct === 'hotel') {
      const [{ data: hgi }, { data: hre }, { data: hee }] = await Promise.all([
        supabase.from('hotel_guest_invoices').select('invoice_number, invoice_date, invoice_amount_usd, currency, guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(10),
        supabase.from('hotel_revenue_entries').select('entry_date, amount_usd, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('entry_date', { ascending: false }).limit(10),
        supabase.from('hotel_expense_entries').select('expense_date, amount_usd, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('expense_date', { ascending: false }).limit(10),
      ])
      const hCombined = [
        ...(hgi || []).map(r => ({ date: r.invoice_date, label: r.guest_name || r.invoice_number, amount: r.invoice_amount_usd, currency: 'USD' })),
        ...(hre || []).map(r => ({ date: r.entry_date, label: r.account?.name || 'Revenue', amount: r.amount_usd, currency: 'USD' })),
        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount_usd, currency: 'USD' })),
      ].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 10)
      setRecentTx(hCombined)
    } else {
      setRecentTx(combined)
    }"""
code = code.replace(old_recent, new_recent)

# 2. Fix Pie Chart radii
code = code.replace("innerRadius={80} outerRadius={120}", "innerRadius=\"60%\" outerRadius=\"80%\"")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
