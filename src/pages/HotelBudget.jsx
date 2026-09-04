import { useEffect, useState } from 'react'
import { Save, TrendingUp, AlertTriangle } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

function daysInMonth(year, month) { return new Date(year, month, 0).getDate() }

export default function HotelBudget() {
  const { activeCompany, activeProduct, can } = useAuth()
  const [totalRooms, setTotalRooms] = useState(0)
  const [savingRooms, setSavingRooms] = useState(false)
  const [startYear, setStartYear] = useState(new Date().getFullYear())
  const [rows, setRows] = useState({}) // key: "year-month" -> { occ, adr, revenue, currency }
  const [actuals, setActuals] = useState({}) // key: "year-month" -> revenue_usd actual
  const [saving, setSaving] = useState({})
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, startYear])
  useEffect(() => { if (displayCurrency === 'USD') { setRate(1); return } getLatestRate(displayCurrency).then(r => setRate(r || 1)) }, [displayCurrency])

  function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }

  async function loadAll() {
    const [{ data: settings }, { data: budgetRows }, { data: statRows }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('budget_year', startYear).lte('budget_year', startYear + 4),
      supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear + 4}-12-31`),
    ])
    setTotalRooms(settings?.total_rooms || 0)
    const rowMap = {}
    ;(budgetRows || []).forEach(b => { rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency } })
    setRows(rowMap)
    const actualMap = {}
    ;(statRows || []).forEach(s => {
      const [y, m] = s.stat_date.split('-')
      const key = `${y}-${Number(m)}`
      actualMap[key] = (actualMap[key] || 0) + Number(s.room_revenue_usd)
    })
    setActuals(actualMap)
  }

  async function saveRoomInventory() {
    setSavingRooms(true)
    await supabase.from('hotel_settings').upsert({ company_id: activeCompany.id, product: activeProduct, total_rooms: totalRooms, updated_at: new Date().toISOString() }, { onConflict: 'company_id,product' })
    setSavingRooms(false)
  }

  function updateRow(year, month, field, value) {
    const key = `${year}-${month}`
    setRows(r => {
      const current = r[key] || { occ: 0, adr: 0, revenue: 0, currency: displayCurrency }
      const next = { ...current, [field]: value }
      // Triangulation: whichever field was just typed, recompute one of the OTHER two
      // that makes least sense to also have been manually set. Priority: if occ+adr
      // present, revenue = rooms*occ%*adr*days. If adr+revenue present, occ derives.
      // If occ+revenue present, adr derives.
      const days = daysInMonth(year, month)
      const roomNights = totalRooms * days
      if (field === 'occ' || field === 'adr') {
        if (roomNights > 0 && Number(next.occ) > 0 && Number(next.adr) > 0) {
          next.revenue = Math.round(roomNights * (Number(next.occ) / 100) * Number(next.adr) * 100) / 100
        }
      } else if (field === 'revenue') {
        if (roomNights > 0 && Number(next.occ) > 0) {
          next.adr = Math.round((Number(next.revenue) / (roomNights * (Number(next.occ) / 100))) * 100) / 100
        } else if (roomNights > 0 && Number(next.adr) > 0) {
          next.occ = Math.round((Number(next.revenue) / Number(next.adr) / roomNights) * 100 * 100) / 100
        }
      }
      return { ...r, [key]: next }
    })
  }

  async function saveRow(year, month) {
    const key = `${year}-${month}`
    const row = rows[key]
    if (!row) return
    setSaving(s => ({ ...s, [key]: true }))
    const currency = row.currency || displayCurrency
    const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
    await supabase.from('hotel_room_revenue_budget').upsert({
      company_id: activeCompany.id, product: activeProduct, budget_year: year, budget_month: month,
      budgeted_occupancy_pct: Number(row.occ) || 0, budgeted_adr: Number(row.adr) || 0, budgeted_room_revenue: Number(row.revenue) || 0,
      currency, fx_rate_locked: fxRate, budgeted_room_revenue_usd: Math.round((Number(row.revenue) || 0) / fxRate * 100) / 100,
    }, { onConflict: 'company_id,product,budget_year,budget_month' })
    setSaving(s => ({ ...s, [key]: false }))
  }

  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const years = [startYear, startYear + 1, startYear + 2, startYear + 3, startYear + 4]
    const tableRows = []
    years.forEach(y => MONTH_NAMES.forEach((m, i) => {
      const key = `${y}-${i + 1}`
      const row = rows[key]
      const actualUsd = actuals[key] || 0
      if (row) tableRows.push([`${m} ${y}`, `${row.occ}%`, f(convertFromUsd(row.adr, 'USD', { USD: 1 })), f(Number(row.revenue) || 0), f(actualUsd), f((Number(row.revenue) || 0) - actualUsd)])
    }))
    const sections = [{ heading: 'Room Revenue Budget', columns: ['Month', 'Budgeted Occ %', 'Budgeted ADR', 'Budgeted Revenue', 'Actual Revenue', 'Variance'], rows: tableRows }]
    const title = 'Room Revenue Budget'
    const subtitle = `${activeCompany.name} • ${startYear}–${startYear + 4} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'room_revenue_budget' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'room_revenue_budget' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'room_revenue_budget' })
  }

  if (!activeCompany) return null

  const now = new Date()
  const thisMonthKey = `${now.getFullYear()}-${now.getMonth() + 1}`
  const thisMonthRow = rows[thisMonthKey]
  const daysElapsed = now.getDate()
  const daysInCurrentMonth = daysInMonth(now.getFullYear(), now.getMonth() + 1)
  const paceExpected = thisMonthRow ? (Number(thisMonthRow.revenue) || 0) * (daysElapsed / daysInCurrentMonth) : 0
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected

  const years = [startYear, startYear + 1, startYear + 2, startYear + 3, startYear + 4]

  return (
    <div>
      <PageHeader
        title="Room Revenue Budget"
        subtitle={`${activeCompany.name} • Feed any two of Occupancy % / ADR / Room Revenue — the third calculates automatically`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </div>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-2">Room Inventory</h3>
        <p className="text-xs text-slate-500 mb-3">Total rooms available — used to calculate Occupancy %, RevPAR, and rooms occupied from your budgeted occupancy percentage.</p>
        <div className="flex items-center gap-2">
          <input type="number" min="0" value={totalRooms} onChange={e => setTotalRooms(Number(e.target.value))} className="w-32 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          {can(['owner', 'admin', 'accountant']) && (
            <button onClick={saveRoomInventory} disabled={savingRooms} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg disabled:opacity-60">
              <Save size={14} /> {savingRooms ? 'Saving…' : 'Save'}
            </button>
          )}
        </div>
      </div>

      {thisMonthRow && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
          <KpiCard label="This Month Budget" value={fmt(Number(thisMonthRow.revenue) || 0)} icon={TrendingUp} tone="gold" />
          <KpiCard label="MTD Actual" value={fmt(mtdActual)} icon={TrendingUp} tone="green" />
          <KpiCard
            label={`Pace Variance (Day ${daysElapsed}/${daysInCurrentMonth})`}
            value={fmt(mtdPaceVariance)}
            icon={mtdPaceVariance >= 0 ? TrendingUp : AlertTriangle}
            tone={mtdPaceVariance >= 0 ? 'green' : 'red'}
            sublabel="Actual vs. where you should be by today"
          />
        </div>
      )}

      <div className="flex items-center gap-2 mb-4">
        <label className="text-sm text-slate-500">Starting Year:</label>
        <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm">
          {Array.from({ length: 8 }, (_, i) => now.getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
        <span className="text-xs text-slate-400">Shows this year + next 4 (5 years total)</span>
      </div>

      {years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year}</div>
          <table className="w-full text-sm min-w-[720px]">
            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 px-3 font-medium">Month</th>
                <th className="py-2 px-3 font-medium">Occupancy %</th>
                <th className="py-2 px-3 font-medium">ADR</th>
                <th className="py-2 px-3 font-medium">Rooms Occ.</th>
                <th className="py-2 px-3 font-medium">Budgeted Revenue</th>
                <th className="py-2 px-3 font-medium">Daily Budget</th>
                <th className="py-2 px-3 font-medium">Actual</th>
                <th className="py-2 px-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {MONTH_NAMES.map((m, i) => {
                const month = i + 1
                const key = `${year}-${month}`
                const row = rows[key] || { occ: 0, adr: 0, revenue: 0 }
                const days = daysInMonth(year, month)
                const dailyBudget = (Number(row.revenue) || 0) / days
                const roomsOcc = totalRooms > 0 ? Math.round((Number(row.occ) / 100) * totalRooms) : 0
                const actualUsd = actuals[key] || 0
                return (
                  <tr key={month} className="border-b border-slate-50 last:border-0">
                    <td className="py-1.5 px-3 font-medium text-slate-700">{m}</td>
                    <td className="py-1.5 px-3"><input type="number" step="0.1" value={row.occ || ''} onChange={e => updateRow(year, month, 'occ', e.target.value)} className="w-20 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="%" /></td>
                    <td className="py-1.5 px-3"><input type="number" step="0.01" value={row.adr || ''} onChange={e => updateRow(year, month, 'adr', e.target.value)} className="w-24 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="ADR" /></td>
                    <td className="py-1.5 px-3 text-slate-500">{roomsOcc}</td>
                    <td className="py-1.5 px-3"><input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-28 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" /></td>
                    <td className="py-1.5 px-3 text-slate-500">{fmt(dailyBudget)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{fmt(actualUsd)}</td>
                    <td className="py-1.5 px-3">
                      {can(['owner', 'admin', 'accountant']) && (
                        <button onClick={() => saveRow(year, month)} disabled={saving[key]} className="text-navy-600 hover:text-navy-800 text-xs font-medium disabled:opacity-50">{saving[key] ? 'Saving…' : 'Save'}</button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ))}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Room Revenue Budget"
          fields={[{ type: 'currency', key: 'currency', default: displayCurrency }]}
          onGenerate={generateBudgetReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
