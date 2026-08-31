import { useEffect, useState } from 'react'
import { Plus, Eye, Pencil, Trash2, Download } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { resolveReportPeriod } from '../lib/fiscalYear'
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

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct])

  async function loadData() {
    const [{ data: inv }, { data: con }, { data: acc }] = await Promise.all([
      supabase.from('purchase_invoices').select('*, contact:contacts(name, email, phone, address, tax_id)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }),
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
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'purchase_invoices_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'purchase_invoices_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'purchase_invoices_report' })
  }

  if (!activeCompany) return null

  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const paidUsd = invoices.filter(i => i.status === 'Paid').reduce((s, i) => s + Number(i.amount_usd), 0)
  const pendingUsd = invoices.filter(i => i.status !== 'Paid').reduce((s, i) => s + Number(i.amount_usd), 0)

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
                <span className="text-slate-500">{v.native.toLocaleString()} • {v.count} invoice(s)</span>
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

      <DataTable
        columns={[
          { key: 'invoice_number', label: 'Invoice #' },
          { key: 'date', label: 'Date', render: r => r.invoice_date },
          { key: 'supplier', label: 'Supplier', render: r => r.contact?.name || r.supplier_name_freeform || '—' },
          { key: 'currency', label: 'Currency' },
          { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
          { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
          { key: 'status', label: 'Status', render: r => <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[r.status]}`}>{r.status}</span> },
          {
            key: 'actions', label: '', render: r => (
              <div className="flex gap-2 justify-end md:justify-start">
                <InvoiceDownloadMenu
                      type="purchase" company={activeCompany} role={activeRole}
                      getData={async () => {
                        const { data: items } = await supabase.from('purchase_invoice_items').select('*').eq('purchase_invoice_id', r.id).order('sort_order')
                        return { invoice: r, items: items || [], contact: r.contact }
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
        rows={invoices}
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
