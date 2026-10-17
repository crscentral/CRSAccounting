import { useState, useEffect, useMemo } from 'react'
import { Plus, Trash2, ArrowRightLeft } from 'lucide-react'
import { getLocalDate } from '../lib/dateUtils'
import { supabase } from '../lib/supabaseClient'
import { getLatestRate } from '../lib/fx'
import Modal, { Field } from './Modal'
import { CURRENCY_LIST } from '../lib/currencies'

const MEAL_PERIODS = ['Breakfast', 'Lunch', 'Dinner', 'All Day']
const PAYMENT_MODES = ['Cash', 'Credit Card', 'Bank Transfer', 'QR Payment']

export default function RestaurantRevenueFormModal({
  companyId,
  product,
  company,
  entry,
  accounts = [],
  onClose,
  onSaved,
}) {
  const defaultCurr = company?.default_currency || company?.base_currency || 'USD'
  const [revenueDate, setRevenueDate] = useState(entry?.revenue_date || getLocalDate())
  const [mealPeriod, setMealPeriod] = useState(entry?.meal_period || 'Dinner')
  const [tableOrSection, setTableOrSection] = useState(entry?.table_or_section || '')
  const [covers, setCovers] = useState(entry?.covers ?? 1)
  const [currency, setCurrency] = useState(entry?.currency || defaultCurr)
  const [paymentMode, setPaymentMode] = useState(entry?.payment_mode || 'Cash')

  // Main Category Amounts in Table/Primary Currency
  const [foodAmount, setFoodAmount] = useState(entry?.food_amount ?? '')
  const [beverageAmount, setBeverageAmount] = useState(entry?.beverage_amount ?? '')
  const [otherAmount, setOtherAmount] = useState(entry?.other_amount ?? '')

  // Additional / Ancillary items posted in separate currencies
  const [lineItems, setLineItems] = useState(
    (entry?.line_items || []).map(li => ({
      category: li.category || 'Other',
      description: li.description || '',
      currency: li.currency || entry?.secondary_currency || defaultCurr,
      amount: li.amount ?? '',
    }))
  )

  // Extra collection currencies explicitly added
  const [extraCollCurrencies, setExtraCollCurrencies] = useState([])

  // Separate collections per currency
  const [collectedByCurr, setCollectedByCurr] = useState(() => {
    if (entry?.currency_breakdown) {
      const init = {}
      Object.entries(entry.currency_breakdown).forEach(([c, val]) => {
        init[c] = val.collected !== undefined ? String(val.collected) : ''
      })
      return init
    }
    if (entry?.collected !== undefined && entry?.currency) {
      return { [entry.currency]: String(entry.collected) }
    }
    return {}
  })

  // Editable conversion rates (1 USD = X Currency)
  const [customFxRates, setCustomFxRates] = useState(() => {
    const init = {}
    if (entry?.currency_breakdown) {
      Object.entries(entry.currency_breakdown).forEach(([c, val]) => {
        if (val.rate) init[c] = String(val.rate)
      })
    }
    if (entry?.currency && entry?.fx_rate_locked) {
      init[entry.currency] = String(entry.fx_rate_locked)
    }
    if (entry?.secondary_currency && entry?.secondary_fx_rate) {
      init[entry.secondary_currency] = String(entry.secondary_fx_rate)
    }
    return init
  })

  const [ratesToUsd, setRatesToUsd] = useState({ USD: 1 })
  const [notes, setNotes] = useState(entry?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // Identify all distinct currencies present in this entry
  const distinctCurrencies = useMemo(() => {
    const set = new Set([currency])
    lineItems.forEach(li => {
      if (li.currency) set.add(li.currency)
    })
    extraCollCurrencies.forEach(c => {
      if (c) set.add(c)
    })
    return Array.from(set)
  }, [currency, lineItems, extraCollCurrencies])

  const nonUsdCurrencies = useMemo(() => {
    return distinctCurrencies.filter(c => c !== 'USD')
  }, [distinctCurrencies])

  // Fetch live exchange rates for distinct currencies
  useEffect(() => {
    async function fetchRates() {
      const newRates = { USD: 1 }
      for (const c of distinctCurrencies) {
        if (c !== 'USD') {
          const r = await getLatestRate(c)
          newRates[c] = r || 1
        }
      }
      setRatesToUsd(prev => ({ ...prev, ...newRates }))

      setCustomFxRates(prev => {
        const updated = { ...prev }
        let changed = false
        for (const c of distinctCurrencies) {
          if (c !== 'USD' && (!updated[c] || Number(updated[c]) <= 0)) {
            updated[c] = String(newRates[c] || 1)
            changed = true
          }
        }
        return changed ? updated : prev
      })
    }
    fetchRates()
  }, [distinctCurrencies.join(',')])

  function getRateFor(c) {
    if (c === 'USD') return 1
    const custom = Number(customFxRates[c])
    if (custom && custom > 0) return custom
    return ratesToUsd[c] || 1
  }

  function convertToUsd(amount, fromC) {
    if (!amount) return 0
    if (fromC === 'USD') return Number(amount)
    const rate = getRateFor(fromC)
    return Number(amount) / rate
  }

  function convertFromUsd(amountUsd, targetC) {
    if (!amountUsd) return 0
    if (targetC === 'USD') return Number(amountUsd)
    const rate = getRateFor(targetC)
    return Number(amountUsd) * rate
  }

  // Totals by currency
  const totalsByCurr = useMemo(() => {
    const totals = {}
    distinctCurrencies.forEach(c => { totals[c] = 0 })

    // Primary currency main heads
    const mainSum = (Number(foodAmount) || 0) + (Number(beverageAmount) || 0) + (Number(otherAmount) || 0)
    if (currency) {
      totals[currency] = (totals[currency] || 0) + mainSum
    }

    // Ancillary items
    lineItems.forEach(li => {
      const c = li.currency || currency
      const amt = Number(li.amount) || 0
      totals[c] = (totals[c] || 0) + amt
    })
    return totals
  }, [distinctCurrencies, currency, foodAmount, beverageAmount, otherAmount, lineItems])

  const hasAnyExplicitCollection = useMemo(() => {
    return Object.values(collectedByCurr).some(v => v !== undefined && v !== '' && !isNaN(Number(v)))
  }, [collectedByCurr])

  function getCollectedFor(c) {
    if (hasAnyExplicitCollection) {
      const val = collectedByCurr[c]
      return (val !== undefined && val !== '') ? Number(val) : 0
    }
    return totalsByCurr[c] || 0
  }

  // Revenue totals by category in USD
  const { foodUsd, bevUsd, otherUsd, finalRevenueAmountUsd } = useMemo(() => {
    let fUsd = convertToUsd(Number(foodAmount) || 0, currency)
    let bUsd = convertToUsd(Number(beverageAmount) || 0, currency)
    let oUsd = convertToUsd(Number(otherAmount) || 0, currency)

    lineItems.forEach(li => {
      const liCurr = li.currency || currency
      const liUsd = convertToUsd(Number(li.amount) || 0, liCurr)
      if (li.category === 'Food') fUsd += liUsd
      else if (li.category === 'Beverage') bUsd += liUsd
      else oUsd += liUsd
    })

    const totalUsd = Math.round((fUsd + bUsd + oUsd) * 100) / 100
    return {
      foodUsd: Math.round(fUsd * 100) / 100,
      bevUsd: Math.round(bUsd * 100) / 100,
      otherUsd: Math.round(oUsd * 100) / 100,
      finalRevenueAmountUsd: totalUsd,
    }
  }, [foodAmount, beverageAmount, otherAmount, lineItems, currency, customFxRates, ratesToUsd])

  // Total collected in USD
  const finalCollectedAmountUsd = useMemo(() => {
    let sumUsd = 0
    distinctCurrencies.forEach(c => {
      sumUsd += convertToUsd(getCollectedFor(c), c)
    })
    return Math.round(sumUsd * 100) / 100
  }, [distinctCurrencies, collectedByCurr, totalsByCurr, hasAnyExplicitCollection, customFxRates, ratesToUsd])

  // Values in Primary Currency
  const finalRevenueAmountPrimary = useMemo(() => {
    if (currency === 'USD') return finalRevenueAmountUsd
    const primRate = getRateFor(currency)
    return Math.round(finalRevenueAmountUsd * primRate * 100) / 100
  }, [finalRevenueAmountUsd, currency, customFxRates, ratesToUsd])

  const finalCollectedAmountPrimary = useMemo(() => {
    if (currency === 'USD') return finalCollectedAmountUsd
    const primRate = getRateFor(currency)
    return Math.round(finalCollectedAmountUsd * primRate * 100) / 100
  }, [finalCollectedAmountUsd, currency, customFxRates, ratesToUsd])

  const balanceAmountUsd = useMemo(() => {
    return Math.round((finalRevenueAmountUsd - finalCollectedAmountUsd) * 100) / 100
  }, [finalRevenueAmountUsd, finalCollectedAmountUsd])

  const balanceAmountPrimary = useMemo(() => {
    if (currency === 'USD') return balanceAmountUsd
    const primRate = getRateFor(currency)
    return Math.round(balanceAmountUsd * primRate * 100) / 100
  }, [balanceAmountUsd, currency, customFxRates, ratesToUsd])

  const perCoverUsd = covers > 0 ? finalRevenueAmountUsd / covers : 0
  const perCoverPrimary = covers > 0 ? finalRevenueAmountPrimary / covers : 0

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!revenueDate || finalRevenueAmountUsd <= 0) {
      setError('Date and at least one positive revenue amount are required.')
      return
    }
    setSaving(true)
    try {
      const primFxRate = getRateFor(currency)
      const secCurr = nonUsdCurrencies.find(c => c !== currency) || nonUsdCurrencies[0] || null
      const secFxRate = secCurr ? getRateFor(secCurr) : null

      const breakdown = {}
      distinctCurrencies.forEach(c => {
        const rev = totalsByCurr[c] || 0
        const coll = getCollectedFor(c)
        const rate = getRateFor(c)
        breakdown[c] = { revenue: rev, collected: coll, rate: rate }
      })

      const enrichedLineItems = lineItems.map(li => {
        const itemCurr = li.currency || currency
        const itemFx = getRateFor(itemCurr)
        const amt = Number(li.amount) || 0
        const amtUsd = Math.round((amt / itemFx) * 100) / 100
        return {
          ...li,
          category: li.category || 'Other',
          description: li.description || li.category || 'Extra Service',
          amount: amt,
          currency: itemCurr,
          fx_rate: itemFx,
          amount_usd: amtUsd,
          collected_usd: amtUsd,
        }
      })

      const payload = {
        company_id: companyId,
        product,
        revenue_date: revenueDate,
        meal_period: mealPeriod,
        table_or_section: tableOrSection.trim() || null,
        covers: Number(covers) || 0,
        currency,
        payment_mode: paymentMode || 'Cash',
        fx_rate_locked: primFxRate,
        secondary_currency: secCurr,
        secondary_fx_rate: secFxRate,
        currency_breakdown: breakdown,
        line_items: enrichedLineItems,
        food_amount: Math.round(foodUsd * primFxRate * 100) / 100,
        beverage_amount: Math.round(bevUsd * primFxRate * 100) / 100,
        other_amount: Math.round(otherUsd * primFxRate * 100) / 100,
        food_amount_usd: foodUsd,
        beverage_amount_usd: bevUsd,
        other_amount_usd: otherUsd,
        amount_usd: finalRevenueAmountUsd,
        collected: finalCollectedAmountPrimary,
        collected_usd: finalCollectedAmountUsd,
        notes: notes.trim() || null,
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

  const inputClass = "w-full h-[40px] border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-navy-500"
  const selectClass = "w-full h-[40px] border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium bg-white focus:outline-none focus:ring-1 focus:ring-navy-500"

  return (
    <Modal title={entry ? 'Edit Table Revenue' : 'New Table Revenue Entry'} maxWidth="max-w-2xl" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Row 1: Date & Meal Period */}
        <div className="grid grid-cols-2 gap-3">
          <Field label="Date *">
            <input
              type="date"
              required
              value={revenueDate}
              onChange={e => setRevenueDate(e.target.value)}
              className={inputClass}
            />
          </Field>
          <Field label="Meal Period">
            <select
              value={mealPeriod}
              onChange={e => setMealPeriod(e.target.value)}
              className={selectClass}
            >
              {MEAL_PERIODS.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </Field>
        </div>

        {/* Row 2: Table/Section & Covers */}
        <div className="grid grid-cols-2 gap-3">
          <Field label="Table / Section">
            <input
              value={tableOrSection}
              onChange={e => setTableOrSection(e.target.value)}
              className={inputClass}
              placeholder="e.g. Table 12, Patio"
            />
          </Field>
          <Field label="Covers (guests) *">
            <input
              type="number"
              min="0"
              required
              value={covers}
              onChange={e => setCovers(e.target.value)}
              className={inputClass}
            />
          </Field>
        </div>

        {/* Row 3: Currency & Mode of Payment */}
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select
              value={currency}
              onChange={e => setCurrency(e.target.value)}
              className={selectClass}
            >
              {CURRENCY_LIST.map(c => (
                <option key={c.code} value={c.code}>{c.code} — {c.name}</option>
              ))}
            </select>
          </Field>
          <Field label="Mode of Payment">
            <select
              value={paymentMode}
              onChange={e => setPaymentMode(e.target.value)}
              className={selectClass}
            >
              {PAYMENT_MODES.map(pm => (
                <option key={pm} value={pm}>{pm}</option>
              ))}
            </select>
          </Field>
        </div>

        {/* Core Revenue Heads in Table Currency */}
        <div className="border-t border-slate-200 pt-3">
          <label className="text-xs font-semibold text-slate-700 block mb-2">
            Revenue Heads ({currency})
          </label>
          <div className="grid grid-cols-3 gap-3">
            <Field label="Food Revenue">
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={foodAmount}
                onChange={e => setFoodAmount(e.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="Beverage Revenue">
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={beverageAmount}
                onChange={e => setBeverageAmount(e.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="Other Revenue">
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={otherAmount}
                onChange={e => setOtherAmount(e.target.value)}
                className={inputClass}
              />
            </Field>
          </div>
        </div>

        {/* Ancillary Items Section (Can be posted in separate currencies) */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2.5">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-xs font-semibold text-slate-700 block">
                Other Revenue (Ancillary)
              </label>
              <span className="text-[11px] text-slate-400">
                Can be posted in a separate currency (e.g. LAK, THB, USD)
              </span>
            </div>
            <button
              type="button"
              onClick={() =>
                setLineItems([
                  ...lineItems,
                  {
                    category: 'Other',
                    description: '',
                    amount: '',
                    currency: nonUsdCurrencies.find(c => c !== currency) || currency,
                  },
                ])
              }
              className="text-xs text-navy-600 font-semibold hover:text-navy-800 flex items-center gap-1 bg-white border border-navy-200 px-2.5 py-1 rounded shadow-sm"
            >
              <Plus size={13} /> Add Item
            </button>
          </div>

          {lineItems.map((li, i) => (
            <div key={i} className="flex gap-2 items-center w-full min-w-0">
              <select
                value={li.category}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].category = e.target.value
                  setLineItems(nu)
                }}
                className="w-32 shrink-0 border border-slate-300 rounded-lg h-[38px] px-2 text-xs bg-white font-medium text-slate-700"
              >
                <option value="Food">Food</option>
                <option value="Beverage">Beverage</option>
                <option value="Other">Other Revenue</option>
              </select>

              <input
                type="text"
                placeholder="Description / Service"
                value={li.description}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].description = e.target.value
                  setLineItems(nu)
                }}
                className="flex-1 min-w-0 border border-slate-300 rounded-lg h-[38px] px-2.5 text-xs bg-white truncate"
              />

              <select
                value={li.currency || currency}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].currency = e.target.value
                  setLineItems(nu)
                }}
                className="w-20 shrink-0 border border-slate-300 rounded-lg h-[38px] px-1.5 text-xs bg-white font-medium text-slate-700"
              >
                {CURRENCY_LIST.map(c => (
                  <option key={c.code} value={c.code}>{c.code}</option>
                ))}
              </select>

              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="Amount"
                value={li.amount}
                onChange={e => {
                  const nu = [...lineItems]
                  nu[i].amount = e.target.value
                  setLineItems(nu)
                }}
                className="w-28 shrink-0 border border-slate-300 rounded-lg h-[38px] px-2 text-xs bg-white font-semibold"
              />

              <button
                type="button"
                onClick={() => setLineItems(lineItems.filter((_, idx) => idx !== i))}
                className="shrink-0 text-slate-400 hover:text-red-500 p-1"
                title="Remove item"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}

          {lineItems.length === 0 && (
            <div className="text-xs text-slate-400 italic">No extra charges added.</div>
          )}
        </div>

        {/* Currency Breakdown & Separate Collections */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2.5">
          <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
            <div>
              <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                Currency Breakdown & Collections
              </span>
              <span className="text-[11px] text-slate-500 block">
                Enter collection per currency
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <select
                onChange={e => {
                  if (e.target.value && !distinctCurrencies.includes(e.target.value)) {
                    setExtraCollCurrencies(prev => [...prev, e.target.value])
                  }
                  e.target.value = ''
                }}
                defaultValue=""
                className="text-[11px] border border-slate-300 bg-white rounded px-2 py-1 text-slate-600"
              >
                <option value="" disabled>+ Add Currency</option>
                {CURRENCY_LIST.filter(c => !distinctCurrencies.includes(c.code)).map(c => (
                  <option key={c.code} value={c.code}>{c.code}</option>
                ))}
              </select>
            </div>
          </div>

          {distinctCurrencies.map(curr => {
            const rev = totalsByCurr[curr] || 0
            const currentColl = collectedByCurr[curr] !== undefined ? collectedByCurr[curr] : ''
            return (
              <div
                key={curr}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 bg-white rounded-lg border border-slate-200 shadow-sm"
              >
                <div className="text-sm font-medium text-slate-700">
                  Total <span className="font-bold text-navy-700">{curr}</span> Rev ={' '}
                  <span className="font-bold text-slate-900">
                    {Number(rev).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {curr}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-500 font-medium whitespace-nowrap">
                    Collected {curr}:
                  </span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder={hasAnyExplicitCollection ? '0.00' : `Full (${rev.toFixed(2)})`}
                    value={currentColl}
                    onChange={e => setCollectedByCurr({ ...collectedByCurr, [curr]: e.target.value })}
                    className="w-32 border border-slate-300 rounded h-[36px] px-2.5 text-sm font-semibold text-slate-800 bg-white"
                  />
                  <div className="flex gap-1 shrink-0">
                    <button
                      type="button"
                      onClick={() => setCollectedByCurr(prev => ({ ...prev, [curr]: String(rev) }))}
                      className="px-2 py-1 h-[36px] text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded"
                      title="Set to full revenue"
                    >
                      Full
                    </button>
                    <button
                      type="button"
                      onClick={() => setCollectedByCurr(prev => ({ ...prev, [curr]: '0' }))}
                      className="px-2 py-1 h-[36px] text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded"
                      title="Set to 0"
                    >
                      0
                    </button>
                  </div>
                </div>
              </div>
            )
          })}

          {/* Editable Conversion Rates */}
          {nonUsdCurrencies.length > 0 && (
            <div className="p-2.5 bg-amber-50/80 rounded-lg border border-amber-200 text-xs space-y-2">
              <div className="flex items-center gap-1.5 font-semibold text-amber-900">
                <ArrowRightLeft size={13} />
                <span>Conversion Rates:</span>
                <span className="text-[10px] text-amber-700 font-normal italic">
                  (Editable - 1 USD to currency)
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {nonUsdCurrencies.map(c => (
                  <div
                    key={c}
                    className="flex items-center justify-between gap-1.5 bg-white p-2 rounded border border-amber-200 shadow-sm"
                  >
                    <span className="text-slate-700 font-medium whitespace-nowrap">1 USD =</span>
                    <input
                      type="number"
                      step="0.0001"
                      min="0"
                      value={customFxRates[c] !== undefined ? customFxRates[c] : ''}
                      onChange={e => setCustomFxRates(prev => ({ ...prev, [c]: e.target.value }))}
                      className="w-28 border border-amber-300 rounded px-2 py-1 text-xs font-bold text-amber-950 bg-white shadow-inner"
                    />
                    <span className="text-slate-800 font-semibold">{c}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Remarks / Notes */}
        <Field label="Remarks / Notes">
          <textarea
            rows={2}
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="Add any remarks, guest requests, or notes..."
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-navy-500"
          />
        </Field>

        {/* Final Revenue Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 border-t border-slate-200 pt-3">
          <div className="flex flex-col bg-slate-50 border border-slate-200 rounded-lg p-3">
            <span className="text-xs font-semibold text-slate-700 mb-1">
              Total Revenue (USD) *
            </span>
            <div className="text-base font-bold text-slate-900">
              ${Number(finalRevenueAmountUsd).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {currency !== 'USD' && (
              <div className="text-[11px] font-normal text-slate-500 mt-0.5">
                ≈ {Number(finalRevenueAmountPrimary).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency}
              </div>
            )}
          </div>

          <div className="flex flex-col bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <span className="text-xs font-semibold text-emerald-800 mb-1">
              Total Amount Collected (USD)
            </span>
            <div className="text-base font-bold text-emerald-900">
              ${Number(finalCollectedAmountUsd).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            {currency !== 'USD' && (
              <div className="text-[11px] font-normal text-emerald-700 mt-0.5">
                ≈ {Number(finalCollectedAmountPrimary).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency}
              </div>
            )}
          </div>

          <div
            className={`flex flex-col rounded-lg p-3 border ${
              balanceAmountUsd > 0.009
                ? 'bg-amber-50 border-amber-200 text-amber-900'
                : balanceAmountUsd < -0.009
                ? 'bg-blue-50 border-blue-200 text-blue-900'
                : 'bg-slate-50 border-slate-200 text-slate-800'
            }`}
          >
            <span className="text-xs font-semibold mb-1">Balance Amount (USD)</span>
            <div className="text-base font-bold">
              ${Number(Math.abs(balanceAmountUsd)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              {balanceAmountUsd > 0.009 && (
                <span className="text-xs font-medium text-amber-700 ml-1.5">(Pending)</span>
              )}
              {balanceAmountUsd < -0.009 && (
                <span className="text-xs font-medium text-blue-700 ml-1.5">(Overpaid)</span>
              )}
              {Math.abs(balanceAmountUsd) <= 0.009 && (
                <span className="text-xs font-medium text-emerald-600 ml-1.5">(Settled)</span>
              )}
            </div>
            {currency !== 'USD' && (
              <div className="text-[11px] font-normal text-slate-500 mt-0.5">
                ≈ {Number(Math.abs(balanceAmountPrimary)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency}
              </div>
            )}
          </div>
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 border border-slate-300 rounded-lg py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2.5 text-sm font-medium disabled:opacity-60 shadow-sm"
          >
            {saving ? 'Saving…' : entry ? 'Save Changes' : 'Add Entry'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
