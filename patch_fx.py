with open("src/lib/fx.js", "r") as f:
    content = f.read()

replacement = """let isFetchingRates = false;
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
"""

import re
content = re.sub(r'export async function ensureTodayRatesCached\(\) \{[\s\S]*?\}\n', replacement, content)

with open("src/lib/fx.js", "w") as f:
    f.write(content)
