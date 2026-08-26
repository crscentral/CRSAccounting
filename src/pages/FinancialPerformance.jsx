import { useEffect, useState } from 'react'
import { Download } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { DollarSign, TrendingDown, TrendingUp } from 'lucide-react'

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

export default function FinancialPerformance() {
  const { activeCompany, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [tab, setTab] = useState('profit')
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [forecastReportModalOpen, setForecastReportModalOpen] = useState(false)
  const [sales, setSales] = useState([])
  const [purchases, setPurchases] = useState([])
  const [revenueByAccount, setRevenueByAccount] = useState([])
  const [expensesByAccount, setExpensesByAccount] = useState([])
  const [forecast, setForecast] = useState([])
  const [forecastYear, setForecastYear] = useState(new Date().getFullYear() + 1)

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, cp.range.from, cp.range.to])
  useEffect(() => { if (activeCompany) loadForecast() }, [activeCompany, forecastYear])

  async function loadData() {
    const [{ data: s }, { data: p }, { data: entries }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
    ])
    setSales(s || []); setPurchases(p || [])

    // Breakdown by account, for the Revenue and Expenses tabs
    const revMap = {}, expMap = {}
    ;(entries || []).forEach(e => {
      const acc = e.accounts
      if (!acc) return
      const net = Number(e.debit_usd) - Number(e.credit_usd)
      if (acc.type === 'Revenue') {
        revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }
        revMap[acc.id].amount += -net // revenue is credit-normal
      } else if (acc.type === 'Expenses') {
        expMap[acc.id] = expMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }
        expMap[acc.id].amount += net
      }
    })
    setRevenueByAccount(Object.values(revMap).sort((a, b) => b.amount - a.amount))
    setExpensesByAccount(Object.values(expMap).sort((a, b) => b.amount - a.amount))
  }

  async function loadForecast() {
    const { data } = await supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('forecast_year', forecastYear).order('forecast_month')
    setForecast(data || [])
  }

  async function saveForecastRow(month, revenue, expenses) {
    await supabase.from('forecast_entries').upsert({
      company_id: activeCompany.id, forecast_year: forecastYear, forecast_month: month,
      revenue_usd: revenue, expenses_usd: expenses,
    }, { onConflict: 'company_id,forecast_year,forecast_month' })
    loadForecast()
  }

  async function generatePerformanceReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const [{ data: s }, { data: p }, { data: entries }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).gte('entry_date', range.from).lte('entry_date', range.to),
    ])
    const rev = (s || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const exp = (p || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const gop = rev - exp
    const marginPct = rev ? (gop / rev) * 100 : 0

    const revMap = {}, expMap = {}
    ;(entries || []).forEach(e => {
      const acc = e.accounts
      if (!acc) return
      const net = Number(e.debit_usd) - Number(e.credit_usd)
      if (acc.type === 'Revenue') { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += -net }
      else if (acc.type === 'Expenses') { expMap[acc.id] = expMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; expMap[acc.id].amount += net }
    })

    const sections = [
      {
        heading: 'Profit & Loss Summary',
        columns: ['Item', 'Amount', 'Amount %'],
        rows: [
          ['Total Revenue', fmt(rev), '100.0%'],
          ['Total Expenses', `-${fmt(exp)}`, rev ? `${((exp / rev) * 100).toFixed(1)}%` : '0%'],
          ['Gross Operating Profit (GOP)', fmt(gop), `${marginPct.toFixed(1)}%`],
        ],
      },
      { heading: 'Revenue by Account', columns: ['Code', 'Account', `Amount (${selections.currency})`], rows: Object.values(revMap).map(a => [a.code, a.name, fmt(a.amount)]) },
      { heading: 'Expenses by Account', columns: ['Code', 'Account', `Amount (${selections.currency})`], rows: Object.values(expMap).map(a => [a.code, a.name, fmt(a.amount)]) },
    ]

    const title = 'Financial Performance'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'financial_performance_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'financial_performance_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'financial_performance_report' })
  }

  async function generateForecastReport(selections, format) {
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const years = selections.forecastYears === 'Selected Year Only' ? [forecastYear] : Array.from({ length: 5 }, (_, i) => new Date().getFullYear() + i)
    const { data } = await supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).in('forecast_year', years).order('forecast_year').order('forecast_month')

    const rows = (data || []).map(f => {
      const profit = Number(f.revenue_usd) - Number(f.expenses_usd)
      const margin = f.revenue_usd ? (profit / f.revenue_usd) * 100 : 0
      const cols = [`${MONTHS[f.forecast_month - 1]} ${f.forecast_year}`]
      if (selections.forecastColumns.includes('Forecast Revenue')) cols.push(fmt(f.revenue_usd))
      if (selections.forecastColumns.includes('Forecast Expenses')) cols.push(fmt(f.expenses_usd))
      if (selections.forecastColumns.includes('Projected Profit')) cols.push(fmt(profit))
      if (selections.forecastColumns.includes('Profit Margin %')) cols.push(`${margin.toFixed(1)}%`)
      return cols
    })
    const columns = ['Month', ...selections.forecastColumns.map(c => `${c} (${c.includes('%') ? '' : selections.currency})`.replace(' ()', ''))]

    const sections = [{ heading: `Forecast — ${years.join(', ')}`, columns, rows }]
    const title = 'Financial Performance — Forecast'
    const subtitle = `${activeCompany.name} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'forecast_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'forecast_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'forecast_report' })
  }

  if (!activeCompany) return null

  const revenue = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const expenses = purchases.reduce((s, i) => s + Number(i.amount_usd), 0)
  const profit = revenue - expenses
  const margin = revenue ? (profit / revenue) * 100 : 0

  const monthMap = {}
  forecast.forEach(f => { monthMap[f.forecast_month] = f })

  return (
    <div>
      <PageHeader
        title="Financial Performance"
        subtitle={`${activeCompany.name} • Revenue Management`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 text-sm text-blue-700 mb-5">
        Revenue and Expenses are auto-calculated from Sales & Purchase Invoices. Revenue: {cp.fmt(revenue)} &nbsp; Expenses: {cp.fmt(expenses)}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Revenue" value={cp.fmt(revenue)} icon={TrendingUp} tone="green" />
        <KpiCard label="Expenses" value={cp.fmt(expenses)} icon={TrendingDown} tone="red" />
        <KpiCard label="Profit (GOP)" value={cp.fmt(profit)} icon={DollarSign} tone="blue" />
        <KpiCard label="GOP Margin %" value={`${margin.toFixed(1)}%`} sublabel="Revenue − Expenses" />
      </div>

      <div className="flex gap-2 mb-5 overflow-x-auto pb-1">
        {['revenue', 'expenses', 'profit', 'forecast'].map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`shrink-0 px-4 py-2 rounded-lg text-sm font-medium capitalize ${tab === t ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
            {t === 'profit' ? 'Profit / P&L' : t}
          </button>
        ))}
      </div>

      {tab === 'profit' && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h3 className="font-semibold text-slate-700 mb-4">Profit & Loss Summary</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 font-medium">Item</th>
                <th className="py-2 font-medium">Current Period</th>
                <th className="py-2 font-medium">Amount %</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-50"><td className="py-2.5 font-semibold">Total Revenue</td><td className="py-2.5">{cp.fmt(revenue)}</td><td className="py-2.5 text-slate-400">100.0%</td></tr>
              <tr className="border-b border-slate-50"><td className="py-2.5">Total Expenses</td><td className="py-2.5">−{cp.fmt(expenses)}</td><td className="py-2.5 text-slate-400">{revenue ? ((expenses / revenue) * 100).toFixed(1) : 0}%</td></tr>
              <tr className="bg-emerald-50"><td className="py-2.5 font-bold text-emerald-700">Gross Operating Profit (GOP)</td><td className="py-2.5 font-bold text-emerald-700">{cp.fmt(profit)}</td><td className="py-2.5 font-bold text-emerald-700">{margin.toFixed(1)}%</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {(tab === 'revenue' || tab === 'expenses') && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h3 className="font-semibold text-slate-700 mb-4">{tab === 'revenue' ? 'Revenue' : 'Expenses'} by Account</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 font-medium">Code</th>
                <th className="py-2 font-medium">Account</th>
                <th className="py-2 font-medium text-right">Amount</th>
                <th className="py-2 font-medium text-right">% of Total</th>
              </tr>
            </thead>
            <tbody>
              {(tab === 'revenue' ? revenueByAccount : expensesByAccount).length === 0 && (
                <tr><td colSpan={4} className="py-6 text-center text-slate-400">No {tab} activity in this period.</td></tr>
              )}
              {(tab === 'revenue' ? revenueByAccount : expensesByAccount).map(a => {
                const total = tab === 'revenue' ? revenue : expenses
                return (
                  <tr key={a.code} className="border-b border-slate-50">
                    <td className="py-2.5">{a.code}</td>
                    <td className="py-2.5">{a.name}</td>
                    <td className="py-2.5 text-right">{cp.fmt(a.amount)}</td>
                    <td className="py-2.5 text-right text-slate-400">{total ? ((a.amount / total) * 100).toFixed(1) : 0}%</td>
                  </tr>
                )
              })}
              <tr className={tab === 'revenue' ? 'bg-emerald-50 font-bold text-emerald-700' : 'bg-rose-50 font-bold text-rose-700'}>
                <td className="py-2.5" colSpan={2}>Total {tab === 'revenue' ? 'Revenue' : 'Expenses'}</td>
                <td className="py-2.5 text-right">{cp.fmt(tab === 'revenue' ? revenue : expenses)}</td>
                <td className="py-2.5 text-right">100.0%</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {tab === 'forecast' && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <h3 className="font-semibold text-slate-700">Monthly Forecast — {forecastYear}</h3>
            <div className="flex items-center gap-2">
              <select value={forecastYear} onChange={e => setForecastYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                {Array.from({ length: 6 }, (_, i) => new Date().getFullYear() + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <button onClick={() => setForecastReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-xs font-medium px-3 py-2 rounded-lg hover:border-navy-400">
                <Download size={13} /> Download
              </button>
            </div>
          </div>

          <div className="grid grid-cols-5 gap-2 px-1 pb-2 text-[11px] font-semibold text-slate-400 uppercase">
            <span>Month</span>
            <span>Forecast Revenue</span>
            <span>Forecast Expenses</span>
            <span>Projected Profit</span>
            <span>Profit Margin %</span>
          </div>
          <div className="space-y-2">
            {MONTHS.map((m, i) => {
              const month = i + 1
              const row = monthMap[month] || { revenue_usd: 0, expenses_usd: 0 }
              return (
                <ForecastRow key={month} label={`${m} ${forecastYear}`} row={row}
                  canEdit={can(['owner', 'admin', 'accountant'])}
                  onSave={(rev, exp) => saveForecastRow(month, rev, exp)} fmt={cp.fmt} />
              )
            })}
          </div>
        </div>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Financial Performance"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'MTD' },
          ]}
          onGenerate={generatePerformanceReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}

      {forecastReportModalOpen && (
        <ReportOptionsModal
          title="Forecast"
          fields={[
            { type: 'radio', key: 'forecastYears', label: 'Years to Include', options: ['Selected Year Only', 'Next 5 Years'], default: 'Selected Year Only' },
            { type: 'checkboxGroup', key: 'forecastColumns', label: 'Columns to Include', options: ['Forecast Revenue', 'Forecast Expenses', 'Projected Profit', 'Profit Margin %'], default: ['Forecast Revenue', 'Forecast Expenses', 'Projected Profit', 'Profit Margin %'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
          ]}
          onGenerate={generateForecastReport}
          onClose={() => setForecastReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function ForecastRow({ label, row, canEdit, onSave, fmt }) {
  const [revenue, setRevenue] = useState(row.revenue_usd)
  const [exp, setExp] = useState(row.expenses_usd)
  useEffect(() => { setRevenue(row.revenue_usd); setExp(row.expenses_usd) }, [row])
  const profit = revenue - exp
  const marginPct = revenue ? (profit / revenue) * 100 : 0
  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 items-center py-2 border-b border-slate-50 last:border-0">
      <span className="text-sm text-slate-600 font-medium">{label}</span>
      <input type="number" disabled={!canEdit} value={revenue} onChange={e => setRevenue(Number(e.target.value))}
        className="border border-slate-200 rounded-md px-2 py-1 text-sm disabled:bg-slate-50" />
      <input type="number" disabled={!canEdit} value={exp} onChange={e => setExp(Number(e.target.value))}
        className="border border-slate-200 rounded-md px-2 py-1 text-sm disabled:bg-slate-50" />
      <span className={`text-sm font-semibold ${profit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>{fmt(profit)}</span>
      <div className="flex items-center justify-between gap-2">
        <span className={`text-sm font-semibold ${marginPct >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>{marginPct.toFixed(1)}%</span>
        {canEdit && <button onClick={() => onSave(revenue, exp)} className="text-xs bg-navy-600 text-white px-2 py-1 rounded-md">Save</button>}
      </div>
    </div>
  )
}
