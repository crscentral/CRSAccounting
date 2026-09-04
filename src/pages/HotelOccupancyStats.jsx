import { useEffect, useState } from 'react'
import { BedDouble, Percent, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { getMTDRange, getYTDRange, getYearRange } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

const VIEWS = [
  { key: 'last_night', label: 'Last Night' },
  { key: 'last_30', label: 'Last 30 Days' },
  { key: 'last_year_daily', label: 'Each Day, Last Year' },
  { key: 'mtd', label: 'MTD' },
  { key: 'ytd', label: 'YTD' },
]

export default function HotelOccupancyStats() {
  const { activeCompany, activeProduct } = useAuth()
  const [view, setView] = useState('mtd')
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [totalRooms, setTotalRooms] = useState(0)
  const [stats, setStats] = useState([])
  const [budget, setBudget] = useState([])
  const [gop, setGop] = useState(0)
  const [loading, setLoading] = useState(true)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, view])
  useEffect(() => { if (displayCurrency === 'USD') { setRate(1); return } getLatestRate(displayCurrency).then(r => setRate(r || 1)) }, [displayCurrency])

  function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }

  function rangeFor(v) {
    const today = new Date()
    if (v === 'last_night') { const d = new Date(today); d.setDate(d.getDate() - 1); const s = d.toISOString().slice(0, 10); return { from: s, to: s } }
    if (v === 'last_30') { const d = new Date(today); d.setDate(d.getDate() - 30); return { from: d.toISOString().slice(0, 10), to: today.toISOString().slice(0, 10) } }
    if (v === 'last_year_daily') return getYearRange(today.getFullYear() - 1)
    if (v === 'mtd') return getMTDRange()
    return getYTDRange(1)
  }

  async function loadAll() {
    setLoading(true)
    const range = rangeFor(view)
    const [{ data: settings }, { data: statRows }, { data: budgetRows }, { data: accounts }, { data: entries }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to).order('stat_date'),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('accounts').select('id, type, subtype, name').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
    ])
    setTotalRooms(settings?.total_rooms || 0)
    setStats(statRows || [])
    setBudget(budgetRows || [])

    // GOP for GOPPAR: Revenue - Operating Expenses (excludes Below-GOP items)
    const balances = {}
    ;(entries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })
    const byType = (t) => (accounts || []).filter(a => a.type === t)
    const revenue = -byType('Revenue').reduce((s, a) => s + (balances[a.id] || 0), 0)
    const operatingExp = byType('Expenses').filter(a => !['Below GOP', 'Below EBITDA'].includes(a.subtype)).reduce((s, a) => s + (balances[a.id] || 0), 0)
    setGop(revenue - operatingExp)

    setLoading(false)
  }

  async function generateStatsReport(selections, format) {
    const range = rangeFor(view)
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to).order('stat_date')
    const rows = statRows || []
    const sections = [{
      heading: `Occupancy & Revenue Statistics — ${VIEWS.find(v => v.key === view)?.label}`,
      columns: ['Date', 'Rooms Occupied', 'Occupancy %', 'ADR', 'RevPAR', 'Room Revenue', 'Collected'],
      rows: rows.map(r => {
        const occPct = totalRooms > 0 ? ((r.rooms_occupied / totalRooms) * 100).toFixed(1) + '%' : '—'
        const adr = r.rooms_occupied > 0 ? f(r.room_revenue_usd / r.rooms_occupied) : '—'
        const revpar = totalRooms > 0 ? f(r.room_revenue_usd / totalRooms) : '—'
        return [r.stat_date, r.rooms_occupied, occPct, adr, revpar, f(r.room_revenue_usd), f(r.room_revenue_collected_usd)]
      }),
    }]

    const title = 'Hotel Revenue & Occupancy Statistics'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'hotel_occupancy_stats' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_occupancy_stats' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_occupancy_stats' })
  }

  if (!activeCompany) return null

  const totalOccupied = stats.reduce((s, r) => s + r.rooms_occupied, 0)
  const totalRevenue = stats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = stats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const availableRoomNights = totalRooms * stats.length
  const occupancyPct = availableRoomNights > 0 ? (totalOccupied / availableRoomNights) * 100 : 0
  const adr = totalOccupied > 0 ? totalRevenue / totalOccupied : 0
  const revpar = availableRoomNights > 0 ? totalRevenue / availableRoomNights : 0
  const goppar = availableRoomNights > 0 ? gop / availableRoomNights : 0

  // Budget comparison
  const now = new Date()
  const thisMonthBudget = budget.find(b => b.budget_year === now.getFullYear() && b.budget_month === now.getMonth() + 1)
  const ytdBudget = budget.filter(b => b.budget_year === now.getFullYear() && b.budget_month <= now.getMonth() + 1).reduce((s, b) => s + Number(b.budgeted_room_revenue_usd), 0)
  const variance = (view === 'mtd' && thisMonthBudget) ? totalRevenue - Number(thisMonthBudget.budgeted_room_revenue_usd)
    : (view === 'ytd' ? totalRevenue - ytdBudget : null)

  const chartData = stats.map(r => ({
    date: r.stat_date,
    'Occupancy %': totalRooms > 0 ? Number(((r.rooms_occupied / totalRooms) * 100).toFixed(1)) : 0,
    ADR: r.rooms_occupied > 0 ? Math.round(r.room_revenue_usd / r.rooms_occupied) : 0,
  }))

  return (
    <div>
      <PageHeader
        title="Revenue & Occupancy Statistics"
        subtitle={`${activeCompany.name} • ${totalRooms} rooms in inventory`}
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

      <div className="flex gap-1 bg-slate-100 rounded-lg p-1 mb-6 overflow-x-auto">
        {VIEWS.map(v => (
          <button key={v.key} onClick={() => setView(v.key)} className={`px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap ${view === v.key ? 'bg-white shadow text-navy-700' : 'text-slate-500'}`}>{v.label}</button>
        ))}
      </div>

      {totalRooms === 0 && (
        <div className="bg-amber-50 border border-amber-100 rounded-lg px-4 py-2.5 text-xs text-amber-700 mb-5 flex items-center gap-2">
          <AlertTriangle size={14} /> Set your total room inventory on the Room Revenue Budget page — Occupancy %, RevPAR, and GOPPAR need it to calculate correctly.
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-400 text-center py-10">Loading…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
            <KpiCard label="Occupancy %" value={`${occupancyPct.toFixed(1)}%`} icon={Percent} tone="blue" />
            <KpiCard label="Rooms Occupied" value={totalOccupied} icon={BedDouble} tone="slate" />
            <KpiCard label="ADR" value={fmt(adr)} icon={DollarSign} tone="green" />
            <KpiCard label="RevPAR" value={fmt(revpar)} icon={TrendingUp} tone="gold" />
            <KpiCard label="GOPPAR" value={fmt(goppar)} icon={TrendingUp} tone="blue" sublabel="GOP per available room" />
            <KpiCard label="Total Room Revenue" value={fmt(totalRevenue)} icon={DollarSign} tone="green" />
            <KpiCard label="Collected" value={fmt(totalCollected)} icon={DollarSign} tone="slate" />
            {variance !== null && (
              <KpiCard label={`Budget Variance (${view === 'mtd' ? 'MTD' : 'YTD'})`} value={fmt(variance)} icon={variance >= 0 ? TrendingUp : AlertTriangle} tone={variance >= 0 ? 'green' : 'red'} />
            )}
          </div>

          {chartData.length > 1 && (
            <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
              <h3 className="font-semibold text-slate-700 mb-4">Occupancy % and ADR Trend</h3>
              <div className="h-64 sm:h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                    <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
                    <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Line yAxisId="left" type="monotone" dataKey="Occupancy %" stroke="#1B3A6B" strokeWidth={2} dot={false} />
                    <Line yAxisId="right" type="monotone" dataKey="ADR" stroke="#C9A84C" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <DataTable
            columns={[
              { key: 'stat_date', label: 'Date' },
              { key: 'rooms_occupied', label: 'Rooms Occupied' },
              { key: 'occ_pct', label: 'Occupancy %', render: r => totalRooms > 0 ? `${((r.rooms_occupied / totalRooms) * 100).toFixed(1)}%` : '—' },
              { key: 'adr', label: 'ADR', render: r => r.rooms_occupied > 0 ? fmt(r.room_revenue_usd / r.rooms_occupied) : '—' },
              { key: 'revpar', label: 'RevPAR', render: r => totalRooms > 0 ? fmt(r.room_revenue_usd / totalRooms) : '—' },
              { key: 'room_revenue_usd', label: 'Room Revenue', render: r => fmt(r.room_revenue_usd) },
              { key: 'room_revenue_collected_usd', label: 'Collected', render: r => fmt(r.room_revenue_collected_usd) },
            ]}
            rows={stats}
            emptyMessage="No room stats entered for this period yet. Add daily entries from Daily Revenue Collection."
          />
        </>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Revenue & Occupancy Statistics"
          fields={[{ type: 'currency', key: 'currency', default: displayCurrency }]}
          onGenerate={generateStatsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
