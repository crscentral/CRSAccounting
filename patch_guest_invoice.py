with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    content = f.read()

# Add invoice_number to state
old_state = "  const [roomNumber, setRoomNumber] = useState(row?.room_number || '')"
new_state = """  const [invoiceNumber, setInvoiceNumber] = useState(row?.invoice_number || '')
  const [roomNumber, setRoomNumber] = useState(row?.room_number || '')"""
content = content.replace(old_state, new_state)

# Add invoice_number to payload
old_payload = "        company_id: companyId, product, invoice_date: invoiceDate, room_number: roomNumber || null, guest_name: guestName.trim(),"
new_payload = "        company_id: companyId, product, invoice_date: invoiceDate, invoice_number: invoiceNumber || null, room_number: roomNumber || null, guest_name: guestName.trim(),"
content = content.replace(old_payload, new_payload)

# Add field to form
old_field = """        <div className="grid grid-cols-2 gap-3">
          <Field label="Date *">
            <input type="date" required value={invoiceDate} onChange={e => setInvoiceDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Room Number">
            <input value={roomNumber} onChange={e => setRoomNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>"""
new_field = """        <div className="grid grid-cols-3 gap-3">
          <Field label="Date *">
            <input type="date" required value={invoiceDate} onChange={e => setInvoiceDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Invoice #">
            <input value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} placeholder="e.g. INV-101" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Room Number">
            <input value={roomNumber} onChange={e => setRoomNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>"""
content = content.replace(old_field, new_field)

# Add to table columns in Guest Invoices
old_col = "{ key: 'room_number', label: 'Room #' },"
new_col = "{ key: 'invoice_number', label: 'Invoice #' }, { key: 'room_number', label: 'Room #' },"
content = content.replace(old_col, new_col)

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(content)
