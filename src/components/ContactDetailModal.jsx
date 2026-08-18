import { useEffect, useState } from 'react'
import { X, Mail, Phone, MapPin, Hash, Pencil } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { getMTDRange, getYTDRange } from '../lib/fiscalYear'
import InvoiceDownloadMenu from './InvoiceDownloadMenu'

export default function ContactDetailModal({ contact, company, role, onClose, onEdit, fmt }) {
  const [invoices, setInvoices] = useState([])
  const isCustomer = contact.type === 'customer'

  useEffect(() => { loadInvoices() }, [contact])

  async function loadInvoices() {
    const table = isCustomer ? 'sales_invoices' : 'purchase_invoices'
    const { data } = await supabase.from(table).select('*').eq('contact_id', contact.id).order('invoice_date', { ascending: false })
    setInvoices(data || [])
  }



  const mtd = getMTDRange()
  const ytd = getYTDRange(company?.fiscal_year_start_month || 1)
  const sum = (arr) => arr.reduce((s, i) => s + Number(i.amount_usd), 0)
  const mtdTotal = sum(invoices.filter(i => i.invoice_date >= mtd.from && i.invoice_date <= mtd.to))
  const ytdTotal = sum(invoices.filter(i => i.invoice_date >= ytd.from && i.invoice_date <= ytd.to))
  const allTimeTotal = sum(invoices)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-xl w-full max-w-2xl max-h-[92vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 sticky top-0 bg-white z-10">
          <div>
            <h2 className="font-semibold text-slate-800">{contact.name}</h2>
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${isCustomer ? 'text-emerald-700 border-emerald-200' : 'text-blue-700 border-blue-200'}`}>
              {isCustomer ? 'Customer' : 'Supplier'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => onEdit(contact)} className="text-slate-400 hover:text-navy-600"><Pencil size={18} /></button>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
          </div>
        </div>

        <div className="p-5 space-y-5">
          <div className="grid sm:grid-cols-2 gap-3 text-sm">
            {contact.email && <div className="flex items-center gap-2 text-slate-600"><Mail size={14} className="text-slate-400" /> {contact.email}</div>}
            {contact.phone && <div className="flex items-center gap-2 text-slate-600"><Phone size={14} className="text-slate-400" /> {contact.phone}</div>}
            {contact.address && <div className="flex items-center gap-2 text-slate-600 sm:col-span-2"><MapPin size={14} className="text-slate-400" /> {contact.address}</div>}
            {contact.tax_id && <div className="flex items-center gap-2 text-slate-600"><Hash size={14} className="text-slate-400" /> Tax ID: {contact.tax_id}</div>}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-2">{isCustomer ? 'Bills Raised' : 'Bills Received'}</h3>
            <div className="grid grid-cols-3 gap-3">
              <StatBox label="This Month" value={fmt(mtdTotal)} />
              <StatBox label="YTD" value={fmt(ytdTotal)} />
              <StatBox label="All Time" value={fmt(allTimeTotal)} />
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Invoice History ({invoices.length})</h3>
            <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 max-h-72 overflow-y-auto">
              {invoices.length === 0 && <p className="text-sm text-slate-400 p-4 text-center">No invoices yet.</p>}
              {invoices.map(inv => (
                <div key={inv.id} className="flex items-center justify-between px-3 py-2.5 text-sm">
                  <div>
                    <div className="font-medium text-slate-700">{inv.invoice_number}</div>
                    <div className="text-xs text-slate-400">{inv.invoice_date} • {inv.status}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-slate-700">{inv.amount} {inv.currency}</span>
                    <InvoiceDownloadMenu
                      type={isCustomer ? 'sales' : 'purchase'} company={company} role={role}
                      getData={async () => {
                        const itemsTable = isCustomer ? 'sales_invoice_items' : 'purchase_invoice_items'
                        const fkCol = isCustomer ? 'sales_invoice_id' : 'purchase_invoice_id'
                        const { data: items } = await supabase.from(itemsTable).select('*').eq(fkCol, inv.id).order('sort_order')
                        return { invoice: inv, items: items || [], contact }
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value }) {
  return (
    <div className="bg-slate-50 rounded-lg p-3 text-center">
      <div className="text-[11px] text-slate-400 mb-1">{label}</div>
      <div className="font-bold text-slate-800 text-sm">{value}</div>
    </div>
  )
}
