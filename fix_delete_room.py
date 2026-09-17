import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

old_delete = """  async function handleDeleteRoomStat(row) {
    if (!confirm('Delete this room revenue entry?')) return
    await supabase.from('hotel_room_stats').delete().eq('id', row.id)
    loadAll()
  }"""

new_delete = """  async function handleDeleteRoomStat(row) {
    if (!confirm('Delete the manual entries for this date? (Guest Invoices will remain attached)')) return
    await supabase.from('hotel_room_stats').update({
      manual_room_revenue: 0, manual_rooms_occupied: 0, manual_room_revenue_collected: 0,
      manual_room_revenue_usd: 0, manual_room_revenue_collected_usd: 0
    }).eq('id', row.id)
    loadAll()
  }"""
code = code.replace(old_delete, new_delete)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
