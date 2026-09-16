import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Add totalRooms state
code = code.replace(
    "const [revenueAccounts, setRevenueAccounts] = useState([])",
    "const [revenueAccounts, setRevenueAccounts] = useState([])\n  const [totalRooms, setTotalRooms] = useState(0)"
)

# Fetch settings
code = code.replace(
    "const [{ data: room }, { data: anc }, { data: accs }] = await Promise.all([",
    "const [{ data: room }, { data: anc }, { data: accs }, { data: settings }] = await Promise.all(["
)
code = code.replace(
    "eq('type', 'Revenue').neq('code', '4010').order('code'),\n    ])",
    "eq('type', 'Revenue').neq('code', '4010').order('code'),\n      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),\n    ])"
)
code = code.replace(
    "setRevenueAccounts(accs || [])\n  }",
    "setRevenueAccounts(accs || [])\n    setTotalRooms(settings?.total_rooms || 0)\n  }"
)

# Open Edit Room
code = code.replace(
    "async function handleDeleteRoom(row) {",
    """function openEditRoom(row) {
    setMode('room')
    setEditingId(row.id)
    setStatDate(row.stat_date)
    setRoomsOccupied(row.rooms_occupied)
    setCurrency(row.currency || 'USD')
    setRoomRevenue(row.room_revenue)
    setCollected(row.room_revenue_collected)
    setNotes(row.notes || '')
    setModalOpen(true)
  }

  async function handleDeleteRoom(row) {"""
)
code = code.replace(
    "const [editingId, setEditingId] = useState(null)",
    "// const [editingId, setEditingId] = useState(null)" # Wait, is editingId already defined? Let's check
)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
