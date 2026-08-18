import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Receipt, AlertCircle, Building2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { getYTDRange, resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function Dashboard() {
  const { activeCompany } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [sales, setSales] = useState([])
  const [purchases, setPurchases] = useState([])
  const [receipts, setReceipts] = useState([])
  const [allSales, setAllSales] = useState([])
  const [allPurchases, setAllPurchases] = useState([])
  const [recentTx, setRecentTx] = useState([])

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, cp.range.from, cp.range.to])

  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id)
        .gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id)
        .gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id)
        .gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id),
      supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id),
    ])
    setSales(s || [])
    setPurchases(p || [])
    setReceipts(r || [])
    setAllSales(allS || [])
    setAllPurchases(allP || [])

    // Recent Transactions: latest 5 across sales, purchases, and receipts, all-time (not period-filtered)
    const [{ data: recentS }, { data: recentP }, { data: recentR }] = await Promise.all([
      supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)').eq('company_id', activeCompany.id).order('invoice_date', { ascending: false }).limit(5),
      supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).order('invoice_date', { ascending: false }).limit(5),
      supabase.from('payment_receipts').select('receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).order('receipt_date', { ascending: false }).limit(5),
    ])
    const combined = [
      ...(recentS || []).map(r => ({ date: r.invoice_date, label: r.contact?.name || r.invoice_number, amount: r.amount, currency: r.currency })),
      ...(recentP || []).map(r => ({ date: r.invoice_date, label: r.contact?.name || r.supplier_name_freeform || r.invoice_number, amount: r.amount, currency: r.currency })),
      ...(recentR || []).map(r => ({ date: r.receipt_date, label: 'Payment Received', amount: r.amount, currency: r.currency })),
    ].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 5)
    setRecentTx(combined)
  }


  async function generateDashboardReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const conv = (usd) => convertFromUsd(usd, selections.currency, { [selections.currency]: rate })
    const fmt = (usd) => formatMoney(conv(usd), selections.currency)

    const [{ data: s }, { data: p }, { data: r }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).gte('receipt_date', range.from).lte('receipt_date', range.to),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []
    const sections = []

    if (selections.sections.includes('Revenue vs Expenses vs Collections')) {
      const monthlyMap = {}
      sSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0, col: 0 }; monthlyMap[k].rev += Number(i.amount_usd) })
      pSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0, col: 0 }; monthlyMap[k].exp += Number(i.amount_usd) })
      rSel.forEach(i => { const k = i.receipt_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0, col: 0 }; monthlyMap[k].col += Number(i.amount_usd) })
      const monthly = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))
      sections.push({ heading: 'Revenue vs Expenses vs Collections', columns: ['Month', 'Revenue', 'Expenses', 'Collected'], rows: monthly.map(m => [m.month, fmt(m.rev), fmt(m.exp), fmt(m.col)]) })
    }

    if (selections.sections.includes('Company Overview - YTD')) {
      const ytd = getYTDRange(activeCompany.fiscal_year_start_month || 1)
      const [{ data: allS }, { data: allP }] = await Promise.all([
        supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).gte('invoice_date', ytd.from).lte('invoice_date', ytd.to),
        supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).gte('invoice_date', ytd.from).lte('invoice_date', ytd.to),
      ])
      const rev = (allS || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      const exp = (allP || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      sections.push({ heading: 'Company Overview - YTD', keyValuePairs: [['YTD Revenue', fmt(rev)], ['YTD Expenses', fmt(exp)], ['YTD Net Profit', fmt(rev - exp)]] })
    }

    if (selections.sections.includes('Company Overview - All Time')) {
      const [{ data: allS }, { data: allP }] = await Promise.all([
        supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id),
        supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id),
      ])
      const rev = (allS || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      const exp = (allP || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      sections.push({ heading: 'Company Overview - All Time', keyValuePairs: [['All Time Revenue', fmt(rev)], ['All Time Expenses', fmt(exp)], ['All Time Net Profit', fmt(rev - exp)]] })
    }

    if (selections.sections.includes('Recent Transactions')) {
      const combined = [
        ...sSel.map(i => ({ date: i.invoice_date, label: i.contact?.name || i.invoice_number, amount: fmt(i.amount_usd) })),
        ...pSel.map(i => ({ date: i.invoice_date, label: i.invoice_number, amount: fmt(i.amount_usd) })),
        ...rSel.map(i => ({ date: i.receipt_date, label: 'Payment Received', amount: fmt(i.amount_usd) })),
      ].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 10)
      sections.push({ heading: 'Recent Transactions', columns: ['Date', 'Description', 'Amount'], rows: combined.map(t => [t.date, t.label, t.amount]) })
    }

    if (selections.sections.includes('Outstanding Invoices')) {
      const outstanding = sSel.filter(i => i.status !== 'Paid')
      sections.push({ heading: 'Outstanding Invoices', columns: ['Invoice #', 'Customer', 'Due Date', 'Balance Due', 'Status'], rows: outstanding.map(i => [i.invoice_number, i.contact?.name || '—', i.due_date || '—', fmt(i.amount_usd), i.status]) })
    }

    const title = 'Financial Dashboard'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'dashboard_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'dashboard_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'dashboard_report' })
  }

  if (!activeCompany) return null

  const totalBilled = sales.reduce((sum, i) => sum + Number(i.amount_usd), 0)
  const totalExpenses = purchases.reduce((sum, i) => sum + Number(i.amount_usd), 0)
  const netProfit = totalBilled - totalExpenses
  const collected = receipts.reduce((sum, r) => sum + Number(r.amount_usd), 0)
  const outstanding = sales.reduce((sum, i) => sum + Number(i.balance_due), 0)
  const draftInvoices = sales.filter(i => i.status !== 'Paid')

  // YTD (respects company fiscal year start month) — independent of the page's period selector
  const ytdRange = getYTDRange(activeCompany.fiscal_year_start_month || 1)
  const ytdSales = allSales.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
  const ytdPurchases = allPurchases.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
  const ytdRevenue = ytdSales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const ytdExpenses = ytdPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)

  // All-Time
  const allTimeRevenue = allSales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const allTimeExpenses = allPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)

  const monthlyMap = {}
  sales.forEach(i => {
    const key = i.invoice_date.slice(0, 7)
    monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0 }
    monthlyMap[key].Revenue += Number(i.amount_usd)
  })
  purchases.forEach(i => {
    const key = i.invoice_date.slice(0, 7)
    monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0 }
    monthlyMap[key].Expenses += Number(i.amount_usd)
  })
  receipts.forEach(r => {
    const key = r.receipt_date.slice(0, 7)
    monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0 }
    monthlyMap[key].Collected += Number(r.amount_usd)
  })
  const chartData = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))

  const reportColumns = [
    { label: 'Invoice #', key: 'invoice_number' }, { label: 'Customer', key: 'customerName' },
    { label: 'Due Date', key: 'due_date' }, { label: 'Balance Due (USD)', key: 'balanceLabel' }, { label: 'Status', key: 'status' },
  ]
  const reportRows = draftInvoices.map(i => ({ ...i, customerName: i.contact?.name || '—', balanceLabel: cp.fmt(i.amount_usd) }))

  return (
    <div>
      <PageHeader
        title="Financial Dashboard"
        subtitle={`${activeCompany.name} • Showing in ${cp.displayCurrency}`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Billed" value={cp.fmt(totalBilled)} sublabel="sales invoices" icon={TrendingUp} tone="green" />
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} sublabel="purchase invoices" icon={TrendingDown} tone="red" />
        <KpiCard label="Net Profit" value={cp.fmt(netProfit)} sublabel="billed minus expenses" icon={DollarSign} tone="blue" />
        <KpiCard label="Collected" value={cp.fmt(collected)} sublabel="payment receipts" icon={Receipt} tone="gold" />
        <KpiCard label="Outstanding" value={cp.fmt(outstanding)} sublabel="pending + overdue" icon={AlertCircle} tone="slate" />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <TrendingUp size={18} /> Revenue vs Expenses vs Collections
        </h2>
        <div className="h-72 sm:h-96 -ml-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => cp.fmt(v)} />
              <Legend />
              <Bar dataKey="Revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Expenses" fill="#f97316" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Collected" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-5 mb-6">
        <OverviewCard title="Company Overview - YTD" subtitle={`${activeCompany.name} • Amounts in ${cp.displayCurrency}`}
          revenue={cp.fmt(ytdRevenue)} expenses={cp.fmt(ytdExpenses)} profit={cp.fmt(ytdRevenue - ytdExpenses)}
          revenueLabel="YTD Revenue" expensesLabel="YTD Expenses" profitLabel="YTD Net Profit" />
        <OverviewCard title="Company Overview - All Time" subtitle={`${activeCompany.name} • Amounts in ${cp.displayCurrency}`}
          revenue={cp.fmt(allTimeRevenue)} expenses={cp.fmt(allTimeExpenses)} profit={cp.fmt(allTimeRevenue - allTimeExpenses)}
          revenueLabel="All Time Revenue" expensesLabel="All Time Expenses" profitLabel="All Time Net Profit" />
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5">
          <h3 className="font-semibold text-slate-700 mb-4 flex items-center gap-2"><Receipt size={16} /> Recent Transactions</h3>
          <div className="space-y-3">
            {recentTx.length === 0 && <p className="text-sm text-slate-400">No transactions yet.</p>}
            {recentTx.map((t, i) => (
              <div key={i} className="flex items-center justify-between text-sm border-b border-slate-50 last:border-0 pb-2 last:pb-0">
                <div>
                  <div className="text-slate-700 font-medium">{t.label}</div>
                  <div className="text-xs text-slate-400">{t.date}</div>
                </div>
                <span className="font-semibold text-slate-700">{t.amount.toLocaleString()} {t.currency}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <AlertCircle size={18} className="text-amber-500" /> Outstanding Invoices ({draftInvoices.length})
        </h2>
        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Invoice #' },
            { key: 'customer', label: 'Customer', render: r => r.contact?.name || '—' },
            { key: 'due_date', label: 'Due Date' },
            { key: 'balance_due', label: 'Balance Due', render: r => cp.fmt(r.amount_usd) },
            { key: 'status', label: 'Status' },
          ]}
          rows={draftInvoices}
          emptyMessage="No outstanding invoices — nice work."
        />
      </div>

      {reportModalOpen && (
        <ReportOptionsModal
          title="Dashboard"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'MTD' },
            { type: 'checkboxGroup', key: 'sections', label: 'Include Sections', options: ['Revenue vs Expenses vs Collections', 'Company Overview - YTD', 'Company Overview - All Time', 'Recent Transactions', 'Outstanding Invoices'], default: ['Revenue vs Expenses vs Collections', 'Company Overview - YTD', 'Company Overview - All Time', 'Recent Transactions', 'Outstanding Invoices'] },
          ]}
          onGenerate={generateDashboardReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function OverviewCard({ title, subtitle, revenue, expenses, profit, revenueLabel, expensesLabel, profitLabel }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5">
      <h3 className="font-semibold text-slate-700 flex items-center gap-2"><Building2 size={16} /> {title}</h3>
      <p className="text-xs text-slate-400 mb-3">{subtitle}</p>
      <div className="space-y-2">
        <div className="flex items-center justify-between bg-emerald-50 rounded-lg px-3 py-2">
          <span className="text-sm text-emerald-700 flex items-center gap-1"><TrendingUp size={14} /> {revenueLabel}</span>
          <span className="font-bold text-slate-800">{revenue}</span>
        </div>
        <div className="flex items-center justify-between bg-rose-50 rounded-lg px-3 py-2">
          <span className="text-sm text-rose-700 flex items-center gap-1"><TrendingDown size={14} /> {expensesLabel}</span>
          <span className="font-bold text-slate-800">{expenses}</span>
        </div>
        <div className="flex items-center justify-between bg-blue-50 rounded-lg px-3 py-2">
          <span className="text-sm text-blue-700 flex items-center gap-1"><DollarSign size={14} /> {profitLabel}</span>
          <span className="font-bold text-slate-800">{profit}</span>
        </div>
      </div>
    </div>
  )
}
