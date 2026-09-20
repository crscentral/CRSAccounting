import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# Remove the manual injection into totalBilled
old_injection = """    // Add restaurant daily revenue to totalBilled
    const restRevTotal = restaurantRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
    totalBilled += restRevTotal
    
    // Add missing ancillary billing to totalBilled
    const ancillaryTotal = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    totalBilled += ancillaryTotal
    
    // Add missing room revenue to totalBilled
    const manualRoomTotal = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_usd || 0), 0)
    totalBilled += manualRoomTotal"""

content = content.replace(old_injection, "")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
