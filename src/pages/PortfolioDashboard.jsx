import { useEffect, useState } from 'react'
import { DollarSign, TrendingDown, TrendingUp, FileCheck, CheckCircle2, Building2 } from 'lucide-react'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import KpiCard from '../components/KpiCard'
import PageHeader from '../components/PageHeader'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

const PRODUCT_LABELS = { basic: 'CRS Basic Accounting', hotel: 'CRS Hotel Accounting', restaurant: 'CRS Restaurant Accounting' }
const DA_INTEREST_NAMES = ['Depreciation & Amortization', 'Loan Interest']

const CARD_STYLES = [
  { bg: 'bg-navy-50', border: 'border-navy-100', accent: 'bg-navy-600', text: 'text-navy-700', hex: '#1B3A6B' },
  { bg: 'bg-gold-50', border: 'border-gold-100', accent: 'bg-gold-600', text: 'text-gold-700', hex: '#C9A84C' },
  { bg: 'bg-emerald-50', border: 'border-emerald-100', accent: 'bg-emerald-600', text: 'text-emerald-700', hex: '#059669' },
  { bg: 'bg-blue-50', border: 'border-blue-100', accent: 'bg-blue-600', text: 'text-blue-700', hex: '#2563eb' },
  { bg: 'bg-amber-50', border: 'border-amber-100', accent: 'bg-amber-600', text: 'text-amber-700', hex: '#d97706' },
  { bg: 'bg-rose-50', border: 'border-rose-100', accent: 'bg-rose-600', text: 'text-rose-700', hex: '#e11d48' },
]

export default function PortfolioDashboard() {
  const { companies } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (companies.length > 0) loadPortfolio(cp.range) }, [companies.length, cp.range.from, cp.range.to])

  async function computeCompanyProductMetrics(companyId, product, range) {
    const [{ data: accounts }, { data: entries }, { data: salesInv }, { data: receipts }] = await Promise.all([
      supabase.from('accounts').select('id, type, subtype, name').eq('company_id', companyId).eq('product', product),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', companyId).eq('product', product).gte('entry_date', range.from).lte('entry_date', range.to),
      supabase.from('sales_invoices').select('id, amount_usd').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('amount_usd').eq('company_id', companyId).eq('product', product).gte('receipt_date', range.from).lte('receipt_date', range.to),
    ])

    const balances = {}
    ;(entries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })
    const byType = (type) => (accounts || []).filter(a => a.type === type)
    const sumAccs = (list) => list.reduce((s, a) => s + (balances[a.id] || 0), 0)

    const revenue = -sumAccs(byType('Revenue'))
    const belowLine = byType('Expenses').filter(a => ['Below GOP', 'Below EBITDA'].includes(a.subtype))
    const otherBelowLineAccs = belowLine.filter(a => !DA_INTEREST_NAMES.includes(a.name))
    const operatingAccs = byType('Expenses').filter(a => !['Below GOP', 'Below EBITDA'].includes(a.subtype))
    const operatingExpenses = sumAccs(operatingAccs)
    const otherBelowLine = sumAccs(otherBelowLineAccs)
    const totalExpenses = sumAccs(byType('Expenses'))
    const gop = revenue - operatingExpenses
    const ebitda = gop - otherBelowLine

    return {
      revenue, expenses: totalExpenses, gop, ebitda,
      invoicesRaised: (salesInv || []).length,
      collected: (receipts || []).reduce((s, r) => s + Number(r.amount_usd), 0),
    }
  }

  async function loadPortfolio(range) {
    setLoading(true)
    const tasks = []
    companies.forEach(({ company }) => {
      ;(company.company_products || []).forEach(({ product }) => {
        tasks.push(
          computeCompanyProductMetrics(company.id, product, range).then(metrics => ({
            companyId: company.id, companyName: company.name, product, ...metrics,
          }))
        )
      })
    })
    const results = await Promise.all(tasks)
    setRows(results)
    setLoading(false)
  }

  async function generatePortfolioReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const tasks = []
    companies.forEach(({ company }) => {
      ;(company.company_products || []).forEach(({ product }) => {
        tasks.push(computeCompanyProductMetrics(company.id, product, range).then(m => ({ companyName: company.name, product, ...m })))
      })
    })
    const reportRows = await Promise.all(tasks)

    const combined = reportRows.reduce((acc, r) => ({
      revenue: acc.revenue + r.revenue, expenses: acc.expenses + r.expenses, gop: acc.gop + r.gop,
      ebitda: acc.ebitda + r.ebitda, invoicesRaised: acc.invoicesRaised + r.invoicesRaised, collected: acc.collected + r.collected,
    }), { revenue: 0, expenses: 0, gop: 0, ebitda: 0, invoicesRaised: 0, collected: 0 })

    const sections = [
      { heading: 'Combined Totals', keyValuePairs: [['Combined Sales', f(combined.revenue)], ['Combined Expenses', f(combined.expenses)], ['Combined GOP', f(combined.gop)], ['Combined EBITDA', f(combined.ebitda)], ['Invoices Raised', combined.invoicesRaised], ['Money Collected', f(combined.collected)]] },
      { heading: 'By Company & Product', columns: ['Company', 'Product', 'Revenue', 'Expenses', 'GOP', 'EBITDA', 'Invoices', 'Collected'], rows: reportRows.map(r => [r.companyName, PRODUCT_LABELS[r.product], f(r.revenue), f(r.expenses), f(r.gop), f(r.ebitda), r.invoicesRaised, f(r.collected)]) },
    ]
    if (selections.charts.includes('Revenue by Company (Bar Chart)')) {
      sections.push({
        heading: 'Revenue by Company & Product',
        chart: { categories: reportRows.map(r => `${r.companyName} (${PRODUCT_LABELS[r.product].replace('CRS ', '')})`), valueFormatter: v => formatMoney(v, selections.currency), series: [{ name: 'Revenue', color: '#1B3A6B', values: reportRows.map(r => convertFromUsd(r.revenue, selections.currency, { [selections.currency]: rate })) }] },
      })
    }

    const title = 'All Companies Overview'
    const subtitle = `Combined portfolio • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'portfolio_overview' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'portfolio_overview' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'portfolio_overview' })
  }

  const combined = rows.reduce((acc, r) => ({
    revenue: acc.revenue + r.revenue,
    expenses: acc.expenses + r.expenses,
    gop: acc.gop + r.gop,
    ebitda: acc.ebitda + r.ebitda,
    invoicesRaised: acc.invoicesRaised + r.invoicesRaised,
    collected: acc.collected + r.collected,
  }), { revenue: 0, expenses: 0, gop: 0, ebitda: 0, invoicesRaised: 0, collected: 0 })

  const barData = rows.map(r => ({ name: `${r.companyName} (${PRODUCT_LABELS[r.product].replace('CRS ', '')})`, Revenue: cp.convert(r.revenue), Expenses: cp.convert(r.expenses) }))
  const pieData = rows.filter(r => r.revenue > 0).map(r => ({ name: `${r.companyName} - ${PRODUCT_LABELS[r.product].replace('CRS ', '')}`, value: cp.convert(r.revenue) }))

  return (
    <div>
      <PageHeader
        title="All Companies Overview"
        subtitle="Combined across every company and product you have access to"
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      {loading ? (
        <p className="text-sm text-slate-400 text-center py-10">Loading combined data across all companies…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4 mb-8">
            <KpiCard label="Combined Sales" value={cp.fmt(combined.revenue)} icon={DollarSign} tone="green" />
            <KpiCard label="Combined Expenses" value={cp.fmt(combined.expenses)} icon={TrendingDown} tone="red" />
            <KpiCard label="Combined GOP" value={cp.fmt(combined.gop)} icon={TrendingUp} tone="gold" />
            <KpiCard label="Combined EBITDA" value={cp.fmt(combined.ebitda)} icon={TrendingUp} tone="blue" />
            <KpiCard label="Invoices Raised" value={combined.invoicesRaised} icon={FileCheck} tone="slate" />
            <KpiCard label="Money Collected" value={cp.fmt(combined.collected)} icon={CheckCircle2} tone="green" />
          </div>

          {rows.length > 0 && (
            <div className="grid lg:grid-cols-2 gap-5 mb-8">
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Revenue vs Expenses by Company</h3>
                <div className="h-64 sm:h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={barData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={60} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip formatter={v => cp.fmt(v)} />
                      <Legend />
                      <Bar dataKey="Revenue" fill="#1B3A6B" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Expenses" fill="#C9A84C" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Revenue Share by Company</h3>
                <div className="h-64 sm:h-72 flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label={({ percent }) => `${(percent * 100).toFixed(0)}%`}>
                        {pieData.map((_, i) => <Cell key={i} fill={CARD_STYLES[i % CARD_STYLES.length].hex} />)}
                      </Pie>
                      <Tooltip formatter={v => cp.fmt(v)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          <h2 className="text-lg font-semibold text-navy-700 mb-4 flex items-center gap-2">
            <Building2 size={18} /> By Company &amp; Product
          </h2>

          {rows.length === 0 ? (
            <div className="text-center text-slate-400 text-sm py-10 bg-white rounded-xl border border-slate-200">
              No companies with an enabled product yet.
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {rows.map((r, i) => {
                const style = CARD_STYLES[i % CARD_STYLES.length]
                return (
                  <div key={`${r.companyId}-${r.product}`} className={`rounded-xl border ${style.border} ${style.bg} overflow-hidden`}>
                    <div className={`${style.accent} px-4 py-2.5`}>
                      <div className="text-white font-semibold text-sm truncate">{r.companyName}</div>
                      <div className="text-white/80 text-xs">{PRODUCT_LABELS[r.product]}</div>
                    </div>
                    <div className="p-4 space-y-2 text-sm">
                      <Row label="Revenue" value={cp.fmt(r.revenue)} />
                      <Row label="Expenses" value={cp.fmt(r.expenses)} />
                      <Row label="GOP" value={cp.fmt(r.gop)} />
                      <Row label="EBITDA" value={cp.fmt(r.ebitda)} bold textClass={style.text} />
                      <Row label="Invoices Raised" value={r.invoicesRaised} />
                      <Row label="Collected" value={cp.fmt(r.collected)} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="All Companies Overview"
          fields={[
            { type: 'checkboxGroup', key: 'charts', label: 'Include Charts', options: ['Revenue by Company (Bar Chart)'], default: ['Revenue by Company (Bar Chart)'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generatePortfolioReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function Row({ label, value, bold, textClass }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate-500">{label}</span>
      <span className={`${bold ? 'font-bold' : 'font-medium'} ${textClass || 'text-slate-700'}`}>{value}</span>
    </div>
  )
}
