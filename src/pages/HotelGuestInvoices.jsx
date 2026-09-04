import { useEffect, useState } from 'react'
import { Plus, Trash2, Pencil, FileCheck, CheckCircle2, AlertTriangle } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { getMTDRange, getYTDRange } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function HotelGuestInvoices() {
  const { activeCompany, activeProduct, can } = useAuth()
  const [modalOpen, setModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [rows, setRows] = useState([])
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)

  const today = new Date().toISOString().slice(0, 10)
  const mtd = getMTDRange()
  const ytd = getYTDRange(1)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct])
  useEffect(() => { if (displayCurrency === 'USD') { setRate(1); return } getLatestRate(displayCurrency).then(r => setRate(r || 1)) }, [displayCurrency])

  function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }

  async function loadAll() {
    const { data } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', ytd.from).order('invoice_date', { ascending: false })
    setRows(data || [])
  }

  async function handleDelete(row) {
    if (!confirm(`Delete invoice for ${row.guest_name}?`)) return
    await supabase.from('hotel_guest_invoices').delete().eq('id', row.id)
    loadAll()
  }

  async function generateInvoicesReport(selections, format) {
    const sections = [{
      heading: 'Guest Invoices (YTD)',
      columns: ['Date', 'Room', 'Guest', 'Check-in', 'Check-out', 'Invoice Amount', 'Collected', 'Pending'],
      rows: rows.map(r => [r.invoice_date, r.room_number || '—', r.guest_name, r.checkin_date || '—', r.checkout_date || '—', fmt(r.invoice_amount_usd), fmt(r.collected_amount_usd), fmt(r.invoice_amount_usd - r.collected_amount_usd)]),
    }]
    const title = 'Guest Invoices'
    const subtitle = `${activeCompany.name} • Year to date`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'guest_invoices' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'guest_invoices' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'guest_invoices' })
  }

  if (!activeCompany) return null

  const todayRows = rows.filter(r => r.invoice_date === today)
  const mtdRows = rows.filter(r => r.invoice_date >= mtd.from && r.invoice_date <= mtd.to)
  const ytdRows = rows // already scoped to YTD in the query

  const sum = (arr, field) => arr.reduce((s, r) => s + Number(r[field]), 0)
  const pending = (arr) => sum(arr, 'invoice_amount_usd') - sum(arr, 'collected_amount_usd')

  return (
    <div>
      <PageHeader
        title="Guest Invoices"
        subtitle={`${activeCompany.name} • Daily front-desk invoice log`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingRow(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                <Plus size={15} /> New Invoice
              </button>
            )}
          </div>
        }
      />

      <h3 className="text-xs font-semibold text-slate-400 uppercase mb-2">Today</h3>
      <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-5">
        <KpiCard label="Invoices Generated" value={fmt(sum(todayRows, 'invoice_amount_usd'))} icon={FileCheck} tone="blue" sublabel={`${todayRows.length} invoice(s)`} />
        <KpiCard label="Collected" value={fmt(sum(todayRows, 'collected_amount_usd'))} icon={CheckCircle2} tone="green" />
        <KpiCard label="Pending" value={fmt(pending(todayRows))} icon={AlertTriangle} tone="red" />
      </div>

      <h3 className="text-xs font-semibold text-slate-400 uppercase mb-2">MTD / YTD</h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="MTD Generated" value={fmt(sum(mtdRows, 'invoice_amount_usd'))} tone="slate" />
        <KpiCard label="MTD Pending" value={fmt(pending(mtdRows))} tone="amber" />
        <KpiCard label="YTD Generated" value={fmt(sum(ytdRows, 'invoice_amount_usd'))} tone="slate" />
        <KpiCard label="YTD Pending" value={fmt(pending(ytdRows))} tone="amber" />
      </div>

      <DataTable
        columns={[
          { key: 'invoice_date', label: 'Date' },
          { key: 'room_number', label: 'Room #', render: r => r.room_number || '—' },
          { key: 'guest_name', label: 'Guest Name' },
          { key: 'checkin_date', label: 'Check-in', render: r => r.checkin_date || '—' },
          { key: 'checkout_date', label: 'Check-out', render: r => r.checkout_date || '—' },
          { key: 'invoice_amount_usd', label: 'Invoice Amount', render: r => fmt(r.invoice_amount_usd) },
          { key: 'collected_amount_usd', label: 'Collected', render: r => fmt(r.collected_amount_usd) },
          { key: 'pending', label: 'Pending', render: r => fmt(r.invoice_amount_usd - r.collected_amount_usd) },
          ...(can(['owner', 'admin', 'accountant']) ? [{
            key: 'actions', label: '', render: r => (
              <div className="flex gap-2 justify-end md:justify-start">
                <button onClick={() => { setEditingRow(r); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
                <button onClick={() => handleDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            )
          }] : []),
        ]}
        rows={rows}
        emptyMessage="No guest invoices yet this year."
      />

      {modalOpen && (
        <GuestInvoiceFormModal companyId={activeCompany.id} product={activeProduct} row={editingRow} onClose={() => setModalOpen(false)} onSaved={loadAll} />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Guest Invoices"
          fields={[{ type: 'currency', key: 'currency', default: displayCurrency }]}
          onGenerate={generateInvoicesReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function GuestInvoiceFormModal({ companyId, product, row, onClose, onSaved }) {
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
      }
      if (row) {
        const { error: err } = await supabase.from('hotel_guest_invoices').update(payload).eq('id', row.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('hotel_guest_invoices').insert(payload)
        if (err) throw err
      }
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={row ? 'Edit Guest Invoice' : 'New Guest Invoice'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Date *">
            <input type="date" required value={invoiceDate} onChange={e => setInvoiceDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Room Number">
            <input value={roomNumber} onChange={e => setRoomNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Guest Name *">
          <input required value={guestName} onChange={e => setGuestName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Check-in Date">
            <input type="date" value={checkinDate} onChange={e => setCheckinDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Check-out Date">
            <input type="date" value={checkoutDate} onChange={e => setCheckoutDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Currency">
          <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Invoice Final Amount *">
            <input type="number" step="0.01" min="0" required value={invoiceAmount} onChange={e => setInvoiceAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collectedAmount} onChange={e => setCollectedAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : row ? 'Save Changes' : 'Add Invoice'}</button>
        </div>
      </form>
    </Modal>
  )
}
