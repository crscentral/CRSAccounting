import { useState, useEffect } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { CURRENCY_LIST } from '../lib/currencies'
import { getLatestRate } from '../lib/fx'
import Modal, { Field } from './Modal'
import { useAuth } from '../lib/AuthContext'
import InvoicePreviewModal from './InvoicePreviewModal'

const emptyItem = () => ({ description: '', qty: 1, unit_price: 0, tax_percent: 0 })

export default function SalesInvoiceFormModal({ companyId, company, contacts, invoice, onClose, onSaved }) {
  const { activeRole } = useAuth()
  const [invoiceType, setInvoiceType] = useState(invoice?.invoice_type || 'sales')
  const [invoiceNumber, setInvoiceNumber] = useState(invoice?.invoice_number || `INV-${Math.floor(Math.random() * 900000 + 100000)}`)
  const [contactId, setContactId] = useState(invoice?.contact_id || '')
  const [newCustomerMode, setNewCustomerMode] = useState(false)
  const [customerName, setCustomerName] = useState('')
  const [customerEmail, setCustomerEmail] = useState(invoice?.customer_email || '')
  const [customerPhone, setCustomerPhone] = useState(invoice?.customer_phone || '')
  const [customerAddress, setCustomerAddress] = useState(invoice?.customer_address || '')
  const [currency, setCurrency] = useState(invoice?.currency || 'USD')
  const [invoiceDate, setInvoiceDate] = useState(invoice?.invoice_date || new Date().toISOString().slice(0, 10))
  const [dueDate, setDueDate] = useState(invoice?.due_date || '')
  const [billingTerms, setBillingTerms] = useState(invoice?.billing_terms || 'Monthly')
  const [servicePeriod, setServicePeriod] = useState(invoice?.service_period || '')
  const [status, setStatus] = useState(invoice?.status || 'Draft')
  const [isExportLut, setIsExportLut] = useState(invoice ? invoice.is_export_lut : !!company?.lut_ack_number)
  const [lutAckNumber, setLutAckNumber] = useState(invoice?.lut_ack_number ?? company?.lut_ack_number ?? '')
  const [lutDate, setLutDate] = useState(invoice?.lut_date ?? company?.lut_expiry_date ?? '')
  const [items, setItems] = useState([emptyItem()])
  const [discountType, setDiscountType] = useState(invoice?.discount_type || 'fixed')
  const [discountValue, setDiscountValue] = useState(invoice?.discount_value || 0)
  const [bankCharges, setBankCharges] = useState(invoice?.bank_charges || 0)
  const [paidAmount, setPaidAmount] = useState(invoice?.paid_amount || 0)
  const [notes, setNotes] = useState(invoice?.notes ?? company?.default_notes ?? '')
  const [paymentTerms, setPaymentTerms] = useState(invoice?.payment_terms ?? company?.default_payment_terms ?? '')
  const [thankYouNote, setThankYouNote] = useState(invoice?.thank_you_note ?? company?.default_thank_you_note ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [previewData, setPreviewData] = useState(null)

  useEffect(() => { if (invoice) loadItems() }, [invoice])

  // Defensive safety net: if the company's LUT data loads/updates *after* this form
  // already mounted (e.g. a stale cached company object in the session), and we're
  // creating a brand-new invoice with nothing entered yet, sync the LUT fields once
  // fresh company data becomes available rather than silently saving an empty value.
  useEffect(() => {
    if (!invoice && company?.lut_ack_number && !lutAckNumber) {
      setLutAckNumber(company.lut_ack_number)
      setLutDate(company.lut_expiry_date || '')
      setIsExportLut(true)
    }
  }, [company])

  useEffect(() => {
    if (!contactId || newCustomerMode) return
    const c = contacts.find(c => c.id === contactId)
    if (c) {
      setCustomerEmail(c.email || '')
      setCustomerPhone(c.phone || '')
      setCustomerAddress(c.address || '')
    }
  }, [contactId, newCustomerMode, contacts])

  async function loadItems() {
    const { data } = await supabase.from('sales_invoice_items').select('*').eq('sales_invoice_id', invoice.id).order('sort_order')
    if (data && data.length > 0) setItems(data.map(d => ({ description: d.description, qty: d.qty, unit_price: d.unit_price, tax_percent: d.tax_percent })))
  }

  const customers = contacts.filter(c => c.type === 'customer')

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
  const discountAmount = discountType === 'percent' ? subtotal * (Number(discountValue || 0) / 100) : Number(discountValue || 0)
  const grandTotal = Math.max(0, subtotal + taxAmount - discountAmount + Number(bankCharges || 0))
  const balanceDue = Math.max(0, grandTotal - Number(paidAmount || 0))

  function buildPayload() {
    return {
      invoice_number: invoiceNumber.trim(), invoice_date: invoiceDate, due_date: dueDate || null,
      currency, status, invoice_type: invoiceType,
      subtotal, discount_type: discountType, discount_value: discountValue,
      tax_amount: taxAmount, bank_charges: bankCharges, paid_amount: paidAmount,
      amount: grandTotal, balance_due: balanceDue,
      notes, payment_terms: paymentTerms, thank_you_note: thankYouNote,
      is_export_lut: isExportLut, lut_ack_number: lutAckNumber || null, lut_date: lutDate || null,
      service_period: servicePeriod || null, billing_terms: billingTerms,
      customer_email: customerEmail || null, customer_phone: customerPhone || null, customer_address: customerAddress || null,
    }
  }

  function handlePreview() {
    if (items.every(it => !it.description.trim())) { setError('Add at least one line item to preview.'); return }
    setError('')
    const contact = customers.find(c => c.id === contactId)
    setPreviewData({
      invoice: buildPayload(),
      items: items.filter(it => it.description.trim()).map((it, idx) => ({ ...it, line_total: lineTotals[idx].total })),
      contactDisplay: newCustomerMode ? customerName : (contact?.name || ''),
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!invoiceNumber.trim()) { setError('Invoice number is required.'); return }
    if (!contactId && !customerName.trim()) { setError('Select or enter a customer.'); return }
    if (items.every(it => !it.description.trim())) { setError('Add at least one line item.'); return }
    setSaving(true)
    try {
      let finalContactId = contactId
      if (newCustomerMode && customerName.trim()) {
        const { data: newContact, error: contactErr } = await supabase.from('contacts')
          .insert({ company_id: companyId, type: 'customer', name: customerName.trim(), email: customerEmail || null, phone: customerPhone || null, address: customerAddress || null })
          .select().single()
        if (contactErr) throw contactErr
        finalContactId = newContact.id
      }

      const rate = await getLatestRate(currency)
      const fxRate = currency === 'USD' ? 1 : (rate || 1)
      const amountUsd = currency === 'USD' ? grandTotal : grandTotal / fxRate

      const payload = {
        company_id: companyId, contact_id: finalContactId || null, fx_rate_locked: fxRate,
        amount_usd: Math.round(amountUsd * 100) / 100, ...buildPayload(),
      }

      let invoiceId = invoice?.id
      if (invoice) {
        const { error: err } = await supabase.from('sales_invoices').update(payload).eq('id', invoice.id)
        if (err) throw err
        await supabase.from('sales_invoice_items').delete().eq('sales_invoice_id', invoice.id)
      } else {
        const { data: newInv, error: err } = await supabase.from('sales_invoices').insert(payload).select().single()
        if (err) throw err
        invoiceId = newInv.id
      }

      const itemRows = items.filter(it => it.description.trim()).map((it, idx) => ({
        sales_invoice_id: invoiceId,
        description: it.description, qty: it.qty, unit_price: it.unit_price, tax_percent: it.tax_percent,
        line_total: lineTotals[idx].total, sort_order: idx,
      }))
      if (itemRows.length > 0) {
        const { error: itemsErr } = await supabase.from('sales_invoice_items').insert(itemRows)
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

  if (previewData) {
    return (
      <InvoicePreviewModal
        type="sales" invoice={previewData.invoice} items={previewData.items} company={company}
        contactDisplay={previewData.contactDisplay}
        role={activeRole}
        onBack={() => setPreviewData(null)}
        onClose={onClose}
      />
    )
  }

  return (
    <Modal title={invoice ? 'Edit Sales Invoice' : 'Create New Invoice'} onClose={onClose} maxWidth="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-2 gap-2">
          <button type="button" onClick={() => setInvoiceType('sales')} className={`py-2.5 rounded-lg text-sm font-semibold ${invoiceType === 'sales' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-500'}`}>Sales Invoice</button>
          <button type="button" onClick={() => setInvoiceType('proforma')} className={`py-2.5 rounded-lg text-sm font-semibold ${invoiceType === 'proforma' ? 'bg-navy-700 text-white' : 'bg-slate-100 text-slate-500'}`}>Proforma Invoice</button>
        </div>
        {invoiceType === 'proforma' && (
          <p className="text-xs text-amber-600 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
            Proforma invoices are quotes/estimates — they won't post to your Ledger, Revenue, or Accounts Receivable until converted to a Sales Invoice.
          </p>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Field label="Invoice #"><input value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 25).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Issue Date"><input type="date" value={invoiceDate} onChange={e => setInvoiceDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          <Field label="Due Date"><input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <Field label="Billing Terms">
            <select value={billingTerms} onChange={e => setBillingTerms(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {['Monthly', 'One-time', 'Quarterly', 'Annual'].map(t => <option key={t}>{t}</option>)}
            </select>
          </Field>
          <Field label="Service Period"><input value={servicePeriod} onChange={e => setServicePeriod(e.target.value)} placeholder="e.g. August 2026" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          <Field label="Status">
            <select value={status} onChange={e => setStatus(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {['Draft', 'Paid', 'Overdue', 'Cancelled'].map(s => <option key={s}>{s}</option>)}
            </select>
          </Field>
        </div>

        <div className="bg-gold-50 border border-gold-100 rounded-lg p-4">
          <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
            <input type="checkbox" checked={isExportLut} onChange={e => setIsExportLut(e.target.checked)} />
            Export Invoice (LUT) — Supply meant for export under LUT without payment of Integrated Tax
          </label>
          {isExportLut && (
            <div className="grid grid-cols-2 gap-3 mt-3">
              <Field label="LUT Acknowledgement Number"><input value={lutAckNumber} onChange={e => setLutAckNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
              <Field label="LUT Date"><input type="date" value={lutDate} onChange={e => setLutDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            </div>
          )}
          {company?.lut_ack_number && <p className="text-[11px] text-slate-400 mt-2">Pre-filled from {company.name}'s default LUT (set in Companies → Invoice Settings). Uncheck above to remove it from this invoice.</p>}
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Bill To</h3>
          <div className="flex gap-2 mb-2">
            <button type="button" onClick={() => setNewCustomerMode(false)} className={`text-xs px-3 py-1 rounded-full font-medium ${!newCustomerMode ? 'bg-navy-600 text-white' : 'bg-slate-100 text-slate-600'}`}>Existing Customer</button>
            <button type="button" onClick={() => setNewCustomerMode(true)} className={`text-xs px-3 py-1 rounded-full font-medium ${newCustomerMode ? 'bg-navy-600 text-white' : 'bg-slate-100 text-slate-600'}`}>New Customer</button>
          </div>
          {!newCustomerMode ? (
            <Field label="Customer">
              <select value={contactId} onChange={e => setContactId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Select customer…</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">Selecting a customer auto-fills their saved email, phone, and address below.</p>
            </Field>
          ) : (
            <Field label="Customer / Company Name *"><input value={customerName} onChange={e => setCustomerName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          )}
          <div className="grid grid-cols-2 gap-3 mt-3">
            <Field label="Email"><input type="email" value={customerEmail} onChange={e => setCustomerEmail(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Phone"><input value={customerPhone} onChange={e => setCustomerPhone(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          </div>
          <Field label="Address" className="mt-3"><input value={customerAddress} onChange={e => setCustomerAddress(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-slate-700">Line Items</h3>
            <button type="button" onClick={addItem} className="flex items-center gap-1 text-xs font-medium text-navy-600"><Plus size={14} /> Add Item</button>
          </div>
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <div className="grid grid-cols-12 gap-2 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase">
              <div className="col-span-5">Item / Description</div>
              <div className="col-span-2">Qty</div>
              <div className="col-span-2">Price</div>
              <div className="col-span-2">Tax %</div>
              <div className="col-span-1"></div>
            </div>
            {items.map((it, i) => (
              <div key={i} className="grid grid-cols-12 gap-2 px-3 py-2 border-t border-slate-100 items-center">
                <input className="col-span-5 border border-slate-200 rounded-md px-2 py-1.5 text-sm" placeholder="Description" value={it.description} onChange={e => updateItem(i, 'description', e.target.value)} />
                <input type="number" step="0.01" className="col-span-2 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.qty} onChange={e => updateItem(i, 'qty', Number(e.target.value))} />
                <input type="number" step="0.01" className="col-span-2 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.unit_price} onChange={e => updateItem(i, 'unit_price', Number(e.target.value))} />
                <input type="number" step="0.01" className="col-span-2 border border-slate-200 rounded-md px-2 py-1.5 text-sm" value={it.tax_percent} onChange={e => updateItem(i, 'tax_percent', Number(e.target.value))} />
                <button type="button" onClick={() => removeItem(i)} className="col-span-1 text-slate-300 hover:text-red-500 flex justify-center"><Trash2 size={15} /></button>
              </div>
            ))}
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-6">
          <div className="space-y-3">
            <Field label="Notes"><textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Payment Terms / Conditions"><textarea value={paymentTerms} onChange={e => setPaymentTerms(e.target.value)} rows={3} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
            <Field label="Thank You Note"><input value={thankYouNote} onChange={e => setThankYouNote(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
          </div>
          <div className="bg-slate-50 rounded-lg p-4 space-y-2 text-sm h-fit">
            <Row label="Subtotal" value={subtotal} />
            <div className="flex items-center justify-between gap-2">
              <span className="text-slate-500">Discount</span>
              <div className="flex items-center gap-1">
                <select value={discountType} onChange={e => setDiscountType(e.target.value)} className="border border-slate-200 rounded-md text-xs px-1 py-1">
                  <option value="fixed">Fixed</option>
                  <option value="percent">%</option>
                </select>
                <input type="number" value={discountValue} onChange={e => setDiscountValue(Number(e.target.value))} className="w-16 border border-slate-200 rounded-md px-2 py-1 text-sm" />
              </div>
            </div>
            <Row label="Tax" value={taxAmount} />
            <div className="flex items-center justify-between font-semibold border-t border-slate-200 pt-2">
              <span>Grand Total</span><span>{grandTotal.toFixed(2)} {currency}</span>
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-slate-500">Bank Charges</span>
              <input type="number" value={bankCharges} onChange={e => setBankCharges(Number(e.target.value))} className="w-20 border border-slate-200 rounded-md px-2 py-1 text-sm" />
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-slate-500">Paid</span>
              <input type="number" value={paidAmount} onChange={e => setPaidAmount(Number(e.target.value))} className="w-20 border border-slate-200 rounded-md px-2 py-1 text-sm" />
            </div>
            <div className="flex items-center justify-between font-semibold text-emerald-700 border-t border-slate-200 pt-2">
              <span>Balance Due</span><span>{balanceDue.toFixed(2)} {currency}</span>
            </div>
          </div>
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex flex-col sm:flex-row gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="button" onClick={handlePreview} className="flex-1 border border-navy-300 text-navy-700 rounded-lg py-2 text-sm font-medium">Preview</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
            {saving ? 'Saving…' : 'Save Invoice'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

function Row({ label, value }) {
  return <div className="flex items-center justify-between"><span className="text-slate-500">{label}</span><span>{value.toFixed(2)}</span></div>
}
