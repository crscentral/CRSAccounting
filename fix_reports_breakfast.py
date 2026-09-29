import re

with open('src/pages/Reports.jsx', 'r') as f:
    content = f.read()

old_block = """      // 5. Restaurant Daily Revenue
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
      })"""

new_block = """      // 5. Restaurant Daily Revenue
      ;(rdr || []).forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        const o = Number(r.other_amount_usd) || 0
        const totalRev = f + b + o
        const col = r.collected_usd !== null && r.collected_usd !== undefined ? Number(r.collected_usd) : totalRev
        const uncol = Math.max(0, totalRev - col)
        
        const meal = (r.meal_period || '').toLowerCase()
        const mealAcc = meal ? (accs || []).find(a => (a.name || '').toLowerCase().includes(meal) && a.type === 'Revenue') : null

        if (mealAcc && totalRev > 0) {
           combined.push({ account_id: mealAcc.id, debit_usd: 0, credit_usd: totalRev, entry_date: r.revenue_date, accounts: { type: mealAcc.type } })
        } else {
           if (foodAcc && f > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: f, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
           if (bevAcc && b > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: b, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
           if (otherFbAcc && o > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: o, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
        }
        
        if (col > 0 && cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.revenue_date, accounts: { type: cashAcc.type } })
        if (uncol > 0 && arAcc) combined.push({ account_id: arAcc.id, debit_usd: uncol, credit_usd: 0, entry_date: r.revenue_date, accounts: { type: arAcc.type } })
      })"""

content = content.replace(old_block, new_block)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(content)
