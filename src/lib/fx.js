import { supabase } from './supabaseClient'

// Free, no-key-required daily exchange rate API (base USD).
const FX_API_URL = 'https://open.er-api.com/v6/latest/USD'

/**
 * Ensures today's FX rates are cached in Supabase. Called once per session/page load.
 * Cheap no-op if today's rates already exist.
 */
let isFetchingRates = false;
let ratesPromise = null;

export async function ensureTodayRatesCached() {
  if (ratesPromise) return ratesPromise;
  ratesPromise = (async () => {
    const today = (() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; })()
    const { data: existing } = await supabase
      .from('fx_rates_cache')
      .select('currency_code')
      .eq('rate_date', today)
      .limit(1)

    if (existing && existing.length > 0) return

    if (isFetchingRates) return
    isFetchingRates = true

    try {
      const res = await fetch(FX_API_URL)
      const json = await res.json()
      if (json.result !== 'success' || !json.rates) return

      const rows = Object.entries(json.rates).map(([currency_code, rate_to_usd]) => ({
        currency_code,
        rate_date: today,
        rate_to_usd,
      }))

      const chunkSize = 100
      for (let i = 0; i < rows.length; i += chunkSize) {
        await supabase.from('fx_rates_cache').upsert(rows.slice(i, i + chunkSize), {
          onConflict: 'currency_code,rate_date',
        })
      }
    } catch (e) {
      console.warn('FX rate refresh failed, will use last cached rates:', e)
    } finally {
      isFetchingRates = false
    }
  })();
  return ratesPromise;
}

/**
 * Fetches the most recent cached rate (today, or most recent available) for a currency.
 * Rate convention: 1 USD = rate_to_usd <currency_code>.
 */
export async function getLatestRate(currencyCode) {
  if (currencyCode === 'USD') return 1
  const { data } = await supabase
    .from('fx_rates_cache')
    .select('rate_to_usd, rate_date')
    .eq('currency_code', currencyCode)
    .order('rate_date', { ascending: false })
    .limit(1)
    .maybeSingle()
  return data?.rate_to_usd ?? null
}

/** Fetches latest rates for many currencies at once (map of code -> rate_to_usd). */
export async function getLatestRatesMap(currencyCodes) {
  const uniq = [...new Set(currencyCodes)].filter(c => c !== 'USD')
  if (uniq.length === 0) return { USD: 1 }

  const { data } = await supabase
    .from('fx_rates_cache')
    .select('currency_code, rate_to_usd, rate_date')
    .in('currency_code', uniq)
    .order('rate_date', { ascending: false })

  const map = { USD: 1 }
  for (const row of data || []) {
    if (!(row.currency_code in map)) map[row.currency_code] = row.rate_to_usd
  }
  return map
}

/** Converts a USD amount to a target display currency using today's cached rate. */
export function convertFromUsd(amountUsd, targetCurrency, ratesMap) {
  if (targetCurrency === 'USD') return amountUsd
  const rate = ratesMap[targetCurrency]
  if (!rate) return amountUsd
  return amountUsd * rate
}

export function formatMoney(amount, currencyCode) {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      maximumFractionDigits: 2,
    }).format(amount)
  } catch {
    return `${amount.toFixed(2)} ${currencyCode}`
  }
}

export function formatMoneyRounded(amount, currencyCode) {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.round(amount))
  } catch {
    return `${Math.round(amount)} ${currencyCode}`
  }
}
