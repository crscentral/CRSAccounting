import { getLocalDate } from '../lib/dateUtils'
import { useEffect, useState } from 'react'
import { BedDouble, Percent, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { getMTDRange, getYTDRange, getYearRange, getMonthRange, MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney, formatReportMoney } from '../lib/fx'
import { CURRENCY_LIST, CURRENCIES } from '../lib/currencies'
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

const currentYearNum = new Date().getFullYear()
const YEAR_OPTIONS = Array.from({ length: 8 }, (_, i) => currentYearNum - 4 + i)

export default function HotelOccupancyStats() {
  const { activeCompany, activeProduct } = useAuth()
  const now = new Date()
  const [view, setView] = useState('mtd')
  const [selectedMonth, setSelectedMonth] = useState(now.getMonth() + 1)
  const [selectedMonthYear, setSelectedMonthYear] = useState(now.getFullYear())
  const [selectedYear, setSelectedYear] = useState(now.getFullYear())
  const [displayCurrency, setDisplayCurrency] = useState(activeCompany?.default_currency || activeCompany?.base_currency || 'USD')
  const [rate, setRate] = useState(1)
  const [totalRooms, setTotalRooms] = useState(0)
  const [stats, setStats] = useState([])
  const [budget, setBudget] = useState([])
  const [hotelRevTotal, setHotelRevTotal] = useState(0)
  const [roomRevTotal, setRoomRevTotal] = useState(0)
  const [hotelColTotal, setHotelColTotal] = useState(0)
  const [budgetVar, setBudgetVar] = useState(null)
  const [gop, setGop] = useState(0)
  const [loading, setLoading] = useState(true)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => {
    const nextCurr = activeCompany?.default_currency || activeCompany?.base_currency || 'USD'
    setDisplayCurrency(nextCurr)
  }, [activeCompany?.id, activeCompany?.default_currency, activeCompany?.base_currency])

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, view, selectedMonth, selectedMonthYear, selectedYear])
  useEffect(() => { if (displayCurrency === 'USD') { setRate(1); return } getLatestRate(displayCurrency).then(r => setRate(r || 1)) }, [displayCurrency])

  function fmtRounded(usd) { return formatMoney(Math.round(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate })), displayCurrency).replace('.00', '') }
  function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }

  function rangeFor(v, sm = selectedMonth, smy = selectedMonthYear, sy = selectedYear) {
    const today = new Date()
    if (v === 'last_night') { const d = new Date(today); d.setDate(d.getDate() - 1); const s = getLocalDate(d); return { from: s, to: s } }
    if (v === 'last_30') { const d = new Date(today); d.setDate(d.getDate() - 30); return { from: getLocalDate(d), to: getLocalDate(today) } }
    if (v === 'last_year_daily') return getYearRange(today.getFullYear() - 1)
    if (v === 'mtd') return getMTDRange()
    if (v === 'ytd') return getYTDRange(1)
    if (v === 'specific_month') return getMonthRange(smy, sm)
    if (v === 'specific_year') return getYearRange(sy)
    return getYTDRange(1)
  }

  async function loadAll() {
    setLoading(true)
    const range = rangeFor(view)
    const targetYear = view === 'specific_month' ? selectedMonthYear : (view === 'specific_year' ? selectedYear : now.getFullYear())
      
    const [{ data: s }, { data: b }, { data: settings }, { data: anc }, { data: restRev }, { data: expBudget }, { data: accounts }] = await Promise.all([
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to).order('stat_date', { ascending: false }),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, amount_usd, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to) : Promise.resolve({ data: [] }),
      supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', targetYear),
      supabase.from('accounts').select('id, type').eq('company_id', activeCompany.id).eq('type', 'Revenue')
    ])
    
    setStats(s || [])
    setBudget(b || [])
    setTotalRooms(settings?.total_rooms || 0)
    
    // Calculate Actuals
    const aRoom = []; const aFB = []; const aOther = [];
    (anc || []).forEach(a => {
      const st = (a.account?.subtype || '').toLowerCase()
      const nm = (a.account?.name || '').toLowerCase()
      if (st.includes('f&b') || nm.includes('breakfast') || nm.includes('food') || nm.includes('beverage')) aFB.push(a)
      else if (st.includes('room') || st.includes('front office') || nm.includes('extra bed') || nm.includes('early check') || nm.includes('late check')) aRoom.push(a)
      else aOther.push(a)
    })
    
    const ancRoomAmt = aRoom.reduce((sum, x) => sum + Number(x.amount_usd || 0), 0)
    const ancRoomCol = aRoom.reduce((sum, x) => sum + Number(x.collected_usd || 0), 0)
    const ancFBAmt = aFB.reduce((sum, x) => sum + Number(x.amount_usd || 0), 0)
    const ancFBCol = aFB.reduce((sum, x) => sum + Number(x.collected_usd || 0), 0)
    const ancOtherAmt = aOther.reduce((sum, x) => sum + Number(x.amount_usd || 0), 0)
    const ancOtherCol = aOther.reduce((sum, x) => sum + Number(x.collected_usd || 0), 0)
    
    const restAmt = (restRev || []).reduce((sum, x) => sum + (Number(x.amount_usd) || Number(x.total_amount_usd) || (Number(x.food_amount_usd||0) + Number(x.beverage_amount_usd||0) + Number(x.other_amount_usd||0))), 0)
    const restCol = (restRev || []).reduce((sum, x) => sum + Number(x.collected_usd || 0), 0)
    
    const roomRevOnly = (s || []).reduce((sum, x) => sum + Number(x.room_revenue_usd || 0), 0)
    const roomColOnly = (s || []).reduce((sum, x) => sum + Number(x.room_revenue_collected_usd || 0), 0)
    
    const tr = roomRevOnly + ancRoomAmt
    const trc = roomColOnly + ancRoomCol
    const th = tr + ancFBAmt + ancOtherAmt + restAmt
    const thc = trc + ancFBCol + ancOtherCol + restCol
    
    setRoomRevTotal(tr)
    setHotelRevTotal(th)
    setHotelColTotal(thc)
    
    // Calculate Budgets
    const isMtd = view === 'mtd'
    const isYtd = view === 'ytd'
    const isSpecMonth = view === 'specific_month'
    const isSpecYear = view === 'specific_year'
    let v = null
    if (isMtd || isYtd || isSpecMonth || isSpecYear) {
        const startMonth = isMtd ? (now.getMonth() + 1) : (isSpecMonth ? selectedMonth : 1)
        const endMonth = isMtd ? (now.getMonth() + 1) : (isSpecMonth ? selectedMonth : (isSpecYear ? 12 : now.getMonth() + 1))
        
        let roomB = 0
        for (let m = startMonth; m <= endMonth; m++) {
           const row = (b || []).find(bx => bx.budget_year === targetYear && bx.budget_month === m)
           if (row) {
              const days = new Date(targetYear, m, 0).getDate()
              roomB += Number(row.budgeted_room_revenue_usd || 0) * days
           }
        }
        
        let ancB = 0
        const revAccIds = new Set((accounts || []).map(a => a.id))
        ;(expBudget || []).forEach(eb => {
           if (revAccIds.has(eb.account_id)) {
               for (let m = startMonth; m <= endMonth; m++) {
                   const key = `month_${m}_amount_usd`
                   ancB += Number(eb[key] || 0)
               }
           }
        })
        
        const totalB = roomB + ancB
        v = th - totalB
    }
    setBudgetVar(v)
    
    // For GOPPAR
    const { data: g } = await supabase.from('hotel_expense_entries').select('amount_usd').eq('company_id', activeCompany.id).in('product', activeProduct === 'hotel' ? ['hotel', 'restaurant'] : [activeProduct]).gte('expense_date', range.from).lte('expense_date', range.to)
    const exps = (g || []).reduce((sum, x) => sum + Number(x.amount_usd || 0), 0)
    setGop(th - exps)
    
    setLoading(false)
  }

  async function generateStatsReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = selections.f || ((usd) => formatReportMoney(usd, selections.currency, rrate))
    const reportView = selections.view || view
    const reportRange = rangeFor(reportView)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', reportRange.from).lte('stat_date', reportRange.to).order('stat_date')
    const rows = statRows || []

    const totOcc = rows.reduce((s, r) => s + Number(r.rooms_occupied || 0), 0)
    const totRev = rows.reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0)
    const totCol = rows.reduce((s, r) => s + Number(r.room_revenue_collected_usd || 0), 0)
    const avgAdr = totOcc > 0 ? totRev / totOcc : 0
    const curLabel = selections.currency === 'USD' ? 'USD' : `${selections.currency} & USD`

    const statTableRows = rows.map(r => {
      const occPct = totalRooms > 0 ? ((r.rooms_occupied / totalRooms) * 100).toFixed(1) + '%' : '—'
      const adr = r.rooms_occupied > 0 ? f(r.room_revenue_usd / r.rooms_occupied) : '—'
      const revpar = totalRooms > 0 ? f(r.room_revenue_usd / totalRooms) : '—'
      return [r.stat_date, r.rooms_occupied, occPct, adr, revpar, f(r.room_revenue_usd), f(r.room_revenue_collected_usd)]
    })
    if (statTableRows.length > 0) {
      statTableRows.push(['Total / Average', totOcc, '', f(avgAdr), '', f(totRev), f(totCol)])
    }

    const periodLabel = reportView === 'specific_month'
      ? `${MONTH_NAMES[selectedMonth - 1]} ${selectedMonthYear}`
      : reportView === 'specific_year'
      ? `Year ${selectedYear}`
      : (VIEWS.find(v => v.key === reportView)?.label || reportView)

    const sections = [
      {
        heading: 'Summary',
        keyValuePairs: [
          ['Total Rooms Occupied', String(totOcc)],
          ['Total Room Revenue', f(totRev)],
          ['Total Collected', f(totCol)],
          ['Average ADR', f(avgAdr)],
        ]
      },
      {
        heading: `Occupancy & Revenue Statistics — ${periodLabel}`,
        columns: ['Date', 'Rooms Occupied', 'Occupancy %', `ADR (${curLabel})`, `RevPAR (${curLabel})`, `Room Revenue (${curLabel})`, `Collected (${curLabel})`],
        rows: statTableRows,
      }
    ]

    const title = 'Hotel Revenue & Occupancy Statistics'
    const subtitle = `${activeCompany.name} • ${reportRange.from} to ${reportRange.to} • ${selections.currency}`
    const logoUrl = activeCompany.logo_url
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'hotel_occupancy_stats', logoUrl })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_occupancy_stats' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_occupancy_stats', logoUrl })
  }

  if (!activeCompany) return null

  const totalOccupied = stats.reduce((s, r) => s + r.rooms_occupied, 0)
  
  
  const currentRange = rangeFor(view)
  const daysInView = Math.max(1, Math.round((new Date(currentRange.to) - new Date(currentRange.from)) / (1000 * 60 * 60 * 24)) + 1)
  const availableRoomNights = totalRooms * daysInView
  const occupancyPct = availableRoomNights > 0 ? (totalOccupied / availableRoomNights) * 100 : 0
  const adr = totalOccupied > 0 ? roomRevTotal / totalOccupied : 0
  const revpar = availableRoomNights > 0 ? roomRevTotal / availableRoomNights : 0
  const goppar = availableRoomNights > 0 ? gop / availableRoomNights : 0

  // Budget comparison

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
            <button
              onClick={() => setReportModalOpen(true)}
              className="h-[38px] flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 rounded-lg hover:border-navy-400"
            >
              Download Report
            </button>
            <select
              value={displayCurrency}
              onChange={e => setDisplayCurrency(e.target.value)}
              className="h-[38px] border border-slate-300 rounded-lg px-3 text-sm font-medium text-slate-700 bg-white hover:border-navy-400 focus:outline-none focus:border-navy-500"
            >
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
            </select>
          </div>
        }
      />

      <div className="flex flex-wrap items-center gap-1.5 bg-slate-100 rounded-lg p-1 mb-6">
        <div className="flex items-center gap-1 overflow-x-auto">
          {VIEWS.map(v => (
            <button
              key={v.key}
              onClick={() => setView(v.key)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors ${
                view === v.key ? 'bg-white shadow text-navy-700' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>

        <div className="h-5 w-px bg-slate-300 mx-1 hidden sm:block" />

        {/* Specific Month */}
        <div
          className={`flex items-center gap-1 px-1.5 py-0.5 rounded-md transition-colors ${
            view === 'specific_month' ? 'bg-white shadow text-navy-700' : 'text-slate-600'
          }`}
        >
          <button
            type="button"
            onClick={() => setView('specific_month')}
            className={`text-xs font-medium px-1 py-1 rounded whitespace-nowrap ${
              view === 'specific_month' ? 'font-semibold text-navy-700' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Month:
          </button>
          <select
            value={selectedMonth}
            onChange={(e) => {
              setSelectedMonth(Number(e.target.value))
              setView('specific_month')
            }}
            className={`text-xs h-7 px-1.5 rounded border ${
              view === 'specific_month'
                ? 'border-navy-400 bg-white text-navy-800 font-medium'
                : 'border-slate-300 bg-white/90 text-slate-700'
            } focus:outline-none focus:ring-1 focus:ring-navy-400`}
          >
            {MONTH_NAMES.map((name, i) => (
              <option key={name} value={i + 1}>
                {name}
              </option>
            ))}
          </select>
          <select
            value={selectedMonthYear}
            onChange={(e) => {
              setSelectedMonthYear(Number(e.target.value))
              setView('specific_month')
            }}
            className={`text-xs h-7 px-1.5 rounded border ${
              view === 'specific_month'
                ? 'border-navy-400 bg-white text-navy-800 font-medium'
                : 'border-slate-300 bg-white/90 text-slate-700'
            } focus:outline-none focus:ring-1 focus:ring-navy-400`}
          >
            {YEAR_OPTIONS.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>

        {/* Specific Year */}
        <div
          className={`flex items-center gap-1 px-1.5 py-0.5 rounded-md transition-colors ${
            view === 'specific_year' ? 'bg-white shadow text-navy-700' : 'text-slate-600'
          }`}
        >
          <button
            type="button"
            onClick={() => setView('specific_year')}
            className={`text-xs font-medium px-1 py-1 rounded whitespace-nowrap ${
              view === 'specific_year' ? 'font-semibold text-navy-700' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Year:
          </button>
          <select
            value={selectedYear}
            onChange={(e) => {
              setSelectedYear(Number(e.target.value))
              setView('specific_year')
            }}
            className={`text-xs h-7 px-1.5 rounded border ${
              view === 'specific_year'
                ? 'border-navy-400 bg-white text-navy-800 font-medium'
                : 'border-slate-300 bg-white/90 text-slate-700'
            } focus:outline-none focus:ring-1 focus:ring-navy-400`}
          >
            {YEAR_OPTIONS.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
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
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 mb-4">
            <KpiCard label="Occupancy %" value={`${occupancyPct.toFixed(1)}%`} icon={Percent} tone="blue" />
            <KpiCard label="Rooms Occupied" value={totalOccupied} icon={BedDouble} tone="slate" />
            <KpiCard label="ADR" value={fmt(adr)} icon={DollarSign} tone="green" />
            <KpiCard label="RevPAR" value={fmt(revpar)} icon={TrendingUp} tone="gold" />
            <KpiCard label="GOPPAR" value={fmt(goppar)} icon={TrendingUp} tone="blue" sublabel="GOP per available room" />
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
            <KpiCard label="Total Revenue" value={fmtRounded(hotelRevTotal)} icon={DollarSign} tone="indigo" />
            <KpiCard label="Total Room Revenue" value={fmtRounded(roomRevTotal)} icon={DollarSign} tone="green" />
            <KpiCard label="Collected" value={fmtRounded(hotelColTotal)} icon={DollarSign} tone="slate" />
            {budgetVar !== null && (
              <KpiCard
                label={`Budget Variance (${
                  view === 'mtd'
                    ? 'MTD'
                    : view === 'ytd'
                    ? 'YTD'
                    : view === 'specific_month'
                    ? `${MONTH_NAMES[selectedMonth - 1]?.slice(0, 3)} ${selectedMonthYear}`
                    : `${selectedYear}`
                })`}
                value={fmtRounded(budgetVar)}
                icon={budgetVar >= 0 ? TrendingUp : AlertTriangle}
                tone={budgetVar >= 0 ? 'green' : 'red'}
              />
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
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'view', 
              label: 'Time Period', 
              default: view,
              options: [
                { value: 'last_night', label: 'Last Night' },
                { value: 'last_30', label: 'Last 30 Days' },
                { value: 'last_year_daily', label: 'Each Day, Last Year' },
                { value: 'mtd', label: 'MTD' },
                { value: 'ytd', label: 'YTD' },
                { value: 'specific_month', label: `Month: ${MONTH_NAMES[selectedMonth - 1]} ${selectedMonthYear}` },
                { value: 'specific_year', label: `Year: ${selectedYear}` },
              ]
            }
          ]}
          onGenerate={generateStatsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
