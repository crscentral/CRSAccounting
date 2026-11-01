import React, { useEffect, useState, useMemo } from 'react'
import { Save, TrendingUp, AlertTriangle } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney, formatMoneyRounded, formatReportMoney, formatReportMoneyRounded } from '../lib/fx'
import { CURRENCY_LIST, CURRENCIES } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import CurrencySwitcher from '../components/CurrencySwitcher'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

function daysInMonth(year, month) { return new Date(year, month, 0).getDate() }

export default function HotelBudget() {
  const { activeCompany, activeProduct, can } = useAuth()
  const [totalRooms, setTotalRooms] = useState(0)
  const [savingRooms, setSavingRooms] = useState(false)
  const [saving, setSaving] = useState({})
  const [startYear, setStartYear] = useState(new Date().getFullYear())
  const [startMonth, setStartMonth] = useState('all')
  const [rows, setRows] = useState({}) // key: "year-month" -> { occ, adr, revenue, currency }
  const [actuals, setActuals] = useState({}) // key: "year-month" -> revenue_usd actual
  const [displayCurrency, setDisplayCurrency] = useState(activeCompany?.default_currency || activeCompany?.base_currency || 'USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})

  useEffect(() => {
    const nextCurr = activeCompany?.default_currency || activeCompany?.base_currency || 'USD'
    setDisplayCurrency(nextCurr)
  }, [activeCompany?.id, activeCompany?.default_currency, activeCompany?.base_currency])


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
            let query = supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').order('subtype', { ascending: true }).order('code', { ascending: true })
      if (activeProduct === 'hotel') query = query.neq('code', '4010')
      const { data } = await query
      setAncillaryAccounts(data || [])
    }
    fetchAncillaryAccounts()
  }, [activeCompany])

  // Fetch Ancillary Data
  useEffect(() => {
    async function loadAncillary() {
      if (!activeCompany || ancillaryAccounts.length === 0) return

      const [{ data: budgetRows }, { data: ledgerRows }, { data: restRev }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
        supabase.from('hotel_revenue_entries').select('amount_usd, entry_date, account:accounts(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`),
        supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`)
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
          if (r.account?.code === '4010') return; // Skip main room revenue
          const m = parseInt(r.entry_date.split('-')[1], 10)
          const k = `${r.account?.code}-${m}`
          const amt = Number(r.amount_usd) || 0
          aMap[k] = (aMap[k] || 0) + amt
        })
      }
      
      // Dynamically Inject Restaurant Table Revenue based on activeProduct and Meal Period
      if (restRev) {
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          
          const foodKey = r.meal_period === 'Breakfast' ? `4016-${m}` : `4011-${m}`
          const bevKey = `4020-${m}`
          const otherKey = `4021-${m}`
          
          aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
          aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
          aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
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
        if (a.subtype === 'Front Office' || (activeProduct === 'restaurant' && (a.name === 'Room Revenue' || a.subtype === 'F&B Revenue' || a.subtype === 'Sales'))) frontOffice += amt
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
      product: activeProduct,
      budget_year: startYear,
      budget_month: ancillaryMonth,
      account_code: accountCode,
      amount: row.amount,
      currency: currency,
      amount_usd: amountUsd
    }, { onConflict: 'company_id, product, budget_year, budget_month, account_code' })
    
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
    const [{ data: settings }, { data: budgetRows }, { data: statRows }, { data: restRevRows }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear}-12-31`) : Promise.resolve({ data: [] }),
      activeProduct === 'restaurant' ? supabase.from('restaurant_daily_revenue').select('revenue_date, food_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`) : Promise.resolve({ data: [] })
    ])
    setTotalRooms(settings?.total_rooms || 0)
    const rowMap = {}
    ;(budgetRows || []).forEach(b => { rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency, revenue_usd: b.budgeted_room_revenue_usd } })
    setRows(rowMap)
    const actualMap = {}
    if (activeProduct === 'hotel') {
      ;(statRows || []).forEach(s => {
        const [y, m] = s.stat_date.split('-')
        const key = `${y}-${Number(m)}`
        actualMap[key] = (actualMap[key] || 0) + Number(s.room_revenue_usd)
      })
    } else {
      ;(restRevRows || []).forEach(s => {
        const [y, m] = s.revenue_date.split('-')
        const key = `${y}-${Number(m)}`
        actualMap[key] = (actualMap[key] || 0) + (Number(s.food_amount_usd) || 0)
      })
    }
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
    const targetCurrency = selections.currency || displayCurrency || 'USD'
    const rrate = targetCurrency === 'USD' ? 1 : ((await getLatestRate(targetCurrency)) || 1)
    const f = (usd) => formatReportMoney(usd, targetCurrency, rrate)
    const fRound = (usd) => formatReportMoneyRounded(usd, targetCurrency, rrate)
    const conv = (usd) => Math.round((Number(usd) || 0) * rrate * 100) / 100

    const pYear = selections.reportYear || String(startYear)
    const pMonth = selections.reportMonth || 'all'
    const isHotel = activeProduct === 'hotel'
    const yearFilter = pYear !== 'all' ? Number(pYear) : null

    const roomRevSectionName = isHotel ? 'Room Revenue Budget vs Actuals' : 'Revenue Budget vs Actuals'
    const otherRevSectionName = isHotel ? 'Other Revenue vs Actuals' : 'F&B Revenue & Actuals'
    const defaultSections = [
      'Budget Performance Summary (KPIs)',
      roomRevSectionName,
      otherRevSectionName,
      'Revenue Account Breakdown',
      'Budget vs Actual Comparison (Chart)'
    ]
    const userSections = selections.sections || defaultSections

    // 1. Fetch all relevant data directly from Supabase for complete reliability
    let budgetQuery = supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    if (yearFilter) budgetQuery = budgetQuery.eq('budget_year', yearFilter)

    let roomStatsQuery = isHotel
      ? supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd, occupied_rooms, rooms_available').eq('company_id', activeCompany.id).eq('product', activeProduct)
      : Promise.resolve({ data: [] })
    if (yearFilter && isHotel) {
      roomStatsQuery = roomStatsQuery.gte('stat_date', `${yearFilter}-01-01`).lte('stat_date', `${yearFilter}-12-31`)
    }

    let restRevQuery = supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id)
    if (yearFilter) {
      restRevQuery = restRevQuery.gte('revenue_date', `${yearFilter}-01-01`).lte('revenue_date', `${yearFilter}-12-31`)
    }

    let ancBudgetQuery = supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    if (yearFilter) ancBudgetQuery = ancBudgetQuery.eq('budget_year', yearFilter)

    let ancLedgerQuery = supabase.from('hotel_revenue_entries').select('amount_usd, entry_date, account:accounts(code, type, subtype, name)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    if (yearFilter) ancLedgerQuery = ancLedgerQuery.gte('entry_date', `${yearFilter}-01-01`).lte('entry_date', `${yearFilter}-12-31`)

    let accountsQuery = supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').order('subtype', { ascending: true }).order('code', { ascending: true })
    if (isHotel) accountsQuery = accountsQuery.neq('code', '4010')

    const [
      { data: settingsData },
      { data: repBudgetRows },
      { data: repStatRows },
      { data: repRestRevRows },
      { data: repAncBudgetRows },
      { data: repAncLedgerRows },
      { data: repAccounts }
    ] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      budgetQuery,
      roomStatsQuery,
      restRevQuery,
      ancBudgetQuery,
      ancLedgerQuery,
      accountsQuery
    ])

    const repTotalRooms = settingsData?.total_rooms || totalRooms || 0

    // Map room revenue budget: key `${budget_year}-${budget_month}`
    const repBudgetMap = {}
    ;(repBudgetRows || []).forEach(b => {
      repBudgetMap[`${b.budget_year}-${b.budget_month}`] = {
        occ: Number(b.budgeted_occupancy_pct) || 0,
        adr: Number(b.budgeted_adr) || 0,
        revenue: Number(b.budgeted_room_revenue) || 0,
        currency: b.currency,
        revenue_usd: Number(b.budgeted_room_revenue_usd) || 0
      }
    })

    // Map room revenue actuals: key `${year}-${month}`
    const repActualMap = {}
    if (isHotel) {
      ;(repStatRows || []).forEach(s => {
        if (!s.stat_date) return
        const [y, m] = s.stat_date.split('-')
        const key = `${y}-${Number(m)}`
        repActualMap[key] = (repActualMap[key] || 0) + (Number(s.room_revenue_usd) || 0)
      })
    } else {
      ;(repRestRevRows || []).forEach(s => {
        if (!s.revenue_date) return
        const [y, m] = s.revenue_date.split('-')
        const key = `${y}-${Number(m)}`
        repActualMap[key] = (repActualMap[key] || 0) + (Number(s.food_amount_usd) || 0)
      })
    }

    // Map ancillary budgets: key `${account_code}-${budget_year}-${budget_month}`
    const repAncBudgetMap = {}
    ;(repAncBudgetRows || []).forEach(r => {
      repAncBudgetMap[`${r.account_code}-${r.budget_year}-${r.budget_month}`] = {
        amount: Number(r.amount) || 0,
        currency: r.currency,
        amount_usd: Number(r.amount_usd) || 0
      }
    })

    // Map ancillary actuals: key `${account_code}-${year}-${month}`
    const repAncActualMap = {}
    ;(repAncLedgerRows || []).forEach(r => {
      if (!r.entry_date || !r.account?.code || r.account.code === '4010') return
      const [y, m] = r.entry_date.split('-')
      const k = `${r.account.code}-${y}-${Number(m)}`
      repAncActualMap[k] = (repAncActualMap[k] || 0) + (Number(r.amount_usd) || 0)
    })
    ;(repRestRevRows || []).forEach(r => {
      if (!r.revenue_date) return
      const [y, m] = r.revenue_date.split('-')
      const mNum = Number(m)
      const foodKey = r.meal_period === 'Breakfast' ? `4016-${y}-${mNum}` : `4011-${y}-${mNum}`
      const bevKey = `4020-${y}-${mNum}`
      const otherKey = `4021-${y}-${mNum}`
      repAncActualMap[foodKey] = (repAncActualMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
      repAncActualMap[bevKey] = (repAncActualMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
      repAncActualMap[otherKey] = (repAncActualMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
    })

    const allRevenueAccounts = repAccounts || []

    // Determine target years
    const distinctYears = pYear === 'all'
      ? Array.from(new Set([
          startYear,
          ...(repBudgetRows || []).map(b => Number(b.budget_year)),
          ...(repAncBudgetRows || []).map(b => Number(b.budget_year))
        ])).filter(Boolean).sort((a, b) => a - b)
      : [Number(pYear)]

    const sections = []

    // Build report content for each year (or the selected year)
    for (const yr of distinctYears) {
      const now = new Date()
      const repActiveM = pMonth !== 'all' ? Number(pMonth) : (now.getFullYear() === yr ? now.getMonth() + 1 : 12)
      const isCurrMonth = yr === now.getFullYear() && repActiveM === now.getMonth() + 1
      const daysInActiveM = daysInMonth(yr, repActiveM)
      const daysElapsed = isCurrMonth ? now.getDate() : daysInActiveM

      // 1. KPI Calculation for yr
      let activeMonthBudgetUsd = 0
      let activeMonthActualUsd = 0
      if (isHotel) {
        const rowThisM = repBudgetMap[`${yr}-${repActiveM}`]
        activeMonthBudgetUsd = (Number(rowThisM?.revenue_usd) || 0) * daysInActiveM
        activeMonthActualUsd = repActualMap[`${yr}-${repActiveM}`] || 0
      } else {
        for (const a of allRevenueAccounts) {
          activeMonthBudgetUsd += Number(repAncBudgetMap[`${a.code}-${yr}-${repActiveM}`]?.amount_usd || 0)
          activeMonthActualUsd += Number(repAncActualMap[`${a.code}-${yr}-${repActiveM}`] || 0)
        }
      }

      const dailyExpectedUsd = activeMonthBudgetUsd / daysInActiveM
      const paceExpected = dailyExpectedUsd * daysElapsed
      const mtdPaceVariance = activeMonthActualUsd - paceExpected

      // Full-year summaries for yr
      let ytdRoomBudgetUsd = 0
      let ytdRoomActualUsd = 0
      for (let m = 1; m <= 12; m++) {
        const b = repBudgetMap[`${yr}-${m}`]
        if (b) ytdRoomBudgetUsd += (Number(b.revenue_usd) || 0) * daysInMonth(yr, m)
        ytdRoomActualUsd += repActualMap[`${yr}-${m}`] || 0
      }

      let ytdFrontOfficeBudgetUsd = ytdRoomBudgetUsd
      let ytdFbServiceBudgetUsd = 0
      let ytdOtherRevBudgetUsd = 0
      let ytdAncillaryActualUsd = 0

      for (let m = 1; m <= 12; m++) {
        for (const a of allRevenueAccounts) {
          const bAmt = Number(repAncBudgetMap[`${a.code}-${yr}-${m}`]?.amount_usd || 0)
          const aAmt = Number(repAncActualMap[`${a.code}-${yr}-${m}`] || 0)
          ytdAncillaryActualUsd += aAmt

          if (a.subtype === 'Front Office' || (!isHotel && (a.name === 'Room Revenue' || a.subtype === 'F&B Revenue' || a.subtype === 'Sales'))) {
            ytdFrontOfficeBudgetUsd += bAmt
          } else if (a.subtype === 'F&B Service') {
            ytdFbServiceBudgetUsd += bAmt
          } else {
            ytdOtherRevBudgetUsd += bAmt
          }
        }
      }

      const ytdTotalBudgetUsd = ytdFrontOfficeBudgetUsd + ytdFbServiceBudgetUsd + ytdOtherRevBudgetUsd
      const ytdTotalActualUsd = ytdRoomActualUsd + ytdAncillaryActualUsd
      const ytdTotalVarianceUsd = ytdTotalActualUsd - ytdTotalBudgetUsd

      // Determine months to include
      const monthsToProcess = pMonth !== 'all' ? [Number(pMonth)] : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

      // Section 1: KPI Summary
      if (userSections.includes('Budget Performance Summary (KPIs)')) {
        sections.push({
          heading: distinctYears.length > 1 ? `${yr} - Budget Performance Summary` : 'Budget Performance Summary (KPIs)',
          keyValuePairs: [
            [`${MONTH_NAMES[repActiveM - 1]} Budget`, f(activeMonthBudgetUsd)],
            [`${MONTH_NAMES[repActiveM - 1]} ${isCurrMonth ? 'MTD ' : ''}Actual`, f(activeMonthActualUsd)],
            [`${MONTH_NAMES[repActiveM - 1]} Pace Variance`, `${mtdPaceVariance >= 0 ? '+' : ''}${f(mtdPaceVariance)} (${isCurrMonth ? 'Actual vs pace expected' : 'Actual vs full month budget'})`],
            ['YTD Actual Revenue', f(ytdTotalActualUsd)],
            ['YTD Total Budget', f(ytdTotalBudgetUsd)],
            ['YTD Variance', `${ytdTotalVarianceUsd >= 0 ? '+' : ''}${f(ytdTotalVarianceUsd)}`],
            [isHotel ? 'YTD FO Revenue Budget' : 'YTD Food Sales Budget', f(ytdFrontOfficeBudgetUsd)],
            [isHotel ? 'YTD F&B Service Budget' : 'YTD Beverage Sales Budget', f(ytdFbServiceBudgetUsd)],
            ['YTD Other Revenue Budget', f(ytdOtherRevBudgetUsd)],
          ]
        })
      }

      // Section 2: Room Revenue Budget with ADR & Occ% vs Actual Table
      if (userSections.includes(roomRevSectionName) && isHotel) {
        const curLabel = targetCurrency === 'USD' ? 'USD' : `${targetCurrency} (USD)`
        const tableCols = ['Month', 'Occ %', `ADR (${curLabel})`, 'Rooms Occ.', `Daily Budget (${curLabel})`, `Monthly Budget (${curLabel})`, `Actual (${curLabel})`, `Variance (${curLabel})`]
        const tableRows = []

        let totMonthlyBudget = 0
        let totActual = 0
        let totRoomsOcc = 0
        let sumOcc = 0
        let countOcc = 0

        monthsToProcess.forEach(m => {
          const mName = MONTH_NAMES[m - 1]
          const bRow = repBudgetMap[`${yr}-${m}`]
          const occ = Number(bRow?.occ) || 0
          const adrUsd = Number(bRow?.adr) || 0
          const roomsOcc = repTotalRooms > 0 ? Math.round((occ / 100) * repTotalRooms) : 0
          const dailyBudgetUsd = Number(bRow?.revenue_usd) || 0
          const days = daysInMonth(yr, m)
          const monthlyBudgetUsd = dailyBudgetUsd * days
          const actualUsd = repActualMap[`${yr}-${m}`] || 0
          const varianceUsd = actualUsd - monthlyBudgetUsd

          totMonthlyBudget += monthlyBudgetUsd
          totActual += actualUsd
          totRoomsOcc += roomsOcc
          if (occ > 0) {
            sumOcc += occ
            countOcc++
          }

          tableRows.push([
            `${mName} ${yr}`,
            occ > 0 ? `${occ}%` : '0%',
            f(adrUsd),
            String(roomsOcc),
            f(dailyBudgetUsd),
            f(monthlyBudgetUsd),
            f(actualUsd),
            `${varianceUsd >= 0 ? '+' : ''}${f(varianceUsd)}`
          ])
        })

        if (monthsToProcess.length > 1) {
          const totVariance = totActual - totMonthlyBudget
          const avgOcc = countOcc > 0 ? (sumOcc / countOcc).toFixed(1) + '%' : '0%'
          const avgDaily = totMonthlyBudget / (monthsToProcess.reduce((acc, m) => acc + daysInMonth(yr, m), 0) || 1)
          const avgAdr = totRoomsOcc > 0 ? (totMonthlyBudget / totRoomsOcc) : 0

          tableRows.push([
            'Full Year Total / Avg',
            avgOcc,
            f(avgAdr),
            String(totRoomsOcc),
            f(avgDaily),
            f(totMonthlyBudget),
            f(totActual),
            `${totVariance >= 0 ? '+' : ''}${f(totVariance)}`
          ])
        }

        sections.push({
          heading: distinctYears.length > 1 ? `${yr} - Room Revenue with ADR & Occ% vs Actual` : 'Room Revenue with ADR & Occ% vs Actual',
          columns: tableCols,
          columnStyles: {
            0: { cellWidth: 32 },
            1: { cellWidth: 20, halign: 'right' },
            2: { cellWidth: 34, halign: 'right' },
            3: { cellWidth: 24, halign: 'right' },
            4: { cellWidth: 38, halign: 'right' },
            5: { cellWidth: 42, halign: 'right' },
            6: { cellWidth: 42, halign: 'right' },
            7: { cellWidth: 42, halign: 'right' },
          },
          rows: tableRows
        })
      }

      // Section 3: Other Revenue / Ancillary vs Actuals Table
      if (userSections.includes(otherRevSectionName)) {
        const curLabel = targetCurrency === 'USD' ? 'USD' : `${targetCurrency} (USD)`
        const headingName = isHotel ? `${yr} - Other Revenue vs Actuals` : `${yr} - F&B Revenue & Actuals`
        const tableCols = ['Month', `Monthly Budget (${curLabel})`, `Actual Revenue (${curLabel})`, `Variance (${curLabel})`]
        const tableRows = []

        let totAncBudget = 0
        let totAncActual = 0

        monthsToProcess.forEach(m => {
          const mName = MONTH_NAMES[m - 1]
          let mBudget = 0
          let mActual = 0
          for (const a of allRevenueAccounts) {
            mBudget += Number(repAncBudgetMap[`${a.code}-${yr}-${m}`]?.amount_usd || 0)
            mActual += Number(repAncActualMap[`${a.code}-${yr}-${m}`] || 0)
          }
          const mVar = mActual - mBudget
          totAncBudget += mBudget
          totAncActual += mActual

          tableRows.push([
            `${mName} ${yr}`,
            f(mBudget),
            f(mActual),
            `${mVar >= 0 ? '+' : ''}${f(mVar)}`
          ])
        })

        if (monthsToProcess.length > 1) {
          const totVar = totAncActual - totAncBudget
          tableRows.push([
            'Full Year Total',
            f(totAncBudget),
            f(totAncActual),
            `${totVar >= 0 ? '+' : ''}${f(totVar)}`
          ])
        }

        sections.push({
          heading: distinctYears.length > 1 ? headingName : (isHotel ? 'Other Revenue vs Actuals' : 'F&B Revenue & Actuals'),
          columns: tableCols,
          columnStyles: {
            0: { cellWidth: 45 },
            1: { cellWidth: 70, halign: 'right' },
            2: { cellWidth: 70, halign: 'right' },
            3: { cellWidth: 70, halign: 'right' },
          },
          rows: tableRows
        })
      }

      // Section 4: Revenue Account Breakdown (Detail)
      if (userSections.includes('Revenue Account Breakdown') && allRevenueAccounts.length > 0) {
        const curLabel = targetCurrency === 'USD' ? 'USD' : `${targetCurrency} (USD)`
        const detailCols = ['Account', 'Subtype', `Budget (${curLabel})`, `Actual (${curLabel})`, `Variance (${curLabel})`]
        const detailRows = []

        let totAcctBudget = 0
        let totAcctActual = 0

        allRevenueAccounts.forEach(a => {
          let acctBudget = 0
          let acctActual = 0
          monthsToProcess.forEach(m => {
            acctBudget += Number(repAncBudgetMap[`${a.code}-${yr}-${m}`]?.amount_usd || 0)
            acctActual += Number(repAncActualMap[`${a.code}-${yr}-${m}`] || 0)
          })
          const acctVar = acctActual - acctBudget
          totAcctBudget += acctBudget
          totAcctActual += acctActual

          detailRows.push([
            `${a.code} - ${a.name}`,
            a.subtype || 'Other Revenue',
            f(acctBudget),
            f(acctActual),
            `${acctVar >= 0 ? '+' : ''}${f(acctVar)}`
          ])
        })

        if (allRevenueAccounts.length > 1) {
          const totAcctVar = totAcctActual - totAcctBudget
          detailRows.push([
            'Total Ancillary Revenue',
            'All Subtypes',
            f(totAcctBudget),
            f(totAcctActual),
            `${totAcctVar >= 0 ? '+' : ''}${f(totAcctVar)}`
          ])
        }

        sections.push({
          heading: distinctYears.length > 1 ? `${yr} - Ancillary Revenue Account Breakdown` : 'Ancillary Revenue Account Breakdown',
          columns: detailCols,
          columnStyles: {
            0: { cellWidth: 75 },
            1: { cellWidth: 45 },
            2: { cellWidth: 45, halign: 'right' },
            3: { cellWidth: 45, halign: 'right' },
            4: { cellWidth: 45, halign: 'right' },
          },
          rows: detailRows
        })
      }

      // Section 5: Monthly Chart (Grouped Bar Chart)
      if (userSections.includes('Budget vs Actual Comparison (Chart)') && monthsToProcess.length > 1) {
        const chartCats = monthsToProcess.map(m => MONTH_NAMES[m - 1])
        const roomBudgets = monthsToProcess.map(m => {
          const b = repBudgetMap[`${yr}-${m}`]
          return conv((Number(b?.revenue_usd) || 0) * daysInMonth(yr, m))
        })
        const actualRevs = monthsToProcess.map(m => {
          const roomAct = repActualMap[`${yr}-${m}`] || 0
          let ancAct = 0
          for (const a of allRevenueAccounts) {
            ancAct += Number(repAncActualMap[`${a.code}-${yr}-${m}`] || 0)
          }
          return conv(roomAct + ancAct)
        })
        const totalBudgets = monthsToProcess.map(m => {
          const roomB = (Number(repBudgetMap[`${yr}-${m}`]?.revenue_usd) || 0) * daysInMonth(yr, m)
          let ancB = 0
          for (const a of allRevenueAccounts) {
            ancB += Number(repAncBudgetMap[`${a.code}-${yr}-${m}`]?.amount_usd || 0)
          }
          return conv(roomB + ancB)
        })

        sections.push({
          heading: distinctYears.length > 1 ? `${yr} - Budget vs Actual Revenue by Month` : 'Budget vs Actual Revenue by Month',
          chart: {
            categories: chartCats,
            valueFormatter: v => formatMoney(v, targetCurrency),
            series: [
              { name: isHotel ? 'Room Budget' : 'Food Budget', color: '#f59e0b', values: roomBudgets },
              { name: 'Total Budget', color: '#6366f1', values: totalBudgets },
              { name: 'Actual Revenue', color: '#10b981', values: actualRevs },
            ]
          }
        })
      }
    }

    const title = isHotel ? 'Room Revenue Budget' : 'Revenue Budget'
    const periodLabel = pYear === 'all'
      ? 'All Available Years'
      : `${pYear}${pMonth !== 'all' ? ' ' + MONTH_NAMES[Number(pMonth) - 1] : ' Full Year'}`
    const subtitle = `${activeCompany.name} • ${periodLabel} • ${targetCurrency}`
    const logoUrl = activeCompany.logo_url

    if (format === 'pdf' || format === 'preview') {
      await exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'revenue_budget_report', logoUrl, orientation: 'landscape' })
    }
    if (format === 'excel') {
      exportMultiSectionExcel({ title, sections, filename: 'revenue_budget_report' })
    }
    if (format === 'word') {
      exportMultiSectionWord({ title, subtitle, sections, filename: 'revenue_budget_report', logoUrl })
    }
  }

  if (!activeCompany) return null

  const now = new Date()
  const activeMonth = startMonth === 'all' ? (now.getFullYear() === startYear ? now.getMonth() + 1 : 12) : Number(startMonth)
  const isCurrentMonth = startYear === now.getFullYear() && activeMonth === now.getMonth() + 1
  const thisMonthKey = `${startYear}-${activeMonth}`
  const thisMonthRow = rows[thisMonthKey] || { revenue_usd: 0 }
  
  const daysElapsed = isCurrentMonth ? now.getDate() : daysInMonth(startYear, activeMonth)
  const daysInActiveMonth = daysInMonth(startYear, activeMonth)
  
  let monthlyBudgetUsd = 0
  let mtdActualUsd = 0
  if (activeProduct === 'hotel') {
    monthlyBudgetUsd = (Number(thisMonthRow.revenue_usd) || 0) * daysInActiveMonth
    mtdActualUsd = actuals[thisMonthKey] || 0
  } else {
    for (const a of ancillaryAccounts) {
      monthlyBudgetUsd += Number(ancillaryBudgets[`${a.code}-${activeMonth}`]?.amount_usd || 0)
      mtdActualUsd += Number(ancillaryActuals[`${a.code}-${activeMonth}`] || 0)
    }
  }
  
  const dailyExpectedUsd = monthlyBudgetUsd / daysInActiveMonth
  const paceExpected = dailyExpectedUsd * daysElapsed
  const mtdPaceVariance = mtdActualUsd - paceExpected

  const years = [startYear]

  return (
    <div>
      <PageHeader
        title={activeProduct === "restaurant" ? "Revenue Budget" : "Room Revenue Budget"}
        subtitle={`${activeCompany.name} • ${activeProduct === "restaurant" ? "Manage your Monthly Budgets for Food, Beverage, and Other Revenue." : "Feed any two of Occupancy % / ADR / Room Revenue — the third calculates automatically"}`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <div className="h-[38px] flex items-center gap-1.5 bg-white border border-slate-300 rounded-lg px-3 shadow-sm">
              <span className="text-sm text-slate-500">Period:</span>
              <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="bg-transparent text-sm font-medium text-slate-700 focus:outline-none pr-1 cursor-pointer">
                {Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <span className="text-slate-300">/</span>
              <select value={startMonth} onChange={e => setStartMonth(e.target.value)} className="bg-transparent text-sm font-medium text-slate-700 focus:outline-none pl-1 cursor-pointer">
                <option value="all">Full Year</option>
                {MONTH_NAMES.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>
            <button
              onClick={() => setReportModalOpen(true)}
              className="h-[38px] flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 rounded-lg hover:border-navy-400 hover:bg-slate-50 transition-colors shadow-sm"
            >
              Download Report
            </button>
            <CurrencySwitcher
              value={displayCurrency}
              onChange={setDisplayCurrency}
            />
          </div>
        }
      />

      {activeProduct === 'hotel' && (<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-2">{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}</h3>
        <p className="text-xs text-slate-500 mb-3">{activeProduct === "restaurant" ? "Total seats available" : "Total rooms available"} — used to calculate Occupancy %, RevPAR, and rooms occupied from your budgeted occupancy percentage.</p>
        <div className="flex items-center gap-2">
          <input type="number" min="0" value={totalRooms} onChange={e => setTotalRooms(Number(e.target.value))} className="w-32 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          {can(['owner', 'admin', 'accountant']) && (
            <button onClick={saveRoomInventory} disabled={savingRooms} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg disabled:opacity-60">
              <Save size={14} /> {savingRooms ? 'Saving…' : 'Save'}
            </button>
          )}
        </div>
      </div>)}

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} Budget`} value={fmtRounded(monthlyBudgetUsd)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} ${isCurrentMonth ? 'MTD ' : ''}Actual`} value={fmtRounded(mtdActualUsd)} icon={TrendingUp} tone="green" />
        <KpiCard
          label="Variance"
          value={fmtRounded(Math.abs(mtdPaceVariance))}
          icon={mtdPaceVariance >= 0 ? TrendingUp : AlertTriangle}
          tone={mtdPaceVariance >= 0 ? 'green' : 'red'}
          sublabel={isCurrentMonth ? "Actual vs. where you should be by today" : "Actual vs. Full Month Budget"}
        />
      </div>

      
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="YTD Actual Revenue" value={fmtRounded(grandTotalRevenueActual)} icon={TrendingUp} tone="green" />
        <KpiCard label="YTD Total Budget" value={fmtRounded(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" />
        <KpiCard label="YTD Variance" value={fmtRounded(grandTotalRevenueActual - (revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev))} icon={grandTotalRevenueActual >= (revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev) ? TrendingUp : AlertTriangle} tone={grandTotalRevenueActual >= (revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev) ? 'green' : 'red'} />
        <KpiCard label={activeProduct === "restaurant" ? "YTD Food Sales Budget" : "YTD FO Revenue Budget"} value={fmtRounded(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" />
        <KpiCard label={activeProduct === "restaurant" ? "YTD Beverage Sales Budget" : "YTD F&B Service Budget"} value={fmtRounded(revenueSummary.fbService)} icon={TrendingUp} tone="blue" />
        <KpiCard label="YTD Other Revenue Budget" value={fmtRounded(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" />
      </div>

      {activeProduct === 'hotel' && years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year} - Room Revenue with ADR & Occ% vs Actual</div>
            <table className="w-full text-sm">
            <thead className="bg-navy-800 text-white text-xs text-left">
              <tr>
                <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                <th className="py-2 px-3 font-semibold">Occupancy %</th>
                <th className="py-2 px-3 font-semibold">{activeProduct === "restaurant" ? "Avg Check" : "ADR"}</th>
                <th className="py-2 px-3 font-semibold">{activeProduct === "restaurant" ? "Covers" : "Rooms Occ."}</th>
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
                    <td className="py-1.5 px-3 text-slate-500 text-[11px]">{roomsOcc}</td>
                    <td className="py-1.5 px-3">
                      <div className="flex items-center gap-1">
                        <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-[10px] bg-slate-50">
                          {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                        </select>
                        <input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-24 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" />
                      </div>
                    </td>
                    <td className="py-1.5 px-3 text-slate-500 text-[11px]">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-[11px] font-medium">{formatMoneyRounded(monthlyBudget, row.currency || displayCurrency)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-[11px]">{fmtRounded(monthlyUsd, 'USD')}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-[11px] font-medium">{formatMoneyRounded(actualLocal, row.currency || displayCurrency)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-[11px]">{fmtRounded(actualUsd, 'USD')}</td>
                    <td className={`py-1.5 px-3 text-[11px] font-medium ${varLocal < 0 ? 'text-red-500' : 'text-green-600'}`}>{formatMoney(Math.abs(Math.round(varLocal)), row.currency || displayCurrency).replace('.00', '')}</td>
                    <td className={`py-1.5 px-3 text-[11px] ${varUsd < 0 ? 'text-red-500' : 'text-green-600'}`}>{formatMoney(Math.abs(Math.round(varUsd)), 'USD').replace('.00', '')}</td>
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

      
      <div className={activeProduct === 'hotel' ? "mt-12 pt-8 border-t border-slate-200" : ""}>
        

        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{activeProduct === 'restaurant' ? `${startYear} - F&B Revenue & Actual` : `${startYear} - Other Revenue vs Actuals`}</div>
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
                    <td className="py-2 px-3 text-slate-500 font-medium">{formatMoneyRounded(m.budgetLocal, displayCurrency)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmtRounded(m.budgetUsd, 'USD')}</td>
                    <td className="py-2 px-3 text-slate-500 font-medium">{formatMoneyRounded(m.actualLocal, displayCurrency)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmtRounded(m.actualUsd, 'USD')}</td>
                    <td className={`py-2 px-3 font-medium ${m.varianceLocal < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{formatMoneyRounded(Math.abs(m.varianceLocal), displayCurrency)}</td>
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
                    const order = { 'Room Revenue': 1, 'Front Office': 1, 'Sales': 1, 'F&B Revenue': 1, 'F&B Service': 2 };
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
                            <td className="py-2 px-3 text-slate-500 min-w-[120px]">{fmtRounded(actualUsd, 'USD')}</td>
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
          title={activeProduct === "restaurant" ? "Revenue Budget" : "Room Revenue Budget"}
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
{ 
              type: 'select', 
              key: 'reportYear', 
              label: 'Select Year', 
              default: String(startYear),
              options: [
                { value: 'all', label: 'All Available Years' },
                ...Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: String(y), label: String(y) } })
              ]
            },
            {
              type: 'select',
              key: 'reportMonth',
              label: 'Select Month',
              default: startMonth || 'all',
              options: [
                { value: 'all', label: 'Full Year' },
                ...Array.from({ length: 12 }, (_, i) => { return { value: String(i + 1), label: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i] } })
              ]
            },
            {
              type: 'checkboxGroup',
              key: 'sections',
              label: 'Include Sections',
              options: [
                'Budget Performance Summary (KPIs)',
                activeProduct === 'restaurant' ? 'Revenue Budget vs Actuals' : 'Room Revenue Budget vs Actuals',
                activeProduct === 'restaurant' ? 'F&B Revenue & Actuals' : 'Other Revenue vs Actuals',
                'Revenue Account Breakdown',
                'Budget vs Actual Comparison (Chart)'
              ],
              default: [
                'Budget Performance Summary (KPIs)',
                activeProduct === 'restaurant' ? 'Revenue Budget vs Actuals' : 'Room Revenue Budget vs Actuals',
                activeProduct === 'restaurant' ? 'F&B Revenue & Actuals' : 'Other Revenue vs Actuals',
                'Revenue Account Breakdown',
                'Budget vs Actual Comparison (Chart)'
              ]
            }
          ]}
          onGenerate={generateBudgetReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
