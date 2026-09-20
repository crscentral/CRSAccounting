import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

old_kpi = """  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const totalAncillary = ancillary.reduce((s, r) => s + Number(r.amount_usd), 0)
  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0), 0)
  const fbCollected = restRevenue.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  
  const totalRev = totalRoomRevenue + totalAncillary + fbRev
  const totalRevCollected = totalCollected + totalAncillary + fbCollected
  const pendingCollection = totalRev - totalRevCollected"""

new_kpi = """  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const totalAncillary = ancillary.reduce((s, r) => s + Number(r.amount_usd), 0)
  const ancillaryCollected = ancillary.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
  const fbCollected = restRevenue.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  
  const totalRev = totalRoomRevenue + totalAncillary + fbRev
  const totalRevCollected = totalCollected + ancillaryCollected + fbCollected
  const pendingCollection = totalRev - totalRevCollected"""

content = content.replace(old_kpi, new_kpi)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
