import re

with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# We need to replace the F&B Revenue injection in two places: loadData and calculateOpeningBalance
old_block1 = """        // F&B Revenue injection
        if (selectedAccount.code && selectedAccount.code.startsWith('41')) {
          const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
          ;(rdr || []).forEach(r => {
            let amount = 0
            if ((selectedAccount.name || '').toLowerCase().includes('food')) amount = Number(r.food_amount_usd) || 0
            else if ((selectedAccount.name || '').toLowerCase().includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
            else if ((selectedAccount.name || '').toLowerCase().includes('other')) amount = Number(r.other_amount_usd) || 0
            else amount = Number(r.total_amount_usd) || 0
            
            if (amount > 0) {
              combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
            }
          })
        }"""

new_block1 = """        // F&B Revenue injection
        if (selectedAccount.code && (selectedAccount.code.startsWith('41') || selectedAccount.code.startsWith('40'))) {
          const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
          ;(rdr || []).forEach(r => {
            let amount = 0
            const accName = (selectedAccount.name || '').toLowerCase()
            const meal = (r.meal_period || '').toLowerCase()
            
            if (accName.includes('food')) amount = Number(r.food_amount_usd) || 0
            else if (accName.includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
            else if (accName.includes('other')) amount = Number(r.other_amount_usd) || 0
            else if (meal && accName.includes(meal)) amount = Number(r.total_amount_usd) || 0
            
            if (amount > 0) {
              combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
            }
          })
        }"""

content = content.replace(old_block1, new_block1)

old_block2 = """      if (account.code && account.code.startsWith('41')) {
        const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
        ;(rdr || []).forEach(r => {
          let amount = 0
          if ((account.name || '').toLowerCase().includes('food')) amount = Number(r.food_amount_usd) || 0
          else if ((account.name || '').toLowerCase().includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
          else if ((account.name || '').toLowerCase().includes('other')) amount = Number(r.other_amount_usd) || 0
          else amount = Number(r.total_amount_usd) || 0
          
          if (amount > 0) {
            combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
          }
        })
      }"""

new_block2 = """      if (account.code && (account.code.startsWith('41') || account.code.startsWith('40'))) {
        const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
        ;(rdr || []).forEach(r => {
          let amount = 0
          const accName = (account.name || '').toLowerCase()
          const meal = (r.meal_period || '').toLowerCase()
          
          if (accName.includes('food')) amount = Number(r.food_amount_usd) || 0
          else if (accName.includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
          else if (accName.includes('other')) amount = Number(r.other_amount_usd) || 0
          else if (meal && accName.includes(meal)) amount = Number(r.total_amount_usd) || 0
          
          if (amount > 0) {
            combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
          }
        })
      }"""

content = content.replace(old_block2, new_block2)

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)
