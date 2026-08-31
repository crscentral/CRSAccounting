import { useState, useEffect } from 'react'
import { Plus, Trash2, Upload } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { CURRENCY_LIST } from '../lib/currencies'
import { getLatestRate } from '../lib/fx'
import Modal, { Field } from './Modal'
import { useAuth } from '../lib/AuthContext'
import InvoicePreviewModal from './InvoicePreviewModal'

const emptyItem = () => ({ product_name: '', hsn_sac: '', qty: 1, unit_price: 0, tax_percent: 0 })

export default function PurchaseInvoiceFormModal({ companyId, product, company, contacts, accounts, invoice, onClose, onSaved }) {
  const { activeRole } = useAuth()
  const [invoiceNumber, setInvoiceNumber] = useState(invoice?.invoice_number || `PINV-${Math.floor(Math.random() * 90000000 + 10000000)}`)
  const [contactId, setContactId] = useState(invoice?.contact_id || '')
  const [newSupplierMode, setNewSupplierMode] = useState(false)
  const [supplierName, setSupplierName] = useState(invoice?.supplier_name_freeform || '')
  const [supplierEmail, setSupplierEmail] = useState(invoice?.supplier_email || '')
  const [supplierPhone, setSupplierPhone] = useState(invoice?.supplier_phone || '')
  const [supplierGstin, setSupplierGstin] = useState(invoice?.supplier_gstin || '')
  const [supplierAddress, setSupplierAddress] = useState(invoice?.supplier_address || '')
  const [invoiceDate, setInvoiceDate] = useState(invoice?.invoice_date || new Date().toISOString().slice(0, 10))
  const [dueDate, setDueDate] = useState(invoice?.due_date || '')
  const [currency, setCurrency] = useState(invoice?.currency || 'USD')
  const [accountId, setAccountId] = useState(invoice?.account_id || '')
  const [items, setItems] = useState([emptyItem()])
  const [tdsPercent, setTdsPercent] = useState(invoice?.tds_percent || 0)
  const [paymentTerms, setPaymentTerms] = useState(invoice?.payment_terms || 'Net 30')
  const [status, setStatus] = useState(invoice?.status || 'Draft')
  const [notes, setNotes] = useState(invoice?.notes || '')
  const [attachmentFile, setAttachmentFile] = useState(null)
  const [attachmentUrl, setAttachmentUrl] = useState(invoice?.attachment_url || '')
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [previewData, setPreviewData] = useState(null)

  useEffect(() => { if (invoice) loadItems() }, [invoice])

  useEffect(() => {
    if (!contactId || newSupplierMode) return
    const c = contacts.find(c => c.id === contactId)
    if (c) {
      setSupplierEmail(c.email || '')
      setSupplierPhone(c.phone || '')
      setSupplierGstin(c.tax_id || '')
      setSupplierAddress(c.address || '')
    }
  }, [contactId, newSupplierMode, contacts])

  async function loadItems() {
    const { data } = await supabase.from('purchase_invoice_items').select('*').eq('purchase_invoice_id', invoice.id).order('sort_order')
    if (data && data.length > 0) setItems(data.map(d => ({ product_name: d.product_name, hsn_sac: d.hsn_sac || '', qty: d.qty, unit_price: d.unit_price, tax_percent: d.tax_percent })))
  }

  const suppliers = contacts.filter(c => c.type === 'supplier')

  function updateItem(i, field, value) { setItems(prev => prev.map((it, idx) => idx === i ? { ...it, [field]: value } : it)) }
  function addItem() { setItems(prev => [...prev, emptyItem()]) }
  function removeItem(i) { setItems(prev => prev.filter((_, idx) => idx !== i)) }

  const lineTotals = items.map(it => {
    const base = Number(it.qty || 0) * Number(it.unit_price || 0)
    const tax = base * (Number(it.tax_percent || 0) / 100)
    return { base, tax, total: base + tax }
  })
  const subtotal = lineTotals.reduce((s, l) => s + l.base, 0)
  const taxAmount = lineTotals.reduce((s, l) => s + l.tax, 0)
  const total = subtotal + taxAmount
  const tdsAmount = total * (Number(tdsPercent || 0) / 100)
  const netPayable = Math.max(0, total - tdsAmount)

  async function handleFileUpload(file) {
    setUploading(true)
    try {
      const path = `${companyId}/${Date.now()}-${file.name}`
      const { error: uploadErr } = await supabase.storage.from('invoice-attachments').upload(path, file)
      if (uploadErr) throw uploadErr
      const { data } = supabase.storage.from('invoice-attachments').getPublicUrl(path)
      setAttachmentUrl(data.publicUrl)
    } catch (err) {
      setError('Attachment upload failed: ' + err.message)
    } finally {
      setUploading(false)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!invoiceNumber.trim()) { setError('Invoice number is required.'); return }
    if (items.every(it => !it.product_name.trim())) { setError('Add at least one line item.'); return }
    setSaving(true)
    try {
      let finalContactId = contactId
      if (newSupplierMode && supplierName.trim()) {
        const { data: newContact, error: contactErr } = await supabase.from('contacts')
          .insert({ company_id: companyId, type: 'supplier', name: supplierName.trim(), email: supplierEmail || null, phone: supplierPhone || null, tax_id: supplierGstin || null, address: supplierAddress || null })
          .select().single()
        if (contactErr) throw contactErr
        finalContactId = newContact.id
      }

      const rate = await getLatestRate(currency)
      const fxRate = currency === 'USD' ? 1 : (rate || 1)
      const amountUsd = currency === 'USD' ? netPayable : netPayable / fxRate

      const payload = {
        company_id: companyId, product,
        invoice_number: invoiceNumber.trim(),
        contact_id: finalContactId || null,
        supplier_name_freeform: !finalContactId ? supplierName.trim() : null,
        supplier_email: supplierEmail || null, supplier_phone: supplierPhone || null,
        supplier_gstin: supplierGstin || null, supplier_address: supplierAddress || null,
        invoice_date: invoiceDate, due_date: dueDate || null,
        currency, fx_rate_locked: fxRate,
        amount: netPayable, amount_usd: Math.round(amountUsd * 100) / 100,
        account_id: accountId || null, status,
        subtotal, tax_amount: taxAmount, tds_percent: tdsPercent, net_payable: netPayable,
        payment_terms: paymentTerms, notes, attachment_url: attachmentUrl || null,
      }

      let invoiceId = invoice?.id
      if (invoice) {
        const { error: err } = await supabase.from('purchase_invoices').update(payload).eq('id', invoice.id)
        if (err) throw err
        await supabase.from('purchase_invoice_items').delete().eq('purchase_invoice_id', invoice.id)
      } else {
        const { data: newInv, error: err } = await supabase.from('purchase_invoices').insert(payload).select().single()
        if (err) throw err
        invoiceId = newInv.id
      }

      const itemRows = items.filter(it => it.product_name.trim()).map((it, idx) => ({
        purchase_invoice_id: invoiceId,
        product_name: it.product_name, hsn_sac: it.hsn_sac, qty: it.qty, unit_price: it.unit_price, tax_percent: it.tax_percent,
        line_total: lineTotals[idx].total, sort_order: idx,
      }))
      if (itemRows.length > 0) {
        const { error: itemsErr } = await supabase.from('purchase_invoice_items').insert(itemRows)
        if (itemsErr) throw itemsErr
      }

      onSaved()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  function handlePreview() {
    if (items.every(it => !it.product_name.trim())) { setError('Add at least one line item to preview.'); return }
    setError('')
    const contact = suppliers.find(c => c.id === contactId)
    setPreviewData({
      invoice: {
        invoice_number: invoiceNumber, invoice_date: invoiceDate, due_date: dueDate, currency, status,
        subtotal, tax_amount: taxAmount, tds_percent: tdsPercent, amount: netPayable, net_payable: netPayable,
        notes, payment_terms: paymentTerms, supplier_gstin: supplierGstin, supplier_email: supplierEmail,
        supplier_phone: supplierPhone, supplier_address: supplierAddress,
      },
      items: items.filter(it => it.product_name.trim()).map((it, idx) => ({ ...it, line_total: lineTotals[idx].total })),
      contactDisplay: newSupplierMode ? supplierName : (contact?.name || ''),
    })
  }

  if (previewData) {
    return (
      <InvoicePreviewModal
        type="purchase" invoice={previewData.invoice} items={previewData.items} company={company}
        contactDisplay={previewData.contactDisplay}
        role={activeRole}
        onBack={() => setPreviewData(null)}
        onClose={onClose}
      />
    )
  }

  return (
    <Modal title={invoice ? 'Edit Purchase Invoice' : 'New Purchase Invoice'} onClose={onClose} maxWidth="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Field label="Invoice Number *"><input required value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          <Field label="Invoice Date *"><input type="date" required value={invoiceDate} onChange={e => setInvoiceDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          <Field label="Due Date"><input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 25).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Supplier Details</h3>
          <div className="flex gap-2 mb-2">
            <button type="button" onClick={() => setNewSupplierMode(false)} className={`text-xs px-3 py-1 rounded-full font-medium ${!newSupplierMode ? 'bg-navy-600 text-white' : 'bg-slate-100 text-slate-600'}`}>Existing Supplier</button>
            <button type="button" onClick={() => setNewSupplierMode(true)} className={`text-xs px-3 py-1 rounded-full font-medium ${newSupplierMode ? 'bg-navy-600 text-white' : 'bg-slate-100 text-slate-600'}`}>New Supplier</button>
          </div>
          {!newSupplierMode ? (
            <Field label="Supplier">
              <select value={contactId} onChange={e => setContactId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Select supplier…</option>
                {suppliers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </Field>
          ) : (
            <Field label="Supplier Name *"><input value={supplierName} onChange={e => setSupplierName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          )}
          <div className="grid grid-cols-2 gap-3 mt-3">
            <Field label="Supplier Email"><input type="email" value={supplierEmail} onChange={e => setSupplierEmail(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Supplier Phone"><input value={supplierPhone} onChange={e => setSupplierPhone(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-3">
            <Field label="GSTIN / Tax Number"><input value={supplierGstin} onChange={e => setSupplierGstin(e.target.value)} placeholder="e.g. 22AAAAA0000A1Z5" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Address"><input value={supplierAddress} onChange={e => setSupplierAddress(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          </div>
        </div>

        <Field label="Expense Account">
          <select value={accountId} onChange={e => setAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select account…</option>
            {accounts.filter(a => a.type === 'Expenses').map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>

        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-slate-700">Line Items</h3>
            <button type="button" onClick={addItem} className="flex items-center gap-1 text-xs font-medium text-navy-600"><Plus size={14} /> Add Item</button>
          </div>
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <div className="grid grid-cols-12 gap-2 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase">
              <div className="col-span-4">Product Name</div>
              <div className="col-span-2">HSN/SAC</div>
              <div className="col-span-2">Qty</div>
              <div className="col-span-2">Unit Price</div>
              <div className="col-span-1">Tax %</div>
              <div className="col-span-1"></div>
            </div>
            {items.map((it, i) => (
              <div key={i} className="grid grid-cols-12 gap-2 px-3 py-2 border-t border-slate-100 items-center">
                <input className="col-span-4 border border-slate-200 rounded-md px-2 py-1.5 text-sm" placeholder="Product / description" value={it.product_name} onChange={e => updateItem(i, 'product_name', e.target.value)} />
                <input className="col-span-2 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.hsn_sac} onChange={e => updateItem(i, 'hsn_sac', e.target.value)} />
                <input type="number" step="0.01" className="col-span-2 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.qty} onChange={e => updateItem(i, 'qty', Number(e.target.value))} />
                <input type="number" step="0.01" className="col-span-2 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.unit_price} onChange={e => updateItem(i, 'unit_price', Number(e.target.value))} />
                <input type="number" step="0.01" className="col-span-1 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.tax_percent} onChange={e => updateItem(i, 'tax_percent', Number(e.target.value))} />
                <button type="button" onClick={() => removeItem(i)} className="col-span-1 text-slate-300 hover:text-red-500 flex justify-center"><Trash2 size={15} /></button>
              </div>
            ))}
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-6">
          <div className="space-y-3">
            <Field label="Payment Terms"><input value={paymentTerms} onChange={e => setPaymentTerms(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Status">
              <select value={status} onChange={e => setStatus(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {['Draft', 'Paid', 'Overdue', 'Cancelled'].map(s => <option key={s}>{s}</option>)}
              </select>
            </Field>
            <Field label="Notes"><textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Upload Supplier Invoice PDF">
              <label className="flex items-center gap-2 border border-dashed border-slate-300 rounded-lg px-3 py-2 text-sm cursor-pointer text-slate-500 hover:border-navy-400">
                <Upload size={15} />
                {uploading ? 'Uploading…' : attachmentUrl ? 'File attached ✓' : 'Choose File'}
                <input type="file" accept="application/pdf" className="hidden" onChange={e => e.target.files[0] && handleFileUpload(e.target.files[0])} />
              </label>
            </Field>
          </div>
          <div className="bg-slate-50 rounded-lg p-4 space-y-2 text-sm h-fit">
            <Row label="Subtotal" value={subtotal} currency={currency} />
            <Row label="Tax" value={taxAmount} currency={currency} />
            <div className="flex items-center justify-between font-semibold border-t border-slate-200 pt-2">
              <span>Total</span><span>{total.toFixed(2)} {currency}</span>
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-slate-500">TDS %</span>
              <input type="number" value={tdsPercent} onChange={e => setTdsPercent(Number(e.target.value))} className="w-20 border border-slate-200 rounded-md px-2 py-1 text-sm" />
            </div>
            <div className="flex items-center justify-between font-semibold text-emerald-700 border-t border-slate-200 pt-2">
              <span>Net Payable</span><span>{netPayable.toFixed(2)} {currency}</span>
            </div>
          </div>
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex flex-col sm:flex-row gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="button" onClick={handlePreview} className="flex-1 border border-navy-300 text-navy-700 rounded-lg py-2 text-sm font-medium">Preview</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

function Row({ label, value, currency }) {
  return <div className="flex items-center justify-between"><span className="text-slate-500">{label}</span><span>{value.toFixed(2)} {currency}</span></div>
}
