import { useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import Modal, { Field } from './Modal'

const TYPES = ['Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses']

export default function AccountFormModal({ companyId, product, account, onClose, onSaved }) {
  const [form, setForm] = useState({
    code: account?.code || '',
    name: account?.name || '',
    type: account?.type || 'Expenses',
    subtype: account?.subtype || '',
    currency: account?.currency || 'USD',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function update(field, value) { setForm(f => ({ ...f, [field]: value })) }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!form.code.trim() || !form.name.trim()) { setError('Code and Name are required.'); return }
    setSaving(true)
    try {
      if (account) {
        const { error: err } = await supabase.from('accounts').update(form).eq('id', account.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('accounts').insert({ ...form, company_id: companyId, product })
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
    <Modal title={account ? 'Edit Account' : 'New Account'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Code *">
            <input required value={form.code} onChange={e => update('code', e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. 5050" />
          </Field>
          <Field label="Type *">
            <select value={form.type} onChange={e => update('type', e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </Field>
        </div>
        <Field label="Name *">
          <input required value={form.name} onChange={e => update('name', e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Software & Subscriptions" />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Subtype">
            <input value={form.subtype} onChange={e => update('subtype', e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Operating Expenses" />
          </Field>
          <Field label="Currency">
            <input value={form.currency} onChange={e => update('currency', e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
            {saving ? 'Saving…' : account ? 'Save Changes' : 'Create Account'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
