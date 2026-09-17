import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_report = """          fields={[{ type: 'currency', key: 'currency', default: displayCurrency }]}
          onGenerate={generateBudgetReport}"""

new_report = """          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'startYear', 
              label: 'Starting Year (Includes Next 4 Years)', 
              default: startYear,
              options: Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: y, label: String(y) } }) 
            }
          ]}
          onGenerate={generateBudgetReport}"""
code = code.replace(old_report, new_report)

# And make sure generateBudgetReport uses selections.startYear instead of the local state startYear
old_generate = """  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const years = [startYear, startYear + 1, startYear + 2, startYear + 3, startYear + 4]"""

new_generate = """  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const sy = Number(selections.startYear || startYear)
    const years = [sy, sy + 1, sy + 2, sy + 3, sy + 4]"""
code = code.replace(old_generate, new_generate)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
