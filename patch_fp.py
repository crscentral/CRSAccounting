import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# Fix the queries
content = content.replace(
    "activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id)",
    "activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id)"
)

# Fix total revenue injection
content = content.replace(
    "const total = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0)",
    "const total = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0)"
)

# Fix the breakdown mapping in loadAll
old_mapping_1 = """    if (activeProduct === 'hotel' && restRev && accs) {
      const acc4019 = accs.find(a => a.code === '4019')
      const acc4011 = accs.find(a => a.code === '4011')
      restRev.forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        if (f > 0 && acc4019) { revMap[acc4019.id] = revMap[acc4019.id] || { code: acc4019.code, name: acc4019.name, amount: 0 }; revMap[acc4019.id].amount += f }
        if (b > 0 && acc4011) { revMap[acc4011.id] = revMap[acc4011.id] || { code: acc4011.code, name: acc4011.name, amount: 0 }; revMap[acc4011.id].amount += b }
      })
    }"""
new_mapping_1 = """    if (activeProduct === 'hotel' && restRev && accs) {
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
content = content.replace(old_mapping_1, new_mapping_1)

# Ensure to do the same for the second instance (Report export)
with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
