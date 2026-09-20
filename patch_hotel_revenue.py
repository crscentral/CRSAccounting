import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# 1. Update state to hold split ancillaries
old_state = """  const [roomStats, setRoomStats] = useState([])
  const [ancillary, setAncillary] = useState([])
  const [revenueAccounts, setRevenueAccounts] = useState([])
  const [restRevenue, setRestRevenue] = useState([])"""
new_state = """  const [roomStats, setRoomStats] = useState([])
  const [ancillary, setAncillary] = useState([])
  const [ancRoom, setAncRoom] = useState([])
  const [ancFB, setAncFB] = useState([])
  const [ancOther, setAncOther] = useState([])
  const [revenueAccounts, setRevenueAccounts] = useState([])
  const [restRevenue, setRestRevenue] = useState([])"""
content = content.replace(old_state, new_state)

# 2. Update loadAll() to also fetch `subtype` for accounts
old_fetch = """      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to).order('entry_date', { ascending: false }),
      supabase.from('accounts').select('id, code, name').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').neq('code', '4010').order('code'),"""
new_fetch = """      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to).order('entry_date', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').neq('code', '4010').order('code'),"""
content = content.replace(old_fetch, new_fetch)

# 3. Update loadAll() to split ancillary
old_setAnc = """    setAncillary(anc || [])
    setRevenueAccounts(accs || [])"""
new_setAnc = """    setAncillary(anc || [])
    const aRoom = []; const aFB = []; const aOther = [];
    (anc || []).forEach(a => {
      const st = (a.account?.subtype || '').toLowerCase()
      const nm = (a.account?.name || '').toLowerCase()
      if (st.includes('f&b') || nm.includes('breakfast') || nm.includes('food') || nm.includes('beverage')) {
        aFB.push(a)
      } else if (st.includes('room') || st.includes('front office') || nm.includes('extra bed') || nm.includes('early check') || nm.includes('late check')) {
        aRoom.push(a)
      } else {
        aOther.push(a)
      }
    })
    setAncRoom(aRoom)
    setAncFB(aFB)
    setAncOther(aOther)
    setRevenueAccounts(accs || [])"""
content = content.replace(old_setAnc, new_setAnc)

# 4. Update KPI variables
old_kpi = """  const totalRoomRevenue = roomStats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const totalAncillary = ancillary.reduce((s, r) => s + Number(r.amount_usd), 0)
  const ancillaryCollected = ancillary.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
  const fbCollected = restRevenue.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)"""

new_kpi = """  const totalRoomRevenue = roomStats.reduce((s, r) => s + Number(r.room_revenue_usd), 0) + ancRoom.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0) + ancRoom.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  const totalAncillary = ancOther.reduce((s, r) => s + Number(r.amount_usd), 0)
  const ancillaryCollected = ancOther.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)
  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0) + ancFB.reduce((s, r) => s + Number(r.amount_usd), 0)
  const fbCollected = restRevenue.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0) + ancFB.reduce((s, r) => s + (Number(r.collected_usd) || 0), 0)"""
content = content.replace(old_kpi, new_kpi)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
