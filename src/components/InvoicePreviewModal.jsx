import { ArrowLeft, X } from 'lucide-react'
import InvoiceDownloadMenu from './InvoiceDownloadMenu'

export default function InvoicePreviewModal({ type, invoice, items, company, contactDisplay, role, onBack, onClose }) {
  const isSales = type === 'sales'
  const lineTotals = items.map(it => Number(it.line_total || 0))
  const subtotal = items.reduce((s, it) => s + Number(it.qty || 0) * Number(it.unit_price || 0), 0)
  const taxAmount = lineTotals.reduce((s, t, i) => s + (t - Number(items[i].qty || 0) * Number(items[i].unit_price || 0)), 0)

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-2 sm:p-4 bg-black/50">
      <div className="bg-white rounded-xl w-full max-w-3xl max-h-[95vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 sticky top-0 bg-navy-800 text-white rounded-t-xl z-20">
          <div className="flex items-center gap-3">
            <button onClick={onBack} className="flex items-center gap-1 text-sm text-white/80 hover:text-white"><ArrowLeft size={16} /> Back to edit</button>
          </div>
          <div className="flex items-center gap-2">
            <div className="bg-gold-500 hover:bg-gold-600 text-navy-900 text-sm font-semibold rounded-lg">
              <InvoiceDownloadMenu
                type={type} company={company} role={role}
                triggerClassName="flex items-center gap-1.5 px-3 py-1.5 text-navy-900 rounded-lg"
                getData={async () => ({ invoice, items, contact: { name: contactDisplay } })}
              />
            </div>
            <button onClick={onClose} className="text-white/70 hover:text-white"><X size={20} /></button>
          </div>
        </div>

        <div className="p-6 sm:p-10">
          <div className="flex items-start justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-800">Invoice</h1>
              <span className={`inline-block mt-2 text-xs font-semibold px-2 py-0.5 rounded ${invoice.status === 'Paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                {invoice.status || 'Draft'}
              </span>
            </div>
            {company?.logo_url && <img src={company.logo_url} alt="" className="h-12 object-contain" />}
          </div>

          <div className="grid sm:grid-cols-3 gap-6 mb-8 text-sm">
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">{isSales ? 'From' : 'Our Company'}</div>
              <div className="font-semibold text-slate-800">{company?.name}</div>
              <div className="text-slate-500">{company?.legal_name}</div>
              <div className="text-slate-500">{[company?.address, company?.city, company?.country].filter(Boolean).join(', ')}</div>
              <div className="text-slate-500">{company?.email}</div>
              {company?.tax_id && <div className="text-slate-500">Tax ID: {company.tax_id}</div>}
            </div>
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">{isSales ? 'Bill To' : 'Supplier'}</div>
              <div className="font-semibold text-slate-800">{contactDisplay || '—'}</div>
              <div className="text-slate-500">{invoice.customer_address || invoice.supplier_address}</div>
              <div className="text-slate-500">{invoice.customer_email || invoice.supplier_email}</div>
              <div className="text-slate-500">{invoice.customer_phone || invoice.supplier_phone}</div>
              {invoice.supplier_gstin && <div className="text-slate-500">GSTIN: {invoice.supplier_gstin}</div>}
            </div>
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">Document</div>
              <div className="font-semibold text-slate-800">{invoice.invoice_number}</div>
              <div className="text-slate-500">Issue: {invoice.invoice_date}</div>
              <div className="text-slate-500">Due: {invoice.due_date || '—'}</div>
              <div className="text-slate-500">Currency: {invoice.currency}</div>
            </div>
          </div>

          {isSales && invoice.is_export_lut && (
            <div className="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 text-xs text-amber-700 mb-6">
              Supply meant for export under LUT without payment of Integrated Tax.
              {(invoice.lut_ack_number || company?.lut_ack_number) && (() => {
                const num = invoice.lut_ack_number || company?.lut_ack_number
                const date = invoice.lut_date || company?.lut_expiry_date
                return <> The LUT acknowledgement number is <strong>{num}</strong>{date ? <> dated <strong>{date}</strong></> : null}.</>
              })()}
            </div>
          )}

          <table className="w-full text-sm mb-6">
            <thead>
              <tr className="bg-navy-800 text-white text-left">
                <th className="px-3 py-2 rounded-l-lg">{isSales ? 'Item' : 'Product'}</th>
                {!isSales && <th className="px-3 py-2">HSN/SAC</th>}
                <th className="px-3 py-2">Qty</th>
                <th className="px-3 py-2">Price</th>
                <th className="px-3 py-2">Tax %</th>
                <th className="px-3 py-2 rounded-r-lg text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it, i) => (
                <tr key={i} className="border-b border-slate-100">
                  <td className="px-3 py-2">{it.description || it.product_name}</td>
                  {!isSales && <td className="px-3 py-2">{it.hsn_sac || '—'}</td>}
                  <td className="px-3 py-2">{it.qty}</td>
                  <td className="px-3 py-2">{Number(it.unit_price).toFixed(2)}</td>
                  <td className="px-3 py-2">{it.tax_percent}%</td>
                  <td className="px-3 py-2 text-right">{Number(it.line_total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-end mb-6">
            <div className="w-full sm:w-72 space-y-1.5 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Subtotal</span><span>{subtotal.toFixed(2)}</span></div>
              {isSales && invoice.discount_value > 0 && <div className="flex justify-between"><span className="text-slate-500">Discount</span><span>-{Number(invoice.discount_value).toFixed(2)}</span></div>}
              <div className="flex justify-between"><span className="text-slate-500">Tax</span><span>{taxAmount.toFixed(2)}</span></div>
              {isSales && invoice.bank_charges > 0 && <div className="flex justify-between"><span className="text-slate-500">Bank Charges</span><span>{Number(invoice.bank_charges).toFixed(2)}</span></div>}
              {!isSales && invoice.tds_percent > 0 && <div className="flex justify-between text-red-600"><span>TDS ({invoice.tds_percent}%)</span><span>-{((subtotal + taxAmount) * invoice.tds_percent / 100).toFixed(2)}</span></div>}
              <div className="flex justify-between font-bold text-base border-t border-slate-200 pt-2">
                <span>{isSales ? 'Grand Total' : 'Net Payable'}</span><span>{Number(invoice.amount).toFixed(2)} {invoice.currency}</span>
              </div>
            </div>
          </div>

          {(invoice.payment_terms || invoice.notes) && (
            <div className="text-xs text-slate-500 mb-4 space-y-1">
              {invoice.payment_terms && <p>{invoice.payment_terms}</p>}
              {invoice.notes && <p>{invoice.notes}</p>}
            </div>
          )}

          {isSales && company?.bank_account_number && (
            <div className="border-t border-slate-100 pt-4 mb-4 text-xs text-slate-500">
              <div className="font-semibold text-slate-400 uppercase text-[11px] mb-1">Bank Details</div>
              <p>Bank: {company.bank_name}</p>
              <p>Account Holder: {company.bank_account_holder}</p>
              <p>Account Number: {company.bank_account_number}</p>
              <p>Branch: {company.bank_branch}</p>
              <p>SWIFT: {company.bank_swift_code}</p>
            </div>
          )}

          {invoice.thank_you_note && <p className="text-center text-sm text-slate-400 mt-6">{invoice.thank_you_note}</p>}
        </div>
      </div>
    </div>
  )
}
