import React, { useEffect, useState, useMemo } from 'react'
import { Save, TrendingUp, AlertTriangle } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST, CURRENCIES } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

function daysInMonth(year, month) { return new Date(year, month, 0).getDate() }

export default function HotelBudget() {
  const { activeCompany, activeProduct, can } = useAuth()
  const [totalRooms, setTotalRooms] = useState(0)
  const [savingRooms, setSavingRooms] = useState(false)
  const [startYear, setStartYear] = useState(new Date().getFullYear())
  const [rows, setRows] = useState({}) // key: "year-month" -> { occ, adr, revenue, currency }
  const [actuals, setActuals] = useState({}) // key: "year-month" -> revenue_usd actual
  const [saving, setSaving] = useState({})
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})


  // --- Ancillary Revenue State ---
    const [ancillaryMonth, setAncillaryMonth] = useState(new Date().getMonth() + 1)
  const [ancillaryAccounts, setAncillaryAccounts] = useState([])
  const [ancillaryBudgets, setAncillaryBudgets] = useState({})
  const [ancillaryActuals, setAncillaryActuals] = useState({})
  const [ancillarySaving, setAncillarySaving] = useState({})

  // Fetch Ancillary Accounts
  useEffect(() => {
    async function fetchAncillaryAccounts() {
      if (!activeCompany) return
      const { data } = await supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', 'hotel').eq('type', 'Revenue').neq('code', '4010').order('subtype', { ascending: true }).order('code', { ascending: true })
      setAncillaryAccounts(data || [])
    }
    fetchAncillaryAccounts()
  }, [activeCompany])

  // Fetch Ancillary Data
  useEffect(() => {
    async function loadAncillary() {
      if (!activeCompany || ancillaryAccounts.length === 0) return

      const [{ data: budgetRows }, { data: ledgerRows }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', startYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')
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
  }, [activeCompany, startYear, ancillaryAccounts])

  const ancillaryMonthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    for (let m = 1; m <= 12; m++) {
      let mBudgetUsd = 0
      let mActualUsd = 0
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        if (ancillaryBudgets[k]) mBudgetUsd += Number(ancillaryBudgets[k].amount_usd) || 0
        if (ancillaryActuals[k]) mActualUsd += Number(ancillaryActuals[k]) || 0
      }
      totalBudget += mBudgetUsd
      totalActual += mActualUsd
      
      const r = displayCurrency === 'USD' ? 1 : (rates[displayCurrency] || rate)
      const mBudgetLocal = displayCurrency === 'USD' ? mBudgetUsd : mBudgetUsd * r
      const mActualLocal = displayCurrency === 'USD' ? mActualUsd : mActualUsd * r
      
      summary.push({ 
        month: m, name: MONTH_NAMES[m - 1], 
        budgetUsd: mBudgetUsd, actualUsd: mActualUsd, varianceUsd: mActualUsd - mBudgetUsd,
        budgetLocal: mBudgetLocal, actualLocal: mActualLocal, varianceLocal: mActualLocal - mBudgetLocal
      })
    }
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget }
  }, [ancillaryBudgets, ancillaryActuals, ancillaryAccounts, displayCurrency, rates, rate])

  const grandTotalRevenueBudget = useMemo(() => {
    // Sum Room Revenue for the selected startYear
    let roomRev = 0
    for (let m = 1; m <= 12; m++) {
      const row = rows[`${startYear}-${m}`]
      if (row) {
        const days = new Date(startYear, m, 0).getDate()
        roomRev += (Number(row.revenue_usd) || 0) * days
      }
    }
    return roomRev + ancillaryMonthlySummary.totalBudget
  }, [rows, startYear, ancillaryMonthlySummary.totalBudget])

  
  const revenueSummary = useMemo(() => {
    let roomRev = 0
    for (let m = 1; m <= 12; m++) {
      const r = rows[`${startYear}-${m}`]
      if (r) {
        roomRev += (Number(r.revenue_usd) || 0) * new Date(startYear, m, 0).getDate()
      }
    }
    
    let frontOffice = roomRev
    let fbService = 0
    let otherRev = 0

    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const amt = ancillaryBudgets[k] ? (Number(ancillaryBudgets[k].amount_usd) || 0) : 0
        if (a.subtype === 'Front Office') frontOffice += amt
        else if (a.subtype === 'F&B Service') fbService += amt
        else otherRev += amt
      }
    }
    return { frontOffice, fbService, otherRev }
  }, [rows, ancillaryBudgets, ancillaryAccounts, startYear])

  const grandTotalRevenueActual = useMemo(() => {
    let roomRevActual = 0
    for (let m = 1; m <= 12; m++) {
      roomRevActual += actuals[`${startYear}-${m}`] || 0
    }
    return roomRevActual + ancillaryMonthlySummary.totalActual
  }, [actuals, startYear, ancillaryMonthlySummary.totalActual])

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
      budget_year: startYear,
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


  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, startYear])

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
  function fmtRoundedAbs(usd) { return formatMoney(Math.abs(Math.round(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }))), displayCurrency).replace('.00', '') }
  function fmtRounded(usd) { return formatMoney(Math.round(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate })), displayCurrency).replace('.00', '') }

  async function loadAll() {
    const [{ data: settings }, { data: budgetRows }, { data: statRows }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
      supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear}-12-31`),
    ])
    setTotalRooms(settings?.total_rooms || 0)
    const rowMap = {}
    ;(budgetRows || []).forEach(b => { rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency, revenue_usd: b.budgeted_room_revenue_usd } })
    setRows(rowMap)
    const actualMap = {}
    ;(statRows || []).forEach(s => {
      const [y, m] = s.stat_date.split('-')
      const key = `${y}-${Number(m)}`
      actualMap[key] = (actualMap[key] || 0) + Number(s.room_revenue_usd)
    })
    setActuals(actualMap)
  }

  async function saveRoomInventory() {
    setSavingRooms(true)
    await supabase.from('hotel_settings').upsert({ company_id: activeCompany.id, product: activeProduct, total_rooms: totalRooms, updated_at: new Date().toISOString() }, { onConflict: 'company_id,product' })
    setSavingRooms(false)
  }

  function updateRow(year, month, field, value) {
    const key = `${year}-${month}`
    setRows(r => {
      const current = r[key] || { occ: 0, adr: 0, revenue: 0, currency: displayCurrency }
      const next = { ...current, [field]: value }
      // Triangulation: whichever field was just typed, recompute one of the OTHER two
      // that makes least sense to also have been manually set. Priority: if occ+adr
      // present, revenue = rooms*occ%*adr*days. If adr+revenue present, occ derives.
      // If occ+revenue present, adr derives.
      const days = daysInMonth(year, month)
      if (field === 'occ' || field === 'adr') {
        if (totalRooms > 0 && Number(next.occ) > 0 && Number(next.adr) > 0) {
          next.revenue = Math.round(totalRooms * (Number(next.occ) / 100) * Number(next.adr) * 100) / 100
        }
      } else if (field === 'revenue') {
        if (totalRooms > 0 && Number(next.occ) > 0) {
          next.adr = Math.round((Number(next.revenue) / (totalRooms * (Number(next.occ) / 100))) * 100) / 100
        } else if (totalRooms > 0 && Number(next.adr) > 0) {
          next.occ = Math.round((Number(next.revenue) / Number(next.adr) / totalRooms) * 100 * 100) / 100
        }
      }
      return { ...r, [key]: next }
    })
  }

  async function clearRow(year, month) {
    if (!confirm('Clear budget entry for this month?')) return
    const key = `${year}-${month}`
    setSaving(s => ({ ...s, [key]: true }))
    await supabase.from('hotel_room_revenue_budget').delete().eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', year).eq('budget_month', month)
    setRows(r => { const next = { ...r }; delete next[key]; return next })
    setSaving(s => ({ ...s, [key]: false }))
  }

  async function saveRow(year, month) {
    const key = `${year}-${month}`
    const row = rows[key]
    if (!row) return
    setSaving(s => ({ ...s, [key]: true }))
    const currency = row.currency || displayCurrency
    const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
    const revenueUsd = Math.round((Number(row.revenue) || 0) / fxRate * 100) / 100
    await supabase.from('hotel_room_revenue_budget').upsert({
      company_id: activeCompany.id, product: activeProduct, budget_year: year, budget_month: month,
      budgeted_occupancy_pct: Number(row.occ) || 0, budgeted_adr: Number(row.adr) || 0, budgeted_room_revenue: Number(row.revenue) || 0,
      currency, fx_rate_locked: fxRate, budgeted_room_revenue_usd: revenueUsd,
    }, { onConflict: 'company_id,product,budget_year,budget_month' })
    setRows(r => ({ ...r, [key]: { ...r[key], revenue_usd: revenueUsd } }))
    setSaving(s => ({ ...s, [key]: false }))
  }

  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const sy = Number(selections.startYear || startYear)
    const years = [sy]
    const tableRows = []
    years.forEach(y => MONTH_NAMES.forEach((m, i) => {
      const key = `${y}-${i + 1}`
      const row = rows[key]
      const actualUsd = actuals[key] || 0
      if (row) {
        const days = daysInMonth(y, i + 1)
        const monthlyRevUsd = (row.revenue_usd || 0) * days
        const roomsOcc = Math.round(totalRooms * (Number(row.occ) || 0) / 100)
        const adrUsd = roomsOcc > 0 ? (row.revenue_usd / roomsOcc) : 0
        tableRows.push([
          `${m} ${y}`, 
          `${row.occ}%`, 
          f(adrUsd), 
          f(monthlyRevUsd), 
          f(actualUsd), 
          f(monthlyRevUsd - actualUsd)
        ])
      }
    }))
    const sections = [{ heading: 'Room Revenue Budget', columns: ['Month', 'Budgeted Occ %', 'Budgeted ADR', 'Budgeted Monthly Revenue', 'Actual Revenue', 'Variance'], rows: tableRows }]
    const title = 'Room Revenue Budget'
    const subtitle = `${activeCompany.name} • ${startYear} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'room_revenue_budget' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'room_revenue_budget' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'room_revenue_budget' })
  }

  if (!activeCompany) return null

  const now = new Date()
  const thisMonthKey = `${now.getFullYear()}-${now.getMonth() + 1}`
  const thisMonthRow = rows[thisMonthKey]
  const daysElapsed = now.getDate()
  const daysInCurrentMonth = daysInMonth(now.getFullYear(), now.getMonth() + 1)
  const paceExpected = thisMonthRow ? (Number(thisMonthRow.revenue) || 0) * (daysElapsed / daysInCurrentMonth) : 0
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected

  const years = [startYear]

  return (
    <div>
      <PageHeader
        title="Room Revenue Budget"
        subtitle={`${activeCompany.name} • Feed any two of Occupancy % / ADR / Room Revenue — the third calculates automatically`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
            </select>
          </div>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-2">Room Inventory</h3>
        <p className="text-xs text-slate-500 mb-3">Total rooms available — used to calculate Occupancy %, RevPAR, and rooms occupied from your budgeted occupancy percentage.</p>
        <div className="flex items-center gap-2">
          <input type="number" min="0" value={totalRooms} onChange={e => setTotalRooms(Number(e.target.value))} className="w-32 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          {can(['owner', 'admin', 'accountant']) && (
            <button onClick={saveRoomInventory} disabled={savingRooms} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg disabled:opacity-60">
              <Save size={14} /> {savingRooms ? 'Saving…' : 'Save'}
            </button>
          )}
        </div>
      </div>

      {thisMonthRow && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
          <KpiCard label="This Month Budget" value={fmt(Number(thisMonthRow.revenue) || 0)} icon={TrendingUp} tone="gold" />
          <KpiCard label="MTD Actual" value={fmt(mtdActual)} icon={TrendingUp} tone="green" />
          <KpiCard
            label={`Pace Variance (Day ${daysElapsed}/${daysInCurrentMonth})`}
            value={fmtRoundedAbs(mtdPaceVariance)}
            icon={mtdPaceVariance >= 0 ? TrendingUp : AlertTriangle}
            tone={mtdPaceVariance >= 0 ? 'green' : 'red'}
            sublabel="Actual vs. where you should be by today"
          />
        </div>
      )}

      
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${startYear} Front Office Revenue`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel="Room Revenue + Front Office" />
        <KpiCard label={`${startYear} F&B Service Revenue`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel="F&B Service Accounts" />
        <KpiCard label={`${startYear} Other Revenue`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
      </div>


      <div className="flex items-center gap-2 mb-4">
        <label className="text-sm text-slate-500">Select Year:</label>
        <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm">
          {Array.from({ length: 8 }, (_, i) => now.getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
        <span className="text-xs text-slate-400">Select year for Room & Ancillary Revenue</span>
      </div>

      {years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year} - Room Revenue with ADR & Occ% vs Actual</div>
            <table className="w-full text-sm">
            <thead className="bg-navy-800 text-white text-xs text-left">
              <tr>
                <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                <th className="py-2 px-3 font-semibold">Occupancy %</th>
                <th className="py-2 px-3 font-semibold">ADR</th>
                <th className="py-2 px-3 font-semibold">Rooms Occ.</th>
                <th className="py-2 px-3 font-semibold">Daily Budget</th>
                <th className="py-2 px-3 font-semibold">Daily (USD)</th>
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
                const row = rows[key] || { occ: 0, adr: 0, revenue: 0, currency: displayCurrency, revenue_usd: 0 }
                const days = daysInMonth(year, month)
                
                const roomsOcc = totalRooms > 0 ? Math.round((Number(row.occ) / 100) * totalRooms) : 0
                const dailyRev = Number(row.revenue) || 0
                const dailyUsd = Number(row.revenue_usd) || 0
                
                const monthlyBudget = dailyRev * days
                const monthlyUsd = dailyUsd * days
                
                const actualUsd = actuals[key] || 0
                const cur = row.currency || displayCurrency
                const r = cur === 'USD' ? 1 : (rates[cur] || rate)
                const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * r)
                
                const varUsd = actualUsd - monthlyUsd
                const varLocal = actualLocal - monthlyBudget

                return (
                  <tr key={month} className="border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors">
                    <td className="py-1.5 px-3 font-medium text-slate-700 text-sm">{m}</td>
                    <td className="py-1.5 px-3">
                      <input type="number" min="0" max="100" step="0.01" value={row.occ || ''} onChange={e => updateRow(year, month, 'occ', e.target.value)} className="w-16 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="%" />
                    </td>
                    <td className="py-1.5 px-3">
                      <input type="number" min="0" step="0.01" value={row.adr || ''} onChange={e => updateRow(year, month, 'adr', e.target.value)} className="w-20 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="ADR" />
                    </td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{roomsOcc}</td>
                    <td className="py-1.5 px-3">
                      <div className="flex items-center gap-1">
                        <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-[10px] bg-slate-50">
                          {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                        </select>
                        <input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-24 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" />
                      </div>
                    </td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs font-medium">{formatMoney(Math.round(monthlyBudget), row.currency || displayCurrency).replace('.00', '')}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{formatMoney(Math.round(monthlyUsd), 'USD').replace('.00', '')}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs font-medium">{formatMoney(actualLocal, row.currency || displayCurrency)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{fmt(actualUsd)}</td>
                    <td className={`py-1.5 px-3 text-xs font-medium ${varLocal < 0 ? 'text-red-500' : 'text-green-600'}`}>{formatMoney(Math.abs(Math.round(varLocal)), row.currency || displayCurrency).replace('.00', '')}</td>
                    <td className={`py-1.5 px-3 text-xs ${varUsd < 0 ? 'text-red-500' : 'text-green-600'}`}>{formatMoney(Math.abs(Math.round(varUsd)), 'USD').replace('.00', '')}</td>
                    <td className="py-1.5 px-3">
                      {can(['owner', 'admin', 'accountant']) && (
                        <div className="flex gap-2 justify-end items-center">
                          <button onClick={() => saveRow(year, month)} disabled={saving[key]} className="text-navy-600 hover:text-navy-800 text-xs font-medium disabled:opacity-50">{saving[key] ? 'Saving…' : 'Save'}</button>
                          <button onClick={() => clearRow(year, month)} disabled={saving[key]} className="text-red-500 hover:text-red-700 text-xs font-medium disabled:opacity-50">Clear</button>
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

      
      <div className="mt-12 pt-8 border-t border-slate-200">
        

        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} - Other Revenue vs Actuals</div>
            <table className="w-full text-sm">
              <thead className="bg-navy-800 text-white text-xs text-left">
                <tr>
                  <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                  <th className="py-2 px-3 font-semibold">Monthly Budget</th>
                  <th className="py-2 px-3 font-semibold">Monthly (USD)</th>
                  <th className="py-2 px-3 font-semibold">Actual</th>
                  <th className="py-2 px-3 font-semibold">Actual (USD)</th>
                  <th className="py-2 px-3 font-semibold">Variance</th>
                  <th className="py-2 px-3 font-semibold rounded-tr-lg">Variance (USD)</th>
                </tr>
              </thead>
              <tbody>
                {ancillaryMonthlySummary.months.map(m => (
                  <tr key={m.month} className="border-b border-slate-50 hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-medium text-slate-700 w-32">{m.name}</td>
                    <td className="py-2 px-3 text-slate-500 font-medium">{formatMoney(m.budgetLocal, displayCurrency)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.budgetUsd)}</td>
                    <td className="py-2 px-3 text-slate-500 font-medium">{formatMoney(m.actualLocal, displayCurrency)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.actualUsd)}</td>
                    <td className={`py-2 px-3 font-medium ${m.varianceLocal < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{formatMoney(Math.abs(m.varianceLocal), displayCurrency)}</td>
                    <td className={`py-2 px-3 ${m.varianceUsd < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{fmt(Math.abs(m.varianceUsd))}</td>
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
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{MONTH_NAMES[ancillaryMonth - 1]} {startYear}</div>
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
                  const subtypes = [...new Set(ancillaryAccounts.map(a => a.subtype))].sort((a, b) => {
                    if (a === 'Other Revenue') return 1;
                    if (b === 'Other Revenue') return -1;
                    const order = { 'Room Revenue': 1, 'Front Office': 1, 'F&B Service': 2 };
                    const oa = order[a] || 99;
                    const ob = order[b] || 99;
                    if (oa !== ob) return oa - ob;
                    return a.localeCompare(b);
                  })
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

      {reportModalOpen && (
        <ReportOptionsModal
          title="Room Revenue Budget"
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'startYear', 
              label: 'Select Year', 
              default: startYear,
              options: Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: y, label: String(y) } }) 
            }
          ]}
          onGenerate={generateBudgetReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
