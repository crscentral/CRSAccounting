import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_loadall = """  async function loadAll() {
    const [{ data: settings }, { data: budgetRows }, { data: statRows }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
      supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear}-12-31`),
    ])
    setTotalRooms(settings?.total_rooms || 0)
    const rowMap = {}
    ;(budgetRows || []).forEach(b => { rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency, revenue_usd: b.budgeted_room_revenue_usd } })
    setRows(rowMap)
    const actualMap = {}
    ;(statRows || []).forEach(s => {
      const [y, m] = s.stat_date.split('-')
      const key = `${y}-${Number(m)}`
      actualMap[key] = (actualMap[key] || 0) + Number(s.room_revenue_usd)
    })
    setActuals(actualMap)
  }"""

new_loadall = """  async function loadAll() {
    const [{ data: settings }, { data: budgetRows }, { data: statRows }, { data: restRevRows }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear}-12-31`) : Promise.resolve({ data: [] }),
      activeProduct === 'restaurant' ? supabase.from('restaurant_daily_revenue').select('revenue_date, food_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`) : Promise.resolve({ data: [] })
    ])
    setTotalRooms(settings?.total_rooms || 0)
    const rowMap = {}
    ;(budgetRows || []).forEach(b => { rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency, revenue_usd: b.budgeted_room_revenue_usd } })
    setRows(rowMap)
    const actualMap = {}
    if (activeProduct === 'hotel') {
      ;(statRows || []).forEach(s => {
        const [y, m] = s.stat_date.split('-')
        const key = `${y}-${Number(m)}`
        actualMap[key] = (actualMap[key] || 0) + Number(s.room_revenue_usd)
      })
    } else {
      ;(restRevRows || []).forEach(s => {
        const [y, m] = s.revenue_date.split('-')
        const key = `${y}-${Number(m)}`
        actualMap[key] = (actualMap[key] || 0) + (Number(s.food_amount_usd) || 0)
      })
    }
    setActuals(actualMap)
  }"""

content = content.replace(old_loadall, new_loadall)


old_ancillary = """      // Inject Restaurant Table Revenue into Hotel F&B Revenue Actuals
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

new_ancillary = """      // Inject Restaurant Table Revenue into Hotel F&B Revenue Actuals
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
      } else if (activeProduct === 'restaurant' && restRev) {
        // In restaurant, the main Food Sales (4010) is handled above. 
        // Beverage Sales is 4011. Other Operating Income is 4019.
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          const bevKey = `4011-${m}`
          aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
        })
      }"""
content = content.replace(old_ancillary, new_ancillary)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
