import { getLocalDate } from '../lib/dateUtils'
import { useEffect, useState } from 'react'
import { Plus, Trash2, Repeat, Pencil } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod, MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import AccountFormModal from '../components/AccountFormModal'
import PurchaseInvoiceFormModal from '../components/PurchaseInvoiceFormModal'
import { FileText } from 'lucide-react'

import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, LabelList } from 'recharts'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'


import React from 'react';
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return <div style={{ padding: '2rem', color: 'red' }}><h1>Something went wrong.</h1><pre>{this.state.error.toString()}</pre></div>;
    }
    return this.props.children;
  }
}


export default function HotelExpenses() {
  return <ErrorBoundary><HotelExpensesInner /></ErrorBoundary>;
}

function HotelExpensesInner() {

  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [expenseModalOpen, setExpenseModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [amcModalOpen, setAmcModalOpen] = useState(false)
  const [newHeadModalOpen, setNewHeadModalOpen] = useState(false)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [entries, setEntries] = useState([])
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [amcContracts, setAmcContracts] = useState([])
  const [expenseAccounts, setExpenseAccounts] = useState([])
  const [purchaseModalOpen, setPurchaseModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('daily') // 'daily' or 'purchase'
  const [purchaseInvoices, setPurchaseInvoices] = useState([])
  const [expandedEntries, setExpandedEntries] = useState({})
  const [expandedAmc, setExpandedAmc] = useState({})
  const [expandedPI, setExpandedPI] = useState({})

  const [contacts, setContacts] = useState([])

  const [totalRooms, setTotalRooms] = useState(0)
  const [totalOccupied, setTotalOccupied] = useState(0)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadAll() {
    const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: roomStats }, { data: pi }, { data: cont }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype, type').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      supabase.from('hotel_room_stats').select('rooms_occupied, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
      supabase.from('purchase_invoices').select('*, contact:contacts(name), account:accounts(code, name)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name'),
      supabase.from('hotel_revenue_entries').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      supabase.from('restaurant_daily_revenue').select('total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
    ])
    
    let rev = 0;
    (roomStats || []).forEach(r => rev += Number(r.room_revenue_usd) || 0);
    (hre || []).forEach(r => rev += Number(r.amount_usd) || 0);
    (rdr || []).forEach(r => {
       const total = Number(r.total_amount_usd) || ((Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0) + (Number(r.other_amount_usd) || 0))
       if (total > 0) rev += total;
    });
    setTotalRevenue(rev);
    
    setEntries(exp || [])
    setAmcContracts(amc || [])
    setExpenseAccounts(accs || [])
    setTotalRooms(settings?.total_rooms || 0)
    setTotalOccupied((roomStats || []).reduce((s, r) => s + (r.rooms_occupied || 0), 0))
    setPurchaseInvoices(pi || [])
    setContacts(cont || [])
  }

  async function handleDeleteEntry(row) {
    if (!confirm('Delete this expense entry?')) return
    await supabase.from('hotel_expense_entries').delete().eq('id', row.id)
    loadAll()
  }
    async function handleDeletePI(row) {
    if (!confirm('Delete this purchase invoice?')) return
    await supabase.from('purchase_invoices').delete().eq('id', row.id)
    loadAll()
  }
  async function handleDeleteAmc(row) {
    if (!confirm(`Delete AMC contract "${row.contract_name}"? This removes all 12 monthly postings.`)) return
    await supabase.from('hotel_amc_contracts').delete().eq('id', row.id)
    loadAll()
  }

  async function generateExpensesReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)
    
    // We already have the current entries and amcContracts in state. 
    // The report generator might fetch a different date range, so let's use the fetched data.
    const { data: exp } = await supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).in('product', ['hotel', 'restaurant']).gte('expense_date', range.from).lte('expense_date', range.to).order('expense_date', { ascending: false })
    
    // Determine selected heads
    const selectedHeads = selections.heads || []
    const includeAll = selectedHeads.length === 0
    const includeAmc = includeAll || selectedHeads.includes('AMC Contracts (Amortized)')
    
    // Calculate AMC amortized amount for this range
    const start = new Date(range.from)
    const end = new Date(range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcMonthlyTotalUsd = amcContracts.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
    const amcTotalForView = amcMonthlyTotalUsd * monthsInView
    
    let totalView = 0
    let expenseRows = []
    
    (exp || []).forEach(r => {
      const head = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
      if (includeAll || selectedHeads.includes(head)) {
        expenseRows.push([r.expense_date, head, f(r.amount_usd), r.notes || '—'])
        totalView += Number(r.amount_usd)
      }
    })
    
    if (includeAmc && amcTotalForView > 0) {
      expenseRows.unshift([range.to, 'AMC Contracts (Amortized)', f(amcTotalForView), 'Auto-Amortized Monthly Portion'])
      totalView += amcTotalForView
    }

    const sections = [
      {
        heading: 'Summary',
        keyValuePairs: [
          ['Total Expenses in Period', f(totalView)],
          ['Number of Expense Heads', String(new Set(expenseRows.map(r => r[1])).size)]
        ]
      },
      {
        heading: 'Expense Detail',
        columns: ['Date', 'Expense Head', 'Amount', 'Notes'],
        rows: expenseRows
      }
    ]
    
    const title = 'Hotel Expenses Report'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    const logoUrl = activeCompany.logo_url
    
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'hotel_expenses', logoUrl })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_expenses' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_expenses' })
  }

  if (!activeCompany) return null
  
  const start = new Date(cp.range.from)
  const end = new Date(cp.range.to)
  const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
  const daysInView = Math.max(1, Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1)
  const availableRoomNights = totalRooms * daysInView

  const amcMonthlyTotalUsd = amcContracts.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
  const amcTotalForView = amcMonthlyTotalUsd * monthsInView

  const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  
  const entriesTotal = entries.reduce((s, r) => s + Number(r.amount_usd), 0)

  const piTotalUsd = purchaseInvoices.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd

  const totalHotelExpenses = entries.filter(e => e.product === 'hotel').reduce((s, r) => s + Number(r.amount_usd), 0)
    + amcContracts.filter(e => e.product === 'hotel').reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    + purchaseInvoices.filter(e => e.product === 'hotel').reduce((s, r) => s + Number(r.amount_usd), 0);

  const totalRestExpenses = entries.filter(e => e.product === 'restaurant').reduce((s, r) => s + Number(r.amount_usd), 0)
    + amcContracts.filter(e => e.product === 'restaurant').reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    + purchaseInvoices.filter(e => e.product === 'restaurant').reduce((s, r) => s + Number(r.amount_usd), 0);


  const entriesTotalPaidUsd = entries.reduce((s, r) => s + Number(r.paid_amount_usd || 0), 0)
  const amcMonthlyPaidUsd = amcContracts.reduce((s, r) => s + (Number(r.paid_amount_usd || 0) / 12), 0)
  const amcTotalPaidForView = amcMonthlyPaidUsd * monthsInView
  const piTotalPaidUsd = purchaseInvoices.reduce((s, r) => s + (r.status === 'Paid' ? Number(r.amount_usd) : 0), 0)


  const totalBilled = totalExpenses
  const totalPaid = entriesTotalPaidUsd + amcTotalPaidForView + piTotalPaidUsd
  const totalPending = totalBilled - totalPaid

  const byHead = { 'AMC Contracts (Amortized)': amcTotalForView }
  entries.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })
  purchaseInvoices.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })
  
  const pieData = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({ 
    name, 
    value,
    percentStr: totalExpenses > 0 ? ((value / totalExpenses) * 100).toFixed(1) + '%' : '0.0%'
  })).sort((a, b) => b.value - a.value)
  const barDataRev = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => {
    const percentStr = totalRevenue > 0 ? ((value / totalRevenue) * 100).toFixed(1) + '%' : '0.0%';
    const shortName = name.split(' - ')[1] || name;
    return {
      name: `${shortName} ${percentStr}`,
      fullName: name,
      value: value,
      percentStr
    }
  }).sort((a, b) => b.value - a.value)

  const barDataExp = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => {
    const percentStr = totalExpenses > 0 ? ((value / totalExpenses) * 100).toFixed(1) + '%' : '0.0%';
    const shortName = name.split(' - ')[1] || name;
    return {
      name: `${shortName} ${percentStr}`,
      fullName: name,
      value: value,
      percentStr
    }
  }).sort((a, b) => b.value - a.value)
  
  const remainingRev = totalRevenue - totalExpenses;
  if (remainingRev > 0) {
    barDataRev.push({
      name: 'Remaining Revenue',
      fullName: 'Remaining Revenue (Gross Profit)',
      value: remainingRev,
      percentStr: ((remainingRev / totalRevenue) * 100).toFixed(1) + '%'
    });
  }
  const totalRevPercent = totalRevenue > 0 ? ((totalExpenses / totalRevenue) * 100).toFixed(1) + '%' : '0.0%';
  const totalExpPercent = '100.0%';

  
  const renderRichLegend = (props) => {
    const { payload } = props;
    const sortedPayload = [...payload].sort((a, b) => b.payload.value - a.payload.value);
    return (
      <ul className="text-[11px] space-y-1.5 m-0 p-0 list-none max-h-64 overflow-y-auto pr-2">
        {sortedPayload.map((entry, index) => (
          <li key={`item-${index}`} className="flex items-center gap-2 text-slate-600 font-medium">
            <span className="w-16 text-right font-bold text-slate-700 shrink-0">{cp.fmt(entry.payload.value)}</span>
            <span className="w-10 text-right text-slate-400 shrink-0">{entry.payload.percentStr}</span>
            <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: entry.color }}></span>
            <span className="truncate" title={entry.payload.fullName || entry.payload.name}>{entry.payload.fullName || entry.payload.name}</span>
          </li>
        ))}
      </ul>
    );
  }
  const renderCustomLegend = (props) => {
    const { payload } = props;
    
  return (
      <ul className="text-[11px] space-y-1.5 w-full">
        {payload.map((entry, index) => (
          <li key={`item-${index}`} className="flex items-center">
            <span className="w-10 text-right mr-2 text-slate-500 font-medium shrink-0">{entry.payload.percentStr}</span>
            <span className="w-2.5 h-2.5 mr-2 rounded-[2px] shrink-0" style={{ backgroundColor: entry.color }}></span>
            <span style={{ color: entry.color }} className="truncate max-w-[160px]" title={entry.value}>{entry.value}</span>
          </li>
        ))}
      </ul>
    );
  }
  const COLORS = ['#1e293b', '#3b82f6', '#10b981', '#f59e0b', '#6366f1', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e', '#64748b']
  const groupedEntriesMap = {}
  entries.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    if (!groupedEntriesMap[key]) groupedEntriesMap[key] = { isGroupHeader: true, name: key, amount_usd: 0, paid_amount_usd: 0, transactions: [], account_id: r.account_id }
    groupedEntriesMap[key].amount_usd += Number(r.amount_usd)
    groupedEntriesMap[key].paid_amount_usd += Number(r.paid_amount_usd || 0)
    groupedEntriesMap[key].transactions.push(r)
  })
  const flattenedEntries = []
  Object.values(groupedEntriesMap).sort((a,b) => b.amount_usd - a.amount_usd).forEach(g => {
    flattenedEntries.push({ ...g, id: 'group_' + g.name })
    if (expandedEntries[g.name]) {
      g.transactions.forEach(t => flattenedEntries.push({ ...t, isGroupChild: true }))
    }
  })

  const groupedAmcMap = {}
  amcContracts.forEach(r => {
    const key = r.contract_name || 'Unknown'
    if (!groupedAmcMap[key]) groupedAmcMap[key] = { isGroupHeader: true, name: key, annual_amount_usd: 0, paid_amount_usd: 0, transactions: [] }
    groupedAmcMap[key].annual_amount_usd += Number(r.annual_amount_usd)
    groupedAmcMap[key].paid_amount_usd += Number(r.paid_amount_usd || 0)
    groupedAmcMap[key].transactions.push(r)
  })
  const flattenedAmc = []
  Object.values(groupedAmcMap).sort((a,b) => b.annual_amount_usd - a.annual_amount_usd).forEach(g => {
    flattenedAmc.push({ ...g, id: 'group_' + g.name })
    if (expandedAmc[g.name]) {
      g.transactions.forEach(t => flattenedAmc.push({ ...t, isGroupChild: true }))
    }
  })

  const groupedPIMap = {}
  purchaseInvoices.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : (r.supplier_name_freeform || 'Unknown')
    if (!groupedPIMap[key]) groupedPIMap[key] = { isGroupHeader: true, name: key, amount_usd: 0, paid: 0, transactions: [] }
    groupedPIMap[key].amount_usd += Number(r.amount_usd)
    groupedPIMap[key].paid += r.status === 'Paid' ? Number(r.amount_usd) : 0
    groupedPIMap[key].transactions.push(r)
  })
  const flattenedPI = []
  Object.values(groupedPIMap).sort((a,b) => b.amount_usd - a.amount_usd).forEach(g => {
    flattenedPI.push({ ...g, id: 'group_' + g.name })
    if (expandedPI[g.name]) {
      g.transactions.forEach(t => flattenedPI.push({ ...t, isGroupChild: true }))
    }
  })

  const topHeads = Object.entries(byHead).sort((a, b) => b[1] - a[1]).slice(0, 3)

  return (
    <div>
      <PageHeader
        title="Expenses"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button onClick={() => { setEditingRow(null); setAmcModalOpen(true); }} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg">
                  <Repeat size={15} /> New AMC Contract
                </button>
                <button onClick={() => { setEditingRow(null); setPurchaseModalOpen(true); }} className="flex items-center gap-1.5 bg-gold-600 hover:bg-gold-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <FileText size={15} /> New Purchase Invoice
                </button>
                <button onClick={() => { setEditingRow(null); setExpenseModalOpen(true); }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={15} /> New Expense
                </button>
              </>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        <KpiCard label="Total Hotel Expenses" value={cp.fmt(totalHotelExpenses)} tone="slate" />
        <KpiCard label="Total Restaurant Expenses" value={cp.fmt(totalRestExpenses)} tone="slate" />
        {topHeads.slice(0, 1).map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}
      </div>

      <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Billed" value={cp.fmt(totalBilled)} tone="slate" />
        <KpiCard label="Total Paid" value={cp.fmt(totalPaid)} tone="green" />
        <KpiCard label="Total Pending" value={cp.fmt(totalPending)} tone="red" />
      </div>
      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Expense Breakdown (Cost Per Occupied Room: {totalOccupied > 0 ? cp.fmt(totalExpenses/totalOccupied) : '—'})</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2}>
                  {pieData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <RechartsTooltip formatter={(value) => cp.fmt(value)} />
                <Legend layout="vertical" verticalAlign="middle" align="right" content={renderCustomLegend} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Expense Breakdown (Cost Per Available Room: {availableRoomNights > 0 ? cp.fmt(totalExpenses/availableRoomNights) : '—'})</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                  {pieData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <RechartsTooltip formatter={(value) => cp.fmt(value)} />
                <Legend layout="vertical" verticalAlign="middle" align="right" content={renderCustomLegend} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex justify-between items-start mb-4">
             <h3 className="text-sm font-semibold text-slate-800">Expense % compared to Revenue Generated</h3>
             <div className="text-right text-xs">
               <div className="text-slate-500 font-medium">Total Revenue</div>
               <div className="font-bold text-slate-700">{cp.fmt(totalRevenue)}</div>
             </div>
          </div>
          <div className="flex h-72 items-center">
            <div className="w-[180px] shrink-0 h-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={barDataRev} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2} stroke="none">
                    {barDataRev.map((e, i) => <Cell key={i} fill={e.fullName === 'Remaining Revenue (Gross Profit)' ? '#e2e8f0' : COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <RechartsTooltip formatter={(value, name, props) => [`${cp.fmt(value)} (${props?.payload?.percentStr || ''})`, 'Amount']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 min-w-0 pl-2 h-full overflow-y-auto flex flex-col justify-center">
               {renderRichLegend({ payload: barDataRev.map((d, i) => ({ payload: d, color: d.fullName === 'Remaining Revenue (Gross Profit)' ? '#e2e8f0' : COLORS[i % COLORS.length] })) })}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-sm font-semibold">
             <span className="text-slate-600">Total Expenses</span>
             <span className="text-slate-800">{cp.fmt(totalExpenses)} <span className="text-blue-600 ml-1">({totalRevPercent})</span></span>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex justify-between items-start mb-4">
             <h3 className="text-sm font-semibold text-slate-800">Expense % compared to Total Expense</h3>
             <div className="text-right text-xs">
               <div className="text-slate-500 font-medium">Total Expenses</div>
               <div className="font-bold text-slate-700">{cp.fmt(totalExpenses)}</div>
             </div>
          </div>
          <div className="flex h-72 items-center">
            <div className="w-[180px] shrink-0 h-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={barDataExp} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={0} outerRadius={80} stroke="none">
                    {barDataExp.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <RechartsTooltip formatter={(value, name, props) => [`${cp.fmt(value)} (${props?.payload?.percentStr || ''})`, 'Amount']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 min-w-0 pl-2 h-full overflow-y-auto flex flex-col justify-center">
               {renderRichLegend({ payload: barDataExp.map((d, i) => ({ payload: d, color: COLORS[i % COLORS.length] })) })}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-sm font-semibold">
             <span className="text-slate-600">Total Expenses</span>
             <span className="text-slate-800">{cp.fmt(totalExpenses)} <span className="text-amber-600 ml-1">({totalExpPercent})</span></span>
          </div>
        </div>
      </div>

      <div className="flex gap-6 border-b border-slate-200 mb-6 mt-8">
        <button onClick={() => setActiveTab('daily')} className={`pb-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'daily' ? 'border-navy-600 text-navy-700' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>Daily Expenses</button>
        <button onClick={() => setActiveTab('purchase')} className={`pb-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'purchase' ? 'border-navy-600 text-navy-700' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>Purchase Invoices</button>
      </div>

      {activeTab === 'daily' && (
        <>
          <div className="flex justify-between items-end mb-3">
            <div>
              <h3 className="font-semibold text-slate-700 flex items-center gap-3">
                <span>Combined Daily Expense Entries</span>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
            )}
          </h3>
        </div>
        <div className="text-sm text-slate-500 font-medium">
          Total Heads: {new Set(entries.map(e => e.account_id)).size} &bull; Total Daily Amount: {cp.fmt(entriesTotal)}
        </div>
      </div>
      <DataTable
        columns={[
          { key: 'expense_date', label: 'Date / Head', render: r => r.isGroupHeader ? <button className="font-bold text-navy-700 hover:text-navy-900 flex items-center gap-2" onClick={() => setExpandedEntries(p => ({...p, [r.name]: !p[r.name]}))}>{expandedEntries[r.name] ? '▼' : '▶'} {r.name}</button> : <span className="pl-6 text-slate-500">{r.expense_date}</span> },
          { key: 'invoice_number', label: 'Invoice #', render: r => r.isGroupHeader ? <span className="text-slate-400 text-xs">{r.transactions.length} items</span> : (r.invoice_number || '—') },
          { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
          { key: 'paid', label: 'Paid', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'pending', label: 'Pending', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span> }, 
          { key: 'notes', label: 'Notes', render: r => r.isGroupHeader ? '—' : (r.notes || '—') },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => r.isGroupHeader ? null : <div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setExpenseModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteEntry(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div> }] : []),
        ]}
        rows={flattenedEntries}
        emptyMessage="No expense entries in this range."
        footer={<span>Total Heads: {new Set(entries.map(e => e.account_id)).size} &nbsp;&bull;&nbsp; Total Daily Amount: {cp.fmt(entriesTotal)}</span>}
      />

      <h3 className="font-semibold text-slate-700 mb-3 mt-6">Combined AMC Contracts (auto-split across 12 months)</h3>
      <DataTable
        columns={[
          { key: 'contract_name', label: 'Contract', render: r => r.isGroupHeader ? <button className="font-bold text-navy-700 hover:text-navy-900 flex items-center gap-2" onClick={() => setExpandedAmc(p => ({...p, [r.name]: !p[r.name]}))}>{expandedAmc[r.name] ? '▼' : '▶'} {r.name} <span className="text-slate-400 text-xs ml-2 font-normal">({r.transactions.length})</span></button> : <span className="pl-6 text-slate-500">{r.contract_name}</span> },
          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd)}</span> },
          { key: 'annual_paid', label: 'Paid (Yr)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'annual_pending', label: 'Pending (Yr)', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
          { key: 'monthly', label: 'Monthly', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd / 12)}</span> },
          { key: 'monthly_paid', label: 'Paid (Mo)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt((r.paid_amount_usd || 0) / 12)}</span> },
          { key: 'monthly_pending', label: 'Pending (Mo)', render: r => <span className="text-rose-600 font-medium">{cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0)) / 12)}</span> }, 
          { key: 'start', label: 'Starts', render: r => r.isGroupHeader ? '—' : `${MONTH_NAMES[r.start_month - 1]} ${r.start_year}` },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => r.isGroupHeader ? null : <div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setAmcModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div> }] : []),
        ]}
        rows={flattenedAmc}
        emptyMessage="No AMC contracts yet."
      />
          
        </>
      )}
      {activeTab === 'purchase' && (
        <>
          <div className="flex justify-between items-end mb-3 mt-8">
            <h3 className="font-semibold text-slate-700">Combined Purchase Invoices</h3>
          </div>
          <DataTable
            columns={[
              { key: 'date', label: 'Date / Head', render: r => r.isGroupHeader ? <button className="font-bold text-navy-700 hover:text-navy-900 flex items-center gap-2" onClick={() => setExpandedPI(p => ({...p, [r.name]: !p[r.name]}))}>{expandedPI[r.name] ? '▼' : '▶'} {r.name}</button> : <span className="pl-6 text-slate-500">{r.invoice_date}</span> },
              { key: 'invoice_no', label: 'Invoice #', render: r => r.isGroupHeader ? <span className="text-slate-400 text-xs">{r.transactions.length} items</span> : r.invoice_number },
              { key: 'supplier', label: 'Supplier', render: r => r.isGroupHeader ? '—' : (r.contact?.name || r.supplier_name_freeform || 'Unknown') },
              { key: 'amount', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
              { key: 'paid', label: 'Paid', render: r => { const paid = r.isGroupHeader ? r.paid : (r.status === 'Paid' ? r.amount_usd : 0); return <span className="text-emerald-600 font-medium">{cp.fmt(paid)}</span> } },
              { key: 'pending', label: 'Pending', render: r => { const pending = r.isGroupHeader ? (r.amount_usd - r.paid) : (r.status === 'Paid' ? 0 : r.amount_usd); return <span className="text-rose-600 font-medium">{cp.fmt(pending)}</span> } }, 
              { key: 'status', label: 'Status', render: r => r.isGroupHeader ? '—' : <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Draft' ? 'bg-slate-100 text-slate-600' : r.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{r.status}</span> },
              ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => r.isGroupHeader ? null : <div className="flex justify-end gap-2">
                <button onClick={() => { setEditingRow(r); setPurchaseModalOpen(true); }} className="text-slate-400 hover:text-navy-600 p-1"><Pencil size={15} /></button>
                <button onClick={() => handleDeletePI(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={15} /></button>
              </div> }] : []),
            ]}
            rows={flattenedPI}
            emptyMessage="No purchase invoices yet."
          />
          
        </>
      )}

            {purchaseModalOpen && (
        <PurchaseInvoiceFormModal companyId={activeCompany.id} product={activeProduct} company={activeCompany} contacts={contacts} accounts={expenseAccounts} invoice={editingRow} onClose={() => { setPurchaseModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />
      )}
      {expenseModalOpen && (
        <ExpenseEntryFormModal companyId={activeCompany.id} product={activeProduct} accounts={expenseAccounts} editingRow={editingRow} onClose={() => { setExpenseModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />
      )}
      {amcModalOpen && (
        <AmcContractFormModal companyId={activeCompany.id} product={activeProduct} editingRow={editingRow} onClose={() => { setAmcModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />
      )}
      {newHeadModalOpen && (
        <AccountFormModal companyId={activeCompany.id} product={activeProduct} account={{ type: 'Expenses', subtype: 'Hotel Operating Expenses' }} onClose={() => setNewHeadModalOpen(false)} onSaved={loadAll} />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Expenses"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
            { type: 'checkboxGroup', key: 'sections', label: 'Select Specific Expense Heads (Optional, leave blank for all)', options: [...new Set(entries.map(e => e.account ? `${e.account.code} - ${e.account.name}` : 'Unknown'))] }
          ]}
          onGenerate={generateExpensesReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function ExpenseEntryFormModal({ companyId, product, accounts, editingRow, onClose, onSaved }) {
  const [expenseDate, setExpenseDate] = useState(editingRow?.expense_date || getLocalDate())
  const [accountId, setAccountId] = useState(editingRow?.account_id || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || '')
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [invoiceNumber, setInvoiceNumber] = useState(editingRow?.invoice_number || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!accountId || Number(amount) <= 0) { setError('Expense head and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, expense_date: expenseDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        paid_amount: Number(paidAmount || 0), paid_amount_usd: Math.round(Number(paidAmount || 0) / fxRate * 100) / 100,
        notes: notes || null,
        invoice_number: invoiceNumber || null
      }
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_expense_entries').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_expense_entries').insert(payload)
        err = error
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const grouped = {}
  accounts.forEach(a => { grouped[a.subtype || 'Other'] = grouped[a.subtype || 'Other'] || []; grouped[a.subtype || 'Other'].push(a) })

  return (
    <Modal title="New Expense" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Date *">
          <input type="date" required value={expenseDate} onChange={e => setExpenseDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Expense Head *">
          <select required value={accountId} onChange={e => setAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select…</option>
            {Object.entries(grouped).map(([group, accs]) => (
              <optgroup key={group} label={group}>
                {accs.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
              </optgroup>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-3 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Paid Amount">
            <input type="number" step="0.01" min="0" value={paidAmount} onChange={e => setPaidAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
                <Field label="Invoice Number">
          <input value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} placeholder="Optional" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function AmcContractFormModal({ companyId, product, editingRow, onClose, onSaved }) {
  const [contractName, setContractName] = useState(editingRow?.contract_name || '')
  const [annualAmount, setAnnualAmount] = useState(editingRow?.annual_amount || '')
  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [startMonth, setStartMonth] = useState(editingRow?.start_month || new Date().getMonth() + 1)
  const [startYear, setStartYear] = useState(editingRow?.start_year || new Date().getFullYear())
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!contractName.trim() || Number(annualAmount) <= 0) { setError('Contract name and a positive annual amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, contract_name: contractName.trim(), annual_amount: Number(annualAmount),
        currency, fx_rate_locked: fxRate, annual_amount_usd: Math.round(Number(annualAmount) / fxRate * 100) / 100,
        paid_amount: Number(paidAmount || 0), paid_amount_usd: Math.round(Number(paidAmount || 0) / fxRate * 100) / 100,
        start_year: startYear, start_month: startMonth, notes: notes || null,
      }
      
      let err
      if (editingRow) {
        const { error } = await supabase.from('hotel_amc_contracts').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_amc_contracts').insert(payload)
        err = error
      }
      
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={editingRow ? "Edit AMC Contract" : "New AMC Contract"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          Enter the annual contract value once — it automatically posts as 12 equal monthly expense entries starting from the month you choose.
        </p>
        <Field label="Contract Name / Type *">
          <input required value={contractName} onChange={e => setContractName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Elevator AMC, HVAC AMC" />
        </Field>
        <div className="grid grid-cols-3 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Annual Amount *">
            <input type="number" step="0.01" min="0" required value={annualAmount} onChange={e => setAnnualAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Paid Amount">
            <input type="number" step="0.01" min="0" value={paidAmount} onChange={e => setPaidAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Start Month">
            <select value={startMonth} onChange={e => setStartMonth(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
            </select>
          </Field>
          <Field label="Start Year">
            <input type="number" value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Create Contract'}</button>
        </div>
      </form>
    </Modal>
  )
}
