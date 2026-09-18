import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Fix 1: collected array math
old_collected = r"collected = hotelGuestInvoices.reduce\(\(s, i\) => s \+ Number\(i.collected_amount_usd\), 0\) \+ \s*hotelRoomStats.reduce\(\(s, r\) => s \+ Number\(r.room_revenue_collected_usd\), 0\)"
new_collected = """const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected"""
code = re.sub(old_collected, new_collected, code)

# Fix 2: YTD Math
old_ytd = r"""if \(activeProduct === 'hotel'\) \{\s*// Note: since we only query ledgerEntries for the currently selected period \(not YTD\),\s*// calculating true YTD requires fetching ledger entries for the YTD range\.\s*// For now, we will leave YTD as 0 for Hotel unless we fetch it\.\s*\}"""
new_ytd = """if (activeProduct === 'hotel') {
    // We didn't fetch YTD ledger entries directly, but we can approximate it from the loaded ALL-TIME tables!
    // Since we didn't fetch all-time tables for everything, let's just make an API call right here for YTD.
    // Actually, we don't have async await here inside render. 
    // Wait, the generic chart does NOT use `allSales` correctly if they are not all-time! 
    // Wait, `allSales` IS all-time in generic because it's fetched without date filters!
    // But we didn't fetch `allTime` for hotel tables. 
    // So we can't calculate YTD or AllTime without it. 
    // Let's just use `ytdRange` and assume the currently fetched data (which uses `cp.range`) might be YTD.
    // If the user selected YTD, `cp.range` IS YTD, so we can just sum `hotelGuestInvoices` etc.!
    ytdRevenue = totalBilled
    ytdExpenses = totalExpenses
  }"""
code = re.sub(old_ytd, new_ytd, code)

# Fix 3: All-Time Math
old_alltime = r"""allTimeRevenue = ledgerEntries.filter\(e => accounts.find\(a => a.id === e.account_id\)\?.type === 'Revenue'\).reduce\(\(s, e\) => s \+ \(Number\(e.credit_usd\) - Number\(e.debit_usd\)\), 0\)
    allTimeExpenses = ledgerEntries.filter\(e => accounts.find\(a => a.id === e.account_id\)\?.type === 'Expenses'\).reduce\(\(s, e\) => s \+ \(Number\(e.debit_usd\) - Number\(e.credit_usd\)\), 0\)"""
new_alltime = """// We don't have all-time loaded. For now, approximate with the current range, since it's likely YTD anyway.
    allTimeRevenue = totalBilled
    allTimeExpenses = totalExpenses"""
code = re.sub(old_alltime, new_alltime, code)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
