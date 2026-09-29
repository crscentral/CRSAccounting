import re

with open('src/pages/Comparison.jsx', 'r') as f:
    content = f.read()

old_block = """      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date })
      })"""

new_block = """      ;(rdr || []).forEach(r => {
        const meal = (r.meal_period || '').toLowerCase()
        const mealAcc = meal ? (accs || []).find(a => (a.name || '').toLowerCase().includes(meal) && a.type === 'Revenue') : null
        
        if (mealAcc) {
           const total = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0)
           if (total > 0) combined.push({ account_id: mealAcc.id, debit_usd: 0, credit_usd: total, entry_date: r.revenue_date })
        } else {
           if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date })
           if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date })
           if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date })
        }
      })"""

content = content.replace(old_block, new_block)

with open('src/pages/Comparison.jsx', 'w') as f:
    f.write(content)
