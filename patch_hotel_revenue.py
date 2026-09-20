import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

old_query = "supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd')"
new_query = "supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd, collected_usd')"
content = content.replace(old_query, new_query)

old_calcs = """  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0), 0)
  
  const totalRev = totalRoomRevenue + totalAncillary + fbRev
  const totalRevCollected = totalCollected + totalAncillary + fbRev
  const pendingCollection = totalRev - totalRevCollected"""
new_calcs = """  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0), 0)
  const fbCollected = restRevenue.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  
  const totalRev = totalRoomRevenue + totalAncillary + fbRev
  const totalRevCollected = totalCollected + totalAncillary + fbCollected
  const pendingCollection = totalRev - totalRevCollected"""
content = content.replace(old_calcs, new_calcs)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
