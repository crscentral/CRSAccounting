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
import PurchaseInvoiceFormModal from '../components/PurchaseInvoiceFormModal'

const STATUS_COLORS = {
  Draft: 'bg-slate-100 text-slate-600',
  Paid: 'bg-emerald-100 text-emerald-700',
  Overdue: 'bg-red-100 text-red-700',
  Cancelled: 'bg-slate-100 text-slate-400',
}

export default function PurchaseInvoices() {
  const { activeCompany, activeProduct, can, activeRole } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [invoices, setInvoices] = useState([])
  const [contacts, setContacts] = useState([])
  const [accounts, setAccounts] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingInvoice, setEditingInvoice] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  // Column filter states for Purchase Invoices
  const [invoiceFilters, setInvoiceFilters] = useState({
    invoiceNumber: '',
    date: '',
    supplier: '',
    currency: '',
    amount: '',
    amountUsd: '',
    status: '',
  })
  const [showInvoiceFilters, setShowInvoiceFilters] = useState(true)

  const invNumRef = useRef(null)
  const dateRef = useRef(null)
  const supplierRef = useRef(null)
  const currencyRef = useRef(null)
  const amountRef = useRef(null)
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
      date: '',
      supplier: '',
      currency: '',
      amount: '',
      amountUsd: '',
      status: '',
    })
  }

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadData() {
    const [{ data: inv }, { data: con }, { data: acc }] = await Promise.all([
      supabase.from('purchase_invoices').select('*, contact:contacts(name, email, phone, address, tax_id)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id),
      supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
    ])
    setInvoices(inv || [])
    setContacts(con || [])
    setAccounts(acc || [])
  }

  async function handleDelete(inv) {
    if (!confirm(`Delete invoice ${inv.invoice_number}? This cannot be undone.`)) return
    const { error } = await supabase.from('purchase_invoices').delete().eq('id', inv.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadData()
  }




  async function generatePurchaseReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const { data: inv } = await supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to).order('invoice_date', { ascending: false })
    const sections = [{
      heading: 'Purchase Invoices',
      columns: ['Invoice #', 'Date', 'Supplier', 'Currency', 'Amount', `Amount (${selections.currency})`, 'Status'],
      rows: (inv || []).map(i => [i.invoice_number, i.invoice_date, i.contact?.name || i.supplier_name_freeform || '—', i.currency, `${i.amount} ${i.currency}`, fmt(i.amount_usd), i.status]),
    }]

    const title = 'Purchase Invoices'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') await exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'purchase_invoices_report' , logoUrl: activeCompany?.logo_url})
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'purchase_invoices_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'purchase_invoices_report' , logoUrl: activeCompany?.logo_url})
  }

  if (!activeCompany) return null

  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const pendingUsd = invoices.reduce((s, i) => s + (i.status === 'Paid' ? 0 : Number(i.amount_usd)), 0)
  const paidUsd = totalUsd - pendingUsd

  const byCurrency = {}
  invoices.forEach(i => {
    byCurrency[i.currency] = byCurrency[i.currency] || { count: 0, native: 0, usd: 0 }
    byCurrency[i.currency].count += 1
    byCurrency[i.currency].native += Number(i.amount)
    byCurrency[i.currency].usd += Number(i.amount_usd)
  })

  const reportColumns = [
    { label: 'Invoice #', key: 'invoice_number' }, { label: 'Date', key: 'invoice_date' },
    { label: 'Supplier', key: 'supplierName' }, { label: 'Currency', key: 'currency' },
    { label: 'Amount', key: 'amountLabel' }, { label: `Amount (${cp.displayCurrency})`, key: 'amountUsdLabel' }, { label: 'Status', key: 'status' },
  ]
  const reportRows = invoices.map(i => ({
    ...i, supplierName: i.contact?.name || i.supplier_name_freeform || '—', amountLabel: `${i.amount} ${i.currency}`, amountUsdLabel: cp.fmt(i.amount_usd),
  }))

  const filteredInvoices = useMemo(() => {
    return invoices.filter(i => {
      if (invoiceFilters.invoiceNumber && !String(i.invoice_number || '').toLowerCase().includes(invoiceFilters.invoiceNumber.toLowerCase().trim())) {
        return false
      }
      if (invoiceFilters.date) {
        const d1 = String(i.invoice_date || '')
        const d2 = formatDate(i.invoice_date) || ''
        const q = invoiceFilters.date.toLowerCase().trim()
        if (!d1.toLowerCase().includes(q) && !d2.toLowerCase().includes(q)) return false
      }
      if (invoiceFilters.supplier) {
        const supp = (i.contact?.name || i.supplier_name_freeform || '').toLowerCase()
        if (!supp.includes(invoiceFilters.supplier.toLowerCase().trim())) return false
      }
      if (invoiceFilters.currency) {
        if (invoiceFilters.currency !== 'All' && String(i.currency || '').toLowerCase() !== invoiceFilters.currency.toLowerCase().trim()) {
          return false
        }
      }
      if (invoiceFilters.amount) {
        const amtStr = `${i.amount || ''} ${i.currency || ''}`.toLowerCase()
        if (!amtStr.includes(invoiceFilters.amount.toLowerCase().trim())) return false
      }
      if (invoiceFilters.amountUsd) {
        const usdVal = cp.fmt(i.amount_usd).toLowerCase()
        const rawUsd = String(i.amount_usd || '').toLowerCase()
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

  const allCurrencies = useMemo(() => {
    return [...new Set(invoices.map(i => i.currency).filter(Boolean))]
  }, [invoices])

  const filteredTotalUsd = useMemo(() => {
    return filteredInvoices.reduce((s, i) => s + Number(i.amount_usd || 0), 0)
  }, [filteredInvoices])

  const invoiceCurrencies = useMemo(() => {
    return [...new Set(filteredInvoices.map(i => i.currency).filter(Boolean))]
  }, [filteredInvoices])

  const singleCurrency = invoiceCurrencies.length === 1 ? invoiceCurrencies[0] : null
  const totalNative = useMemo(() => {
    if (singleCurrency) {
      return filteredInvoices.reduce((s, i) => s + Number(i.amount || 0), 0)
    }
    return null
  }, [filteredInvoices, singleCurrency])

  const purchaseFooterRow = (
    <>
      <td colSpan={3} className="px-4 py-3 text-left font-bold text-slate-700 bg-slate-50">
        Total ({filteredInvoices.length} invoice{filteredInvoices.length === 1 ? '' : 's'})
      </td>
      <td className="px-4 py-3 text-left font-bold text-slate-700 bg-slate-50">
        {singleCurrency || (invoiceCurrencies.length > 0 ? 'Multiple' : '—')}
      </td>
      <td className="px-4 py-3 text-left font-bold text-slate-900 bg-slate-50">
        {singleCurrency ? (
          <span>{totalNative.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {singleCurrency}</span>
        ) : (
          <span className="text-xs text-slate-500 font-normal">Mixed ({invoiceCurrencies.join(', ')})</span>
        )}
      </td>
      <td className="px-4 py-3 text-left font-bold text-emerald-700 bg-slate-50">
        {cp.fmt(filteredTotalUsd)}
      </td>
      <td colSpan={2} className="px-4 py-3 bg-slate-50"></td>
    </>
  )

  const purchaseMobileFooter = (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between text-sm font-semibold">
      <span>Total ({filteredInvoices.length} invoices):</span>
      <div className="flex items-center gap-2">
        {singleCurrency && (
          <span className="text-slate-900">
            {totalNative.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {singleCurrency}
          </span>
        )}
        <span className="text-emerald-700">({cp.fmt(filteredTotalUsd)})</span>
      </div>
    </div>
  )

  const purchaseFilterRow = showInvoiceFilters ? (
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
            ref={supplierRef}
            type="text"
            value={invoiceFilters.supplier}
            onChange={e => setInvoiceFilters(f => ({ ...f, supplier: e.target.value }))}
            placeholder="Filter supplier..."
            className="w-full text-xs px-2 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
          />
          {invoiceFilters.supplier && (
            <button
              onClick={() => setInvoiceFilters(f => ({ ...f, supplier: '' }))}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X size={11} />
            </button>
          )}
        </div>
      </td>
      <td className="px-2 py-1.5">
        <select
          ref={currencyRef}
          value={invoiceFilters.currency}
          onChange={e => setInvoiceFilters(f => ({ ...f, currency: e.target.value }))}
          className="w-full text-xs px-1.5 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-navy-500 font-normal"
        >
          <option value="">All</option>
          {allCurrencies.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
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

  return (
    <div>
      <PageHeader
        title="Purchase Invoices"
        subtitle={`${activeCompany.name} • ${invoices.length} invoices`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingInvoice(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                <Plus size={16} /> New Purchase
              </button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <StatBox label="Total Invoices" value={invoices.length} />
        <StatBox label="Total Paid" value={cp.fmt(paidUsd)} tone="green" />
        <StatBox label="Pending" value={cp.fmt(pendingUsd)} tone="amber" />
        <StatBox label="Overdue" value={cp.fmt(0)} tone="red" />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-4">Purchase Currency Summary ({cp.displayCurrency} Consolidated)</h3>
        <div className="space-y-3">
          {Object.entries(byCurrency).map(([code, v]) => (
            <div key={code} className="flex items-center justify-between text-sm flex-wrap gap-1">
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
          {invoiceFilters.supplier && (
            <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
              Supplier: <strong>{invoiceFilters.supplier}</strong>
              <button onClick={() => setInvoiceFilters(f => ({ ...f, supplier: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
            </span>
          )}
          {invoiceFilters.invoiceNumber && (
            <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
              Invoice #: <strong>{invoiceFilters.invoiceNumber}</strong>
              <button onClick={() => setInvoiceFilters(f => ({ ...f, invoiceNumber: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
            </span>
          )}
          {invoiceFilters.currency && (
            <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
              Currency: <strong>{invoiceFilters.currency}</strong>
              <button onClick={() => setInvoiceFilters(f => ({ ...f, currency: '' }))} className="hover:text-red-600 ml-0.5"><X size={12} /></button>
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
        filterRow={purchaseFilterRow}
        footerRow={purchaseFooterRow}
        footer={purchaseMobileFooter}
        emptyMessage={hasActiveInvoiceFilters ? 'No purchase invoices match the selected filters.' : 'No purchase invoices yet.'}
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
            key: 'date',
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
            key: 'supplier',
            label: (
              <div
                onClick={() => focusColumnFilter(supplierRef)}
                className="flex items-center gap-1.5 cursor-pointer select-none group"
                title="Click to filter by Supplier"
              >
                <span>Supplier</span>
                <Search size={12} className={`transition-opacity ${invoiceFilters.supplier ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                {invoiceFilters.supplier && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
              </div>
            ),
            render: r => r.contact?.name || r.supplier_name_freeform || '—'
          },
          {
            key: 'currency',
            label: (
              <div
                onClick={() => focusColumnFilter(currencyRef)}
                className="flex items-center gap-1.5 cursor-pointer select-none group"
                title="Click to filter by Currency"
              >
                <span>Currency</span>
                <Search size={12} className={`transition-opacity ${invoiceFilters.currency ? 'text-navy-600 opacity-100' : 'text-slate-400 opacity-0 group-hover:opacity-70'}`} />
                {invoiceFilters.currency && <span className="w-1.5 h-1.5 rounded-full bg-navy-600" />}
              </div>
            ),
            render: r => r.currency
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
            key: 'amount_usd',
            label: (
              <div
                onClick={() => focusColumnFilter(amountUsdRef)}
                className="flex items-center gap-1.5 cursor-pointer select-none group"
                title={`Click to filter by Amount (${cp.displayCurrency})`}
              >
                <span>Amount ({cp.displayCurrency})</span>
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
                      type="purchase" company={activeCompany} role={activeRole}
                      getData={async () => {
                        const { data: items } = await supabase.from('purchase_invoice_items').select('*').eq('purchase_invoice_id', r.id).order('sort_order')
                        let accName = ''
                        if (r.account_id) {
                          const { data: acc } = await supabase.from('accounts').select('name').eq('id', r.account_id).single()
                          accName = acc?.name || ''
                        }
                        return { invoice: { ...r, expense_account_name: accName }, items: items || [], contact: r.contact }
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

      {modalOpen && (
        <PurchaseInvoiceFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          company={activeCompany}
          contacts={contacts}
          accounts={accounts}
          invoice={editingInvoice}
          onClose={() => setModalOpen(false)}
          onSaved={loadData}
        />
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Purchase Invoices"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generatePurchaseReport}
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
