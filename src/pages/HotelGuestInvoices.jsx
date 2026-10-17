import { getLocalDate } from '../lib/dateUtils'
import { useEffect, useState, useMemo } from 'react'
import { Plus, Trash2, Pencil, FileCheck, CheckCircle2, AlertTriangle, ArrowRightLeft } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { getMTDRange, getYTDRange, MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney, formatReportMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import InvoiceDownloadMenu from '../components/InvoiceDownloadMenu'
import InvoicePreviewModal from '../components/InvoicePreviewModal'

export default function HotelGuestInvoices() {
  const { activeCompany, activeProduct, activeRole, can } = useAuth()
  const cp = useCurrencyAndPeriod('YTD')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [rows, setRows] = useState([])

  const today = getLocalDate()
  const mtd = getMTDRange()
  const ytd = getYTDRange(1)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  const fmt = cp.fmt

  async function loadAll() {
    const minFrom = cp.range.from < ytd.from ? cp.range.from : ytd.from
    const maxTo = cp.range.to > ytd.to ? cp.range.to : (cp.range.to === '9999-12-31' ? today : ytd.to)
    // Fetch with a 60-day buffer backwards so cross-month stays (e.g. checkin Sep 30, stay in Oct) are included
    const bufferFromDate = new Date(new Date(minFrom).getTime() - 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    const { data } = await supabase.from('hotel_guest_invoices')
      .select('*')
      .eq('company_id', activeCompany.id)
      .eq('product', activeProduct)
      .gte('invoice_date', bufferFromDate)
      .lte('invoice_date', maxTo)
      .order('invoice_date', { ascending: false })
    setRows(data || [])
  }

  async function handleDelete(row) {
    if (!confirm(`Delete invoice for ${row.guest_name}?`)) return
    await supabase.from('hotel_guest_invoices').delete().eq('id', row.id)
    loadAll()
  }

  // Helper: distributes invoice room revenue across stay dates (check-in to check-out)
  function getStayRevenueInRange(r, from, to) {
    const fx = Number(r.fx_rate_locked) || 1
    const totalRoomRev = Number(r.room_revenue) || 0
    const totalNights = Number(r.nights) || 0
    let revUsd = 0
    let collUsd = 0

    // 1. Room revenue distributed by stay nights
    if (totalNights > 0 && r.checkin_date) {
      const dailyRevUsd = (totalRoomRev / totalNights) / fx
      const totalInvUsd = Number(r.invoice_amount_usd) || (Number(r.invoice_amount) / fx) || 1
      const totalCollUsd = Number(r.collected_amount_usd) || (Number(r.collected_amount) / fx) || 0
      const collRatio = totalInvUsd > 0 ? (totalCollUsd / totalInvUsd) : 0
      const dailyCollUsd = dailyRevUsd * collRatio

      const [y, m, d] = r.checkin_date.split('-').map(Number)
      for (let i = 0; i < totalNights; i++) {
        const curDate = new Date(Date.UTC(y, m - 1, d + i)).toISOString().split('T')[0]
        if (curDate >= from && (to === '9999-12-31' || curDate <= to)) {
          revUsd += dailyRevUsd
          collUsd += dailyCollUsd
        }
      }
    } else {
      if (r.invoice_date >= from && (to === '9999-12-31' || r.invoice_date <= to)) {
        revUsd += totalRoomRev / fx
        const totalInvUsd = Number(r.invoice_amount_usd) || (Number(r.invoice_amount) / fx) || 1
        const totalCollUsd = Number(r.collected_amount_usd) || (Number(r.collected_amount) / fx) || 0
        collUsd += (totalRoomRev / fx) * (totalInvUsd > 0 ? totalCollUsd / totalInvUsd : 0)
      }
    }

    // 2. Ancillary revenue counted on invoice_date
    if (r.invoice_date >= from && (to === '9999-12-31' || r.invoice_date <= to)) {
      const otherRevUsd = Math.max(0, (Number(r.invoice_amount_usd) || 0) - (totalRoomRev / fx))
      const totalInvUsd = Number(r.invoice_amount_usd) || (Number(r.invoice_amount) / fx) || 1
      const totalCollUsd = Number(r.collected_amount_usd) || (Number(r.collected_amount) / fx) || 0
      const collRatio = totalInvUsd > 0 ? (totalCollUsd / totalInvUsd) : 0
      revUsd += otherRevUsd
      collUsd += otherRevUsd * collRatio
    }

    return { revUsd, collUsd }
  }

  const sumRangeRev = (from, to) => rows.reduce((s, r) => s + getStayRevenueInRange(r, from, to).revUsd, 0)
  const sumRangeColl = (from, to) => rows.reduce((s, r) => s + getStayRevenueInRange(r, from, to).collUsd, 0)
  const pendingRange = (from, to) => Math.max(0, sumRangeRev(from, to) - sumRangeColl(from, to))

  const todayRev = sumRangeRev(today, today)
  const todayColl = sumRangeColl(today, today)
  const todayPend = pendingRange(today, today)
  const todayCount = rows.filter(r => r.invoice_date === today || (r.checkin_date <= today && r.checkout_date > today)).length

  const selectedMonthNum = cp.periodProps?.selectedMonth || (new Date().getMonth() + 1)
  const monthName = MONTH_NAMES[selectedMonthNum - 1] || 'Month'

  const isMonthOrMtd = cp.periodProps?.periodType === 'MTD' || cp.periodProps?.periodType === 'MONTH'
  const periodLabel = isMonthOrMtd ? `${monthName} Generated` : 'Period Generated'
  const periodPendLabel = isMonthOrMtd ? `${monthName} Pending` : 'Period Pending'

  // Calculate directly for the actively selected date range
  const periodRev = sumRangeRev(cp.range.from, cp.range.to)
  const periodPend = pendingRange(cp.range.from, cp.range.to)

  const ytdRev = sumRangeRev(ytd.from, ytd.to)
  const ytdPend = pendingRange(ytd.from, ytd.to)

  const cpRows = rows.filter(r => {
    const invMatch = r.invoice_date >= cp.range.from && (cp.range.to === '9999-12-31' || r.invoice_date <= cp.range.to)
    const stayMatch = r.checkin_date && (r.checkin_date <= (cp.range.to === '9999-12-31' ? today : cp.range.to) && (r.checkout_date || r.checkin_date) >= cp.range.from)
    return invMatch || stayMatch
  })

  async function generateInvoicesReport(selections, format) {
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = selections.f || ((usd) => formatReportMoney(usd, selections.currency, rate))

    const totInv = cpRows.reduce((s, r) => s + Number(r.invoice_amount_usd || 0), 0)
    const totCol = cpRows.reduce((s, r) => s + Number(r.collected_amount_usd || 0), 0)
    const totPend = totInv - totCol

    const invoiceRows = cpRows.map(r => [
      r.invoice_date,
      r.room_number || '—',
      r.guest_name,
      r.checkin_date || '—',
      r.checkout_date || '—',
      f(r.invoice_amount_usd),
      f(r.collected_amount_usd),
      f(Math.max(0, (Number(r.invoice_amount_usd) || 0) - (Number(r.collected_amount_usd) || 0))),
      r.notes || '—'
    ])
    if (invoiceRows.length > 0) {
      invoiceRows.push(['Total', '', '', '', '', f(totInv), f(totCol), f(totPend), ''])
    }

    const sections = [
      {
        heading: 'Summary',
        keyValuePairs: [
          ['Total Invoices', String(cpRows.length)],
          ['Total Invoice Amount', f(totInv)],
          ['Total Collected', f(totCol)],
          ['Total Pending', f(totPend)],
        ]
      },
      {
        heading: 'Guest Invoices',
        columns: [
          'Date', 'Room #', 'Guest Name', 'Check-in', 'Check-out',
          selections.currency === 'USD' ? 'Invoice Amount (USD)' : `Invoice Amount (${selections.currency} & USD)`,
          selections.currency === 'USD' ? 'Collected (USD)' : `Collected (${selections.currency} & USD)`,
          selections.currency === 'USD' ? 'Pending (USD)' : `Pending (${selections.currency} & USD)`,
          'Remarks / Notes'
        ],
        rows: invoiceRows,
      }
    ]
    const title = 'Guest Invoices'
    const subtitle = `${activeCompany.name} • ${cp.range.from} to ${cp.range.to} • ${selections.currency}`
    const logoUrl = activeCompany.logo_url
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'guest_invoices', logoUrl })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'guest_invoices' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'guest_invoices', logoUrl })
  }

  if (!activeCompany) return null

  return (
    <div>
      <PageHeader
        title="Guest Invoices"
        subtitle={`${activeCompany.name} • Daily front-desk invoice log`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
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
        <KpiCard label="Invoices Generated" value={fmt(todayRev)} icon={FileCheck} tone="blue" sublabel={`${todayCount} active / stay today`} />
        <KpiCard label="Collected" value={fmt(todayColl)} icon={CheckCircle2} tone="green" />
        <KpiCard label="Pending" value={fmt(todayPend)} icon={AlertTriangle} tone="red" />
      </div>

      <h3 className="text-xs font-semibold text-slate-400 uppercase mb-2">
        {isMonthOrMtd ? `${monthName} / YTD` : 'Period / YTD'}
      </h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label={periodLabel} value={fmt(periodRev)} tone="slate" />
        <KpiCard label={periodPendLabel} value={fmt(periodPend)} tone="amber" />
        <KpiCard label="YTD Generated" value={fmt(ytdRev)} tone="slate" />
        <KpiCard label="YTD Pending" value={fmt(ytdPend)} tone="amber" />
      </div>

      <DataTable
        compact
        columns={[
          {
            key: 'invoice_date',
            label: 'Date',
            render: r => <span className="whitespace-nowrap font-medium text-slate-700">{r.invoice_date}</span>
          },
          {
            key: 'room_number',
            label: 'Room',
            render: r => <span className="font-semibold text-slate-800">{r.room_number || '—'}</span>
          },
          {
            key: 'guest_name',
            label: 'Guest Name',
            render: r => <span className="font-medium text-slate-900 whitespace-nowrap">{r.guest_name}</span>
          },
          {
            key: 'stay_dates',
            label: 'Stay',
            render: r => (
              <div className="whitespace-nowrap text-xs leading-tight">
                <div><span className="text-slate-400 text-[10px] uppercase font-semibold mr-1">In:</span><span className="text-slate-700 font-medium">{r.checkin_date || '—'}</span></div>
                <div><span className="text-slate-400 text-[10px] uppercase font-semibold mr-1">Out:</span><span className="text-slate-700 font-medium">{r.checkout_date || '—'}</span></div>
              </div>
            )
          },
          {
            key: 'invoice_amount_usd',
            label: 'Amount',
            align: 'right',
            render: r => {
              const stayRev = getStayRevenueInRange(r, cp.range.from, cp.range.to)
              const hasStayOutside = r.checkin_date && (r.checkin_date < cp.range.from || (cp.range.to !== '9999-12-31' && r.checkout_date > cp.range.to))
              return (
                <div className="text-right">
                  <div className="font-semibold text-slate-800">{fmt(r.invoice_amount_usd)}</div>
                  {r.currency && r.currency !== 'USD' && (
                    <div className="text-[10px] text-slate-400">({Number(r.invoice_amount).toLocaleString()} {r.currency})</div>
                  )}
                  {hasStayOutside && (
                    <div className="text-[10px] text-amber-600 font-medium">In period: {fmt(stayRev.revUsd)}</div>
                  )}
                </div>
              )
            }
          },
          {
            key: 'collected_amount_usd',
            label: 'Collected',
            align: 'right',
            render: r => <div className="text-right font-medium text-slate-700">{fmt(r.collected_amount_usd)}</div>
          },
          {
            key: 'pending',
            label: 'Pending',
            align: 'right',
            render: r => {
              const pend = Math.max(0, (Number(r.invoice_amount_usd) || 0) - (Number(r.collected_amount_usd) || 0))
              return (
                <div className={`text-right font-semibold ${pend > 0.001 ? 'text-amber-600' : 'text-slate-400'}`}>
                  {fmt(pend)}
                </div>
              )
            }
          },
          {
            key: 'notes',
            label: 'Remarks / Notes',
            render: r => r.notes ? (
              <span className="text-xs text-slate-700 max-w-[140px] truncate block font-normal" title={r.notes}>
                {r.notes}
              </span>
            ) : <span className="text-slate-300">—</span>
          },
          {
            key: 'actions',
            label: '',
            align: 'right',
            render: r => (
              <div className="flex gap-2 items-center justify-end whitespace-nowrap">
                <InvoiceDownloadMenu
                  iconOnly={true}
                  type="guest"
                  company={activeCompany}
                  role={activeRole}
                  getData={async () => {
                    const accMap = {}
                    const { data: accounts } = await supabase.from('accounts').select('id, code, name').eq('company_id', activeCompany.id)
                    ;(accounts || []).forEach(a => { accMap[a.id] = `${a.code} - ${a.name}` })

                    const roomItems = (Number(r.room_revenue) > 0 || Number(r.room_rate) > 0) ? [{
                      description: `Room Stay (Room ${r.room_number || '—'})`,
                      qty: Number(r.nights) || 1,
                      unit_price: Number(r.room_rate) || 0,
                      line_total: Number(r.room_revenue) || ((Number(r.room_rate) || 0) * (Number(r.nights) || 1)),
                      tax_percent: 0
                    }] : []

                    const ancillaryItems = (r.line_items || []).map(li => ({
                      description: accMap[li.account_id] || li.description || 'Ancillary Service',
                      qty: 1,
                      unit_price: Number(li.amount) || 0,
                      line_total: Number(li.amount) || 0,
                      tax_percent: 0,
                      currency: li.currency || r.currency
                    }))

                    const allItems = [...roomItems, ...ancillaryItems]
                    if (allItems.length === 0) {
                      allItems.push({
                        description: `Guest Stay Invoice - Room ${r.room_number || '—'}`,
                        qty: 1,
                        unit_price: Number(r.invoice_amount) || 0,
                        line_total: Number(r.invoice_amount) || 0,
                        tax_percent: 0
                      })
                    }

                    const invObj = {
                      ...r,
                      amount: Number(r.invoice_amount),
                      amount_usd: Number(r.invoice_amount_usd),
                      paid_amount: Number(r.collected_amount),
                      collected_amount: Number(r.collected_amount),
                      status: (Number(r.invoice_amount) - Number(r.collected_amount || 0) <= 0.001) ? 'Paid' : 'Unpaid',
                      notes: r.notes || '',
                      due_date: r.checkout_date || r.invoice_date,
                    }

                    return {
                      invoice: invObj,
                      items: allItems,
                      contact: { name: r.guest_name }
                    }
                  }}
                />
                {can(['owner', 'admin', 'accountant']) && (
                  <>
                    <button onClick={() => { setEditingRow(r); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600" title="Edit Invoice">
                      <Pencil size={15} />
                    </button>
                    <button onClick={() => handleDelete(r)} className="text-slate-400 hover:text-red-600" title="Delete Invoice">
                      <Trash2 size={15} />
                    </button>
                  </>
                )}
              </div>
            )
          },
        ]}
        rows={cpRows}
        emptyMessage="No guest invoices yet this year."
      />

      {modalOpen && (
        <GuestInvoiceFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          company={activeCompany}
          row={editingRow}
          onClose={() => setModalOpen(false)}
          onSaved={loadAll}
        />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Guest Invoices"
          fields={[{ type: 'currency', key: 'currency', default: cp.displayCurrency }]}
          onGenerate={generateInvoicesReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function GuestInvoiceFormModal({ companyId, product, company, row, onClose, onSaved }) {
  const { activeRole } = useAuth()
  const [invoiceDate, setInvoiceDate] = useState(row?.invoice_date || getLocalDate())
  const [invoiceNumber, setInvoiceNumber] = useState(row?.invoice_number || '')
  const [roomNumber, setRoomNumber] = useState(row?.room_number || '')
  const [guestName, setGuestName] = useState(row?.guest_name || '')
  const [checkinDate, setCheckinDate] = useState(row?.checkin_date || '')
  const [checkoutDate, setCheckoutDate] = useState(row?.checkout_date || '')
  const [currency, setCurrency] = useState(row?.currency || 'USD')
  const [roomRate, setRoomRate] = useState(row?.room_rate ?? '')
  const [nights, setNights] = useState(row?.nights ?? '')
  const [notes, setNotes] = useState(row?.notes || '')
  const [previewData, setPreviewData] = useState(null)
  
  // Ancillary items now have their own currency
  const [lineItems, setLineItems] = useState(
    (row?.line_items || []).map(li => ({
      ...li,
      currency: li.currency || (row?.secondary_currency) || row?.currency || 'LAK'
    }))
  )
  
  // Separate collections per currency
  const [collectedByCurr, setCollectedByCurr] = useState(() => {
    if (row?.currency_breakdown) {
      const init = {}
      Object.entries(row.currency_breakdown).forEach(([c, val]) => {
        init[c] = val.collected !== undefined ? String(val.collected) : ''
      })
      return init
    }
    return {}
  })

  // Editable conversion rates for all non-USD currencies (1 USD = X Currency)
  const [customFxRates, setCustomFxRates] = useState(() => {
    const init = {}
    if (row?.currency_breakdown) {
      Object.entries(row.currency_breakdown).forEach(([c, val]) => {
        if (val.rate) init[c] = String(val.rate)
      })
    }
    if (row?.secondary_currency && row?.secondary_fx_rate) {
      init[row.secondary_currency] = String(row.secondary_fx_rate)
    }
    return init
  })
  const [ratesToUsd, setRatesToUsd] = useState({ USD: 1 })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [revenueAccounts, setRevenueAccounts] = useState([])

  useEffect(() => {
    supabase.from('accounts').select('id, code, name').eq('company_id', companyId).eq('product', product).eq('type', 'Revenue').neq('code', '4010').order('code')
      .then(({ data }) => setRevenueAccounts(data || []))
  }, [companyId, product])

  // Auto-calc nights if checkin and checkout dates are provided
  useEffect(() => {
    if (checkinDate && checkoutDate) {
      const d1 = new Date(checkinDate); const d2 = new Date(checkoutDate);
      const diff = Math.max(1, Math.round((d2 - d1) / 86400000));
      setNights(diff);
    }
  }, [checkinDate, checkoutDate]);

  const roomRevenue = (Number(roomRate) || 0) * (Number(nights) || 0)

  // Identify all distinct currencies present in this invoice
  const distinctCurrencies = useMemo(() => {
    const set = new Set([currency])
    lineItems.forEach(li => {
      if (li.currency) set.add(li.currency)
    })
    return Array.from(set)
  }, [currency, lineItems])

  const nonUsdCurrencies = useMemo(() => {
    return distinctCurrencies.filter(c => c !== 'USD')
  }, [distinctCurrencies])

  const secondaryCurrency = nonUsdCurrencies.find(c => c !== currency) || nonUsdCurrencies[0] || null

  // Fetch live rates for all present currencies
  useEffect(() => {
    async function fetchRates() {
      const newRates = { USD: 1 }
      for (const c of distinctCurrencies) {
        if (c !== 'USD') {
          const r = await getLatestRate(c)
          newRates[c] = r || 1
        }
      }
      setRatesToUsd(prev => ({ ...prev, ...newRates }))

      setCustomFxRates(prev => {
        const updated = { ...prev }
        let changed = false
        for (const c of distinctCurrencies) {
          if (c !== 'USD' && (!updated[c] || Number(updated[c]) <= 0)) {
            updated[c] = String(newRates[c] || 1)
            changed = true
          }
        }
        return changed ? updated : prev
      })
    }
    fetchRates()
  }, [distinctCurrencies.join(',')])

  function getRateFor(c) {
    if (c === 'USD') return 1
    const custom = Number(customFxRates[c])
    if (custom && custom > 0) return custom
    return ratesToUsd[c] || 1
  }

  function convertToUsd(amount, fromC) {
    if (!amount) return 0
    if (fromC === 'USD') return Number(amount)
    const rate = getRateFor(fromC)
    return Number(amount) / rate
  }

  function convertUsdToCurrency(amountUsd, targetC) {
    if (!amountUsd) return 0
    if (targetC === 'USD') return Number(amountUsd)
    const rate = getRateFor(targetC)
    return Number(amountUsd) * rate
  }

  function convertToPrimary(amount, fromC) {
    if (!amount) return 0
    if (fromC === currency) return Number(amount)
    const inUsd = convertToUsd(amount, fromC)
    return convertUsdToCurrency(inUsd, currency)
  }

  // Totals by currency
  const totalsByCurr = useMemo(() => {
    const totals = {}
    distinctCurrencies.forEach(c => { totals[c] = 0 })

    // Add room revenue to primary currency
    if (currency) totals[currency] = (totals[currency] || 0) + roomRevenue

    // Add ancillary line items
    lineItems.forEach(li => {
      const c = li.currency || currency
      const amt = Number(li.amount) || 0
      totals[c] = (totals[c] || 0) + amt
    })
    return totals
  }, [distinctCurrencies, currency, roomRevenue, lineItems])

  const hasAnyExplicitCollection = useMemo(() => {
    return Object.values(collectedByCurr).some(v => v !== undefined && v !== '' && !isNaN(Number(v)))
  }, [collectedByCurr])

  function getCollectedFor(c) {
    if (hasAnyExplicitCollection) {
      const val = collectedByCurr[c]
      return (val !== undefined && val !== '') ? Number(val) : 0
    }
    return totalsByCurr[c] || 0
  }

  // Combined Invoice Final Amount in USD
  const finalInvoiceAmountUsd = useMemo(() => {
    let sumUsd = 0
    distinctCurrencies.forEach(c => {
      sumUsd += convertToUsd(totalsByCurr[c] || 0, c)
    })
    return Math.round(sumUsd * 100) / 100
  }, [distinctCurrencies, totalsByCurr, customFxRates, ratesToUsd])

  // Combined Invoice Final Amount in primary currency
  const finalInvoiceAmount = useMemo(() => {
    if (currency === 'USD') return finalInvoiceAmountUsd
    const primRate = getRateFor(currency)
    return Math.round(finalInvoiceAmountUsd * primRate * 100) / 100
  }, [finalInvoiceAmountUsd, currency, customFxRates, ratesToUsd])

  // Combined Collected Amount in USD
  const finalCollectedAmountUsd = useMemo(() => {
    let sumUsd = 0
    distinctCurrencies.forEach(c => {
      sumUsd += convertToUsd(getCollectedFor(c), c)
    })
    return Math.round(sumUsd * 100) / 100
  }, [distinctCurrencies, collectedByCurr, totalsByCurr, hasAnyExplicitCollection, customFxRates, ratesToUsd])

  // Combined Collected Amount in primary currency
  const finalCollectedAmount = useMemo(() => {
    if (currency === 'USD') return finalCollectedAmountUsd
    const primRate = getRateFor(currency)
    return Math.round(finalCollectedAmountUsd * primRate * 100) / 100
  }, [finalCollectedAmountUsd, currency, customFxRates, ratesToUsd])

  // Balance Amount in USD: Invoice Final Amount (USD) - Total Amount Collected (USD)
  const balanceAmountUsd = useMemo(() => {
    return Math.round((finalInvoiceAmountUsd - finalCollectedAmountUsd) * 100) / 100
  }, [finalInvoiceAmountUsd, finalCollectedAmountUsd])

  // Balance Amount in primary currency
  const balanceAmountPrimary = useMemo(() => {
    if (currency === 'USD') return balanceAmountUsd
    const primRate = getRateFor(currency)
    return Math.round(balanceAmountUsd * primRate * 100) / 100
  }, [balanceAmountUsd, currency, customFxRates, ratesToUsd])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!guestName.trim() || (finalInvoiceAmountUsd <= 0 && finalInvoiceAmount <= 0)) {
      setError('Guest name and a positive total invoice amount are required.')
      return
    }
    setSaving(true)
    try {
      const primFxRate = getRateFor(currency)
      const secCurr = nonUsdCurrencies.find(c => c !== currency) || nonUsdCurrencies[0] || null
      const secFxRate = secCurr ? getRateFor(secCurr) : null

      const breakdown = {}
      distinctCurrencies.forEach(c => {
        const rev = totalsByCurr[c] || 0
        const coll = getCollectedFor(c)
        const rate = getRateFor(c)
        breakdown[c] = { revenue: rev, collected: coll, rate: rate }
      })

      const enrichedLineItems = lineItems.map(li => {
        const itemCurr = li.currency || currency
        const itemFx = getRateFor(itemCurr)
        const amt = Number(li.amount) || 0
        const amtUsd = Math.round((amt / itemFx) * 100) / 100
        return {
          ...li,
          amount: amt,
          currency: itemCurr,
          fx_rate: itemFx,
          amount_usd: amtUsd,
          collected_usd: amtUsd
        }
      })

      const payload = {
        company_id: companyId,
        product,
        invoice_date: invoiceDate,
        invoice_number: invoiceNumber || null,
        room_number: roomNumber || null,
        guest_name: guestName.trim(),
        checkin_date: checkinDate || null,
        checkout_date: checkoutDate || null,
        currency,
        fx_rate_locked: primFxRate,
        secondary_currency: secCurr,
        secondary_fx_rate: secFxRate,
        currency_breakdown: breakdown,
        room_rate: Number(roomRate) || 0,
        nights: Number(nights) || 0,
        room_revenue: roomRevenue,
        other_revenue: Math.round((finalInvoiceAmount - roomRevenue) * 100) / 100,
        line_items: enrichedLineItems,
        invoice_amount: finalInvoiceAmount,
        collected_amount: finalCollectedAmount,
        invoice_amount_usd: finalInvoiceAmountUsd,
        collected_amount_usd: finalCollectedAmountUsd,
        notes: notes.trim() || null,
      }

      if (row) {
        const { error: err } = await supabase.from('hotel_guest_invoices').update(payload).eq('id', row.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('hotel_guest_invoices').insert(payload)
        if (err) throw err
      }

      onSaved()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  function handlePreview() {
    if (!guestName.trim()) {
      setError('Guest name is required to preview the invoice.')
      return
    }
    if (finalInvoiceAmount <= 0) {
      setError('Invoice amount must be greater than zero to preview.')
      return
    }
    setError('')

    const roomItems = (Number(roomRevenue) > 0 || Number(roomRate) > 0) ? [{
      description: `Room Stay (Room ${roomNumber || '—'})`,
      qty: Number(nights) || 1,
      unit_price: Number(roomRate) || 0,
      line_total: Number(roomRevenue) || 0,
      tax_percent: 0
    }] : []

    const ancillaryItems = lineItems.map(li => {
      const acc = revenueAccounts.find(a => a.id === li.account_id)
      return {
        description: acc ? `${acc.code} - ${acc.name}` : (li.description || 'Ancillary Service'),
        qty: 1,
        unit_price: Number(li.amount) || 0,
        line_total: Number(li.amount) || 0,
        tax_percent: 0,
        currency: li.currency || currency
      }
    })

    const allItems = [...roomItems, ...ancillaryItems]
    if (allItems.length === 0) {
      allItems.push({
        description: `Guest Stay Invoice - Room ${roomNumber || '—'}`,
        qty: 1,
        unit_price: Number(finalInvoiceAmount) || 0,
        line_total: Number(finalInvoiceAmount) || 0,
        tax_percent: 0
      })
    }

    const previewInvoice = {
      invoice_number: invoiceNumber || 'INV-DRAFT',
      invoice_date: invoiceDate,
      due_date: checkoutDate || invoiceDate,
      room_number: roomNumber,
      guest_name: guestName.trim(),
      checkin_date: checkinDate,
      checkout_date: checkoutDate,
      nights: Number(nights) || 1,
      currency,
      amount: finalInvoiceAmount,
      amount_usd: finalInvoiceAmountUsd,
      paid_amount: finalCollectedAmount,
      collected_amount: finalCollectedAmount,
      notes: notes.trim() || '',
      status: (balanceAmountUsd <= 0.009) ? 'Paid' : 'Unpaid'
    }

    setPreviewData({
      invoice: previewInvoice,
      items: allItems,
      contactDisplay: guestName.trim()
    })
  }

  if (previewData) {
    return (
      <InvoicePreviewModal
        type="guest"
        invoice={previewData.invoice}
        items={previewData.items}
        company={company}
        contactDisplay={previewData.contactDisplay}
        role={activeRole}
        onBack={() => setPreviewData(null)}
        onClose={onClose}
      />
    )
  }

  return (
    <Modal title={row ? 'Edit Guest Invoice' : 'New Guest Invoice'} maxWidth="max-w-2xl" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-3 gap-3">
          <Field label="Date *">
            <input type="date" required value={invoiceDate} onChange={e => setInvoiceDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Invoice #">
            <input value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} placeholder="e.g. INV-101" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
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

        <Field label="Room Night Currency">
          <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium">
            {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
          </select>
        </Field>

        <div className="grid grid-cols-2 gap-3 border-t border-slate-200 pt-3 mt-1">
          <Field label={`Room Rate (${currency} / night)`}>
            <input type="number" step="0.01" min="0" value={roomRate} onChange={e => setRoomRate(e.target.value)} placeholder="Per night" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Nights">
            <input type="number" min="0" value={nights} onChange={e => setNights(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        {roomRevenue > 0 && (
          <div className="text-xs text-slate-500 font-medium -mt-2">
            Room Revenue Subtotal: <strong className="text-slate-800">{Number(roomRevenue).toLocaleString()} {currency}</strong>
          </div>
        )}

        {/* Other Revenue (Ancillary) Section */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2.5 mt-2">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-xs font-semibold text-slate-700 block">Other Revenue (Ancillary)</label>
              <span className="text-[11px] text-slate-400">Can be posted in a separate currency (e.g. LAK)</span>
            </div>
            <button
              type="button"
              onClick={() => setLineItems([...lineItems, { account_id: '', amount: '', currency: secondaryCurrency || 'LAK' }])}
              className="text-xs text-navy-600 font-semibold hover:text-navy-800 flex items-center gap-1 bg-white border border-navy-200 px-2 py-1 rounded shadow-sm"
            >
              <Plus size={13} /> Add Item
            </button>
          </div>

          {lineItems.map((li, i) => (
            <div key={i} className="flex gap-2 items-center w-full min-w-0">
              <select
                value={li.account_id}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].account_id = e.target.value
                  setLineItems(nu)
                }}
                className="flex-1 min-w-0 border border-slate-300 rounded py-1.5 px-2 text-sm bg-white truncate"
              >
                <option value="">Select Revenue Head...</option>
                {revenueAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
              </select>

              <select
                value={li.currency || currency}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].currency = e.target.value
                  setLineItems(nu)
                }}
                className="w-20 shrink-0 border border-slate-300 rounded py-1.5 px-1.5 text-sm bg-white font-medium text-slate-700"
              >
                {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
              </select>

              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="Amount"
                value={li.amount}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].amount = e.target.value
                  setLineItems(nu)
                }}
                className="w-28 shrink-0 border border-slate-300 rounded py-1.5 px-2 text-sm bg-white"
              />

              <button
                type="button"
                onClick={() => setLineItems(lineItems.filter((_, idx) => idx !== i))}
                className="shrink-0 text-slate-400 hover:text-red-500 p-1"
                title="Remove item"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}

          {lineItems.length === 0 && <div className="text-xs text-slate-400 italic">No extra charges added.</div>}
        </div>

        {/* Currency Breakdown & Separate Collections */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
            <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
              Currency Breakdown & Collections
            </span>
            <span className="text-[11px] text-slate-500">Enter collection per currency</span>
          </div>

          {distinctCurrencies.map(curr => {
            const rev = totalsByCurr[curr] || 0
            const currentColl = collectedByCurr[curr] !== undefined ? collectedByCurr[curr] : ''
            return (
              <div key={curr} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2 bg-white rounded border border-slate-200 shadow-sm">
                <div className="text-sm font-medium text-slate-700">
                  Total <span className="font-bold text-navy-700">{curr}</span> Rev ={' '}
                  <span className="font-bold text-slate-900">{Number(rev).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {curr}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-500 font-medium whitespace-nowrap">Collected {curr}:</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder={hasAnyExplicitCollection ? '0.00' : `Full (${rev.toFixed(2)})`}
                    value={currentColl}
                    onChange={e => setCollectedByCurr({ ...collectedByCurr, [curr]: e.target.value })}
                    className="w-32 border border-slate-300 rounded px-2.5 py-1 text-sm font-semibold text-slate-800 bg-white"
                  />
                  <div className="flex gap-1 shrink-0">
                    <button
                      type="button"
                      onClick={() => setCollectedByCurr(prev => ({ ...prev, [curr]: String(rev) }))}
                      className="px-1.5 py-1 text-[10px] font-semibold bg-slate-100 hover:bg-slate-200 text-slate-600 rounded"
                      title="Set to full revenue"
                    >
                      Full
                    </button>
                    <button
                      type="button"
                      onClick={() => setCollectedByCurr(prev => ({ ...prev, [curr]: '0' }))}
                      className="px-1.5 py-1 text-[10px] font-semibold bg-slate-100 hover:bg-slate-200 text-slate-600 rounded"
                      title="Set to 0"
                    >
                      0
                    </button>
                  </div>
                </div>
              </div>
            )
          })}

          {/* Editable Conversion Rates for all non-USD currencies selected */}
          {nonUsdCurrencies.length > 0 && (
            <div className="p-2.5 bg-amber-50/80 rounded border border-amber-200 text-xs space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-amber-900">
                <ArrowRightLeft size={13} />
                <span>Conversion Rates:</span>
                <span className="text-[10px] text-amber-700 font-normal italic">(Editable - 1 USD to currency)</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {nonUsdCurrencies.map(c => (
                  <div key={c} className="flex items-center justify-between gap-1.5 bg-white p-2 rounded border border-amber-200 shadow-sm">
                    <span className="text-slate-700 font-medium whitespace-nowrap">1 USD =</span>
                    <input
                      type="number"
                      step="0.0001"
                      min="0"
                      value={customFxRates[c] !== undefined ? customFxRates[c] : ''}
                      onChange={e => setCustomFxRates(prev => ({ ...prev, [c]: e.target.value }))}
                      className="w-28 border border-amber-300 rounded px-2 py-1 text-xs font-bold text-amber-950 bg-white shadow-inner"
                    />
                    <span className="text-slate-800 font-semibold">{c}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Remarks / Notes */}
        <Field label="Remarks / Notes">
          <textarea
            rows={2}
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="Add any remarks, special requests, or notes..."
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-navy-500"
          />
        </Field>

        {/* Final Invoice Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 border-t border-slate-200 pt-3">
          <div className="flex flex-col bg-slate-50 border border-slate-200 rounded-lg p-3">
            <span className="text-xs font-semibold text-slate-700 mb-1">Invoice Final Amount (USD) *</span>
            <div className="text-base font-bold text-slate-900">
              ${Number(finalInvoiceAmountUsd).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {currency !== 'USD' && (
              <div className="text-[11px] font-normal text-slate-500 mt-0.5">
                ≈ {Number(finalInvoiceAmount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency}
              </div>
            )}
          </div>

          <div className="flex flex-col bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <span className="text-xs font-semibold text-emerald-800 mb-1">Total Amount Collected (USD)</span>
            <div className="text-base font-bold text-emerald-900">
              ${Number(finalCollectedAmountUsd).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {currency !== 'USD' && (
              <div className="text-[11px] font-normal text-emerald-700 mt-0.5">
                ≈ {Number(finalCollectedAmount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency}
              </div>
            )}
          </div>

          <div className={`flex flex-col rounded-lg p-3 border ${
            balanceAmountUsd > 0.009 
              ? 'bg-amber-50 border-amber-200 text-amber-900' 
              : balanceAmountUsd < -0.009
              ? 'bg-blue-50 border-blue-200 text-blue-900'
              : 'bg-slate-50 border-slate-200 text-slate-800'
          }`}>
            <span className="text-xs font-semibold mb-1">Balance Amount (USD)</span>
            <div className="text-base font-bold">
              ${Number(Math.abs(balanceAmountUsd)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              {balanceAmountUsd > 0.009 && <span className="text-xs font-medium text-amber-700 ml-1.5">(Pending)</span>}
              {balanceAmountUsd < -0.009 && <span className="text-xs font-medium text-blue-700 ml-1.5">(Overpaid)</span>}
              {Math.abs(balanceAmountUsd) <= 0.009 && <span className="text-xs font-medium text-emerald-600 ml-1.5">(Settled)</span>}
            </div>
            {currency !== 'USD' && (
              <div className="text-[11px] font-normal text-slate-500 mt-0.5">
                ≈ {Number(Math.abs(balanceAmountPrimary)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency}
              </div>
            )}
          </div>
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex flex-col sm:flex-row gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600 hover:bg-slate-50">Cancel</button>
          <button type="button" onClick={handlePreview} className="flex-1 border border-navy-300 text-navy-700 hover:bg-navy-50 rounded-lg py-2 text-sm font-medium">Preview</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
            {saving ? 'Saving…' : row ? 'Save Changes' : 'Add Invoice'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
