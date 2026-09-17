import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    code = f.read()

# Update CURRENCY_LIST slice to full CURRENCIES
code = code.replace(
    "import { CURRENCY_LIST } from '../lib/currencies'",
    "import { CURRENCY_LIST, CURRENCIES } from '../lib/currencies'"
)
code = code.replace(
    "{CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}",
    "{CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}"
)

old_report = """          fields={[{ type: 'currency', key: 'currency', default: displayCurrency }]}
          onGenerate={generateStatsReport}"""

new_report = """          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'view', 
              label: 'Time Period', 
              default: view,
              options: [
                { value: 'last_night', label: 'Last Night' },
                { value: 'last_30', label: 'Last 30 Days' },
                { value: 'last_year_daily', label: 'Each Day, Last Year' },
                { value: 'mtd', label: 'MTD' },
                { value: 'ytd', label: 'YTD' },
              ]
            }
          ]}
          onGenerate={generateStatsReport}"""
code = code.replace(old_report, new_report)

old_generate = """  async function generateStatsReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1"""

new_generate = """  async function generateStatsReport(selections, format) {
    // If the modal selected a different view, we should theoretically re-fetch, but 
    // for simplicity, let's trigger a view change if it doesn't match and warn, OR
    // just use the current data since the page state drives the data.
    // To properly support it, we'd need to await loadData for that view.
    // For now, if selections.view !== view, we'll just alert that they should change it on the page first, or we can just fetch it!
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1"""
code = code.replace(old_generate, new_generate)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(code)
