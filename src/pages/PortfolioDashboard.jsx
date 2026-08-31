import { useEffect, useState } from 'react'
import { DollarSign, TrendingDown, TrendingUp, FileCheck, CheckCircle2, Building2 } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { getMTDRange, getYTDRange, resolvePeriodRange } from '../lib/fiscalYear'
import { getLatestRatesMap, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import KpiCard from '../components/KpiCard'

const PRODUCT_LABELS = { basic: 'CRS Basic Accounting', hotel: 'CRS Hotel Accounting', restaurant: 'CRS Restaurant Accounting' }
const DA_INTEREST_NAMES = ['Depreciation & Amortization', 'Loan Interest']

// Brand-consistent card accents -- navy and gold (the two brand colors) plus the
// status colors already used across KpiCard/StatBox elsewhere in the app, so this
// page looks native rather than introducing a new palette.
const CARD_STYLES = [
  { bg: 'bg-navy-50', border: 'border-navy-100', accent: 'bg-navy-600', text: 'text-navy-700' },
  { bg: 'bg-gold-50', border: 'border-gold-100', accent: 'bg-gold-600', text: 'text-gold-700' },
  { bg: 'bg-emerald-50', border: 'border-emerald-100', accent: 'bg-emerald-600', text: 'text-emerald-700' },
  { bg: 'bg-blue-50', border: 'border-blue-100', accent: 'bg-blue-600', text: 'text-blue-700' },
  { bg: 'bg-amber-50', border: 'border-amber-100', accent: 'bg-amber-600', text: 'text-amber-700' },
  { bg: 'bg-rose-50', border: 'border-rose-100', accent: 'bg-rose-600', text: 'text-rose-700' },
]

export default function PortfolioDashboard() {
  const { companies } = useAuth()
  const [periodType, setPeriodType] = useState('MTD')
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [ratesMap, setRatesMap] = useState({ USD: 1 })
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  const range = resolvePeriodRange(periodType, {})

  useEffect(() => { loadRates() }, [displayCurrency])
  useEffect(() => { if (companies.length > 0) loadPortfolio() }, [companies.length, periodType])

  async function loadRates() {
    const codes = CURRENCY_LIST.map(c => c.code)
    setRatesMap(await getLatestRatesMap(codes))
  }

  function fmt(usd) {
    return formatMoney(convertFromUsd(usd, displayCurrency, ratesMap), displayCurrency)
  }

  async function computeCompanyProductMetrics(companyId, product) {
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

  async function loadPortfolio() {
    setLoading(true)
    const tasks = []
    companies.forEach(({ company }) => {
      ;(company.company_products || []).forEach(({ product }) => {
        tasks.push(
          computeCompanyProductMetrics(company.id, product).then(metrics => ({
            companyId: company.id, companyName: company.name, product, ...metrics,
          }))
        )
      })
    })
    const results = await Promise.all(tasks)
    setRows(results)
    setLoading(false)
  }

  const combined = rows.reduce((acc, r) => ({
    revenue: acc.revenue + r.revenue,
    expenses: acc.expenses + r.expenses,
    gop: acc.gop + r.gop,
    ebitda: acc.ebitda + r.ebitda,
    invoicesRaised: acc.invoicesRaised + r.invoicesRaised,
    collected: acc.collected + r.collected,
  }), { revenue: 0, expenses: 0, gop: 0, ebitda: 0, invoicesRaised: 0, collected: 0 })

  return (
    <div>
      <div className="mb-5 sm:mb-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-navy-700 font-[var(--font-display)]">All Companies Overview</h1>
            <p className="text-sm text-slate-500 mt-1">Combined across every company and product you have access to</p>
          </div>
          <div className="flex gap-2">
            <div className="flex gap-1 bg-slate-100 rounded-lg p-1">
              {[['MTD', 'This Month'], ['YTD', 'This Year'], ['ALL_TIME', 'All Time']].map(([val, label]) => (
                <button key={val} onClick={() => setPeriodType(val)} className={`px-3 py-1.5 rounded-md text-xs font-medium ${periodType === val ? 'bg-white shadow text-navy-700' : 'text-slate-500'}`}>{label}</button>
              ))}
            </div>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-slate-400 text-center py-10">Loading combined data across all companies…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-4 mb-8">
            <KpiCard label="Combined Sales" value={fmt(combined.revenue)} icon={DollarSign} tone="green" />
            <KpiCard label="Combined Expenses" value={fmt(combined.expenses)} icon={TrendingDown} tone="red" />
            <KpiCard label="Combined GOP" value={fmt(combined.gop)} icon={TrendingUp} tone="gold" />
            <KpiCard label="Combined EBITDA" value={fmt(combined.ebitda)} icon={TrendingUp} tone="blue" />
            <KpiCard label="Invoices Raised" value={combined.invoicesRaised} icon={FileCheck} tone="slate" />
            <KpiCard label="Money Collected" value={fmt(combined.collected)} icon={CheckCircle2} tone="green" />
          </div>

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
                      <Row label="Revenue" value={fmt(r.revenue)} />
                      <Row label="Expenses" value={fmt(r.expenses)} />
                      <Row label="GOP" value={fmt(r.gop)} />
                      <Row label="EBITDA" value={fmt(r.ebitda)} bold textClass={style.text} />
                      <Row label="Invoices Raised" value={r.invoicesRaised} />
                      <Row label="Collected" value={fmt(r.collected)} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
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
