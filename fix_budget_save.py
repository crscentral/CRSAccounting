import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_save = """    await supabase.from('hotel_room_revenue_budget').upsert({
      company_id: activeCompany.id, product: activeProduct, budget_year: year, budget_month: month,
      budgeted_occupancy_pct: Number(row.occ) || 0, budgeted_adr: Number(row.adr) || 0, budgeted_room_revenue: Number(row.revenue) || 0,
      currency, fx_rate_locked: fxRate, budgeted_room_revenue_usd: Math.round((Number(row.revenue) || 0) / fxRate * 100) / 100,
    }, { onConflict: 'company_id,product,budget_year,budget_month' })
    setSaving(s => ({ ...s, [key]: false }))"""

new_save = """    const revenueUsd = Math.round((Number(row.revenue) || 0) / fxRate * 100) / 100
    await supabase.from('hotel_room_revenue_budget').upsert({
      company_id: activeCompany.id, product: activeProduct, budget_year: year, budget_month: month,
      budgeted_occupancy_pct: Number(row.occ) || 0, budgeted_adr: Number(row.adr) || 0, budgeted_room_revenue: Number(row.revenue) || 0,
      currency, fx_rate_locked: fxRate, budgeted_room_revenue_usd: revenueUsd,
    }, { onConflict: 'company_id,product,budget_year,budget_month' })
    setRows(r => ({ ...r, [key]: { ...r[key], revenue_usd: revenueUsd } }))
    setSaving(s => ({ ...s, [key]: false }))"""
code = code.replace(old_save, new_save)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
