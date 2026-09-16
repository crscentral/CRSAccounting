import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    code = f.read()

# Replace availableRoomNights logic
old_calc = """  const totalOccupied = stats.reduce((s, r) => s + r.rooms_occupied, 0)
  const totalRevenue = stats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = stats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const availableRoomNights = totalRooms * stats.length"""

new_calc = """  const totalOccupied = stats.reduce((s, r) => s + r.rooms_occupied, 0)
  const totalRevenue = stats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = stats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  
  const currentRange = rangeFor(view)
  const daysInView = Math.max(1, Math.round((new Date(currentRange.to) - new Date(currentRange.from)) / (1000 * 60 * 60 * 24)) + 1)
  const availableRoomNights = totalRooms * daysInView"""

code = code.replace(old_calc, new_calc)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(code)
