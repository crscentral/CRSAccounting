import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Receipt, AlertCircle, Building2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { getYTDRange, resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

const renderCustomLegend = (props, formatter) => {
  const { payload } = props;
  return (
    <ul className="flex flex-wrap justify-center gap-4 mt-2 text-xs">
      {payload.map((entry, index) => (
        <li key={`item-${index}`} className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-slate-600 font-medium">
            {entry.value}: {formatter(entry.payload.realValue)}
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function Dashboard() {
  const { activeCompany, activeProduct } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [sales, setSales] = useState([])
  const [purchases, setPurchases] = useState([])
  const [receipts, setReceipts] = useState([])
  const [allSales, setAllSales] = useState([])
  const [allPurchases, setAllPurchases] = useState([])
  const [recentTx, setRecentTx] = useState([])
  const [hotelStats, setHotelStats] = useState(null)
  const [ledgerEntries, setLedgerEntries] = useState([])
  const [accounts, setAccounts] = useState([])
  const [hotelRoomStats, setHotelRoomStats] = useState([])
  const [hotelGuestInvoices, setHotelGuestInvoices] = useState([])
  const [hotelExpenseEntries, setHotelExpenseEntries] = useState([])
  const [hotelAmc, setHotelAmc] = useState([])
  const [hotelRevenueEntries, setHotelRevenueEntries] = useState([])

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])
  useEffect(() => { if (activeCompany && activeProduct === 'hotel') loadHotelStats() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadHotelStats() {
    const [{ data: settings }, { data: stats }, { data: invoices }, { data: budgetRows }] = await Promise.all([
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', 'hotel').maybeSingle(),
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('stat_date', cp.range.from).lte('stat_date', cp.range.to).order('stat_date'),
      supabase.from('hotel_guest_invoices').select('invoice_amount_usd, collected_amount_usd').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', 'hotel'),
    ])
    const totalRooms = settings?.total_rooms || 0
    const totalOccupied = (stats || []).reduce((s, r) => s + r.rooms_occupied, 0)
    const totalRevenue = (stats || []).reduce((s, r) => s + Number(r.room_revenue_usd), 0)
    const daysInView = Math.max(1, Math.round((Math.min(new Date(cp.range.to).getTime(), new Date().getTime()) - new Date(cp.range.from).getTime()) / (1000 * 60 * 60 * 24)) + 1)
    const availableRoomNights = totalRooms * daysInView
    const occupancyPct = availableRoomNights > 0 ? (totalOccupied / availableRoomNights) * 100 : 0
    const adr = totalOccupied > 0 ? totalRevenue / totalOccupied : 0
    const revpar = availableRoomNights > 0 ? totalRevenue / availableRoomNights : 0
    const invoicesPending = (invoices || []).reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)

    // Daily Actual vs Budget trend -- budget is now saved as the DAILY budgeted figure directly.
    const budgetByMonth = {}
    ;(budgetRows || []).forEach(b => { budgetByMonth[`${b.budget_year}-${b.budget_month}`] = Number(b.budgeted_room_revenue_usd) })
    
    // Create a complete date range array for the trend chart and budget calculation
    const dailyTrendMap = {}
    let currentDate = new Date(cp.range.from)
    const endDate = new Date(Math.min(new Date(cp.range.to).getTime(), new Date().getTime()))
    let totalBudgetUsd = 0
    
    while (currentDate <= endDate) {
      const d = currentDate.toISOString().slice(0, 10)
      const y = currentDate.getUTCFullYear()
      const m = currentDate.getUTCMonth() + 1
      const dailyBudget = budgetByMonth[`${y}-${m}`] || 0
      dailyTrendMap[d] = { date: d, Actual: 0, Budget: dailyBudget }
      totalBudgetUsd += dailyBudget
      currentDate.setUTCDate(currentDate.getUTCDate() + 1)
    }
    
    // Fill in the actuals
    ;(stats || []).forEach(s => {
      if (dailyTrendMap[s.stat_date]) {
        dailyTrendMap[s.stat_date].Actual = Number(s.room_revenue_usd)
      } else {
        // If it's somehow out of bounds but returned by the query, add it anyway
        const [y, m] = s.stat_date.split('-')
        const dailyBudget = budgetByMonth[`${y}-${Number(m)}`] || 0
        dailyTrendMap[s.stat_date] = { date: s.stat_date, Actual: Number(s.room_revenue_usd), Budget: dailyBudget }
        totalBudgetUsd += dailyBudget
      }
    })
    
    const dailyTrend = Object.values(dailyTrendMap).sort((a, b) => a.date.localeCompare(b.date))
    const totalVarianceUsd = totalRevenue - totalBudgetUsd
    setHotelStats({ occupancyPct, adr, revpar, invoicesPending, totalRevenue, totalBudgetUsd, totalVarianceUsd,
      budgetCurrency: budgetRows?.[0]?.currency || activeCompany?.currency || 'USD', dailyTrend })
  }

  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('accounts').select('id, type, name').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
    ])
    setAccounts(accs || [])
    setLedgerEntries(led || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
    setSales(s || [])
    setPurchases(p || [])
    setReceipts(r || [])
    setAllSales(allS || [])
    setAllPurchases(allP || [])

    // Recent Transactions: latest 5 across sales, purchases, and receipts, all-time (not period-filtered)
    const [{ data: recentS }, { data: recentP }, { data: recentR }] = await Promise.all([
      supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(5),
      supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(5),
      supabase.from('payment_receipts').select('receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).order('receipt_date', { ascending: false }).limit(5),
    ])
    const combined = [
      ...(recentS || []).map(r => ({ date: r.invoice_date, label: r.contact?.name || r.invoice_number, amount: r.amount, currency: r.currency })),
      ...(recentP || []).map(r => ({ date: r.invoice_date, label: r.contact?.name || r.supplier_name_freeform || r.invoice_number, amount: r.amount, currency: r.currency })),
      ...(recentR || []).map(r => ({ date: r.receipt_date, label: 'Payment Received', amount: r.amount, currency: r.currency })),
    ].sort((a, b) => String(b.date || '').localeCompare(String(a.date || ''))).slice(0, 5)
    if (activeProduct === 'hotel') {
      const [{ data: hgi }, { data: hre }, { data: hee }] = await Promise.all([
        supabase.from('hotel_guest_invoices').select('id, invoice_date, invoice_amount_usd, currency, guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(10),
        supabase.from('hotel_revenue_entries').select('entry_date, amount_usd, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('entry_date', { ascending: false }).limit(10),
        supabase.from('hotel_expense_entries').select('expense_date, amount_usd, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('expense_date', { ascending: false }).limit(10),
      ])
      const hCombined = [
        ...(hgi || []).map(r => ({ date: r.invoice_date, label: r.guest_name || 'Guest Invoice', amount: r.invoice_amount_usd, currency: 'USD' })),
        ...(hre || []).map(r => ({ date: r.entry_date, label: r.account?.name || 'Revenue', amount: r.amount_usd, currency: 'USD' })),
        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount_usd, currency: 'USD' })),
      ].sort((a, b) => String(b.date || '').localeCompare(String(a.date || ''))).slice(0, 10)
      setRecentTx(hCombined)
    } else {
      setRecentTx(combined)
    }
  }


  async function generateDashboardReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const conv = (usd) => convertFromUsd(usd, selections.currency, { [selections.currency]: rate })
    const fmt = (usd) => formatMoney(conv(usd), selections.currency)

    const [{ data: s }, { data: p }, { data: r }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []
    const sections = []

    if (selections.sections.includes('Revenue, Expenses & Profit/Loss (Chart)')) {
      const monthlyMap = {}
      sSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0 }; monthlyMap[k].rev += Number(i.amount_usd) })
      pSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0 }; monthlyMap[k].exp += Number(i.amount_usd) })
      const monthly = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))
      sections.push({
        heading: 'Revenue, Expenses & Profit/Loss',
        chart: {
          categories: monthly.map(m => m.month),
          valueFormatter: v => formatMoney(v, selections.currency),
          series: [
            { name: 'Revenue', color: '#10b981', values: monthly.map(m => conv(m.rev)) },
            { name: 'Expenses', color: '#f97316', values: monthly.map(m => conv(m.exp)) },
            { name: 'Profit/Loss', color: '#3b82f6', values: monthly.map(m => conv(m.rev - m.exp)) },
          ],
        },
      })
    }

    if (selections.sections.includes('Billing & Outstanding Overview (Chart)')) {
      const monthlyMap = {}
      sSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0, out: 0 }; monthlyMap[k].rev += Number(i.amount_usd); monthlyMap[k].out += (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)) })
      pSel.forEach(i => { const k = i.invoice_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, rev: 0, exp: 0, out: 0 }; monthlyMap[k].exp += Number(i.amount_usd) })
      const monthly = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))
      sections.push({
        heading: 'Billing & Outstanding Overview',
        chart: {
          categories: monthly.map(m => m.month),
          valueFormatter: v => formatMoney(v, selections.currency),
          series: [
            { name: 'Revenue Billed', color: '#10b981', values: monthly.map(m => conv(m.rev)) },
            { name: 'Outstanding Payment', color: '#f59e0b', values: monthly.map(m => conv(m.out)) },
            { name: 'Expenses Billed', color: '#f97316', values: monthly.map(m => conv(m.exp)) },
            { name: 'Profit Expected', color: '#3b82f6', values: monthly.map(m => conv(m.rev - m.exp)) },
          ],
        },
      })
    }

    if (selections.sections.includes('Company Overview - YTD')) {
      const ytd = getYTDRange(activeCompany.fiscal_year_start_month || 1)
      const [{ data: allS }, { data: allP }] = await Promise.all([
        supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', ytd.from).lte('invoice_date', ytd.to),
        supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', ytd.from).lte('invoice_date', ytd.to),
      ])
      const rev = (allS || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      const exp = (allP || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
      sections.push({ heading: 'Company Overview - YTD', keyValuePairs: [['YTD Revenue', fmt(rev)], ['YTD Expenses', fmt(exp)], ['YTD Net Profit', fmt(rev - exp)]] })
    }

    if (selections.sections.includes('Company Overview - All Time')) {
      const [{ data: allS }, { data: allP }] = await Promise.all([
        supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
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
      ].sort((a, b) => String(b.date || '').localeCompare(String(a.date || ''))).slice(0, 10)
      sections.push({ heading: 'Recent Transactions', columns: ['Date', 'Description', 'Amount'], rows: combined.map(t => [t.date, t.label, t.amount]) })
    }

    if (selections.sections.includes('Outstanding Invoices')) {
      const outstanding = sSel.filter(i => i.status !== 'Paid')
      sections.push({ heading: 'Outstanding Invoices', columns: ['Invoice #', 'Customer', 'Due Date', 'Balance Due', 'Status'], rows: outstanding.map(i => [i.invoice_number, i.contact?.name || '—', i.due_date || '—', fmt(i.amount_usd), i.status]) })
    }

    const title = 'Financial Dashboard'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') await exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'dashboard_report' , logoUrl: activeCompany?.logo_url})
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'dashboard_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'dashboard_report' , logoUrl: activeCompany?.logo_url})
  }

  if (!activeCompany) return null

  // Compute ledger-based revenue and expenses (Universal)
  const balances = {}
  ledgerEntries.forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })
  const sumAccs = (type) => accounts.filter(a => a.type === type).reduce((s, a) => s + (balances[a.id] || 0), 0)
  
  let totalBilled = 0
  let totalExpenses = 0
  let outstanding = 0
  let collected = 0
  let expensesMade = 0

  if (activeProduct === 'hotel') {
    // For Hotel, Revenue and Expense come directly from the ledger
    totalBilled = -sumAccs('Revenue')
    totalExpenses = sumAccs('Expenses')
    
    // Outstanding = Unpaid Guest Invoices
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
    
    // Collected = Guest Invoices Paid + Daily Room Revenue Collected
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected
                
    // Expenses Made = Expense entries + amortized AMC (assuming paid for simplicity)
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    expensesMade = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal
  } else {
    // For Basic, use standard invoices
    totalBilled = sales.reduce((sum, i) => sum + Number(i.amount_usd), 0)
    totalExpenses = purchases.reduce((sum, i) => sum + Number(i.amount_usd), 0)
    outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalBilled - outstanding
    expensesMade = purchases.reduce((sum, i) => sum + (i.status === 'Paid' ? Number(i.amount_usd) : 0), 0)
  }

  const netProfit = totalBilled - totalExpenses
  const actualProfit = collected - expensesMade
  const draftInvoices = activeProduct === 'hotel' 
    ? hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)).map(i => ({
        ...i,
        contact: { name: i.guest_name || 'Guest' },
        balance_due: Number(i.invoice_amount_usd) - Number(i.collected_amount_usd),
        amount: i.invoice_amount_usd,
        amount_usd: i.invoice_amount_usd,
        due_date: i.invoice_date,
        status: 'Pending',
        invoice_number: i.id ? i.id.slice(0, 8).toUpperCase() : '—'
      }))
    : sales.filter(i => i.status !== 'Paid')
  const draftExpenses = activeProduct === 'hotel' ? [] : purchases.filter(i => i.status === 'Draft')

  // YTD (respects company fiscal year start month) — independent of the page's period selector
  const ytdRange = getYTDRange(activeCompany.fiscal_year_start_month || 1)
  let ytdRevenue = 0
  let ytdExpenses = 0
  
  if (activeProduct === 'hotel') {
    ytdRevenue = totalBilled
    ytdExpenses = totalExpenses
  } else {
    const ytdSales = allSales.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
    const ytdPurchases = allPurchases.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
    ytdRevenue = ytdSales.reduce((s, i) => s + Number(i.amount_usd), 0)
    ytdExpenses = ytdPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)
  }

  // All-Time
  let allTimeRevenue = 0
  let allTimeExpenses = 0
  const monthlyMap = {}
  
  if (activeProduct === 'hotel') {
    allTimeRevenue = totalBilled
    allTimeExpenses = totalExpenses
    
    hotelGuestInvoices.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Outstanding += (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd))
      monthlyMap[key].Collected += Number(i.collected_amount_usd)
    })
    hotelRoomStats.forEach(r => {
      const key = r.stat_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.room_revenue_usd)
      monthlyMap[key].Collected += Number(r.manual_room_revenue_collected_usd || 0)
    })
    hotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.amount_usd)
      monthlyMap[key].Collected += Number(r.amount_usd)
    })
    hotelExpenseEntries.forEach(r => {
      const key = r.expense_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(r.amount_usd)
    })
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const amcMonthly = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
    let cur = new Date(start.getFullYear(), start.getMonth(), 1)
    while (cur <= end) {
      const key = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}`
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += amcMonthly
      cur.setMonth(cur.getMonth() + 1)
    }
  } else {
    allTimeRevenue = allSales.reduce((s, i) => s + Number(i.amount_usd), 0)
    allTimeExpenses = allPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)
    
    sales.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(i.amount_usd)
      monthlyMap[key].Outstanding += (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))
    })
    purchases.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(i.amount_usd)
    })
    receipts.forEach(r => {
      const key = r.receipt_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Collected += Number(r.amount_usd)
    })
  }
  const chartData = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))
    .map(m => ({ ...m, Profit: m.Revenue - m.Expenses }))

  const billingChartData = chartData.map(m => ({
    month: m.month,
    'Revenue Billed': m.Revenue,
    'Outstanding Payment': m.Outstanding,
    'Expenses Billed': m.Expenses,
    'Profit Expected': m.Revenue - m.Expenses,
  }))

  const reportColumns = [
    { label: 'Invoice #', key: 'invoice_number' }, { label: 'Customer', key: 'customerName' },
    { label: 'Due Date', key: 'due_date' }, { label: 'Balance Due (USD)', key: 'balanceLabel' }, { label: 'Status', key: 'status' },
  ]
  const reportRows = draftInvoices.map(i => ({ ...i, customerName: i.contact?.name || '—', balanceLabel: cp.fmt((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)) }))

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

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalBilled)} sublabel="sales invoices" icon={TrendingUp} tone="green" />
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} sublabel="purchase invoices" icon={TrendingDown} tone="red" />
        <KpiCard label="Expected Net Profit" value={cp.fmt(netProfit)} sublabel="billed minus expenses" icon={DollarSign} tone={netProfit >= 0 ? 'green' : 'red'} />
        <KpiCard label="Outstanding" value={cp.fmt(outstanding)} sublabel="pending + overdue" icon={AlertCircle} tone="slate" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue Collected" value={cp.fmt(collected)} sublabel="actual paid revenue" icon={Receipt} tone="gold" />
        <KpiCard label="Total Expenses Made" value={cp.fmt(expensesMade)} sublabel="actual paid expenses" icon={TrendingDown} tone="orange" />
        <KpiCard label="Actual Profit" value={cp.fmt(actualProfit)} sublabel="collected minus made" icon={DollarSign} tone={actualProfit >= 0 ? 'green' : 'red'} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <DollarSign size={18} /> Expected Profit Breakdown
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={netProfit >= 0 ? [
                    { name: 'Revenue', value: cp.convert(totalBilled), color: '#10b981' },
                    { name: 'Expenses', value: cp.convert(totalExpenses), color: '#ef4444' },
                    { name: 'Profit', value: cp.convert(netProfit), color: '#3b82f6' }
                  ] : [
                    { name: 'Revenue', value: cp.convert(totalBilled), color: '#10b981' },
                    { name: 'Expenses', value: cp.convert(totalExpenses), color: '#ef4444' },
                    { name: 'Loss', value: cp.convert(Math.abs(netProfit)), color: '#f59e0b' }
                  ]}
                  cx="50%" cy="50%" innerRadius="60%" outerRadius="80%" paddingAngle={2} dataKey="value"
                >
                  {(netProfit >= 0 ? [1,2,3] : [1,2,3]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(netProfit >= 0 ? ['#10b981', '#ef4444', '#3b82f6'] : ['#10b981', '#ef4444', '#f59e0b'])[index]} />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      // Base percentage on Total Revenue to show true margins
                      const totalRev = cp.convert(totalBilled) || 1;
                      const pct = ((data.value / totalRev) * 100).toFixed(1);
                      return (
                        <div className="bg-white border border-slate-200 p-2 shadow-lg rounded text-sm">
                          <p className="font-semibold" style={{ color: data.color }}>{data.name}</p>
                          <p>{cp.fmt(data.value)} ({pct}%)</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Revenue: {cp.fmt(totalBilled)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> Expenses: {cp.fmt(totalExpenses)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: netProfit >= 0 ? '#3b82f6' : '#f59e0b'}}></span> {netProfit >= 0 ? 'Profit' : 'Loss'}: {cp.fmt(Math.abs(netProfit))}</div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <Receipt size={18} /> Actual Profit Breakdown
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={actualProfit >= 0 ? [
                    { name: 'Revenue', value: cp.convert(collected), color: '#10b981' },
                    { name: 'Expense', value: cp.convert(expensesMade), color: '#f97316' },
                    { name: 'Profit', value: cp.convert(actualProfit), color: '#3b82f6' }
                  ] : [
                    { name: 'Revenue', value: cp.convert(collected), color: '#10b981' },
                    { name: 'Expense', value: cp.convert(expensesMade), color: '#f97316' },
                    { name: 'Loss', value: cp.convert(Math.abs(actualProfit)), color: '#f59e0b' }
                  ]}
                  cx="50%" cy="50%" innerRadius="60%" outerRadius="80%" paddingAngle={2} dataKey="value"
                >
                  {(actualProfit >= 0 ? [1,2,3] : [1,2,3]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(actualProfit >= 0 ? ['#10b981', '#f97316', '#3b82f6'] : ['#10b981', '#f97316', '#f59e0b'])[index]} />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const totalCol = cp.convert(collected) || 1;
                      const pct = ((data.value / totalCol) * 100).toFixed(1);
                      return (
                        <div className="bg-white border border-slate-200 p-2 shadow-lg rounded text-sm">
                          <p className="font-semibold" style={{ color: data.color }}>{data.name}</p>
                          <p>{cp.fmt(data.value)} ({pct}%)</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Revenue: {cp.fmt(collected)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Expense: {cp.fmt(expensesMade)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: actualProfit >= 0 ? '#3b82f6' : '#f59e0b'}}></span> {actualProfit >= 0 ? 'Profit' : 'Loss'}: {cp.fmt(Math.abs(actualProfit))}</div>
          </div>
        </div>
      </div>
      {activeProduct === 'hotel' && hotelStats && (
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-slate-500 uppercase mb-3">Hotel Performance</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <KpiCard label="Occupancy %" value={`${hotelStats.occupancyPct.toFixed(1)}%`} tone="blue" />
            <KpiCard label="ADR" value={cp.fmt(hotelStats.adr)} tone="green" />
            <KpiCard label="RevPAR" value={cp.fmt(hotelStats.revpar)} tone="gold" />
            <KpiCard label="Guest Invoices Pending" value={cp.fmt(hotelStats.invoicesPending)} tone="red" />
          </div>
          {hotelStats.dailyTrend.length > 1 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
                <h3 className="font-semibold text-slate-700 mb-4 self-start">Actual vs Budget ({hotelStats.budgetCurrency})</h3>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(props.payload.realValue)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#1B3A6B'}}></span> Actual: {new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(hotelStats.totalRevenue)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#C9A84C'}}></span> Budgeted: {new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(hotelStats.totalBudgetUsd)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444'}}></span> Variance: {new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(hotelStats.totalVarianceUsd)}</div>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
                <h3 className="font-semibold text-slate-700 mb-4 self-start">Actual vs Budget ({cp.displayCurrency})</h3>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#1B3A6B'}}></span> Actual: {cp.fmt(hotelStats.totalRevenue)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#C9A84C'}}></span> Budgeted: {cp.fmt(hotelStats.totalBudgetUsd)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444'}}></span> Variance: {cp.fmt(hotelStats.totalVarianceUsd)}</div>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">
                <h3 className="font-semibold text-slate-700 mb-4">Room Revenue: Actual vs Daily Budget</h3>
                <div className="h-64 sm:h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={hotelStats.dailyTrend}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip formatter={v => cp.fmt(v)} />
                      <Legend />
                      <Bar dataKey="Actual" fill="#1B3A6B" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="Budget" fill="#C9A84C" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <TrendingUp size={18} /> Revenue, Expenses &amp; Profit/Loss
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
              <Bar dataKey="Profit" name="Profit/Loss" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <Receipt size={18} /> Billing &amp; Outstanding Overview
        </h2>
        <div className="h-72 sm:h-96 -ml-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={billingChartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => cp.fmt(v)} />
              <Legend />
              <Bar dataKey="Revenue Billed" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Outstanding Payment" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Expenses Billed" fill="#f97316" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Profit Expected" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-5 mb-6">
        <OverviewCard title="Company Overview - YTD" subtitle={`${activeCompany.name} • Amounts in ${cp.displayCurrency}`}
          revenue={cp.fmt(ytdRevenue)} expenses={cp.fmt(ytdExpenses)} profit={cp.fmt(ytdRevenue - ytdExpenses)} profitValue={ytdRevenue - ytdExpenses}
          revenueLabel="YTD Revenue" expensesLabel="YTD Expenses" profitLabel="YTD Net Profit" />
        <OverviewCard title="Company Overview - All Time" subtitle={`${activeCompany.name} • Amounts in ${cp.displayCurrency}`}
          revenue={cp.fmt(allTimeRevenue)} expenses={cp.fmt(allTimeExpenses)} profit={cp.fmt(allTimeRevenue - allTimeExpenses)} profitValue={allTimeRevenue - allTimeExpenses}
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
            { key: 'balance_due', label: 'Balance Due', render: r => `${Number(r.balance_due).toLocaleString()} ${r.currency}` },
            { key: 'balance_usd', label: `Balance (${cp.displayCurrency})`, render: r => cp.fmt((Number(r.balance_due) / (Number(r.amount) || 1)) * Number(r.amount_usd)) },
            { key: 'status', label: 'Status' },
          ]}
          rows={draftInvoices}
          emptyMessage="No outstanding invoices — nice work."
        />
      </div>

      {activeProduct !== 'hotel' && (
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <AlertCircle size={18} className="text-slate-400" /> Draft Expenses ({draftExpenses.length})
        </h2>
        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Invoice #' },
            { key: 'supplier', label: 'Supplier', render: r => r.contact?.name || r.supplier_name_freeform || '—' },
            { key: 'invoice_date', label: 'Date' },
            { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
            { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
          ]}
          rows={draftExpenses}
          emptyMessage="No draft expenses."
        />
      </div>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Dashboard"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'MTD' },
            { type: 'checkboxGroup', key: 'sections', label: 'Include Sections', options: ['Revenue, Expenses & Profit/Loss (Chart)', 'Billing & Outstanding Overview (Chart)', 'Company Overview - YTD', 'Company Overview - All Time', 'Recent Transactions', 'Outstanding Invoices'], default: ['Revenue, Expenses & Profit/Loss (Chart)', 'Billing & Outstanding Overview (Chart)', 'Company Overview - YTD', 'Company Overview - All Time', 'Recent Transactions', 'Outstanding Invoices'] },
          ]}
          onGenerate={generateDashboardReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function OverviewCard({ title, subtitle, revenue, expenses, profit, profitValue = 0, revenueLabel, expensesLabel, profitLabel }) {
  const isPositive = profitValue >= 0
  const pBg = isPositive ? 'bg-emerald-50' : 'bg-red-50'
  const pText = isPositive ? 'text-emerald-700' : 'text-red-700'
  
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
        <div className={`flex items-center justify-between ${pBg} rounded-lg px-3 py-2`}>
          <span className={`text-sm ${pText} flex items-center gap-1`}><DollarSign size={14} /> {profitLabel}</span>
          <span className="font-bold text-slate-800">{profit}</span>
        </div>
      </div>
    </div>
  )
}
