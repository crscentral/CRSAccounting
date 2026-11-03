import { useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import Modal, { Field } from './Modal'

function computeFeaturedAddress(hAddr, bAddr, showH, showB) {
  const h = (hAddr || '').trim()
  const b = (bAddr || '').trim()
  if (showH && showB && h && b) {
    return `Hotel Address: ${h}\nBanking Address: ${b}`
  }
  if (showH && h) return h
  if (showB && b) return b
  return h || b || ''
}

export default function ContactFormModal({ companyId, product = 'basic', contact, defaultType = 'customer', onClose, onSaved }) {
  const [form, setForm] = useState({
    type: contact?.type || defaultType,
    name: contact?.name || '',
    email: contact?.email || '',
    phone: contact?.phone || '',
    tax_id: contact?.tax_id || '',
    hotel_address: contact?.hotel_address ?? (contact?.address || ''),
    banking_address: contact?.banking_address ?? '',
    show_hotel_address: contact?.show_hotel_address !== undefined ? Boolean(contact.show_hotel_address) : true,
    show_banking_address: contact?.show_banking_address !== undefined ? Boolean(contact.show_banking_address) : false,
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function update(field, value) { setForm(f => ({ ...f, [field]: value })) }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!form.name.trim()) { setError('Name is required.'); return }
    setSaving(true)
    try {
      const computedAddress = computeFeaturedAddress(
        form.hotel_address,
        form.banking_address,
        form.show_hotel_address,
        form.show_banking_address
      )

      const payload = {
        type: form.type,
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        tax_id: form.tax_id.trim(),
        hotel_address: form.hotel_address.trim(),
        banking_address: form.banking_address.trim(),
        show_hotel_address: form.show_hotel_address,
        show_banking_address: form.show_banking_address,
        address: computedAddress,
      }

      if (contact) {
        const { error: err } = await supabase.from('contacts').update(payload).eq('id', contact.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('contacts').insert({ ...payload, company_id: companyId, product })
        if (err) throw err
      }
      onSaved()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal maxWidth="max-w-2xl" title={contact ? 'Edit Contact' : (defaultType === 'customer' ? 'New Customer' : 'New Supplier')} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Type">
          <div className="flex gap-2">
            {['customer', 'supplier'].map(t => (
              <button key={t} type="button" onClick={() => update('type', t)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium capitalize ${form.type === t ? 'bg-navy-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
                {t}
              </button>
            ))}
          </div>
        </Field>
        <Field label="Name *">
          <input required value={form.name} onChange={e => update('name', e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Email">
            <input type="email" value={form.email} onChange={e => update('email', e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Phone">
            <input value={form.phone} onChange={e => update('phone', e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Tax ID / GSTIN">
          <input value={form.tax_id} onChange={e => update('tax_id', e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>

        <div className="border border-slate-200 rounded-xl p-3.5 bg-slate-50/60 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">Addresses & Invoice Selection</label>
            <span className="text-[11px] text-slate-500">Tick which address to feature on invoices</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700">Hotel / Property Address</span>
                <label className="flex items-center gap-1.5 text-xs text-navy-700 font-medium cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.show_hotel_address}
                    onChange={e => update('show_hotel_address', e.target.checked)}
                    className="rounded border-slate-300 text-navy-600 focus:ring-navy-500"
                  />
                  <span>Feature on Invoice</span>
                </label>
              </div>
              <textarea
                value={form.hotel_address}
                onChange={e => update('hotel_address', e.target.value)}
                placeholder="Enter physical hotel or property address..."
                rows={3}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-1 focus:ring-navy-500 focus:border-navy-500"
              />
            </div>

            <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700">Banking / Billing Address</span>
                <label className="flex items-center gap-1.5 text-xs text-navy-700 font-medium cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.show_banking_address}
                    onChange={e => update('show_banking_address', e.target.checked)}
                    className="rounded border-slate-300 text-navy-600 focus:ring-navy-500"
                  />
                  <span>Feature on Invoice</span>
                </label>
              </div>
              <textarea
                value={form.banking_address}
                onChange={e => update('banking_address', e.target.value)}
                placeholder="Enter registered banking or billing address..."
                rows={3}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-1 focus:ring-navy-500 focus:border-navy-500"
              />
            </div>
          </div>
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
            {saving ? 'Saving…' : contact ? 'Save Changes' : 'Create Contact'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
