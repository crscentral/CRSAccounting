import re

with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    code = f.read()

# Update the modal to handle line items and auto-calc amount
old_modal_start = """function GuestInvoiceFormModal({ companyId, product, row, onClose, onSaved }) {
  const [invoiceDate, setInvoiceDate] = useState(row?.invoice_date || new Date().toISOString().slice(0, 10))
  const [roomNumber, setRoomNumber] = useState(row?.room_number || '')
  const [guestName, setGuestName] = useState(row?.guest_name || '')
  const [checkinDate, setCheckinDate] = useState(row?.checkin_date || '')
  const [checkoutDate, setCheckoutDate] = useState(row?.checkout_date || '')
  const [currency, setCurrency] = useState(row?.currency || 'USD')
  const [invoiceAmount, setInvoiceAmount] = useState(row?.invoice_amount ?? '')
  const [collectedAmount, setCollectedAmount] = useState(row?.collected_amount ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!guestName.trim() || Number(invoiceAmount) <= 0) { setError('Guest name and a positive invoice amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, invoice_date: invoiceDate, room_number: roomNumber || null, guest_name: guestName.trim(),
        checkin_date: checkinDate || null, checkout_date: checkoutDate || null,
        currency, fx_rate_locked: fxRate,
        invoice_amount: Number(invoiceAmount), collected_amount: Number(collectedAmount) || 0,
        invoice_amount_usd: Math.round(Number(invoiceAmount) / fxRate * 100) / 100,
        collected_amount_usd: Math.round((Number(collectedAmount) || 0) / fxRate * 100) / 100,
      }"""

new_modal_start = """function GuestInvoiceFormModal({ companyId, product, row, onClose, onSaved }) {
  const [invoiceDate, setInvoiceDate] = useState(row?.invoice_date || new Date().toISOString().slice(0, 10))
  const [roomNumber, setRoomNumber] = useState(row?.room_number || '')
  const [guestName, setGuestName] = useState(row?.guest_name || '')
  const [checkinDate, setCheckinDate] = useState(row?.checkin_date || '')
  const [checkoutDate, setCheckoutDate] = useState(row?.checkout_date || '')
  const [currency, setCurrency] = useState(row?.currency || 'USD')
  const [roomRate, setRoomRate] = useState(row?.room_rate ?? '')
  const [nights, setNights] = useState(row?.nights ?? '')
  const [lineItems, setLineItems] = useState(row?.line_items || [])
  const [collectedAmount, setCollectedAmount] = useState(row?.collected_amount ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [revenueAccounts, setRevenueAccounts] = useState([])

  useEffect(() => {
    supabase.from('accounts').select('id, code, name').eq('company_id', companyId).eq('product', product).eq('type', 'Revenue').neq('code', '4010').order('code')
      .then(({ data }) => setRevenueAccounts(data || []))
  }, [companyId, product])

  const roomRevenue = (Number(roomRate) || 0) * (Number(nights) || 0)
  const otherRevenue = lineItems.reduce((s, li) => s + (Number(li.amount) || 0), 0)
  const invoiceAmount = roomRevenue + otherRevenue

  // Auto-calc nights if dates provided
  useEffect(() => {
    if (checkinDate && checkoutDate) {
      const d1 = new Date(checkinDate); const d2 = new Date(checkoutDate);
      const diff = Math.max(1, Math.round((d2 - d1) / 86400000));
      setNights(diff);
    }
  }, [checkinDate, checkoutDate]);

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!guestName.trim() || invoiceAmount <= 0) { setError('Guest name and a positive total invoice amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, invoice_date: invoiceDate, room_number: roomNumber || null, guest_name: guestName.trim(),
        checkin_date: checkinDate || null, checkout_date: checkoutDate || null,
        currency, fx_rate_locked: fxRate,
        room_rate: Number(roomRate) || 0, nights: Number(nights) || 0,
        room_revenue: roomRevenue, other_revenue: otherRevenue,
        line_items: lineItems,
        invoice_amount: invoiceAmount, collected_amount: Number(collectedAmount) || 0,
        invoice_amount_usd: Math.round(invoiceAmount / fxRate * 100) / 100,
        collected_amount_usd: Math.round((Number(collectedAmount) || 0) / fxRate * 100) / 100,
      }"""
code = code.replace(old_modal_start, new_modal_start)

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(code)
