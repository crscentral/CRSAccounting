import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. Add restaurant_daily_revenue to Promise.all in loadAncillary
old_promise = """      const [{ data: budgetRows }, { data: ledgerRows }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', startYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')
      ])"""

new_promise = """      const [{ data: budgetRows }, { data: ledgerRows }, { data: restRev }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', startYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010'),
        supabase.from('restaurant_daily_revenue').select('revenue_date, food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`)
      ])"""

content = content.replace(old_promise, new_promise)

# 2. Add injection logic after ledgerRows
old_amap = """      if (ledgerRows) {
        ledgerRows.forEach(r => {
          const m = parseInt(r.entry_date.split('-')[1], 10)
          const k = `${r.accounts.code}-${m}`
          const amt = (Number(r.credit_usd) || 0) - (Number(r.debit_usd) || 0) // Revenue is credit
          aMap[k] = (aMap[k] || 0) + amt
        })
      }"""

new_amap = """      if (ledgerRows) {
        ledgerRows.forEach(r => {
          const m = parseInt(r.entry_date.split('-')[1], 10)
          const k = `${r.accounts.code}-${m}`
          const amt = (Number(r.credit_usd) || 0) - (Number(r.debit_usd) || 0) // Revenue is credit
          aMap[k] = (aMap[k] || 0) + amt
        })
      }
      
      // Inject Restaurant Table Revenue into Hotel F&B Revenue Actuals
      if (restRev) {
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          // food_amount -> 4019 - Restaurant Revenue
          const foodKey = `4019-${m}`
          // beverage_amount -> 4011 - Beverage Revenue
          const bevKey = `4011-${m}`
          
          aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
          aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
        })
      }"""

content = content.replace(old_amap, new_amap)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
