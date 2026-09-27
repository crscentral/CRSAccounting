import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod, formatDate } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function Transactions() {
  const { activeCompany, activeProduct } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [rows, setRows] = useState([])
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadData() {
    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to)
    let rdrPromise = Promise.resolve({ data: [] })
    let hrsPromise = Promise.resolve({ data: [] })
    let hrePromise = Promise.resolve({ data: [] })
    let amcPromise = Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      siPromise = supabase.from('hotel_guest_invoices').select('id, invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, currency, amount:invoice_amount, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:notes').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
      rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
      hrsPromise = supabase.from('hotel_room_stats').select('id, stat_date, room_revenue_usd, manual_room_revenue_collected_usd, currency, room_revenue').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to)
      hrePromise = supabase.from('hotel_revenue_entries').select('id, entry_date, amount_usd, currency, amount, notes, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to)
      amcPromise = supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    } else {
      siPromise = supabase.from('sales_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('purchase_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }, { data: hrs }, { data: hre }, { data: amc }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise, hrsPromise, hrePromise, amcPromise])

    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || 'Expense'}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(rdr || []).map(r => { const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return { id: `rdr-${r.id}`, date: r.revenue_date, type: 'F&B Revenue', desc: `${r.meal_period} F&B Revenue`, amount_usd: total, amount: total, currency: 'USD', direction: 'in' } }),
      ...(hre || []).map(r => ({ id: `hre-${r.id}`, date: r.entry_date, type: 'Ancillary Revenue', desc: r.account?.name || r.notes || 'Revenue', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(hrs || []).filter(r => Number(r.room_revenue_usd) > 0).map(r => ({ id: `hrs-${r.id}`, date: r.stat_date, type: 'Room Revenue', desc: 'Daily Room Revenue', amount_usd: r.room_revenue_usd, amount: r.room_revenue || r.room_revenue_usd, currency: r.currency || 'USD', direction: 'in' })),
    ]
    
        // Add AMC Contract lines (Actual Posting or Amortized depending on view)
    if (amc && amc.length > 0) {
      const isMonth = cp.periodProps.periodType.includes('MONTH') || cp.periodProps.periodType === 'LAST_30_DAYS' || (new Date(cp.range.to) - new Date(cp.range.from)) <= 35 * 24 * 60 * 60 * 1000
      amc.forEach(r => {
        if (isMonth) {
          combined.push({ id: `amc-${r.id}`, date: cp.range.from, type: 'AMC Contract', desc: `${r.contract_name || 'AMC Contract'} - Amortized AMC (Monthly)`, amount_usd: Number(r.annual_amount_usd)/12, amount: Number(r.annual_amount || r.annual_amount_usd)/12, currency: r.currency || 'USD', direction: 'out' })
        } else {
          const dStr = r.start_year ? `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01` : (r.created_at || '').split('T')[0] || cp.range.from
          combined.push({ id: `amc-${r.id}`, date: dStr >= cp.range.from && dStr <= cp.range.to ? dStr : cp.range.from, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount_usd: r.annual_amount_usd, amount: r.annual_amount || r.annual_amount_usd, currency: r.currency || 'USD', direction: 'out' })
        }
      })
    }
    
    combined.sort((a, b) => b.date.localeCompare(a.date))

    setRows(combined)
  }

  async function generateTransactionsReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const wantSales = selections.txType.includes('Sales Invoices')
    const wantPurchase = selections.txType.includes('Purchase Invoices')
    const wantReceipts = selections.txType.includes('Payment Receipts')

    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] })
    let rdrPromise = Promise.resolve({ data: [] })
    let hrsPromise = Promise.resolve({ data: [] })
    let hrePromise = Promise.resolve({ data: [] })
    let amcPromise = Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      if (wantSales) siPromise = supabase.from('hotel_guest_invoices').select('invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('hotel_expense_entries').select('invoice_number:id, invoice_date:expense_date, amount_usd, contact:notes').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to)
      if (wantSales) rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
      if (wantSales) hrsPromise = supabase.from('hotel_room_stats').select('id, stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to)
      if (wantSales) hrePromise = supabase.from('hotel_revenue_entries').select('id, entry_date, amount_usd, notes, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to)
      if (wantPurchase) amcPromise = supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    } else {
      if (wantSales) siPromise = supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }, { data: hrs }, { data: hre }, { data: amc }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise, hrsPromise, hrePromise, amcPromise])

    const combined = [
      ...(si || []).map(r => ({ date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount: fmt(r.amount_usd), direction: '+' })),
      ...(pi || []).map(r => ({ date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || 'Expense'}`, amount: fmt(r.amount_usd), direction: '-' })),
      ...(pr || []).map(r => ({ date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount: fmt(r.amount_usd), direction: '+' })),
      ...(rdr || []).map(r => { const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return { date: r.revenue_date, type: 'F&B Revenue', desc: `${r.meal_period} F&B Revenue`, amount: fmt(total), direction: '+' } }),
      ...(hre || []).map(r => ({ date: r.entry_date, type: 'Ancillary Revenue', desc: r.account?.name || r.notes || 'Revenue', amount: fmt(r.amount_usd), direction: '+' })),
      ...(hrs || []).filter(r => Number(r.room_revenue_usd) > 0).map(r => ({ date: r.stat_date, type: 'Room Revenue', desc: 'Daily Room Revenue', amount: fmt(r.room_revenue_usd), direction: '+' })),
    ]

        // Add AMC Contract lines (Actual Posting or Amortized depending on view)
    if (amc && amc.length > 0) {
      const isMonth = selections.period.includes('MONTH') || selections.period === 'LAST_30_DAYS' || (new Date(range.to) - new Date(range.from)) <= 35 * 24 * 60 * 60 * 1000
      amc.forEach(r => {
        if (isMonth) {
          combined.push({ date: range.from, type: 'AMC Contract', desc: `${r.contract_name || 'AMC Contract'} - Amortized AMC (Monthly)`, amount: fmt(Number(r.annual_amount_usd)/12), direction: '-' })
        } else {
          const dStr = r.start_year ? `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01` : (r.created_at || '').split('T')[0] || range.from
          combined.push({ date: dStr >= range.from && dStr <= range.to ? dStr : range.from, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount: fmt(r.annual_amount_usd), direction: '-' })
        }
      })
    }
    
    combined.sort((a, b) => b.date.localeCompare(a.date))

    const sections = [{
      heading: 'Transactions',
      columns: ['Date', 'Type', 'Description', `Amount (${selections.currency})`],
      rows: combined.map(t => [t.date, t.type, t.desc, `${t.direction}${t.amount}`]),
    }]

    const title = 'Transactions'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') await exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'transactions_report' , logoUrl: activeCompany?.logo_url})
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'transactions_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'transactions_report' , logoUrl: activeCompany?.logo_url})
  }

  if (!activeCompany) return null

  return (
    <div>
      <PageHeader
        title="Transactions"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <StatBox label={`Total Inflow (${cp.displayCurrency})`} value={cp.fmt(rows.filter(r => r.direction === 'in').reduce((s, r) => s + Number(r.amount_usd), 0))} tone="green" />
        <StatBox label={`Total Outflow (${cp.displayCurrency})`} value={cp.fmt(rows.filter(r => r.direction === 'out').reduce((s, r) => s + Number(r.amount_usd), 0))} tone="red" />
        <StatBox label={`Net Position (${cp.displayCurrency})`} value={cp.fmt(rows.reduce((s, r) => s + (r.direction === 'in' ? Number(r.amount_usd) : -Number(r.amount_usd)), 0))} tone="slate" />
      </div>

      <DataTable
        columns={[
          { key: 'date', label: 'Date', render: r => <span className="whitespace-nowrap">{formatDate(r.date)}</span> },
          { key: 'type', label: 'Type' },
          { key: 'desc', label: 'Description' },
          {
            key: 'amount_native', label: 'Original Amount', render: r => (
              <span className={r.direction === 'in' ? 'text-emerald-600 font-medium' : 'text-red-600 font-medium'}>
                {r.direction === 'in' ? '+' : '−'} {Number(r.amount)?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {r.currency}
              </span>
            )
          },
          {
            key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => (
              <span className={r.direction === 'in' ? 'text-emerald-600 font-medium' : 'text-red-600 font-medium'}>
                {r.direction === 'in' ? '+' : '−'}{cp.fmt(r.amount_usd)}
              </span>
            )
          },
        ]}
        rows={rows}
      />

      {reportModalOpen && (
        <ReportOptionsModal
          title="Transactions"
          fields={[
            { type: 'checkboxGroup', key: 'txType', label: 'Transaction Types', options: ['Sales Invoices', 'Purchase Invoices', 'Payment Receipts'], default: ['Sales Invoices', 'Purchase Invoices', 'Payment Receipts'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateTransactionsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function StatBox({ label, value, tone = 'slate' }) {
  const tones = { green: 'text-emerald-600', amber: 'text-amber-600', red: 'text-red-600', slate: 'text-slate-800' }
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-xl sm:text-2xl font-bold ${tones[tone]}`}>{value}</div>
    </div>
  )
}
