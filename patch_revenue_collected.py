with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# Replace the fake collected logic with the real invoiced_room_revenue_collected_usd
old_col_render = "{ key: 'room_revenue_collected', label: 'Collected', render: r => <div><span className=\"font-semibold\">{cp.fmt(r.room_revenue_collected_usd)}</span><div className=\"text-[10px] text-slate-500\">({cp.fmt(r.manual_room_revenue_collected_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },"
new_col_render = "{ key: 'room_revenue_collected', label: 'Collected', render: r => <div><span className=\"font-semibold\">{cp.fmt(r.room_revenue_collected_usd)}</span><div className=\"text-[10px] text-slate-500\">({cp.fmt(r.manual_room_revenue_collected_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_collected_usd||0)} inv.)</div></div> },"
content = content.replace(old_col_render, new_col_render)

# Total collected logic is already right?
#   const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0) + ancRoom.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
# But wait, does room_revenue_collected_usd in the DB automatically include the invoiced portion now?
# Let's check how room_revenue_collected_usd is generated in hotel_room_stats. Is it a generated column?
