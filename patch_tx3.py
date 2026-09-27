import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

# Replace the first amc loop:
old_1 = """    // Add AMC Contract lines (Actual Posting)
    if (amc && amc.length > 0) {
      amc.forEach(r => {
        const dStr = r.start_year ? `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01` : (r.created_at || '').split('T')[0]
        if (dStr >= cp.range.from && dStr <= cp.range.to) {
          combined.push({ id: `amc-${r.id}`, date: dStr, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount_usd: r.annual_amount_usd, amount: r.annual_amount || r.annual_amount_usd, currency: r.currency || 'USD', direction: 'out' })
        }
      })
    }"""

new_1 = """    // Add AMC Contract lines (Actual Posting or Amortized depending on view)
    if (amc && amc.length > 0) {
      const isMonth = cp.periodProps.periodType.includes('MONTH') || cp.periodProps.periodType === 'LAST_30_DAYS' || (new Date(cp.range.to) - new Date(cp.range.from)) <= 35 * 24 * 60 * 60 * 1000
      amc.forEach(r => {
        if (isMonth) {
          combined.push({ id: `amc-${r.id}`, date: cp.range.from, type: 'AMC Contract', desc: `${r.contract_name || 'AMC Contract'} - Amortized AMC (Monthly)`, amount_usd: Number(r.annual_amount_usd)/12, amount: Number(r.annual_amount || r.annual_amount_usd)/12, currency: r.currency || 'USD', direction: 'out' })
        } else {
          const dStr = r.start_year ? `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01` : (r.created_at || '').split('T')[0] || cp.range.from
          combined.push({ id: `amc-${r.id}`, date: dStr >= cp.range.from && dStr <= cp.range.to ? dStr : cp.range.from, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount_usd: r.annual_amount_usd, amount: r.annual_amount || r.annual_amount_usd, currency: r.currency || 'USD', direction: 'out' })
        }
      })
    }"""

# Replace the second amc loop in generateReport:
old_2 = """    // Add AMC Contract lines (Actual Posting)
    if (amc && amc.length > 0) {
      amc.forEach(r => {
        const dStr = `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01`
        if (dStr >= range.from && dStr <= range.to) {
          combined.push({ date: dStr, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount: fmt(r.annual_amount_usd), direction: '-' })
        }
      })
    }"""

new_2 = """    // Add AMC Contract lines (Actual Posting or Amortized depending on view)
    if (amc && amc.length > 0) {
      const isMonth = selections.period.includes('MONTH') || selections.period === 'LAST_30_DAYS' || (new Date(range.to) - new Date(range.from)) <= 35 * 24 * 60 * 60 * 1000
      amc.forEach(r => {
        if (isMonth) {
          combined.push({ date: range.from, type: 'AMC Contract', desc: `${r.contract_name || 'AMC Contract'} - Amortized AMC (Monthly)`, amount: fmt(Number(r.annual_amount_usd)/12), direction: '-' })
        } else {
          const dStr = r.start_year ? `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01` : (r.created_at || '').split('T')[0] || range.from
          combined.push({ date: dStr >= range.from && dStr <= range.to ? dStr : range.from, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount: fmt(r.annual_amount_usd), direction: '-' })
        }
      })
    }"""

content = content.replace(old_1, new_1)
content = content.replace(old_2, new_2)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)
