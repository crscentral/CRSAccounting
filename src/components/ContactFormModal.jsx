import { useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import Modal, { Field } from './Modal'

export default function ContactFormModal({ companyId, contact, defaultType = 'customer', onClose, onSaved }) {
  const [form, setForm] = useState({
    type: contact?.type || defaultType,
    name: contact?.name || '',
    email: contact?.email || '',
    phone: contact?.phone || '',
    tax_id: contact?.tax_id || '',
    address: contact?.address || '',
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
      if (contact) {
        const { error: err } = await supabase.from('contacts').update(form).eq('id', contact.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('contacts').insert({ ...form, company_id: companyId })
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
    <Modal title={contact ? 'Edit Contact' : (defaultType === 'customer' ? 'New Customer' : 'New Supplier')} onClose={onClose}>
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
        <Field label="Address">
          <textarea value={form.address} onChange={e => update('address', e.target.value)} rows={2}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>

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
