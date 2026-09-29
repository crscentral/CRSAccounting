import re

with open('src/pages/Reports.jsx', 'r') as f:
    content = f.read()

# I will completely rewrite the inner part of the hotel/restaurant block to guarantee balancing.
# From `if (roomRevAcc) {` down to `if (arAcc) { ... }`

old_block = """      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) {
            combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date, accounts: { type: roomRevAcc.type } })
            if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: r.room_revenue_usd, credit_usd: 0, entry_date: r.stat_date, accounts: { type: cashAcc.type } })
          }
        })
      }
      
      ;(hre || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) {
          combined.push({ account_id: a.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date, accounts: { type: a.type } })
          if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.entry_date, accounts: { type: cashAcc.type } })
        }
      })
      
      ;(hee || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) {
          combined.push({ account_id: a.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type } })
          if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.expense_date, accounts: { type: cashAcc.type } })
        }
      })
      
      if (mainAcc && amc && amc.length > 0) {
        const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
        if (amcMonthly > 0) {
          const start = new Date(cp.range.from < '2020-01-01' ? '2020-01-01' : cp.range.from)
          const end = new Date(cp.range.to)
          let cur = new Date(start.getFullYear(), start.getMonth(), 1)
          while (cur <= end) {
            const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
            combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type } })
            if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: 0, credit_usd: amcMonthly, entry_date: dStr, accounts: { type: cashAcc.type } })
            cur.setMonth(cur.getMonth() + 1)
          }
        }
      }
      
      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
        const totalRev = Number(r.food_amount_usd || 0) + Number(r.beverage_amount_usd || 0) + Number(r.other_amount_usd || 0)
        if (cashAcc && totalRev > 0) combined.push({ account_id: cashAcc.id, debit_usd: totalRev, credit_usd: 0, entry_date: r.revenue_date, accounts: { type: cashAcc.type } })
      })
      
      if (arAcc) {
        ;(hgi || []).forEach(r => {
          const inv = Number(r.invoice_amount_usd) || 0
          const col = Number(r.collected_amount_usd) || 0
          if (inv > 0) combined.push({ account_id: arAcc.id, debit_usd: inv, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (col > 0) combined.push({ account_id: arAcc.id, debit_usd: 0, credit_usd: col, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (cashAcc && col > 0) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: cashAcc.type } })
        })
      }"""

new_block = """      // 1. Hotel Room Stats (Daily Revenue)
      ;(hrs || []).forEach(r => {
        const rev = Number(r.room_revenue_usd) || 0
        const col = Number(r.manual_room_revenue_collected_usd) || rev // Default to full collection if not specified
        const uncol = Math.max(0, rev - col)
        if (rev > 0 && roomRevAcc) {
          combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: rev, entry_date: r.stat_date, accounts: { type: roomRevAcc.type } })
          if (col > 0 && cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.stat_date, accounts: { type: cashAcc.type } })
          if (uncol > 0 && arAcc) combined.push({ account_id: arAcc.id, debit_usd: uncol, credit_usd: 0, entry_date: r.stat_date, accounts: { type: arAcc.type } })
        }
      })
      
      // 2. Hotel Ancillary Revenue
      ;(hre || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        const rev = Number(r.amount_usd) || 0
        const col = Number(r.collected_usd) || rev // Default to full
        const uncol = Math.max(0, rev - col)
        if (a && rev > 0) {
          combined.push({ account_id: a.id, debit_usd: 0, credit_usd: rev, entry_date: r.entry_date, accounts: { type: a.type } })
          if (col > 0 && cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.entry_date, accounts: { type: cashAcc.type } })
          if (uncol > 0 && arAcc) combined.push({ account_id: arAcc.id, debit_usd: uncol, credit_usd: 0, entry_date: r.entry_date, accounts: { type: arAcc.type } })
        }
      })
      
      // 3. Hotel Expenses
      ;(hee || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        const exp = Number(r.amount_usd) || 0
        if (a && exp > 0) {
          combined.push({ account_id: a.id, debit_usd: exp, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type } })
          if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: 0, credit_usd: exp, entry_date: r.expense_date, accounts: { type: cashAcc.type } })
        }
      })
      
      // 4. Hotel AMC Contracts
      if (mainAcc && amc && amc.length > 0) {
        const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
        if (amcMonthly > 0) {
          const start = new Date(cp.range.from < '2020-01-01' ? '2020-01-01' : cp.range.from)
          const end = new Date(cp.range.to)
          let cur = new Date(start.getFullYear(), start.getMonth(), 1)
          while (cur <= end) {
            const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
            combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type } })
            if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: 0, credit_usd: amcMonthly, entry_date: dStr, accounts: { type: cashAcc.type } })
            cur.setMonth(cur.getMonth() + 1)
          }
        }
      }
      
      // 5. Restaurant Daily Revenue
      ;(rdr || []).forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        const o = Number(r.other_amount_usd) || 0
        const totalRev = f + b + o
        const col = r.collected_usd !== null && r.collected_usd !== undefined ? Number(r.collected_usd) : totalRev
        const uncol = Math.max(0, totalRev - col)
        
        if (foodAcc && f > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: f, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
        if (bevAcc && b > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: b, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
        if (otherFbAcc && o > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: o, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
        
        if (col > 0 && cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.revenue_date, accounts: { type: cashAcc.type } })
        if (uncol > 0 && arAcc) combined.push({ account_id: arAcc.id, debit_usd: uncol, credit_usd: 0, entry_date: r.revenue_date, accounts: { type: arAcc.type } })
      })
      
      // 6. Hotel Guest Invoices
      ;(hgi || []).forEach(r => {
        const inv = Number(r.invoice_amount_usd) || 0
        const col = Number(r.collected_amount_usd) || 0
        if (inv > 0) {
          if (roomRevAcc) combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: inv, entry_date: r.invoice_date, accounts: { type: roomRevAcc.type } })
          if (arAcc) combined.push({ account_id: arAcc.id, debit_usd: inv, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
        }
        if (col > 0) {
          if (arAcc) combined.push({ account_id: arAcc.id, debit_usd: 0, credit_usd: col, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: cashAcc.type } })
        }
      })"""

# Notice I replaced old_block in TWO places! `loadData` and `generateFinancialReport`
content = content.replace(old_block, new_block)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(content)
