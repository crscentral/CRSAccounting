import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Add new state variables and imports
if 'const [ancillaryYear, setAncillaryYear]' not in content:
    # 1. Update imports to ensure we have useMemo
    content = content.replace("import { useState, useEffect } from 'react'", "import { useState, useEffect, useMemo } from 'react'")
    if "useMemo" not in content:
        content = content.replace("import { useEffect, useState } from 'react'", "import { useEffect, useState, useMemo } from 'react'")

    # 2. Add Ancillary Revenue State inside the component
    state_injection = """
  // --- Ancillary Revenue State ---
  const [ancillaryYear, setAncillaryYear] = useState(new Date().getFullYear())
  const [ancillaryMonth, setAncillaryMonth] = useState(new Date().getMonth() + 1)
  const [ancillaryAccounts, setAncillaryAccounts] = useState([])
  const [ancillaryBudgets, setAncillaryBudgets] = useState({})
  const [ancillaryActuals, setAncillaryActuals] = useState({})
  const [ancillarySaving, setAncillarySaving] = useState({})

  // Fetch Ancillary Accounts
  useEffect(() => {
    async function fetchAncillaryAccounts() {
      if (!activeCompany) return
      const { data } = await supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('type', 'Revenue').neq('code', '4010').order('subtype', { ascending: true }).order('code', { ascending: true })
      setAncillaryAccounts(data || [])
    }
    fetchAncillaryAccounts()
  }, [activeCompany])

  // Fetch Ancillary Data
  useEffect(() => {
    async function loadAncillary() {
      if (!activeCompany || ancillaryAccounts.length === 0) return

      const [{ data: budgetRows }, { data: ledgerRows }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', ancillaryYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${ancillaryYear}-01-01`).lte('entry_date', `${ancillaryYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')
      ])

      const bMap = {}
      if (budgetRows) {
        budgetRows.forEach(r => {
          bMap[`${r.account_code}-${r.budget_month}`] = { amount: r.amount, currency: r.currency, amount_usd: r.amount_usd }
        })
      }
      setAncillaryBudgets(bMap)

      const aMap = {}
      if (ledgerRows) {
        ledgerRows.forEach(r => {
          const m = parseInt(r.entry_date.split('-')[1], 10)
          const k = `${r.accounts.code}-${m}`
          const amt = (Number(r.credit_usd) || 0) - (Number(r.debit_usd) || 0) // Revenue is credit
          aMap[k] = (aMap[k] || 0) + amt
        })
      }
      setAncillaryActuals(aMap)
    }
    loadAncillary()
  }, [activeCompany, ancillaryYear, ancillaryAccounts])

  const ancillaryMonthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    for (let m = 1; m <= 12; m++) {
      let mBudget = 0
      let mActual = 0
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        if (ancillaryBudgets[k]) mBudget += Number(ancillaryBudgets[k].amount_usd) || 0
        if (ancillaryActuals[k]) mActual += Number(ancillaryActuals[k]) || 0
      }
      totalBudget += mBudget
      totalActual += mActual
      summary.push({ month: m, name: MONTH_NAMES[m - 1], budget: mBudget, actual: mActual, variance: mActual - mBudget })
    }
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget }
  }, [ancillaryBudgets, ancillaryActuals, ancillaryAccounts])

  const grandTotalRevenueBudget = useMemo(() => {
    // Sum Room Revenue for the selected ancillaryYear
    let roomRev = 0
    for (let m = 1; m <= 12; m++) {
      const row = rows[`${ancillaryYear}-${m}`]
      if (row) {
        const days = new Date(ancillaryYear, m, 0).getDate()
        roomRev += (Number(row.revenue_usd) || 0) * days
      }
    }
    return roomRev + ancillaryMonthlySummary.totalBudget
  }, [rows, ancillaryYear, ancillaryMonthlySummary.totalBudget])

  const grandTotalRevenueActual = useMemo(() => {
    let roomRevActual = 0
    for (let m = 1; m <= 12; m++) {
      roomRevActual += actuals[`${ancillaryYear}-${m}`] || 0
    }
    return roomRevActual + ancillaryMonthlySummary.totalActual
  }, [actuals, ancillaryYear, ancillaryMonthlySummary.totalActual])

  async function handleAncillarySaveRow(accountCode) {
    if (!activeCompany) return
    const key = `${accountCode}-${ancillaryMonth}`
    const row = ancillaryBudgets[key] || { amount: 0, currency: displayCurrency }
    if (!row.amount) return

    setAncillarySaving(s => ({ ...s, [accountCode]: true }))
    
    const currency = row.currency || displayCurrency
    const fxRate = currency === 'USD' ? 1 : (rates[currency] || rate)
    const amountUsd = currency === 'USD' ? row.amount : (row.amount / fxRate)
    
    const { error } = await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      budget_year: ancillaryYear,
      budget_month: ancillaryMonth,
      account_code: accountCode,
      amount: row.amount,
      currency: currency,
      amount_usd: amountUsd
    }, { onConflict: 'company_id, budget_year, budget_month, account_code' })
    
    if (error) alert('Error saving budget: ' + error.message)
    setAncillarySaving(s => ({ ...s, [accountCode]: false }))
  }

  function handleAncillaryRowChange(accountCode, field, val) {
    const key = `${accountCode}-${ancillaryMonth}`
    const cur = ancillaryBudgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
    const updated = { ...cur, [field]: val }
    if (field === 'currency') updated.currency = val
    const c = updated.currency || displayCurrency
    const r = c === 'USD' ? 1 : (rates[c] || rate)
    if (r) {
      updated.amount_usd = c === 'USD' ? updated.amount : (updated.amount / r)
    }
    setAncillaryBudgets(b => ({ ...b, [key]: updated }))
  }

  function clearAncillaryRow(accountCode) {
    const key = `${accountCode}-${ancillaryMonth}`
    if (!ancillaryBudgets[key]) return
    const updated = { ...ancillaryBudgets[key], amount: 0, amount_usd: 0 }
    setAncillaryBudgets(b => ({ ...b, [key]: updated }))
  }
"""
    content = content.replace("const [actuals, setActuals] = useState({}) // key: \"year-month\" -> revenue_usd actual", "const [actuals, setActuals] = useState({}) // key: \"year-month\" -> revenue_usd actual\n" + state_injection)

    # 3. Add the Summary Cards
    cards_injection = """
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${ancillaryYear} Total Revenue Budget`} value={fmt(grandTotalRevenueBudget)} icon={TrendingUp} tone="gold" sublabel="Room Revenue + Ancillary Revenue" />
        <KpiCard label={`${ancillaryYear} Total Revenue Actual`} value={fmt(grandTotalRevenueActual)} icon={TrendingUp} tone="green" sublabel="Room Revenue + Ancillary Revenue" />
        <KpiCard label={`${ancillaryYear} Total Revenue Variance`} value={fmt(grandTotalRevenueActual - grandTotalRevenueBudget)} icon={AlertTriangle} tone={(grandTotalRevenueActual - grandTotalRevenueBudget) < 0 ? "red" : "green"} />
      </div>
"""
    content = content.replace("<div className=\"flex items-center gap-2 mb-4\">", cards_injection + "\n      <div className=\"flex items-center gap-2 mb-4\">")

    # 4. Append Ancillary UI at the bottom
    bottom_ui = """
      <div className="mt-12 pt-8 border-t border-slate-200">
        <h2 className="text-2xl font-bold text-slate-800 font-[var(--font-display)] mb-6">Ancillary Revenue Budget</h2>

        <div className="flex items-center gap-3 mb-6 bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-sm font-medium text-slate-600">Select Year:</span>
          <select value={ancillaryYear} onChange={e => setAncillaryYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
            {Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
          </select>
          <span className="text-xs text-slate-400">View and manage ancillary revenue</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{ancillaryYear} Annual Ancillary Summary</div>
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
                {ancillaryMonthlySummary.months.map(m => (
                  <tr key={m.month} className="border-b border-slate-50 hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-medium text-slate-700 w-32">{m.name}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.budget)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.actual)}</td>
                    <td className={`py-2 px-3 font-medium ${m.variance < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{fmt(m.variance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex items-center gap-3 mb-4 bg-slate-50 p-3 rounded-xl border border-slate-200">
          <span className="text-sm font-medium text-slate-600">Select Month:</span>
          <select value={ancillaryMonth} onChange={e => setAncillaryMonth(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
            {MONTH_NAMES.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
          </select>
          <span className="text-xs text-slate-400">Manage budget for ancillary revenue accounts</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{MONTH_NAMES[ancillaryMonth - 1]} {ancillaryYear}</div>
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
                {(() => {
                  const subtypes = [...new Set(ancillaryAccounts.map(a => a.subtype))]
                  return subtypes.map(subtype => (
                    <React.Fragment key={subtype}>
                      <tr className="bg-slate-100/80">
                        <td colSpan={8} className="py-2 px-4 font-bold text-slate-800 text-xs tracking-wider uppercase">{subtype}</td>
                      </tr>
                      {ancillaryAccounts.filter(a => a.subtype === subtype).map(a => {
                        const key = `${a.code}-${ancillaryMonth}`
                        const row = ancillaryBudgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
                        const monthlyUsd = Number(row.amount_usd) || 0
                        const actualUsd = ancillaryActuals[key] || 0
                        const cur = row.currency || displayCurrency
                        const r = cur === 'USD' ? 1 : (rates[cur] || rate)
                        const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * r)
                        const monthlyLocal = cur === 'USD' ? monthlyUsd : (monthlyUsd * r)
                        const varUsd = actualUsd - monthlyUsd
                        const varLocal = actualLocal - monthlyLocal
                        const isSaving = ancillarySaving[a.code]

                        return (
                          <tr key={a.code} className="border-b border-slate-50 hover:bg-slate-50/50">
                            <td className="py-2 px-4 font-medium text-slate-700 pl-6 w-64">{a.code} - {a.name}</td>
                            <td className="py-2 px-3">
                              <div className="flex items-center gap-1 min-w-[180px]">
                                <select value={row.currency || displayCurrency} onChange={e => handleAncillaryRowChange(a.code, 'currency', e.target.value)}
                                  className="border border-slate-300 rounded-lg px-2 py-1.5 text-[10px] bg-white" disabled={!can(['owner','admin','accountant'])}>
                                  {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                                </select>
                                <input type="number" value={row.amount || ''} onChange={e => handleAncillaryRowChange(a.code, 'amount', e.target.value)}
                                  placeholder="Amount" className="w-24 border border-slate-300 rounded-lg px-2 py-1.5 text-xs" disabled={!can(['owner','admin','accountant'])} />
                              </div>
                            </td>
                            <td className="py-2 px-3 text-slate-500 min-w-[120px]">{formatMoney(monthlyUsd, 'USD')}</td>
                            <td className="py-2 px-3 text-slate-500 min-w-[120px]">{formatMoney(actualLocal, cur)}</td>
                            <td className="py-2 px-3 text-slate-500 min-w-[120px]">{formatMoney(actualUsd, 'USD')}</td>
                            <td className={`py-2 px-3 font-medium min-w-[120px] ${varLocal < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{formatMoney(Math.abs(varLocal), cur)}</td>
                            <td className={`py-2 px-3 font-medium min-w-[120px] ${varUsd < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{formatMoney(Math.abs(varUsd), 'USD')}</td>
                            <td className="py-2 px-3 text-right">
                              {can(['owner','admin','accountant']) && (
                                <div className="flex items-center justify-end gap-2">
                                  <button onClick={() => handleAncillarySaveRow(a.code)} disabled={isSaving} className="text-navy-600 hover:text-navy-800 text-xs font-semibold">{isSaving ? 'Saving...' : 'Save'}</button>
                                  <button onClick={() => { clearAncillaryRow(a.code); setTimeout(()=> handleAncillarySaveRow(a.code), 100) }} className="text-rose-500 hover:text-rose-700 text-xs font-semibold">Clear</button>
                                </div>
                              )}
                            </td>
                          </tr>
                        )
                      })}
                    </React.Fragment>
                  ))
                })()}
                {ancillaryAccounts.length === 0 && (
                  <tr>
                    <td colSpan={8} className="py-6 text-center text-slate-500 text-sm italic">No ancillary revenue accounts found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
"""
    content = content.replace("{reportModalOpen && (", bottom_ui + "\n      {reportModalOpen && (")
    content = content.replace("import { useEffect, useState } from 'react'", "import React, { useEffect, useState } from 'react'")

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
