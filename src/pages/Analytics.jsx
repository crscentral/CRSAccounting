import { useEffect, useState } from 'react'
import { LineChart, Line, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { DollarSign, CheckCircle2, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'

const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export default function Analytics() {
  const { activeCompany, activeProduct } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [sales, setSales] = useState([])
  const [purchases, setPurchases] = useState([])
  const [receipts, setReceipts] = useState([])
  const [hotelRoomStats, setHotelRoomStats] = useState([])
  const [hotelGuestInvoices, setHotelGuestInvoices] = useState([])
  const [hotelExpenseEntries, setHotelExpenseEntries] = useState([])
  const [hotelAmc, setHotelAmc] = useState([])
  const [hotelRevenueEntries, setHotelRevenueEntries] = useState([])

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  const [restaurantRevenue, setRestaurantRevenue] = useState([])

  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])
    setSales(s || []); setPurchases(p || []); setReceipts(r || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
    setRestaurantRevenue(rdr || [])
  }


  async function generateAnalyticsReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to) : Promise.resolve({ data: [] }),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []
    const hrsSel = hrs || [], hgiSel = hgi || [], heeSel = hee || [], hamcSel = hamc || [], hreSel = hre || []
    let totalInvoiced = 0
    let outstanding = 0
    let collected = 0
    let expenses = 0
    const monthlyMap = {}

    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const manualRoomCollected = hrsSel.reduce((s2, r) => s2 + Number(r.manual_room_revenue_collected_usd || 0), 0)
      const manualRoomRevenue = hrsSel.reduce((s2, r) => s2 + Number(r.room_revenue_usd || 0), 0)
      const guestInvoiceCollected = hgiSel.reduce((s2, i) => s2 + Number(i.collected_amount_usd || 0), 0)
      const guestInvoiceRevenue = hgiSel.reduce((s2, i) => s2 + Number(i.invoice_amount_usd || 0), 0)
      const ancillaryCollected = hreSel.reduce((s2, r) => s2 + Number(r.amount_usd || 0), 0)

      totalInvoiced = manualRoomRevenue + guestInvoiceRevenue + ancillaryCollected
      collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected
      outstanding = hgiSel.reduce((s2, i) => s2 + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)

      const start = new Date(range.from)
      const end = new Date(Math.min(new Date(range.to).getTime(), new Date().getTime()))
      const monthsInView = Math.max(1, (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1)
      const amcTotal = hamcSel.reduce((s2, r) => s2 + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
      expenses = heeSel.reduce((s2, e) => s2 + Number(e.amount_usd), 0) + amcTotal

      hgiSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.invoice_amount_usd || 0); monthlyMap[k].collected += Number(i.collected_amount_usd || 0) })
      hrsSel.forEach(i => { const k = i.stat_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.room_revenue_usd || 0); monthlyMap[k].collected += Number(i.manual_room_revenue_collected_usd || 0) })
      hreSel.forEach(i => { const k = i.entry_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd || 0); monthlyMap[k].collected += Number(i.amount_usd || 0) })

    } else {
      totalInvoiced = sSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      outstanding = sSel.reduce((s2, i) => s2 + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
      collected = totalInvoiced - outstanding
      expenses = pSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)

      sSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd) })
      rSel.forEach(i => { const k = i.receipt_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].collected += Number(i.amount_usd) })
    }

    const monthlySel = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))

    const sections = [
      { heading: 'Summary', keyValuePairs: [['Total Invoiced', fmt(totalInvoiced)], ['Collected', fmt(collected)], ['Outstanding', fmt(outstanding)], ['Expenses', fmt(expenses)]] },
      { heading: 'Monthly Summary', columns: ['Month', 'Invoices', `Revenue (${selections.currency})`, `Collected (${selections.currency})`], rows: monthlySel.map(m => [m.month, m.invoices, fmt(m.revenue), fmt(m.collected)]) },
    ]

    const title = 'Analytics'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'analytics_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'analytics_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'analytics_report' })
  }

  if (!activeCompany) return null

  let totalInvoiced = 0
  let outstanding = 0
  let collected = 0
  let expenses = 0
  let overdueCount = 0

  const monthlyMap = {}
  let statusPie = []
  let txTypePie = []

  if (['hotel', 'restaurant'].includes(activeProduct)) {
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const manualRoomRevenue = hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const guestInvoiceRevenue = hotelGuestInvoices.reduce((s, i) => s + Number(i.invoice_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || r.amount_usd || 0), 0)
    const ancillaryRevenue = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    
    const restRevRevenue = restaurantRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)

    totalInvoiced = manualRoomRevenue + guestInvoiceRevenue + ancillaryRevenue + restRevRevenue
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected + restRevCollected
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)

    const start = new Date(cp.range.from)
    const end = new Date(Math.min(new Date(cp.range.to).getTime(), new Date().getTime()))
    const monthsInView = Math.max(1, (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1)
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    expenses = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal

    overdueCount = hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)).length

    hotelGuestInvoices.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(i.invoice_amount_usd || 0)
      monthlyMap[key].collected += Number(i.collected_amount_usd || 0)
    })
    hotelRoomStats.forEach(r => {
      const key = r.stat_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.room_revenue_usd || 0)
      monthlyMap[key].collected += Number(r.manual_room_revenue_collected_usd || 0)
    })
    hotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.amount_usd || 0)
      monthlyMap[key].collected += Number(r.amount_usd || 0)
    })

    const fullyPaidCount = hotelGuestInvoices.filter(i => Number(i.collected_amount_usd) >= Number(i.invoice_amount_usd)).length
    const pendingCount = hotelGuestInvoices.length - fullyPaidCount
    statusPie = [
      { name: 'Paid', value: fullyPaidCount },
      { name: 'Pending', value: pendingCount }
    ].filter(x => x.value > 0)

    txTypePie = [
      { name: 'Guest Invoices', value: hotelGuestInvoices.length },
      { name: 'Daily Room Rev', value: hotelRoomStats.length },
      { name: 'Ancillary Rev', value: hotelRevenueEntries.length },
      { name: 'Expense Entries', value: hotelExpenseEntries.length }
    ].filter(x => x.value > 0)

  } else {
    totalInvoiced = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
    outstanding = sales.reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalInvoiced - outstanding
    expenses = purchases.reduce((s, i) => s + Number(i.amount_usd), 0)
    overdueCount = sales.filter(i => i.status === 'Overdue').length

    sales.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(i.amount_usd)
    })
    receipts.forEach(r => {
      const key = r.receipt_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].collected += Number(r.amount_usd)
    })

    const statusCounts = sales.reduce((acc, i) => { acc[i.status] = (acc[i.status] || 0) + 1; return acc }, {})
    statusPie = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

    txTypePie = [
      { name: 'Sales Invoice', value: sales.length },
      { name: 'Purchase Invoice', value: purchases.length },
    ]
  }

  const monthly = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))

  return (
    <div>
      <PageHeader
        title="Analytics" subtitle="Invoice and financial activity trends" currencyProps={cp.currencyProps} periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Invoiced" value={cp.fmt(totalInvoiced)} icon={DollarSign} tone="green" />
        <KpiCard label="Collected" value={cp.fmt(collected)} icon={CheckCircle2} tone="blue" />
        <KpiCard label="Outstanding" value={cp.fmt(outstanding)} icon={TrendingUp} tone="gold" />
        <KpiCard label="Expenses" value={cp.fmt(expenses)} icon={TrendingDown} tone="red" />
        <KpiCard label="Overdue Invoices" value={overdueCount} icon={AlertTriangle} tone="slate" />
      </div>

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h3 className="font-semibold text-slate-700 mb-4">Revenue vs Collected</h3>
          <div className="h-64 sm:h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={v => cp.fmt(v)} />
                <Legend />
                <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="collected" name="Collected" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h3 className="font-semibold text-slate-700 mb-4">Invoices Issued per Month</h3>
          <div className="h-64 sm:h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="invoices" fill="#1B3A6B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h3 className="font-semibold text-slate-700 mb-4">Invoice Status Breakdown</h3>
          <div className="h-56 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={statusPie} dataKey="value" nameKey="name" outerRadius={80} label>
                  {statusPie.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h3 className="font-semibold text-slate-700 mb-4">Transaction Types</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={txTypePie} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={110} />
                <Tooltip />
                <Bar dataKey="value" fill="#C9A84C" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 overflow-x-auto">
        <h3 className="font-semibold text-slate-700 mb-4">Monthly Summary</h3>
        <table className="w-full text-sm min-w-[500px]">
          <thead>
            <tr className="text-left text-slate-400 border-b border-slate-100">
              <th className="py-2 font-medium">Month</th>
              <th className="py-2 font-medium">Invoices</th>
              <th className="py-2 font-medium">Revenue</th>
              <th className="py-2 font-medium">Collected</th>
              <th className="py-2 font-medium">Collection Rate</th>
            </tr>
          </thead>
          <tbody>
            {monthly.map(m => (
              <tr key={m.month} className="border-b border-slate-50 last:border-0">
                <td className="py-2">{m.month}</td>
                <td className="py-2">{m.invoices}</td>
                <td className="py-2">{cp.fmt(m.revenue)}</td>
                <td className="py-2 text-emerald-600">{cp.fmt(m.collected)}</td>
                <td className="py-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${m.revenue && m.collected >= m.revenue ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                    {m.revenue ? Math.round((m.collected / m.revenue) * 100) : 0}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    
      {reportModalOpen && (
        <ReportOptionsModal
          title="Analytics"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateAnalyticsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
