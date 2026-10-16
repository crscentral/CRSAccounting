import { useEffect, useState, useRef, useMemo } from 'react'
import { Plus, Eye, Pencil, Trash2, Download, Search, Filter, X } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { resolveReportPeriod, formatDate } from '../lib/fiscalYear'
import InvoiceDownloadMenu from '../components/InvoiceDownloadMenu'
import SalesInvoiceFormModal from '../components/SalesInvoiceFormModal'
import PaymentReceiptFormModal from '../components/PaymentReceiptFormModal'
import ReceiptCurrencySummary from '../components/ReceiptCurrencySummary'

const STATUS_COLORS = {
  Draft: 'bg-slate-100 text-slate-600',
  Paid: 'bg-emerald-100 text-emerald-700',
  Overdue: 'bg-red-100 text-red-700',
  Cancelled: 'bg-slate-100 text-slate-400',
}

export default function SalesInvoices() {
  const { activeCompany, activeProduct, can, activeRole } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [tab, setTab] = useState('invoices')
  const [invoices, setInvoices] = useState([])
  const [receipts, setReceipts] = useState([])
  const [contacts, setContacts] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingInvoice, setEditingInvoice] = useState(null)
  const [receiptModalOpen, setReceiptModalOpen] = useState(false)
  const [editingReceipt, setEditingReceipt] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  // Column filter states for Invoices
  const [invoiceFilters, setInvoiceFilters] = useState({
    invoiceNumber: '',
    customer: '',
    date: '',
    dueDate: '',
    amount: '',
    rate: '',
    amountUsd: '',
    status: '',
  })
  const [showInvoiceFilters, setShowInvoiceFilters] = useState(true)

  const invNumRef = useRef(null)
  const customerRef = useRef(null)
  const dateRef = useRef(null)
  const dueRef = useRef(null)
  const amountRef = useRef(null)
  const rateRef = useRef(null)
  const amountUsdRef = useRef(null)
  const statusRef = useRef(null)

  function focusColumnFilter(ref) {
    setShowInvoiceFilters(true)
    setTimeout(() => {
      if (ref.current) {
        ref.current.focus()
        if (ref.current.select) ref.current.select()
      }
    }, 50)
  }

  const activeInvoiceFilterCount = Object.values(invoiceFilters).filter(v => Boolean(v && v.trim())).length
  const hasActiveInvoiceFilters = activeInvoiceFilterCount > 0

  function clearInvoiceFilters() {
    setInvoiceFilters({
      invoiceNumber: '',
      customer: '',
      date: '',
      dueDate: '',
      amount: '',
      rate: '',
      amountUsd: '',
      status: '',
    })
  }

  // Column filter states for Payment Receipts
  const [receiptFilters, setReceiptFilters] = useState({
    receiptNumber: '',
    invoiceNumber: '',
    date: '',
    customer: '',
    amount: '',
    rate: '',
    amountUsd: '',
    method: '',
  })
  const [showReceiptFilters, setShowReceiptFilters] = useState(true)

  const recNumRef = useRef(null)
  const recInvNumRef = useRef(null)
  const recDateRef = useRef(null)
  const recCustomerRef = useRef(null)
  const recAmountRef = useRef(null)
  const recRateRef = useRef(null)
  const recAmountUsdRef = useRef(null)
  const recMethodRef = useRef(null)

  function focusReceiptFilter(ref) {
    setShowReceiptFilters(true)
    setTimeout(() => {
      if (ref.current) {
        ref.current.focus()
        if (ref.current.select) ref.current.select()
      }
    }, 50)
  }

  const activeReceiptFilterCount = Object.values(receiptFilters).filter(v => Boolean(v && v.trim())).length
  const hasActiveReceiptFilters = activeReceiptFilterCount > 0

  function clearReceiptFilters() {
    setReceiptFilters({
      receiptNumber: '',
      invoiceNumber: '',
      date: '',
      customer: '',
      amount: '',
      rate: '',
      amountUsd: '',
      method: '',
    })
  }

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadData() {
    const [{ data: inv }, { data: rec }, { data: con }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name, email, phone, address)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*, invoice:sales_invoices(invoice_number), contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to).order('receipt_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id),
    ])
    setInvoices(inv || [])
    setReceipts(rec || [])
    setContacts(con || [])
  }

  async function handleDelete(inv) {
    if (!confirm(`Delete invoice ${inv.invoice_number}? This cannot be undone.`)) return
    const { error } = await supabase.from('sales_invoices').delete().eq('id', inv.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadData()
  }




  async function generateSalesReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const sections = []
    if (selections.dataType === 'Invoices' || selections.dataType === 'Both') {
      const { data: inv } = await supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to).order('invoice_date', { ascending: false })
      sections.push({
        heading: 'Invoices',
        columns: ['Invoice #', 'Customer', 'Date', 'Due', 'Amount', `Amount (${selections.currency})`, 'Status'],
        rows: (inv || []).map(i => [i.invoice_number, i.contact?.name || '—', i.invoice_date, i.due_date || '—', `${i.amount} ${i.currency}`, fmt(i.amount_usd), i.status]),
      })
    }
    if (selections.dataType === 'Payment Receipts' || selections.dataType === 'Both') {
      const { data: rec } = await supabase.from('payment_receipts').select('*, invoice:sales_invoices(invoice_number), contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to).order('receipt_date', { ascending: false })
      sections.push({
        heading: 'Payment Receipts',
        columns: ['Invoice #', 'Date', 'Amount', `Amount (${selections.currency})`, 'Method'],
        rows: (rec || []).map(r => [r.invoice?.invoice_number || '—', r.receipt_date, `${r.amount} ${r.currency}`, fmt(r.amount_usd), r.method || '—']),
      })
    }

    const title = 'Sales & Receipts'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') await exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'sales_receipts_report' , logoUrl: activeCompany?.logo_url})
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'sales_receipts_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'sales_receipts_report' , logoUrl: activeCompany?.logo_url})
  }


  async function handleReceiptDelete(r) {
    if (!confirm('Delete this receipt?')) return
    const { error } = await supabase.from('payment_receipts').delete().eq('id', r.id)
    if (error) alert(error.message)
    else loadData()
  }

  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd || 0), 0)
  const pendingUsd = invoices.reduce((s, i) => s + (i.status === 'Paid' ? 0 : ((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))), 0)
  const collectedUsd = totalUsd - pendingUsd

  const byCurrency = {}
  invoices.forEach(i => {
    byCurrency[i.currency] = byCurrency[i.currency] || { count: 0, native: 0, usd: 0 }
    byCurrency[i.currency].count += 1
    byCurrency[i.currency].native += Number(i.amount)
    byCurrency[i.currency].usd += Number(i.amount_usd)
  })

  const reportColumns = [
    { label: 'Invoice #', key: 'invoice_number' }, { label: 'Customer', key: 'customerName' },
    { label: 'Date', key: 'invoice_date' }, { label: 'Due', key: 'due_date' },
    { label: 'Amount', key: 'amountLabel' }, { label: 'Amount (USD)', key: 'amountUsdLabel' }, { label: 'Status', key: 'status' },
  ]
  const reportRows = invoices.map(i => ({
    ...i, customerName: i.contact?.name || '—', amountLabel: `${i.amount} ${i.currency}`, amountUsdLabel: cp.fmt(i.amount_usd || 0),
  }))

  // Filtered invoices logic
  const filteredInvoices = useMemo(() => {
    return invoices.filter(i => {
      if (invoiceFilters.invoiceNumber && !String(i.invoice_number || '').toLowerCase().includes(invoiceFilters.invoiceNumber.toLowerCase().trim())) {
        return false
      }
      if (invoiceFilters.customer) {
        const cust = (i.contact?.name || i.customer_name_freeform || '').toLowerCase()
        if (!cust.includes(invoiceFilters.customer.toLowerCase().trim())) return false
      }
      if (invoiceFilters.date) {
        const d1 = String(i.invoice_date || '')
        const d2 = formatDate(i.invoice_date) || ''
        const q = invoiceFilters.date.toLowerCase().trim()
        if (!d1.toLowerCase().includes(q) && !d2.toLowerCase().includes(q)) return false
      }
      if (invoiceFilters.dueDate) {
        const d1 = String(i.due_date || '')
        const d2 = formatDate(i.due_date) || ''
        const q = invoiceFilters.dueDate.toLowerCase().trim()
        if (!d1.toLowerCase().includes(q) && !d2.toLowerCase().includes(q)) return false
      }
      if (invoiceFilters.amount) {
        const amtStr = `${i.amount || ''} ${i.currency || ''}`.toLowerCase()
        if (!amtStr.includes(invoiceFilters.amount.toLowerCase().trim())) return false
      }
      if (invoiceFilters.rate) {
        const rateVal = i.currency === 'USD' ? '1.00' : Number(i.fx_rate_locked || (i.amount / (i.amount_usd || 1))).toFixed(2)
        if (!rateVal.includes(invoiceFilters.rate.trim())) return false
      }
      if (invoiceFilters.amountUsd) {
        const usdVal = cp.fmt(i.amount_usd || 0).toLowerCase()
        const rawUsd = String(i.amount_usd ?? '').toLowerCase()
        const q = invoiceFilters.amountUsd.toLowerCase().trim()
        if (!usdVal.includes(q) && !rawUsd.includes(q)) return false
      }
      if (invoiceFilters.status) {
        if (invoiceFilters.status !== 'All' && (i.status || '').toLowerCase() !== invoiceFilters.status.toLowerCase().trim()) {
          return false
        }
      }
      return true
    })
  }, [invoices, invoiceFilters, cp])

  const filteredTotalUsd = useMemo(() => {
    return filteredInvoices.reduce((s, i) => s + Number(i.amount_usd || 0), 0)
  }, [filteredInvoices])

  const invoiceCurrencies = useMemo(() => {
    return [...new Set(filteredInvoices.map(i => i.currency).filter(Boolean))]
  }, [filteredInvoices])

  const singleInvoiceCurrency = invoiceCurrencies.length === 1 ? invoiceCurrencies[0] : null
  const filteredTotalNative = useMemo(() => {
    if (singleInvoiceCurrency) {
      return filteredInvoices.reduce((s, i) => s + Number(i.amount || 0), 0)
    }
    return null
  }, [filteredInvoices, singleInvoiceCurrency])

  const invoiceFooterRow = (
    <>
      <td colSpan={4} className="px-4 py-3 text-left font-bold text-slate-700 bg-slate-50">
        Total ({filteredInvoices.length} invoice{filteredInvoices.length === 1 ? '' : 's'})
      </td>
      <td className="px-4 py-3 text-left font-bold text-slate-900 bg-slate-50">
        {singleInvoiceCurrency ? (
          <span>{filteredTotalNative.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {singleInvoiceCurrency}</span>
        ) : (
          <span className="text-xs text-slate-500 font-normal">Mixed ({invoiceCurrencies.join(', ')})</span>
        )}
      </td>
      <td className="px-4 py-3 bg-slate-50"></td>
      <td className="px-4 py-3 text-left font-bold text-emerald-700 bg-slate-50">
        {cp.fmt(filteredTotalUsd)}
      </td>
      <td colSpan={2} className="px-4 py-3 bg-slate-50"></td>
    </>
  )

  const invoiceMobileFooter = (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between text-sm font-semibold">
      <span>Total ({filteredInvoices.length} invoices):</span>
      <div className="flex items-center gap-2">
        {singleInvoiceCurrency && (
          <span className="text-slate-900">
            {filteredTotalNative.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {singleInvoiceCurrency}
          </span>
        )}
        <span className="text-emerald-700">({cp.fmt(filteredTotalUsd)})</span>
      </div>
    </div>
  )

  const invoiceFilterRow = showInvoiceFilters ? (
    <>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={invNumRef}
            type="text"
            value={invoiceFilters.invoiceNumber}
            onChange={e => setInvoiceFilters(f => ({ ...f, invoiceNumber: e.target.value }))}
            placeholder="Filter #..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.invoiceNumber && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, invoiceNumber: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={customerRef}
            type="text"
            value={invoiceFilters.customer}
            onChange={e => setInvoiceFilters(f => ({ ...f, customer: e.target.value }))}
            placeholder="Filter customer..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.customer && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, customer: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={dateRef}
            type="text"
            value={invoiceFilters.date}
            onChange={e => setInvoiceFilters(f => ({ ...f, date: e.target.value }))}
            placeholder="Filter date..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.date && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, date: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={dueRef}
            type="text"
            value={invoiceFilters.dueDate}
            onChange={e => setInvoiceFilters(f => ({ ...f, dueDate: e.target.value }))}
            placeholder="Filter due..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.dueDate && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, dueDate: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={amountRef}
            type="text"
            value={invoiceFilters.amount}
            onChange={e => setInvoiceFilters(f => ({ ...f, amount: e.target.value }))}
            placeholder="Filter amount..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.amount && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, amount: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={rateRef}
            type="text"
            value={invoiceFilters.rate}
            onChange={e => setInvoiceFilters(f => ({ ...f, rate: e.target.value }))}
            placeholder="Rate..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.rate && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, rate: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={amountUsdRef}
            type="text"
            value={invoiceFilters.amountUsd}
            onChange={e => setInvoiceFilters(f => ({ ...f, amountUsd: e.target.value }))}
            placeholder="USD..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.amountUsd && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, amountUsd: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <select
          ref={statusRef}
          value={invoiceFilters.status}
          onChange={e => setInvoiceFilters(f => ({ ...f, status: e.target.value }))}
          className="w-full text-xs px-1.5 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
        >
          <option value="">All</option>
          <option value="Draft">Draft</option>
          <option value="Paid">Paid</option>
          <option value="Overdue">Overdue</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </td>
      <td className="px-2 py-1.5 text-center">
        {hasActiveInvoiceFilters && (
          <button
            onClick={clearInvoiceFilters}
            className="text-[11px] text-red-600 hover:underline font-medium whitespace-nowrap"
            title="Clear all filters"
          >
            Clear
          </button>
        )}
      </td>
    </>
  ) : null

  // Filtered receipts logic
  const filteredReceipts = useMemo(() => {
    return receipts.filter(r => {
      if (receiptFilters.receiptNumber && !String(r.receipt_number || '').toLowerCase().includes(receiptFilters.receiptNumber.toLowerCase().trim())) {
        return false
      }
      if (receiptFilters.invoiceNumber && !String(r.invoice?.invoice_number || '').toLowerCase().includes(receiptFilters.invoiceNumber.toLowerCase().trim())) {
        return false
      }
      if (receiptFilters.date) {
        const d1 = String(r.receipt_date || '')
        const d2 = formatDate(r.receipt_date) || ''
        const q = receiptFilters.date.toLowerCase().trim()
        if (!d1.toLowerCase().includes(q) && !d2.toLowerCase().includes(q)) return false
      }
      if (receiptFilters.customer) {
        const cust = (r.customer_name_freeform || r.contact?.name || '').toLowerCase()
        if (!cust.includes(receiptFilters.customer.toLowerCase().trim())) return false
      }
      if (receiptFilters.amount) {
        const amtStr = `${r.amount || ''} ${r.currency || ''}`.toLowerCase()
        if (!amtStr.includes(receiptFilters.amount.toLowerCase().trim())) return false
      }
      if (receiptFilters.rate) {
        const rateVal = r.currency === 'USD' ? '1.00' : Number(r.fx_rate_locked || (r.amount / (r.amount_usd || 1))).toFixed(2)
        if (!rateVal.includes(receiptFilters.rate.trim())) return false
      }
      if (receiptFilters.amountUsd) {
        const usdVal = cp.fmt(r.amount_usd || 0).toLowerCase()
        const rawUsd = String(r.amount_usd ?? '').toLowerCase()
        const q = receiptFilters.amountUsd.toLowerCase().trim()
        if (!usdVal.includes(q) && !rawUsd.includes(q)) return false
      }
      if (receiptFilters.method && !String(r.method || '').toLowerCase().includes(receiptFilters.method.toLowerCase().trim())) {
        return false
      }
      return true
    })
  }, [receipts, receiptFilters, cp])

  const filteredReceiptsTotalUsd = useMemo(() => {
    return filteredReceipts.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
  }, [filteredReceipts])

  const receiptCurrencies = useMemo(() => {
    return [...new Set(filteredReceipts.map(r => r.currency).filter(Boolean))]
  }, [filteredReceipts])

  const singleReceiptCurrency = receiptCurrencies.length === 1 ? receiptCurrencies[0] : null
  const filteredReceiptsTotalNative = useMemo(() => {
    if (singleReceiptCurrency) {
      return filteredReceipts.reduce((s, r) => s + Number(r.amount || 0), 0)
    }
    return null
  }, [filteredReceipts, singleReceiptCurrency])

  const receiptFooterRow = (
    <>
      <td colSpan={4} className="px-4 py-3 text-left font-bold text-slate-700 bg-slate-50">
        Total ({filteredReceipts.length} receipt{filteredReceipts.length === 1 ? '' : 's'})
      </td>
      <td className="px-4 py-3 text-left font-bold text-slate-900 bg-slate-50">
        {singleReceiptCurrency ? (
          <span>{filteredReceiptsTotalNative.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {singleReceiptCurrency}</span>
        ) : (
          <span className="text-xs text-slate-500 font-normal">Mixed ({receiptCurrencies.join(', ')})</span>
        )}
      </td>
      <td className="px-4 py-3 bg-slate-50"></td>
      <td className="px-4 py-3 text-left font-bold text-emerald-700 bg-slate-50">
        {cp.fmt(filteredReceiptsTotalUsd)}
      </td>
      <td colSpan={2} className="px-4 py-3 bg-slate-50"></td>
    </>
  )

  const receiptMobileFooter = (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between text-sm font-semibold">
      <span>Total ({filteredReceipts.length} receipts):</span>
      <div className="flex items-center gap-2">
        {singleReceiptCurrency && (
          <span className="text-slate-900">
            {filteredReceiptsTotalNative.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {singleReceiptCurrency}
          </span>
        )}
        <span className="text-emerald-700">({cp.fmt(filteredReceiptsTotalUsd)})</span>
      </div>
    </div>
  )

  const receiptFilterRow = showReceiptFilters ? (
    <>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recNumRef}
            type="text"
            value={receiptFilters.receiptNumber}
            onChange={e => setReceiptFilters(f => ({ ...f, receiptNumber: e.target.value }))}
            placeholder="Filter #..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.receiptNumber && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, receiptNumber: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recInvNumRef}
            type="text"
            value={receiptFilters.invoiceNumber}
            onChange={e => setReceiptFilters(f => ({ ...f, invoiceNumber: e.target.value }))}
            placeholder="Inv #..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.invoiceNumber && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, invoiceNumber: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recDateRef}
            type="text"
            value={receiptFilters.date}
            onChange={e => setReceiptFilters(f => ({ ...f, date: e.target.value }))}
            placeholder="Date..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.date && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, date: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recCustomerRef}
            type="text"
            value={receiptFilters.customer}
            onChange={e => setReceiptFilters(f => ({ ...f, customer: e.target.value }))}
            placeholder="Customer..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.customer && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, customer: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recAmountRef}
            type="text"
            value={receiptFilters.amount}
            onChange={e => setReceiptFilters(f => ({ ...f, amount: e.target.value }))}
            placeholder="Amount..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.amount && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, amount: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recRateRef}
            type="text"
            value={receiptFilters.rate}
            onChange={e => setReceiptFilters(f => ({ ...f, rate: e.target.value }))}
            placeholder="Rate..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.rate && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, rate: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recAmountUsdRef}
            type="text"
            value={receiptFilters.amountUsd}
            onChange={e => setReceiptFilters(f => ({ ...f, amountUsd: e.target.value }))}
            placeholder="USD..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.amountUsd && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, amountUsd: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <div className="relative">
          <input
            ref={recMethodRef}
            type="text"
            value={receiptFilters.method}
            onChange={e => setReceiptFilters(f => ({ ...f, method: e.target.value }))}
            placeholder="Method..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {receiptFilters.method && (
            <button
              onClick={() => setReceiptFilters(f => ({ ...f, method: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5 text-center">
        {hasActiveReceiptFilters && (
          <button
            onClick={clearReceiptFilters}
            className="text-[11px] text-red-600 hover:underline font-medium whitespace-nowrap"
            title="Clear all filters"
          >
            Clear
          </button>
        )}
      </td>
    </>
  ) : null

  if (!activeCompany) return null

  return (
    <div>
      <PageHeader
        title="Sales & Receipts"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              tab === 'invoices' ? (
                <button onClick={() => { setEditingInvoice(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                  <Plus size={16} /> New Invoice
                </button>
              ) : (
                <button onClick={() => { setEditingReceipt(null); setReceiptModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                  <Plus size={16} /> New Receipt
                </button>
              )
            )}
          </div>
        }
      />

      <div className="flex gap-2 mb-5">
        <button onClick={() => setTab('invoices')} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'invoices' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          Invoices ({invoices.length})
        </button>
        <button onClick={() => setTab('receipts')} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'receipts' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          Payment Receipts ({receipts.length})
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <StatBox label="Total Invoices" value={invoices.length} />
        <StatBox label="Collected" value={cp.fmt(collectedUsd)} tone="green" />
        <StatBox label="Pending" value={cp.fmt(pendingUsd)} tone="amber" />
        <StatBox label="Overdue" value={cp.fmt(0)} tone="red" />
      </div>

      {tab === 'invoices' ? (
        <>
          <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
            <h3 className="font-semibold text-slate-700 mb-4">Invoice Currency Summary</h3>
            <div className="space-y-3">
              {Object.entries(byCurrency).map(([code, v]) => (
                <div key={code} className="flex items-center justify-between text-sm">
                  <div>
                    <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium mr-2">{code}</span>
                    <span className="text-slate-500">{v.native.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} • {v.count} invoice(s)</span>
                  </div>
                  <span className="font-semibold text-slate-700">{cp.fmt(v.usd)}</span>
                </div>
              ))}
              <div className="flex items-center justify-between pt-3 border-t border-slate-100 font-bold text-emerald-700">
                <span>Grand Total ({cp.displayCurrency})</span>
                <span>{cp.fmt(totalUsd)}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-slate-700">
                Invoices ({filteredInvoices.length}{filteredInvoices.length !== invoices.length ? ` of ${invoices.length}` : ''})
              </span>
              {hasActiveInvoiceFilters && (
                <span className="inline-flex items-center gap-1 text-xs bg-navy-50 text-navy-700 font-medium px-2 py-0.5 rounded-full border border-navy-200">
                  <Filter size={11} /> {activeInvoiceFilterCount} filter{activeInvoiceFilterCount > 1 ? 's' : ''} applied
                </span>
              )}
              {invoiceFilters.customer && (
                <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                  Customer: <strong>{invoiceFilters.customer}</strong>
                  <button onClick={() => setInvoiceFilters(f => ({ ...f, customer: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
                </span>
              )}
              {invoiceFilters.invoiceNumber && (
                <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                  Invoice #: <strong>{invoiceFilters.invoiceNumber}</strong>
                  <button onClick={() => setInvoiceFilters(f => ({ ...f, invoiceNumber: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
                </span>
              )}
              {invoiceFilters.status && (
                <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                  Status: <strong>{invoiceFilters.status}</strong>
                  <button onClick={() => setInvoiceFilters(f => ({ ...f, status: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
                </span>
              )}
              {hasActiveInvoiceFilters && (
                <button onClick={clearInvoiceFilters} className="text-xs text-red-600 hover:underline font-medium ml-1">
                  Clear All
                </button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowInvoiceFilters(s => !s)}
                className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-colors ${
                  showInvoiceFilters ? 'bg-navy-50 border-navy-300 text-navy-700' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                }`}
                title="Toggle column filters row"
              >
                <Filter size={13} />
                <span>{showInvoiceFilters ? 'Hide Filters' : 'Filter Columns'}</span>
              </button>
            </div>
          </div>

          <DataTable
            filterRow={invoiceFilterRow}
            footerRow={invoiceFooterRow}
            footer={invoiceMobileFooter}
            emptyMessage={hasActiveInvoiceFilters ? 'No invoices match the selected filters.' : 'No invoices yet.'}
            columns={[
              {
                key: 'invoice_number',
                label: (
                  <div
                    onClick={() => focusColumnFilter(invNumRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Invoice #"
                  >
                    <span>Invoice #</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.invoiceNumber ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.invoiceNumber && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => <span className="font-medium text-slate-800">{r.invoice_number}</span>
              },
              {
                key: 'customer',
                label: (
                  <div
                    onClick={() => focusColumnFilter(customerRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Customer"
                  >
                    <span>Customer</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.customer ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.customer && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.contact?.name || r.customer_name_freeform || '—'
              },
              {
                key: 'invoice_date',
                label: (
                  <div
                    onClick={() => focusColumnFilter(dateRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Date"
                  >
                    <span>Date</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.date ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.date && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => <span className="whitespace-nowrap">{formatDate(r.invoice_date)}</span>
              },
              {
                key: 'due_date',
                label: (
                  <div
                    onClick={() => focusColumnFilter(dueRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Due Date"
                  >
                    <span>Due</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.dueDate ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.dueDate && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => <span className="whitespace-nowrap">{formatDate(r.due_date)}</span>
              },
              {
                key: 'amount',
                label: (
                  <div
                    onClick={() => focusColumnFilter(amountRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Amount"
                  >
                    <span>Amount</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.amount ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.amount && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => `${r.amount.toLocaleString()} ${r.currency}`
              },
              {
                key: 'rate',
                label: (
                  <div
                    onClick={() => focusColumnFilter(rateRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Rate"
                  >
                    <span>Rate</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.rate ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.rate && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.currency === 'USD' ? '1.00' : Number(r.fx_rate_locked || (r.amount / r.amount_usd)).toFixed(2)
              },
              {
                key: 'amount_usd',
                label: (
                  <div
                    onClick={() => focusColumnFilter(amountUsdRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Amount (USD)"
                  >
                    <span>Amount (USD)</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.amountUsd ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.amountUsd && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => cp.fmt(r.amount_usd)
              },
              {
                key: 'status',
                label: (
                  <div
                    onClick={() => focusColumnFilter(statusRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Status"
                  >
                    <span>Status</span>
                    <Search size={12} className={`transition-opacity ${invoiceFilters.status ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {invoiceFilters.status && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[r.status]}`}>{r.status}</span>
              },
              {
                key: 'actions', label: '', render: r => (
                  <div className="flex gap-2 justify-end md:justify-start">
                    <InvoiceDownloadMenu
                      type="sales" company={activeCompany} role={activeRole}
                      getData={async () => {
                        const { data: items } = await supabase.from('sales_invoice_items').select('*').eq('sales_invoice_id', r.id).order('sort_order')
                        const fullContact = contacts.find(c => c.id === r.contact_id) || r.contact
                        return { invoice: r, items: items || [], contact: fullContact }
                      }}
                    />
                    {can(['owner', 'admin', 'accountant']) && (
                      <>
                        <button onClick={() => { setEditingInvoice(r); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
                        <button onClick={() => handleDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
                      </>
                    )}
                  </div>
                )
              },
            ]}
            rows={filteredInvoices}
          />
        </>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-slate-700">
                Payment Receipts ({filteredReceipts.length}{filteredReceipts.length !== receipts.length ? ` of ${receipts.length}` : ''})
              </span>
              {hasActiveReceiptFilters && (
                <span className="inline-flex items-center gap-1 text-xs bg-navy-50 text-navy-700 font-medium px-2 py-0.5 rounded-full border border-navy-200">
                  <Filter size={11} /> {activeReceiptFilterCount} filter{activeReceiptFilterCount > 1 ? 's' : ''} applied
                </span>
              )}
              {receiptFilters.customer && (
                <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                  Customer: <strong>{receiptFilters.customer}</strong>
                  <button onClick={() => setReceiptFilters(f => ({ ...f, customer: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
                </span>
              )}
              {receiptFilters.receiptNumber && (
                <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                  Receipt #: <strong>{receiptFilters.receiptNumber}</strong>
                  <button onClick={() => setReceiptFilters(f => ({ ...f, receiptNumber: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
                </span>
              )}
              {hasActiveReceiptFilters && (
                <button onClick={clearReceiptFilters} className="text-xs text-red-600 hover:underline font-medium ml-1">
                  Clear All
                </button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowReceiptFilters(s => !s)}
                className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-colors ${
                  showReceiptFilters ? 'bg-navy-50 border-navy-300 text-navy-700' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                }`}
                title="Toggle column filters row"
              >
                <Filter size={13} />
                <span>{showReceiptFilters ? 'Hide Filters' : 'Filter Columns'}</span>
              </button>
            </div>
          </div>

          <DataTable
            filterRow={receiptFilterRow}
            footerRow={receiptFooterRow}
            footer={receiptMobileFooter}
            emptyMessage={hasActiveReceiptFilters ? 'No receipts match the selected filters.' : 'No receipts yet.'}
            columns={[
              {
                key: 'receipt_number',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recNumRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Receipt #"
                  >
                    <span>Receipt #</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.receiptNumber ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.receiptNumber && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.receipt_number || '—'
              },
              {
                key: 'invoice',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recInvNumRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Invoice #"
                  >
                    <span>Invoice #</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.invoiceNumber ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.invoiceNumber && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.invoice?.invoice_number || '—'
              },
              {
                key: 'receipt_date',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recDateRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Date"
                  >
                    <span>Date</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.date ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.date && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => <span className="whitespace-nowrap">{formatDate(r.receipt_date)}</span>
              },
              {
                key: 'customer',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recCustomerRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Customer"
                  >
                    <span>Customer</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.customer ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.customer && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.customer_name_freeform || r.contact?.name || '—'
              },
              {
                key: 'amount',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recAmountRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Amount"
                  >
                    <span>Amount</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.amount ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.amount && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => `${r.amount.toLocaleString()} ${r.currency}`
              },
              {
                key: 'rate',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recRateRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Rate"
                  >
                    <span>Rate</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.rate ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.rate && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.currency === 'USD' ? '1.00' : Number(r.fx_rate_locked || (r.amount / r.amount_usd)).toFixed(2)
              },
              {
                key: 'amount_usd',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recAmountUsdRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Amount (USD)"
                  >
                    <span>Amount (USD)</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.amountUsd ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.amountUsd && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => cp.fmt(r.amount_usd)
              },
              {
                key: 'method',
                label: (
                  <div
                    onClick={() => focusReceiptFilter(recMethodRef)}
                    className="flex items-center gap-1.5 cursor-pointer select-none group"
                    title="Click to filter by Method"
                  >
                    <span>Method</span>
                    <Search size={12} className={`transition-opacity ${receiptFilters.method ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                    {receiptFilters.method && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
                  </div>
                ),
                render: r => r.method || '—'
              },
              {
                key: 'actions', label: '', render: r => (
                  <div className="flex gap-2 justify-end md:justify-start">
                    <InvoiceDownloadMenu
                      type="receipt" company={activeCompany} role={activeRole}
                      getData={async () => {
                        const fullContact = contacts.find(c => c.id === r.contact_id) || r.contact
                        return { invoice: r, items: [{ description: 'Payment Received', amount: r.amount }], contact: fullContact }
                      }}
                    />
                    {can(['owner', 'admin', 'accountant']) && (
                      <>
                        <button onClick={() => { setEditingReceipt(r); setReceiptModalOpen(true) }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
                        <button onClick={() => handleReceiptDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
                      </>
                    )}
                  </div>
                )
              }
            ]}
            rows={filteredReceipts}
          />
          <ReceiptCurrencySummary receipts={receipts} />
        </>
      )}

      {modalOpen && (
        <SalesInvoiceFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          company={activeCompany}
          contacts={contacts}
          invoice={editingInvoice}
          onClose={() => setModalOpen(false)}
          onSaved={loadData}
        />
      )}

            {receiptModalOpen && (
        <PaymentReceiptFormModal
          open={receiptModalOpen}
          onClose={() => setReceiptModalOpen(false)}
          companyId={activeCompany?.id}
          product={activeProduct}
          initialData={editingReceipt}
          onSuccess={loadData}
          invoices={invoices}
          contacts={contacts}
        />
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Sales & Receipts"
          fields={[
            { type: 'radio', key: 'dataType', label: 'Include', options: ['Invoices', 'Payment Receipts', 'Both'], default: 'Both' },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateSalesReport}
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
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className={`text-xl sm:text-2xl font-bold ${tones[tone]}`}>{value}</div>
    </div>
  )
}
