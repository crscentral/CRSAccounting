import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# 1. Fetch accounts for BOTH hotel and restaurant, and fetch restRev for BOTH
old_fetch = """      activeProduct === 'hotel' ? supabase.from('accounts').select('id, code, name, type').eq('company_id', activeCompany.id).eq('product', 'hotel') : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })"""
new_fetch = """      supabase.from('accounts').select('id, code, name, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('restaurant_daily_revenue').select('meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd, total_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)"""
content = content.replace(old_fetch, new_fetch)

# Need to replace the second instance (for generateReport)
old_fetch_report = """      activeProduct === 'hotel' ? supabase.from('accounts').select('id, code, name, type').eq('company_id', activeCompany.id).eq('product', 'hotel') : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to) : Promise.resolve({ data: [] })"""
new_fetch_report = """      supabase.from('accounts').select('id, code, name, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('restaurant_daily_revenue').select('meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd, total_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)"""
content = content.replace(old_fetch_report, new_fetch_report)

# 2. Inject into salesData for BOTH
old_sales = """    let salesData = s || []
    if (activeProduct === 'hotel' && restRev) {
      restRev.forEach(r => {
        const total = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0)
        if (total > 0) salesData.push({ amount_usd: total })
      })
    }"""
new_sales = """    let salesData = s || []
    if (restRev) {
      restRev.forEach(r => {
        const total = Number(r.total_amount_usd) || ((Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0))
        if (total > 0) salesData.push({ amount_usd: total })
      })
    }"""
content = content.replace(old_sales, new_sales)

# Do it again for generateReport
content = content.replace(old_sales, new_sales) # it might have replaced both if they are identical

# 3. Bridge restRev into revMap
old_bridge = """    if (activeProduct === 'hotel' && restRev && accs) {
      const acc4016 = accs.find(a => a.code === '4016') // Breakfast
      const acc4011 = accs.find(a => a.code === '4011') // Food
      const acc4020 = accs.find(a => a.code === '4020') // Beverage
      const acc4021 = accs.find(a => a.code === '4021') // Other

      restRev.forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        const o = Number(r.other_amount_usd) || 0
        
        if (f > 0) {
          const acc = r.meal_period === 'Breakfast' ? acc4016 : acc4011
          if (acc) { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += f }
        }
        if (b > 0 && acc4020) { revMap[acc4020.id] = revMap[acc4020.id] || { code: acc4020.code, name: acc4020.name, amount: 0 }; revMap[acc4020.id].amount += b }
        if (o > 0 && acc4021) { revMap[acc4021.id] = revMap[acc4021.id] || { code: acc4021.code, name: acc4021.name, amount: 0 }; revMap[acc4021.id].amount += o }
      })
    }"""
new_bridge = """    if (restRev && accs) {
      restRev.forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        const o = Number(r.other_amount_usd) || 0
        
        if (activeProduct === 'hotel') {
          const acc4016 = accs.find(a => a.code === '4016'); const acc4011 = accs.find(a => a.code === '4011');
          const acc4020 = accs.find(a => a.code === '4020'); const acc4021 = accs.find(a => a.code === '4021');
          if (f > 0) { const acc = r.meal_period === 'Breakfast' ? acc4016 : acc4011; if (acc) { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += f } }
          if (b > 0 && acc4020) { revMap[acc4020.id] = revMap[acc4020.id] || { code: acc4020.code, name: acc4020.name, amount: 0 }; revMap[acc4020.id].amount += b }
          if (o > 0 && acc4021) { revMap[acc4021.id] = revMap[acc4021.id] || { code: acc4021.code, name: acc4021.name, amount: 0 }; revMap[acc4021.id].amount += o }
        } else if (activeProduct === 'restaurant') {
          const acc4016 = accs.find(a => a.code === '4016'); const acc4010 = accs.find(a => a.code === '4010');
          const acc4011 = accs.find(a => a.code === '4011'); const acc4019 = accs.find(a => a.code === '4019');
          if (f > 0) { const acc = r.meal_period === 'Breakfast' ? acc4016 : acc4010; if (acc) { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += f } }
          if (b > 0 && acc4011) { revMap[acc4011.id] = revMap[acc4011.id] || { code: acc4011.code, name: acc4011.name, amount: 0 }; revMap[acc4011.id].amount += b }
          if (o > 0 && acc4019) { revMap[acc4019.id] = revMap[acc4019.id] || { code: acc4019.code, name: acc4019.name, amount: 0 }; revMap[acc4019.id].amount += o }
        }
      })
    }"""
content = content.replace(old_bridge, new_bridge)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
