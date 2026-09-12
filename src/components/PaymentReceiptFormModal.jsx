import { useState, useEffect } from 'react'
import { Calendar } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import Modal, { Field } from './Modal'
import { getLatestRate } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'

const PAYMENT_METHODS = ['Bank Transfer', 'Cash', 'Card', 'Cheque', 'Other']

export default function PaymentReceiptFormModal({ open, onClose, companyId, product, initialData, onSuccess, invoices }) {
  const [saving, setSaving] = useState(false)

  const [receiptNumber, setReceiptNumber] = useState('')
  const [receiptDate, setReceiptDate] = useState('')
  const [invoiceId, setInvoiceId] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [method, setMethod] = useState('Bank Transfer')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (open) {
      if (initialData) {
        setReceiptNumber(initialData.receipt_number || '')
        setReceiptDate(initialData.receipt_date || '')
        setInvoiceId(initialData.sales_invoice_id || '')
        setCustomerName(initialData.customer_name_freeform || initialData.contact?.name || '')
        setAmount(initialData.amount || '')
        setCurrency(initialData.currency || 'USD')
        setFxRate(initialData.fx_rate_locked || '')
        setMethod(initialData.method || 'Bank Transfer')
        setNotes(initialData.notes || '')
      } else {
        setReceiptNumber(`RCP-${Math.floor(Math.random() * 1000000)}`)
        setReceiptDate(new Date().toISOString().slice(0, 10))
        setInvoiceId('')
        setCustomerName('')
        setAmount('')
        setCurrency('USD')
        setMethod('Bank Transfer')
        setNotes('')
      }
    }
  }, [open, initialData])

  // Auto-fill customer/currency when linking invoice
  function handleInvoiceSelect(val) {
    setInvoiceId(val)
    if (val) {
      const inv = invoices.find(i => i.id === val)
      if (inv) {
        if (!customerName) setCustomerName(inv.contact?.name || '')
        setCurrency(inv.currency)
        // Only set amount if empty, to allow partial payments
        if (!amount) setAmount(inv.amount)
      }
    }
  }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    try {
      let finalFxRate = 1
      if (currency !== 'USD') {
        if (fxRate && !isNaN(Number(fxRate))) {
          finalFxRate = Number(fxRate)
        } else {
          const rate = await getLatestRate(currency)
          finalFxRate = rate || 1
        }
      }

      const amt = Number(amount) || 0
      const amountUsd = currency === 'USD' ? amt : amt / finalFxRate

      const payload = {
        company_id: companyId,
        product,
        receipt_number: receiptNumber.trim() || null,
        receipt_date: receiptDate,
        sales_invoice_id: invoiceId || null,
        customer_name_freeform: customerName.trim() || null,
        currency,
        amount: amt,
        amount_usd: Math.round(amountUsd * 100) / 100,
        fx_rate_locked: fxRate,
        method,
        notes: notes.trim() || null,
      }

      if (initialData) {
        const { error } = await supabase.from('payment_receipts').update(payload).eq('id', initialData.id)
        if (error) throw error
      } else {
        const { error } = await supabase.from('payment_receipts').insert([payload])
        if (error) throw error
      }

      // If an invoice is linked, checking if it should be marked as Paid is something that could be done here, 
      // but usually requires fetching all receipts for that invoice and checking total paid vs total due. 
      // For simplicity, we just let the user update the invoice status manually or handle it if there's an existing trigger.

      onSuccess()
      onClose()
    } catch (err) {
      alert('Save failed: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={initialData ? "Edit Payment Receipt" : "New Payment Receipt"} maxWidth="max-w-xl">
      <form onSubmit={handleSave} className="p-4 sm:p-6 space-y-4">
        
        <div className="grid grid-cols-2 gap-4">
          <Field label="Receipt Number">
            <input type="text" required value={receiptNumber} onChange={e => setReceiptNumber(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none" />
          </Field>
          <Field label="Date">
            <div className="relative">
              <input type="date" required value={receiptDate} onChange={e => setReceiptDate(e.target.value)} className="w-full border border-slate-300 rounded-lg pl-3 pr-10 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none appearance-none" />
              <Calendar size={15} className="absolute right-3 top-2.5 text-slate-400 pointer-events-none" />
            </div>
          </Field>
        </div>

        <Field label="Link to Invoice (optional)">
          <select value={invoiceId} onChange={e => handleInvoiceSelect(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none bg-white">
            <option value="">— No linked invoice —</option>
            {invoices.map(inv => (
              <option key={inv.id} value={inv.id}>{inv.invoice_number} ({inv.currency} {inv.amount})</option>
            ))}
          </select>
        </Field>

        <Field label="Customer Name">
          <input type="text" value={customerName} onChange={e => setCustomerName(e.target.value)} placeholder="Customer name" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none" />
        </Field>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Amount Received">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none" />
          </Field>
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none bg-white">
              {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
            </select>
          </Field>
        </div>

        <Field label="Payment Method">
          <select value={method} onChange={e => setMethod(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none bg-white">
            {PAYMENT_METHODS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </Field>

        <Field label="Notes (optional)">
          <textarea rows="3" value={notes} onChange={e => setNotes(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:border-navy-500 focus:ring-1 focus:ring-navy-500 outline-none resize-none"></textarea>
        </Field>

        <div className="pt-2 flex gap-3">
          <button type="button" onClick={onClose} disabled={saving} className="flex-1 bg-white border border-slate-300 text-slate-700 py-2.5 rounded-lg text-sm font-semibold hover:bg-slate-50 disabled:opacity-50">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-emerald-500 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-emerald-600 disabled:opacity-50">Save Receipt</button>
        </div>
      </form>
    </Modal>
  )
}
