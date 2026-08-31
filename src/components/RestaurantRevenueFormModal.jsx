import { useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { getLatestRate } from '../lib/fx'
import Modal, { Field } from './Modal'
import { CURRENCY_LIST } from '../lib/currencies'

const MEAL_PERIODS = ['Breakfast', 'Lunch', 'Dinner', 'All Day']

export default function RestaurantRevenueFormModal({ companyId, product, company, entry, onClose, onSaved }) {
  const [revenueDate, setRevenueDate] = useState(entry?.revenue_date || new Date().toISOString().slice(0, 10))
  const [mealPeriod, setMealPeriod] = useState(entry?.meal_period || 'Dinner')
  const [tableOrSection, setTableOrSection] = useState(entry?.table_or_section || '')
  const [covers, setCovers] = useState(entry?.covers ?? 1)
  const [currency, setCurrency] = useState(entry?.currency || company?.base_currency || 'USD')
  const [foodAmount, setFoodAmount] = useState(entry?.food_amount ?? 0)
  const [beverageAmount, setBeverageAmount] = useState(entry?.beverage_amount ?? 0)
  const [otherAmount, setOtherAmount] = useState(entry?.other_amount ?? 0)
  const [notes, setNotes] = useState(entry?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const total = Number(foodAmount || 0) + Number(beverageAmount || 0) + Number(otherAmount || 0)
  const perCover = covers > 0 ? total / covers : 0

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!revenueDate || total <= 0) { setError('Date and at least one revenue amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product,
        revenue_date: revenueDate, meal_period: mealPeriod, table_or_section: tableOrSection.trim() || null,
        covers: Number(covers) || 0,
        currency, fx_rate_locked: fxRate,
        food_amount: Number(foodAmount) || 0, beverage_amount: Number(beverageAmount) || 0, other_amount: Number(otherAmount) || 0,
        food_amount_usd: Math.round((Number(foodAmount) || 0) / fxRate * 100) / 100,
        beverage_amount_usd: Math.round((Number(beverageAmount) || 0) / fxRate * 100) / 100,
        other_amount_usd: Math.round((Number(otherAmount) || 0) / fxRate * 100) / 100,
        amount_usd: Math.round(total / fxRate * 100) / 100,
        notes: notes || null,
      }
      if (entry) {
        const { error: err } = await supabase.from('restaurant_daily_revenue').update(payload).eq('id', entry.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('restaurant_daily_revenue').insert(payload)
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
    <Modal title={entry ? 'Edit Table Revenue' : 'New Table Revenue Entry'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Date *">
            <input type="date" required value={revenueDate} onChange={e => setRevenueDate(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Meal Period">
            <select value={mealPeriod} onChange={e => setMealPeriod(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {MEAL_PERIODS.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Table / Section">
            <input value={tableOrSection} onChange={e => setTableOrSection(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Table 12, Patio" />
          </Field>
          <Field label="Covers (guests) *">
            <input type="number" min="0" required value={covers} onChange={e => setCovers(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>

        <Field label="Currency">
          <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
          </select>
        </Field>

        <div className="grid grid-cols-3 gap-3">
          <Field label="Food Revenue">
            <input type="number" step="0.01" min="0" value={foodAmount} onChange={e => setFoodAmount(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Beverage Revenue">
            <input type="number" step="0.01" min="0" value={beverageAmount} onChange={e => setBeverageAmount(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Other Revenue">
            <input type="number" step="0.01" min="0" value={otherAmount} onChange={e => setOtherAmount(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>

        <div className="bg-slate-50 rounded-lg p-3 flex items-center justify-between text-sm">
          <span className="text-slate-500">Total: <strong className="text-slate-700">{total.toFixed(2)} {currency}</strong></span>
          <span className="text-slate-500">Revenue / Cover: <strong className="text-slate-700">{perCover.toFixed(2)} {currency}</strong></span>
        </div>

        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
            {saving ? 'Saving…' : entry ? 'Save Changes' : 'Add Entry'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
