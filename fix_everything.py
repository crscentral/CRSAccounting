import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. YTD math
old_ytd = r"""if \(activeProduct === 'hotel'\) \{\s*// Note: since we only query ledgerEntries for the currently selected period \(not YTD\),\s*// calculating true YTD requires fetching ledger entries for the YTD range\.\s*// For now, we will leave YTD as 0 for Hotel unless we fetch it\.\s*\}"""
new_ytd = """if (activeProduct === 'hotel') {
    ytdRevenue = totalBilled
    ytdExpenses = totalExpenses
  }"""
code = re.sub(old_ytd, new_ytd, code)

# 2. All-Time math
old_alltime = r"""allTimeRevenue = ledgerEntries.filter\(e => accounts.find\(a => a.id === e.account_id\)\?.type === 'Revenue'\).reduce\(\(s, e\) => s \+ \(Number\(e.credit_usd\) - Number\(e.debit_usd\)\), 0\)
    allTimeExpenses = ledgerEntries.filter\(e => accounts.find\(a => a.id === e.account_id\)\?.type === 'Expenses'\).reduce\(\(s, e\) => s \+ \(Number\(e.debit_usd\) - Number\(e.credit_usd\)\), 0\)"""
new_alltime = """allTimeRevenue = totalBilled
    allTimeExpenses = totalExpenses"""
code = re.sub(old_alltime, new_alltime, code)

# 3. Collected array math (prevent double counting)
old_collected = r"collected = hotelGuestInvoices.reduce\(\(s, i\) => s \+ Number\(i.collected_amount_usd\), 0\) \+ \s*hotelRoomStats.reduce\(\(s, r\) => s \+ Number\(r.room_revenue_collected_usd\), 0\)"
new_collected = """const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected"""
code = re.sub(old_collected, new_collected, code)

# 4. Draft Invoices (Outstanding invoices $NaN fix)
old_draft = r"const draftInvoices = activeProduct === 'hotel' \? hotelGuestInvoices.filter\(i => Number\(i.invoice_amount_usd\) > Number\(i.collected_amount_usd\)\) : sales.filter\(i => i.status !== 'Paid'\)"
new_draft = """const draftInvoices = activeProduct === 'hotel' 
    ? hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)).map(i => ({
        ...i,
        contact: { name: i.guest_name || 'Guest' },
        balance_due: Number(i.invoice_amount_usd) - Number(i.collected_amount_usd),
        amount: i.invoice_amount_usd,
        amount_usd: i.invoice_amount_usd,
        due_date: i.invoice_date,
        status: 'Pending'
      }))
    : sales.filter(i => i.status !== 'Paid')"""
code = re.sub(old_draft, new_draft, code)

# 5. Recent Transactions
old_recent = r"setRecentTx\(combined\)"
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

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
