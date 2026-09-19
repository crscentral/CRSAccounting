import { useEffect, useState } from 'react'
import { Save } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST, CURRENCIES } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'

export default function HotelExpenseBudget() {
  const { activeCompany, activeProduct, can } = useAuth()
  const [startYear, setStartYear] = useState(new Date().getFullYear())
  const [accounts, setAccounts] = useState([])
  const [activeAccount, setActiveAccount] = useState('')
  const [rows, setRows] = useState({}) // key: "year-month" -> { amount, currency, amount_usd }
  const [actuals, setActuals] = useState({}) // key: "year-month" -> amount_usd actual
  const [saving, setSaving] = useState({})
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})

  useEffect(() => {
    async function fetchAccounts() {
      if (!activeCompany) return
      const { data } = await supabase.from('accounts').select('code, name').eq('company_id', activeCompany.id).eq('type', 'Expense').order('code')
      setAccounts(data || [])
      if (data && data.length > 0 && !activeAccount) setActiveAccount(data[0].code)
    }
    fetchAccounts()
  }, [activeCompany])

  useEffect(() => { if (activeCompany && activeAccount) loadAll() }, [activeCompany, activeAccount, startYear])

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
  useEffect(() => { if (displayCurrency === 'USD') { setRate(1); return } getLatestRate(displayCurrency).then(r => setRate(r || 1)) }, [displayCurrency])

  function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }

  async function loadAll() {
    const [{ data: budgetRows }, { data: ledgerRows }] = await Promise.all([
      supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('account_code', activeAccount).gte('budget_year', startYear).lte('budget_year', startYear + 4),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear + 4}-12-31`).eq('accounts.code', activeAccount)
    ])

    const rMap = {}
    if (budgetRows) {
      budgetRows.forEach(r => {
        rMap[`${r.budget_year}-${r.budget_month}`] = { amount: r.amount, currency: r.currency, amount_usd: r.amount_usd }
      })
    }
    setRows(rMap)

    const aMap = {}
    if (ledgerRows) {
      ledgerRows.forEach(r => {
        const d = new Date(r.entry_date)
        const k = `${d.getFullYear()}-${d.getMonth() + 1}`
        const amt = Number(r.debit_usd || 0) - Number(r.credit_usd || 0)
        aMap[k] = (aMap[k] || 0) + amt
      })
    }
    setActuals(aMap)
  }

  async function handleSaveRow(year, month) {
    const key = `${year}-${month}`
    const row = rows[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
    setSaving({ ...saving, [key]: true })
    
    // Ensure amount is populated
    row.amount = Number(row.amount) || 0
    
    const { error } = await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      budget_year: year,
      budget_month: month,
      account_code: activeAccount,
      amount: row.amount,
      currency: row.currency,
      amount_usd: row.amount_usd,
    }, { onConflict: 'company_id,budget_year,budget_month,account_code' })
    
    if (error) alert('Error saving budget: ' + error.message)
    setSaving({ ...saving, [key]: false })
  }

  function handleRowChange(year, month, field, val) {
    const key = `${year}-${month}`
    const cur = rows[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
    const updated = { ...cur, [field]: val }
    
    if (field === 'currency') updated.currency = val
    
    // Auto convert to USD
    const c = updated.currency || displayCurrency
    const r = c === 'USD' ? 1 : (rates[c] || rate)
    if (r) {
      updated.amount_usd = c === 'USD' ? updated.amount : (updated.amount / r)
    }
    setRows({ ...rows, [key]: updated })
  }

  function clearRow(year, month) {
    const key = `${year}-${month}`
    if (!rows[key]) return
    const cur = rows[key]
    const updated = { ...cur, amount: 0, amount_usd: 0 }
    setRows({ ...rows, [key]: updated })
  }

  if (!activeCompany) return null

  // Calc top summary cards for the selected year
  let thisYearBudget = 0
  let thisYearActual = 0
  for (let m=1; m<=12; m++) {
      const k = `${startYear}-${m}`
      if (rows[k]) thisYearBudget += Number(rows[k].amount_usd) || 0
      if (actuals[k]) thisYearActual += Number(actuals[k]) || 0
  }
  const thisYearVar = thisYearActual - thisYearBudget

  const years = Array.from({ length: 5 }, (_, i) => startYear + i)

  return (
    <div>
      <PageHeader
        title="Expenses Budget"
        subtitle="Manage monthly budgets for each expense category"
        currencyProps={{ displayCurrency, setDisplayCurrency }}
        actions={
          <div className="flex items-center gap-2">
            <select value={activeAccount} onChange={e => setActiveAccount(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-700 bg-white shadow-sm focus:ring-2 focus:ring-navy-500 max-w-[200px]">
              {accounts.map(a => <option key={a.code} value={a.code}>{a.code} - {a.name}</option>)}
            </select>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${startYear} Budget`} amount={fmt(thisYearBudget)} icon={<TrendingUp size={20} className="text-emerald-600" />} />
        <KpiCard label={`${startYear} Actual`} amount={fmt(thisYearActual)} icon={<TrendingUp size={20} className="text-emerald-600" />} />
        <KpiCard label={`${startYear} Variance`} amount={fmt(thisYearVar)} amountColor={thisYearVar > 0 ? 'text-red-600' : 'text-emerald-600'} icon={<AlertTriangle size={20} className="text-rose-500" />} />
      </div>

      <div className="flex items-center gap-3 mb-6 bg-slate-50 p-3 rounded-xl border border-slate-200">
        <span className="text-sm font-medium text-slate-600">Starting Year:</span>
        <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
          {Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - 1 + i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
        <span className="text-xs text-slate-400">Shows this year + next 4 (5 years total)</span>
      </div>

      {years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year}</div>
            <table className="w-full text-sm">
            <thead className="bg-navy-800 text-white text-xs text-left">
              <tr>
                <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
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
              {MONTH_NAMES.map((m, i) => {
                const month = i + 1
                const key = `${year}-${month}`
                const row = rows[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
                
                const monthlyUsd = Number(row.amount_usd) || 0
                
                const actualUsd = actuals[key] || 0
                const cur = row.currency || displayCurrency
                const r = cur === 'USD' ? 1 : (rates[cur] || rate)
                const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * r)
                
                const monthlyLocal = cur === 'USD' ? monthlyUsd : (monthlyUsd * r)
                
                const varUsd = actualUsd - monthlyUsd
                const varLocal = actualLocal - monthlyLocal

                const isSaving = saving[key]

                return (
                  <tr key={month} className="border-b border-slate-50 hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-medium text-slate-700 w-24">{m}</td>
                    
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-1 min-w-[180px]">
                        <select value={row.currency || displayCurrency} onChange={e => handleRowChange(year, month, 'currency', e.target.value)}
                          className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm bg-white" disabled={!can(['owner','admin','accountant'])}>
                          {CURRENCY_LIST.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                        <input type="number" value={row.amount || ''} onChange={e => handleRowChange(year, month, 'amount', e.target.value)}
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
                          <button onClick={() => handleSaveRow(year, month)} disabled={isSaving} className="text-navy-600 hover:text-navy-800 text-xs font-semibold">
                            {isSaving ? 'Saving...' : 'Save'}
                          </button>
                          <button onClick={() => { clearRow(year,month); setTimeout(()=> handleSaveRow(year,month), 100) }} className="text-rose-500 hover:text-rose-700 text-xs font-semibold">
                            Clear
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          </div>
        </div>
      ))}
    </div>
  )
}
