import { useEffect, useState } from 'react'
import { ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES, getMonthRange, getYearRange } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

const DA_INTEREST_NAMES = ['Depreciation & Amortization', 'Loan Interest']
const now = new Date()

export default function Comparison() {
  const { activeCompany, activeProduct } = useAuth()
  const [mode, setMode] = useState('month') // 'month' | 'year'
  const [aYear, setAYear] = useState(now.getFullYear())
  const [aMonth, setAMonth] = useState(now.getMonth() === 0 ? 12 : now.getMonth())
  const [bYear, setBYear] = useState(now.getFullYear())
  const [bMonth, setBMonth] = useState(now.getMonth() + 1)
  const [currency, setCurrency] = useState('USD')
  const [dataA, setDataA] = useState(null)
  const [dataB, setDataB] = useState(null)
  const [loading, setLoading] = useState(false)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  const rangeA = mode === 'month' ? getMonthRange(aYear, aMonth) : getYearRange(aYear)
  const rangeB = mode === 'month' ? getMonthRange(bYear, bMonth) : getYearRange(bYear)
  const labelA = mode === 'month' ? `${MONTH_NAMES[aMonth - 1]} ${aYear}` : `${aYear}`
  const labelB = mode === 'month' ? `${MONTH_NAMES[bMonth - 1]} ${bYear}` : `${bYear}`

  useEffect(() => { if (activeCompany) loadComparison() }, [activeCompany, activeProduct, mode, aYear, aMonth, bYear, bMonth, currency])

  async function computeMetrics(range) {
    const { data: accounts } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date')
      .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to)

    const balances = {}
    ;(entries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })

    const byType = (type) => (accounts || []).filter(a => a.type === type)
    const sumAccs = (list) => list.reduce((s, a) => s + (balances[a.id] || 0), 0)

    const revenue = -sumAccs(byType('Revenue'))
    const belowLine = byType('Expenses').filter(a => ['Below GOP', 'Below EBITDA'].includes(a.subtype))
    const daInterestAccs = belowLine.filter(a => DA_INTEREST_NAMES.includes(a.name))
    const otherBelowLineAccs = belowLine.filter(a => !DA_INTEREST_NAMES.includes(a.name))
    const operatingAccs = byType('Expenses').filter(a => !['Below GOP', 'Below EBITDA'].includes(a.subtype))
    const operatingExpenses = sumAccs(operatingAccs)
    const otherBelowLine = sumAccs(otherBelowLineAccs)
    const daInterest = sumAccs(daInterestAccs)
    const totalExpenses = operatingExpenses + otherBelowLine + daInterest
    const ebitda = revenue - operatingExpenses - otherBelowLine
    const netIncome = revenue - totalExpenses

    return { revenue, operatingExpenses, otherBelowLine, daInterest, totalExpenses, ebitda, netIncome }
  }

  async function loadComparison() {
    setLoading(true)
    const rate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
    const [a, b] = await Promise.all([computeMetrics(rangeA), computeMetrics(rangeB)])
    setDataA({ ...a, rate }); setDataB({ ...b, rate })
    setLoading(false)
  }

  function fmt(usd) {
    return formatMoney(convertFromUsd(usd, currency, { [currency]: dataA?.rate || 1 }), currency)
  }

  async function generateComparisonReport(selections, format) {
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)
    const [a, b] = await Promise.all([computeMetrics(rangeA), computeMetrics(rangeB)])

    const rows = [
      ['Revenue', f(a.revenue), f(b.revenue), f(b.revenue - a.revenue)],
      ['Operating Expenses', f(a.operatingExpenses), f(b.operatingExpenses), f(b.operatingExpenses - a.operatingExpenses)],
      ['EBITDA', f(a.ebitda), f(b.ebitda), f(b.ebitda - a.ebitda)],
      ['Net Income', f(a.netIncome), f(b.netIncome), f(b.netIncome - a.netIncome)],
    ]
    const sections = [{ heading: 'Period Comparison', columns: ['Metric', labelA, labelB, 'Variance'], rows }]

    const title = 'Period Comparison'
    const subtitle = `${activeCompany.name} • ${labelA} vs ${labelB} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'period_comparison' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'period_comparison' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'period_comparison' })
  }

  if (!activeCompany) return null

  const years = Array.from({ length: 8 }, (_, i) => now.getFullYear() - 6 + i)

  const metrics = dataA && dataB ? [
    { label: 'Revenue', a: dataA.revenue, b: dataB.revenue, positive: true },
    { label: 'Operating Expenses', a: dataA.operatingExpenses, b: dataB.operatingExpenses, positive: false },
    { label: 'EBITDA', a: dataA.ebitda, b: dataB.ebitda, positive: true },
    { label: 'Net Income', a: dataA.netIncome, b: dataB.netIncome, positive: true },
  ] : []

  return (
    <div>
      <PageHeader
        title="Compare Periods"
        subtitle={`${activeCompany.name} • This month vs last month, same month last year, or any year vs any year`}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <div className="flex flex-wrap items-center gap-3 mb-5">
          <div className="flex gap-1 bg-slate-100 rounded-lg p-1">
            <button onClick={() => setMode('month')} className={`px-3 py-1.5 rounded-md text-xs font-medium ${mode === 'month' ? 'bg-white shadow text-navy-700' : 'text-slate-500'}`}>Month vs Month</button>
            <button onClick={() => setMode('year')} className={`px-3 py-1.5 rounded-md text-xs font-medium ${mode === 'year' ? 'bg-white shadow text-navy-700' : 'text-slate-500'}`}>Year vs Year</button>
          </div>
          <div className="flex gap-2 ml-auto">
            {mode === 'month' && (
              <button onClick={() => {
                const d = new Date(); const lastMonth = d.getMonth() === 0 ? 12 : d.getMonth(); const lastYear = d.getMonth() === 0 ? d.getFullYear() - 1 : d.getFullYear()
                setAYear(lastYear); setAMonth(lastMonth); setBYear(d.getFullYear()); setBMonth(d.getMonth() + 1)
              }} className="text-xs px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:border-navy-400">This Month vs Last Month</button>
            )}
            {mode === 'month' && (
              <button onClick={() => {
                const d = new Date(); setAYear(d.getFullYear() - 1); setAMonth(d.getMonth() + 1); setBYear(d.getFullYear()); setBMonth(d.getMonth() + 1)
              }} className="text-xs px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:border-navy-400">Same Month, Last Year</button>
            )}
          </div>
          <select value={currency} onChange={e => setCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
          </select>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div className="border border-slate-200 rounded-lg p-3">
            <div className="text-xs font-semibold text-slate-400 uppercase mb-2">Period A</div>
            {mode === 'month' ? (
              <div className="flex gap-2">
                <select value={aMonth} onChange={e => setAMonth(Number(e.target.value))} className="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                  {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                </select>
                <select value={aYear} onChange={e => setAYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                  {years.map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
            ) : (
              <select value={aYear} onChange={e => setAYear(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                {years.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            )}
          </div>
          <div className="border border-slate-200 rounded-lg p-3">
            <div className="text-xs font-semibold text-slate-400 uppercase mb-2">Period B</div>
            {mode === 'month' ? (
              <div className="flex gap-2">
                <select value={bMonth} onChange={e => setBMonth(Number(e.target.value))} className="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                  {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                </select>
                <select value={bYear} onChange={e => setBYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                  {years.map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
            ) : (
              <select value={bYear} onChange={e => setBYear(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                {years.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            )}
          </div>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-slate-400 text-center py-10">Loading comparison…</p>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">
          <table className="w-full text-sm min-w-[560px]">
            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-3 px-4 font-medium">Metric</th>
                <th className="py-3 px-4 font-medium">{labelA}</th>
                <th className="py-3 px-4 font-medium"><ArrowRight size={14} className="inline" /></th>
                <th className="py-3 px-4 font-medium">{labelB}</th>
                <th className="py-3 px-4 font-medium">Variance</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map(m => {
                const diff = m.b - m.a
                const pct = m.a !== 0 ? (diff / Math.abs(m.a)) * 100 : (diff !== 0 ? 100 : 0)
                const isGood = m.positive ? diff >= 0 : diff <= 0
                const Icon = diff === 0 ? Minus : (diff > 0 ? TrendingUp : TrendingDown)
                return (
                  <tr key={m.label} className="border-b border-slate-50 last:border-0">
                    <td className="py-3 px-4 font-medium text-slate-700">{m.label}</td>
                    <td className="py-3 px-4 text-slate-600">{fmt(m.a)}</td>
                    <td></td>
                    <td className="py-3 px-4 text-slate-600">{fmt(m.b)}</td>
                    <td className={`py-3 px-4 font-medium flex items-center gap-1 ${diff === 0 ? 'text-slate-400' : isGood ? 'text-emerald-600' : 'text-red-600'}`}>
                      <Icon size={14} /> {fmt(Math.abs(diff))} ({pct >= 0 ? '+' : ''}{pct.toFixed(1)}%)
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Period Comparison"
          fields={[{ type: 'currency', key: 'currency', default: currency }]}
          onGenerate={generateComparisonReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
