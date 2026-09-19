import { useEffect, useState, useMemo } from 'react'
import { Save, TrendingUp, AlertTriangle } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCIES } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function HotelExpenseBudget() {
  const { activeCompany, activeProduct, can } = useAuth()
  
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
  
  const [accounts, setAccounts] = useState([])
  const [budgets, setBudgets] = useState({}) // key: "accountCode-month" -> { amount, currency, amount_usd }
  const [actuals, setActuals] = useState({}) // key: "accountCode-month" -> amount_usd
  const [saving, setSaving] = useState({})
  
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})
  
  const [reportModalOpen, setReportModalOpen] = useState(false)

  // Load FX
  useEffect(() => {
    async function loadRates() {
      const rs = {}
      for (const c of CURRENCIES) {
        if (c.code !== 'USD') rs[c.code] = await getLatestRate(c.code)
      }
      setRates(rs)
    }
    loadRates()
  }, [])
  
  useEffect(() => { 
    if (displayCurrency === 'USD') { setRate(1); return } 
    getLatestRate(displayCurrency).then(r => setRate(r || 1)) 
  }, [displayCurrency])

  function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }

  // 1. Fetch Accounts
  useEffect(() => {
    async function fetchAccounts() {
      if (!activeCompany) return
      const { data } = await supabase.from('accounts').select('code, name').eq('company_id', activeCompany.id).eq('type', 'Expense').order('code')
      setAccounts(data || [])
    }
    fetchAccounts()
  }, [activeCompany])

  // 2. Fetch Data for Selected Year
  useEffect(() => {
    async function loadAll() {
      if (!activeCompany || accounts.length === 0) return

      const [{ data: budgetRows }, { data: ledgerRows }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', selectedYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${selectedYear}-01-01`).lte('entry_date', `${selectedYear}-12-31`).eq('accounts.type', 'Expense')
      ])

      const bMap = {}
      if (budgetRows) {
        budgetRows.forEach(r => {
          bMap[`${r.account_code}-${r.budget_month}`] = { amount: r.amount, currency: r.currency, amount_usd: r.amount_usd }
        })
      }
      setBudgets(bMap)

      const aMap = {}
      if (ledgerRows) {
        ledgerRows.forEach(r => {
          const m = parseInt(r.entry_date.split('-')[1], 10)
          const k = `${r.accounts.code}-${m}`
          const amt = (Number(r.debit_usd) || 0) - (Number(r.credit_usd) || 0) // Expenses are debits
          aMap[k] = (aMap[k] || 0) + amt
        })
      }
      setActuals(aMap)
    }
    loadAll()
  }, [activeCompany, selectedYear, accounts])

  async function handleSaveRow(accountCode) {
    if (!activeCompany) return
    const key = `${accountCode}-${selectedMonth}`
    const row = budgets[key] || { amount: 0, currency: displayCurrency }
    if (!row.amount) return

    setSaving(s => ({ ...s, [accountCode]: true }))
    
    const currency = row.currency || displayCurrency
    const fxRate = currency === 'USD' ? 1 : (rates[currency] || rate)
    const amountUsd = currency === 'USD' ? row.amount : (row.amount / fxRate)
    
    const { error } = await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      budget_year: selectedYear,
      budget_month: selectedMonth,
      account_code: accountCode,
      amount: row.amount,
      currency: currency,
      amount_usd: amountUsd
    }, { onConflict: 'company_id, budget_year, budget_month, account_code' })
    
    if (error) alert('Error saving budget: ' + error.message)
    setSaving(s => ({ ...s, [accountCode]: false }))
  }

  function handleRowChange(accountCode, field, val) {
    const key = `${accountCode}-${selectedMonth}`
    const cur = budgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
    const updated = { ...cur, [field]: val }
    
    if (field === 'currency') updated.currency = val
    
    const c = updated.currency || displayCurrency
    const r = c === 'USD' ? 1 : (rates[c] || rate)
    if (r) {
      updated.amount_usd = c === 'USD' ? updated.amount : (updated.amount / r)
    }
    setBudgets(b => ({ ...b, [key]: updated }))
  }

  function clearRow(accountCode) {
    const key = `${accountCode}-${selectedMonth}`
    if (!budgets[key]) return
    const updated = { ...budgets[key], amount: 0, amount_usd: 0 }
    setBudgets(b => ({ ...b, [key]: updated }))
  }

  // Calculate 12-Month Summary
  const monthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    
    for (let m = 1; m <= 12; m++) {
      let mBudget = 0
      let mActual = 0
      for (const a of accounts) {
        const k = `${a.code}-${m}`
        if (budgets[k]) mBudget += Number(budgets[k].amount_usd) || 0
        if (actuals[k]) mActual += Number(actuals[k]) || 0
      }
      totalBudget += mBudget
      totalActual += mActual
      summary.push({ month: m, name: MONTH_NAMES[m - 1], budget: mBudget, actual: mActual, variance: mActual - mBudget })
    }
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget }
  }, [budgets, actuals, accounts])
  
  if (!activeCompany) return null
  
  // Reports
  async function generateReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (rates[selections.currency] || 1)
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    
    const sections = []
    
    // 1. Annual Summary
    const summaryRows = []
    for (const m of monthlySummary.months) {
      summaryRows.push([
        m.name,
        f(m.budget),
        f(m.actual),
        f(m.variance)
      ])
    }
    summaryRows.push([
      'Total',
      f(monthlySummary.totalBudget),
      f(monthlySummary.totalActual),
      f(monthlySummary.totalVariance)
    ])
    
    sections.push({
      title: `${selectedYear} Annual Summary`,
      headers: ['Month', 'Budget', 'Actual', 'Variance'],
      rows: summaryRows
    })
    
    // 2. Selected Month Detailed Budget
    const monthName = MONTH_NAMES[selectedMonth - 1]
    const detailRows = []
    for (const a of accounts) {
      const key = `${a.code}-${selectedMonth}`
      const row = budgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
      const monthlyUsd = Number(row.amount_usd) || 0
      const actualUsd = actuals[key] || 0
      
      const cur = row.currency || displayCurrency
      const rr = cur === 'USD' ? 1 : (rates[cur] || rate)
      const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * rr)
      const monthlyLocal = cur === 'USD' ? monthlyUsd : (monthlyUsd * rr)
      
      detailRows.push([
        `${a.code} - ${a.name}`,
        formatMoney(monthlyLocal, cur),
        f(monthlyUsd),
        formatMoney(actualLocal, cur),
        f(actualUsd),
        formatMoney(actualLocal - monthlyLocal, cur),
        f(actualUsd - monthlyUsd)
      ])
    }
    
    sections.push({
      title: `${monthName} ${selectedYear} Detailed Budget`,
      headers: ['Account', 'Monthly Budget', 'Monthly (USD)', 'Actual', 'Actual (USD)', 'Variance', 'Variance (USD)'],
      rows: detailRows
    })
    
    const ctx = {
      companyName: activeCompany.name,
      reportName: `Expenses Budget - ${selectedYear}`,
      currencyCode: selections.currency,
      dateRange: `${selectedYear}`
    }
    
    if (format === 'pdf') exportMultiSectionPDF(ctx, sections)
    else if (format === 'excel') exportMultiSectionExcel(ctx, sections)
    else if (format === 'word') exportMultiSectionWord(ctx, sections)
  }

  return (
    <div>
      <PageHeader
        title="Expenses Budget"
        subtitle="Manage monthly budgets for all expense categories"
        actions={
          <div className="flex items-center gap-3">
            <button onClick={() => setReportModalOpen(true)} className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors shadow-sm">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </div>
        }
      />

      <div className="flex items-center gap-3 mb-6 bg-slate-50 p-3 rounded-xl border border-slate-200">
        <span className="text-sm font-medium text-slate-600">Select Year:</span>
        <select value={selectedYear} onChange={e => setSelectedYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
          {Array.from({ length: 11 }, (_, i) => new Date().getFullYear() - 5 + i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${selectedYear} Total Actual`} value={fmt(monthlySummary.totalActual)} icon={TrendingUp} tone="green" />
        <KpiCard label={`${selectedYear} Total Variance`} value={fmt(monthlySummary.totalVariance)} icon={AlertTriangle} tone={monthlySummary.totalVariance > 0 ? "red" : "green"} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
        <div className="min-w-max w-full">
          <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">${selectedYear} Annual Summary</div>
          <table className="w-full text-sm">
            <thead className="bg-navy-800 text-white text-xs text-left">
              <tr>
                <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                <th className="py-2 px-3 font-semibold">Budget (USD)</th>
                <th className="py-2 px-3 font-semibold">Actual (USD)</th>
                <th className="py-2 px-3 font-semibold rounded-tr-lg">Variance (USD)</th>
              </tr>
            </thead>
            <tbody>
              {monthlySummary.months.map(m => (
                <tr key={m.month} className="border-b border-slate-50 hover:bg-slate-50/50">
                  <td className="py-2 px-3 font-medium text-slate-700 w-32">{m.name}</td>
                  <td className="py-2 px-3 text-slate-500">{fmt(m.budget)}</td>
                  <td className="py-2 px-3 text-slate-500">{fmt(m.actual)}</td>
                  <td className={`py-2 px-3 font-medium ${m.variance > 0 ? 'text-red-600' : 'text-emerald-600'}`}>{fmt(m.variance)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4 mt-8">
        <h2 className="text-xl font-bold text-slate-800 font-[var(--font-display)]">Detailed Monthly Budget</h2>
      </div>

      <div className="flex items-center gap-3 mb-4 bg-slate-50 p-3 rounded-xl border border-slate-200">
        <span className="text-sm font-medium text-slate-600">Select Month:</span>
        <select value={selectedMonth} onChange={e => setSelectedMonth(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
          {MONTH_NAMES.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
        </select>
        <span className="text-xs text-slate-400">Manage budget for each of the 63 expense accounts</span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
        <div className="min-w-max w-full">
          <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{MONTH_NAMES[selectedMonth - 1]} {selectedYear}</div>
          <table className="w-full text-sm">
            <thead className="bg-navy-800 text-white text-xs text-left">
              <tr>
                <th className="py-2 px-3 font-semibold rounded-tl-lg">Account</th>
                <th className="py-2 px-3 font-semibold">Monthly Budget</th>
                <th className="py-2 px-3 font-semibold">Monthly (USD)</th>
                <th className="py-2 px-3 font-semibold">Actual</th>
                <th className="py-2 px-3 font-semibold">Actual (USD)</th>
                <th className="py-2 px-3 font-semibold">Variance</th>
                <th className="py-2 px-3 font-semibold">Variance (USD)</th>
                <th className="py-2 px-3 font-semibold rounded-tr-lg"></th>
              </tr>
            </thead>
            <tbody>
              {accounts.map(a => {
                const key = `${a.code}-${selectedMonth}`
                const row = budgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
                
                const monthlyUsd = Number(row.amount_usd) || 0
                const actualUsd = actuals[key] || 0
                
                const cur = row.currency || displayCurrency
                const r = cur === 'USD' ? 1 : (rates[cur] || rate)
                
                const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * r)
                const monthlyLocal = cur === 'USD' ? monthlyUsd : (monthlyUsd * r)
                
                const varUsd = actualUsd - monthlyUsd
                const varLocal = actualLocal - monthlyLocal

                const isSaving = saving[a.code]

                return (
                  <tr key={a.code} className="border-b border-slate-50 hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-medium text-slate-700 w-64">
                      {a.code} - {a.name}
                    </td>
                    
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-1 min-w-[180px]">
                        <select value={row.currency || displayCurrency} onChange={e => handleRowChange(a.code, 'currency', e.target.value)}
                          className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm bg-white" disabled={!can(['owner','admin','accountant'])}>
                          {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                        </select>
                        <input type="number" value={row.amount || ''} onChange={e => handleRowChange(a.code, 'amount', e.target.value)}
                          placeholder="Amount" className="w-24 border border-slate-300 rounded-lg px-2 py-1.5 text-sm" disabled={!can(['owner','admin','accountant'])} />
                      </div>
                    </td>
                    
                    <td className="py-2 px-3 text-slate-500 min-w-[120px]">{formatMoney(monthlyUsd, 'USD')}</td>
                    <td className="py-2 px-3 text-slate-500 min-w-[120px]">{formatMoney(actualLocal, cur)}</td>
                    <td className="py-2 px-3 text-slate-500 min-w-[120px]">{formatMoney(actualUsd, 'USD')}</td>
                    
                    <td className={`py-2 px-3 font-medium min-w-[120px] ${varLocal > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                      {formatMoney(varLocal, cur)}
                    </td>
                    <td className={`py-2 px-3 font-medium min-w-[120px] ${varUsd > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                      {formatMoney(varUsd, 'USD')}
                    </td>

                    <td className="py-2 px-3 text-right">
                      {can(['owner','admin','accountant']) && (
                        <div className="flex items-center justify-end gap-2">
                          <button onClick={() => handleSaveRow(a.code)} disabled={isSaving} className="text-navy-600 hover:text-navy-800 text-xs font-semibold">
                            {isSaving ? 'Saving...' : 'Save'}
                          </button>
                          <button onClick={() => { clearRow(a.code); setTimeout(()=> handleSaveRow(a.code), 100) }} className="text-rose-500 hover:text-rose-700 text-xs font-semibold">
                            Clear
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
              {accounts.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-6 text-center text-slate-500 text-sm italic">
                    No expense accounts found for this company.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {reportModalOpen && (
        <ReportOptionsModal
          onClose={() => setReportModalOpen(false)}
          onGenerate={generateReport}
          title="Expenses Budget"
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency }
          ]}
        />
      )}
    </div>
  )
}
