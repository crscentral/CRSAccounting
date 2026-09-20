import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. fix fetchAncillaryAccounts
old_fetch = "const { data } = await supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', 'hotel').eq('type', 'Revenue').neq('code', '4010').order('subtype', { ascending: true }).order('code', { ascending: true })"
new_fetch = """      let query = supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').order('subtype', { ascending: true }).order('code', { ascending: true })
      if (activeProduct === 'hotel') query = query.neq('code', '4010')
      const { data } = await query"""
content = content.replace(old_fetch, new_fetch)

# 2. fix ledger query in loadAncillary
old_ledger = "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')"
new_ledger = "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue')"
content = content.replace(old_ledger, new_ledger)
# wait, for hotel I still need to exclude 4010! 
# Let me replace the entire Promise.all in loadAncillary:
old_promise_all = """      const [{ data: budgetRows }, { data: ledgerRows }, { data: restRev }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', startYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010'),
        supabase.from('restaurant_daily_revenue').select('revenue_date, food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`)
      ])"""
new_promise_all = """      let ledgerQuery = supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue')
      if (activeProduct === 'hotel') ledgerQuery = ledgerQuery.neq('accounts.code', '4010')

      const [{ data: budgetRows }, { data: ledgerRows }, { data: restRev }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
        ledgerQuery,
        supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`)
      ])"""
content = content.replace(old_promise_all, new_promise_all)

# 3. fix restRev mapping in loadAncillary
old_mapping = """      // Inject Restaurant Table Revenue into Hotel F&B Revenue Actuals
      if (activeProduct === 'hotel' && restRev) {
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          // food_amount -> 4019 - Restaurant Revenue
          const foodKey = `4019-${m}`
          // beverage_amount -> 4011 - Beverage Revenue
          const bevKey = `4011-${m}`
          aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
          aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
        })
      }
      setAncillaryActuals(aMap)"""
new_mapping = """      // Dynamically Inject Restaurant Table Revenue based on activeProduct and Meal Period
      if (restRev) {
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          
          if (activeProduct === 'hotel') {
            const foodKey = r.meal_period === 'Breakfast' ? `4016-${m}` : `4011-${m}`
            const bevKey = `4020-${m}`
            const otherKey = `4021-${m}`
            
            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
            
          } else if (activeProduct === 'restaurant') {
            const foodKey = r.meal_period === 'Breakfast' ? `4016-${m}` : `4010-${m}`
            const bevKey = `4011-${m}`
            const otherKey = `4019-${m}`
            
            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
          }
        })
      }
      setAncillaryActuals(aMap)"""
content = content.replace(old_mapping, new_mapping)

# 4. fix revenueSummary KPI injection
old_kpi = """    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const amt = ancillaryBudgets[k] ? (Number(ancillaryBudgets[k].amount_usd) || 0) : 0
        if (a.subtype === 'Front Office') frontOffice += amt
        else if (a.subtype === 'F&B Service') fbService += amt
        else otherRev += amt
      }
    }"""
new_kpi = """    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const amt = ancillaryBudgets[k] ? (Number(ancillaryBudgets[k].amount_usd) || 0) : 0
        if (a.subtype === 'Front Office' || (activeProduct === 'restaurant' && (a.code === '4010' || a.subtype === 'F&B Revenue' || a.subtype === 'Sales'))) frontOffice += amt
        else if (a.subtype === 'F&B Service') fbService += amt
        else otherRev += amt
      }
    }"""
content = content.replace(old_kpi, new_kpi)

# 5. fix sorting
old_sorting = "const order = { 'Room Revenue': 1, 'Front Office': 1, 'F&B Service': 2 };"
new_sorting = "const order = { 'Room Revenue': 1, 'Front Office': 1, 'Sales': 1, 'F&B Revenue': 1, 'F&B Service': 2 };"
content = content.replace(old_sorting, new_sorting)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
