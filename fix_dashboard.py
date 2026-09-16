import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Fix the availableRoomNights logic
old_calc = """    const totalRooms = settings?.total_rooms || 0
    const totalOccupied = (stats || []).reduce((s, r) => s + r.rooms_occupied, 0)
    const totalRevenue = (stats || []).reduce((s, r) => s + Number(r.room_revenue_usd), 0)
    const availableRoomNights = totalRooms * (stats || []).length"""

new_calc = """    const totalRooms = settings?.total_rooms || 0
    const totalOccupied = (stats || []).reduce((s, r) => s + r.rooms_occupied, 0)
    const totalRevenue = (stats || []).reduce((s, r) => s + Number(r.room_revenue_usd), 0)
    const daysInView = Math.max(1, Math.round((new Date(cp.range.to) - new Date(cp.range.from)) / (1000 * 60 * 60 * 24)) + 1)
    const availableRoomNights = totalRooms * daysInView"""

code = code.replace(old_calc, new_calc)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
