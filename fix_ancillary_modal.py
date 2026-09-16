import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Fix AncillaryRevenueFormModal
old_anc = """function AncillaryRevenueFormModal({ companyId, product, accounts, totalRooms, editingRow, roomStats, onClose, onSaved }) {
  const [statDate, setStatDate] = useState(new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(accounts[0]?.id || '')
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')"""

new_anc = """function AncillaryRevenueFormModal({ companyId, product, accounts, totalRooms, editingRow, roomStats, onClose, onSaved }) {
  const [statDate, setStatDate] = useState(editingRow?.entry_date || new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(editingRow?.account_id || accounts[0]?.id || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')"""

code = code.replace(old_anc, new_anc)

# Fix Ancillary Update
old_anc_insert = """      const { error: err } = await supabase.from('hotel_revenue_entries').insert({
        company_id: companyId, product, account_id: accountId, entry_date: statDate,
        currency, fx_rate_locked: fxRate,
        amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      })"""

new_anc_insert = """      const payload = {
        company_id: companyId, product, account_id: accountId, entry_date: statDate,
        currency, fx_rate_locked: fxRate,
        amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_revenue_entries').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_revenue_entries').insert(payload)
        err = error
      }"""

code = code.replace(old_anc_insert, new_anc_insert)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
