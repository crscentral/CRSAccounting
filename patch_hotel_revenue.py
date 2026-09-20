import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# 1. Update restRevenue query
old_query = "activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd, collected_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })"
new_query = "activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd, total_amount_usd, collected_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to).order('revenue_date', { ascending: false }) : Promise.resolve({ data: [] })"
content = content.replace(old_query, new_query)

# 2. Add Pending to Room Revenue table
old_room_table = """          { key: 'room_revenue_collected', label: 'Collected', render: r => <div><span className="font-semibold">{cp.fmt(r.room_revenue_collected_usd)}</span><div className="text-[10px] text-slate-500">({cp.fmt(r.manual_room_revenue_collected_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => ("""
new_room_table = """          { key: 'room_revenue_collected', label: 'Collected', render: r => <div><span className="font-semibold">{cp.fmt(r.room_revenue_collected_usd)}</span><div className="text-[10px] text-slate-500">({cp.fmt(r.manual_room_revenue_collected_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },
          { key: 'pending_collection', label: 'Pending Collection', render: r => <span className="font-semibold text-red-500">{cp.fmt((r.room_revenue_usd || 0) - (r.room_revenue_collected_usd || 0))}</span> },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => ("""
content = content.replace(old_room_table, new_room_table)

# 3. Add F&B Table & add columns to Other Revenue Table
old_other_table = """      <h3 className="font-semibold text-slate-700 mb-3 mt-6 flex items-center justify-between">
        <span>Other Revenue (Extra Bed, Early Check-in, Late Check-out, Breakfast, Transportation, SPA, etc.)</span>
        {can(['owner', 'admin', 'accountant']) && (
          <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Revenue Head</button>
        )}
      </h3>
      <DataTable
        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'account', label: 'Revenue Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => ("""

new_other_table = """      {activeProduct === 'hotel' && (
        <>
          <h3 className="font-semibold text-slate-700 mb-3 mt-6">F&B Revenue</h3>
          <DataTable
            columns={[
              { key: 'revenue_date', label: 'Date' },
              { key: 'meal_period', label: 'Meal Period' },
              { key: 'total_amount_usd', label: 'Total F&B Rev', render: r => cp.fmt(r.total_amount_usd) },
              { key: 'collected_usd', label: 'Collected', render: r => cp.fmt(r.collected_usd) },
              { key: 'pending_collection', label: 'Pending Collection', render: r => <span className="font-semibold text-red-500">{cp.fmt((r.total_amount_usd || 0) - (r.collected_usd || 0))}</span> },
            ]}
            data={restRevenue}
            emptyState="No F&B revenue entries in this range."
          />
        </>
      )}

      <h3 className="font-semibold text-slate-700 mb-3 mt-6 flex items-center justify-between">
        <span>Other Revenue (Extra Bed, Early Check-in, Late Check-out, Breakfast, Transportation, SPA, etc.)</span>
        {can(['owner', 'admin', 'accountant']) && (
          <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Revenue Head</button>
        )}
      </h3>
      <DataTable
        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'account', label: 'Revenue Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
          { key: 'collected_usd', label: 'Collected', render: r => cp.fmt(r.collected_usd || 0) },
          { key: 'pending_usd', label: 'Pending Collection', render: r => <span className="text-red-500 font-medium">{cp.fmt((r.amount_usd || 0) - (r.collected_usd || 0))}</span> },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => ("""
content = content.replace(old_other_table, new_other_table)


# 4. AncillaryRevenueFormModal Additions
old_ancillary_state = """  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')"""
new_ancillary_state = """  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [collected, setCollected] = useState(editingRow?.collected ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')"""
content = content.replace(old_ancillary_state, new_ancillary_state)

old_ancillary_payload = """      const payload = {
        company_id: companyId, product, entry_date: entryDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }"""
new_ancillary_payload = """      const payload = {
        company_id: companyId, product, entry_date: entryDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        collected: Number(collected) || 0, collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,
        notes: notes || null,
      }"""
content = content.replace(old_ancillary_payload, new_ancillary_payload)


old_ancillary_ui = """          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">"""
new_ancillary_ui = """          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collected} onChange={e => setCollected(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">"""
content = content.replace(old_ancillary_ui, new_ancillary_ui)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)

