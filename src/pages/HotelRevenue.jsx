import { useEffect, useState } from 'react'
import { Plus, Trash2, BedDouble } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import AccountFormModal from '../components/AccountFormModal'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function HotelRevenue() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [roomModalOpen, setRoomModalOpen] = useState(false)
  const [ancillaryModalOpen, setAncillaryModalOpen] = useState(false)
  const [newHeadModalOpen, setNewHeadModalOpen] = useState(false)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [roomStats, setRoomStats] = useState([])
  const [ancillary, setAncillary] = useState([])
  const [revenueAccounts, setRevenueAccounts] = useState([])

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadAll() {
    const [{ data: room }, { data: anc }, { data: accs }] = await Promise.all([
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to).order('stat_date', { ascending: false }),
      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to).order('entry_date', { ascending: false }),
      supabase.from('accounts').select('id, code, name').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').neq('code', '4010').order('code'),
    ])
    setRoomStats(room || [])
    setAncillary(anc || [])
    setRevenueAccounts(accs || [])
  }

  async function handleDeleteRoom(row) {
    if (!confirm('Delete this room revenue entry?')) return
    await supabase.from('hotel_room_stats').delete().eq('id', row.id)
    loadAll()
  }
  async function handleDeleteAncillary(row) {
    if (!confirm('Delete this entry?')) return
    await supabase.from('hotel_revenue_entries').delete().eq('id', row.id)
    loadAll()
  }

  async function generateRevenueReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const [{ data: room }, { data: anc }] = await Promise.all([
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to).order('stat_date', { ascending: false }),
      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to).order('entry_date', { ascending: false }),
    ])
    const sections = [
      { heading: 'Room Revenue', columns: ['Date', 'Rooms Occupied', 'Room Revenue', 'Collected'], rows: (room || []).map(r => [r.stat_date, r.rooms_occupied, f(r.room_revenue_usd), f(r.room_revenue_collected_usd)]) },
      { heading: 'Ancillary Revenue', columns: ['Date', 'Head', 'Amount', 'Notes'], rows: (anc || []).map(r => [r.entry_date, r.account ? `${r.account.code} - ${r.account.name}` : '—', f(r.amount_usd), r.notes || '—']) },
    ]
    const title = 'Daily Revenue Collection'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'daily_revenue_collection' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'daily_revenue_collection' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'daily_revenue_collection' })
  }

  if (!activeCompany) return null

  const totalRoomRevenue = roomStats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const totalAncillary = ancillary.reduce((s, r) => s + Number(r.amount_usd), 0)

  return (
    <div>
      <PageHeader
        title="Daily Revenue Collection"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button onClick={() => setRoomModalOpen(true)} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <BedDouble size={15} /> Room Revenue
                </button>
                <button onClick={() => setAncillaryModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={15} /> Other Revenue
                </button>
              </>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Room Revenue" value={cp.fmt(totalRoomRevenue)} tone="green" />
        <KpiCard label="Room Revenue Collected" value={cp.fmt(totalCollected)} tone="blue" />
        <KpiCard label="Ancillary Revenue" value={cp.fmt(totalAncillary)} tone="gold" />
      </div>

      <h3 className="font-semibold text-slate-700 mb-3">Room Revenue</h3>
      <DataTable
        columns={[
          { key: 'stat_date', label: 'Date' },
          { key: 'rooms_occupied', label: 'Rooms Occupied' },
          { key: 'room_revenue_usd', label: 'Room Revenue', render: r => cp.fmt(r.room_revenue_usd) },
          { key: 'room_revenue_collected_usd', label: 'Collected', render: r => cp.fmt(r.room_revenue_collected_usd) },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <button onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button> }] : []),
        ]}
        rows={roomStats}
        emptyMessage="No room revenue entries in this range."
      />

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
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <button onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button> }] : []),
        ]}
        rows={ancillary}
        emptyMessage="No other revenue entries in this range."
      />

      {roomModalOpen && (
        <RoomRevenueFormModal companyId={activeCompany.id} product={activeProduct} onClose={() => setRoomModalOpen(false)} onSaved={loadAll} />
      )}
      {ancillaryModalOpen && (
        <AncillaryRevenueFormModal companyId={activeCompany.id} product={activeProduct} accounts={revenueAccounts} onClose={() => setAncillaryModalOpen(false)} onSaved={loadAll} />
      )}
      {newHeadModalOpen && (
        <AccountFormModal companyId={activeCompany.id} product={activeProduct} account={{ type: 'Revenue', subtype: 'Front Office' }} onClose={() => setNewHeadModalOpen(false)} onSaved={loadAll} />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Daily Revenue Collection"
          fields={[{ type: 'currency', key: 'currency', default: cp.displayCurrency }, { type: 'period', key: 'period', default: 'ALL_TIME' }]}
          onGenerate={generateRevenueReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function RoomRevenueFormModal({ companyId, product, onClose, onSaved }) {
  const [statDate, setStatDate] = useState(new Date().toISOString().slice(0, 10))
  const [roomsOccupied, setRoomsOccupied] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [roomRevenue, setRoomRevenue] = useState('')
  const [collected, setCollected] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!statDate || Number(roomRevenue) <= 0) { setError('Date and Room Revenue are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const { error: err } = await supabase.from('hotel_room_stats').upsert({
        company_id: companyId, product, stat_date: statDate, rooms_occupied: Number(roomsOccupied) || 0,
        currency, fx_rate_locked: fxRate,
        room_revenue: Number(roomRevenue), room_revenue_collected: Number(collected) || 0,
        room_revenue_usd: Math.round(Number(roomRevenue) / fxRate * 100) / 100,
        room_revenue_collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,
        notes: notes || null,
      }, { onConflict: 'company_id,product,stat_date' })
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title="Room Revenue Entry" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Date *">
            <input type="date" required value={statDate} onChange={e => setStatDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Rooms Occupied *">
            <input type="number" min="0" required value={roomsOccupied} onChange={e => setRoomsOccupied(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Currency">
          <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Room Revenue *">
            <input type="number" step="0.01" min="0" required value={roomRevenue} onChange={e => setRoomRevenue(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collected} onChange={e => setCollected(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="If different from Room Revenue" />
          </Field>
        </div>
        <p className="text-[11px] text-slate-400">If Collected is less than Room Revenue, the shortfall is tracked as receivable (a guest still owes it), not as unrecorded revenue.</p>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function AncillaryRevenueFormModal({ companyId, product, accounts, onClose, onSaved }) {
  const [entryDate, setEntryDate] = useState(new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(accounts[0]?.id || '')
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!accountId || Number(amount) <= 0) { setError('Revenue head and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const { error: err } = await supabase.from('hotel_revenue_entries').insert({
        company_id: companyId, product, entry_date: entryDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      })
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title="Other Revenue Entry" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Date *">
          <input type="date" required value={entryDate} onChange={e => setEntryDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Revenue Head *">
          <select required value={accountId} onChange={e => setAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select…</option>
            {accounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}
