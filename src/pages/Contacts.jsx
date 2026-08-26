import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import PageHeader from '../components/PageHeader'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import ContactFormModal from '../components/ContactFormModal'
import ContactDetailModal from '../components/ContactDetailModal'

export default function Contacts() {
  const { activeCompany, can, activeRole } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [tab, setTab] = useState('customers')
  const [customers, setCustomers] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [salesInvoices, setSalesInvoices] = useState([])
  const [purchaseInvoices, setPurchaseInvoices] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingContact, setEditingContact] = useState(null)
  const [viewingContact, setViewingContact] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany])

  async function loadAll() {
    const [{ data: contacts }, { data: si }, { data: pi }] = await Promise.all([
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).order('name'),
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id),
    ])
    setCustomers((contacts || []).filter(c => c.type === 'customer'))
    setSuppliers((contacts || []).filter(c => c.type === 'supplier'))
    setSalesInvoices(si || [])
    setPurchaseInvoices(pi || [])
  }

  async function handleDelete(contact) {
    if (!confirm(`Delete ${contact.name}? This cannot be undone.`)) return
    const { error } = await supabase.from('contacts').delete().eq('id', contact.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAll()
  }


  async function generateContactsReport(selections, format) {
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const sections = []
    const wantCustomers = selections.contactType === 'All' || selections.contactType === 'Customers'
    const wantSuppliers = selections.contactType === 'All' || selections.contactType === 'Suppliers'

    if (wantCustomers) {
      sections.push({
        heading: 'Customers',
        columns: ['Name', 'Email', 'Phone', 'Invoices', `Total (${selections.currency})`],
        rows: customers.map(c => {
          const invs = invoicesFor(c.id, true)
          return [c.name, c.email || '—', c.phone || '—', invs.length, fmt(invs.reduce((s, i) => s + Number(i.amount_usd), 0))]
        }),
      })
    }
    if (wantSuppliers) {
      sections.push({
        heading: 'Suppliers',
        columns: ['Name', 'Email', 'Phone', 'Invoices', `Total (${selections.currency})`],
        rows: suppliers.map(c => {
          const invs = invoicesFor(c.id, false)
          return [c.name, c.email || '—', c.phone || '—', invs.length, fmt(invs.reduce((s, i) => s + Number(i.amount_usd), 0))]
        }),
      })
    }

    const title = 'Customers & Suppliers'
    const subtitle = `${activeCompany.name} • ${selections.contactType} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'contacts_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'contacts_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'contacts_report' })
  }

  if (!activeCompany) return null

  const totalCustomerBills = salesInvoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const totalSupplierBills = purchaseInvoices.reduce((s, i) => s + Number(i.amount_usd), 0)

  const list = tab === 'customers' ? customers : suppliers
  const invoicesFor = (contactId, isCustomer) => {
    const source = isCustomer ? salesInvoices : purchaseInvoices
    return source.filter(i => i.contact_id === contactId)
  }

  const reportColumns = [
    { label: 'Name', key: 'name' }, { label: 'Type', key: 'type' }, { label: 'Email', key: 'email' },
    { label: 'Phone', key: 'phone' }, { label: 'Invoices', key: 'invoiceCount' }, { label: 'Total (USD)', key: 'total' },
  ]
  const reportRows = list.map(c => {
    const invs = invoicesFor(c.id, tab === 'customers')
    return { ...c, invoiceCount: invs.length, total: invs.reduce((s, i) => s + Number(i.amount_usd), 0).toFixed(2) }
  })

  return (
    <div>
      <PageHeader
        title="Customers & Suppliers"
        subtitle="Manage all your contacts in one place"
        currencyProps={cp.currencyProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button onClick={() => { setEditingContact(null); setTab('customers'); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={16} /> New Customer
                </button>
                <button onClick={() => { setEditingContact(null); setTab('suppliers'); setModalOpen(true) }} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={16} /> New Supplier
                </button>
              </>
            )}
          </div>
        }
      />

      <div className="grid sm:grid-cols-2 gap-4 mb-6">
        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-5">
          <div className="text-sm text-emerald-700 font-medium mb-1">Total Customer Bills Raised</div>
          <div className="text-3xl font-bold text-slate-800">{cp.fmt(totalCustomerBills)}</div>
          <div className="text-xs text-slate-500 mt-1">{customers.length} customer(s) • {salesInvoices.length} invoices</div>
        </div>
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">
          <div className="text-sm text-blue-700 font-medium mb-1">Total Supplier Bills Received</div>
          <div className="text-3xl font-bold text-slate-800">{cp.fmt(totalSupplierBills)}</div>
          <div className="text-xs text-slate-500 mt-1">{suppliers.length} supplier(s) • {purchaseInvoices.length} invoices</div>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => setTab('customers')} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'customers' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          Customers ({customers.length})
        </button>
        <button onClick={() => setTab('suppliers')} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'suppliers' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          Suppliers ({suppliers.length})
        </button>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {list.map(c => {
          const invs = invoicesFor(c.id, tab === 'customers')
          const total = invs.reduce((s, i) => s + Number(i.amount_usd), 0)
          return (
            <div key={c.id} onClick={() => setViewingContact(c)} className="bg-white rounded-xl border border-slate-200 p-4 cursor-pointer hover:border-navy-300 transition-colors">
              <div className="flex items-start justify-between mb-1">
                <h3 className="font-semibold text-slate-800 text-sm leading-snug pr-2">{c.name}</h3>
                <span className={`shrink-0 text-[11px] font-medium px-2 py-0.5 rounded-full border ${tab === 'customers' ? 'text-emerald-700 border-emerald-200' : 'text-blue-700 border-blue-200'}`}>
                  {tab === 'customers' ? 'Customer' : 'Supplier'}
                </span>
              </div>
              {c.email && <div className="text-xs text-slate-400">{c.email}</div>}
              {c.phone && <div className="text-xs text-slate-400">{c.phone}</div>}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
                <span className="text-xs text-slate-400">{invs.length} invoices</span>
                <span className="font-semibold text-slate-700">{cp.fmt(total)}</span>
              </div>
              {can(['owner', 'admin', 'accountant']) && (
                <div className="flex gap-2 mt-3" onClick={e => e.stopPropagation()}>
                  <button onClick={() => { setEditingContact(c); setModalOpen(true) }} className="flex-1 flex items-center justify-center gap-1 border border-slate-200 rounded-lg py-1.5 text-xs font-medium text-slate-600"><Pencil size={13} /> Edit</button>
                  <button onClick={() => handleDelete(c)} className="border border-red-200 text-red-500 rounded-lg px-3"><Trash2 size={13} /></button>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {viewingContact && (
        <ContactDetailModal
          contact={viewingContact}
          company={activeCompany}
          role={activeRole}
          fmt={cp.fmt}
          onClose={() => setViewingContact(null)}
          onEdit={(c) => { setViewingContact(null); setEditingContact(c); setModalOpen(true) }}
        />
      )}

      {modalOpen && (
        <ContactFormModal
          companyId={activeCompany.id}
          contact={editingContact}
          defaultType={tab === 'customers' ? 'customer' : 'supplier'}
          onClose={() => setModalOpen(false)}
          onSaved={loadAll}
        />
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Customers & Suppliers"
          fields={[
            { type: 'radio', key: 'contactType', label: 'Show', options: ['All', 'Customers', 'Suppliers'], default: 'All' },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
          ]}
          onGenerate={generateContactsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
