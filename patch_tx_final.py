import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

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
    }
    
    combined.sort((a, b) => b.date.localeCompare(a.date))"""

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
    }
    
    combined.sort((a, b) => b.date.localeCompare(a.date))"""

# Replace first block
content = re.sub(r'// Add AMC amortization lines[\s\S]*?combined\.sort\(\(a, b\) => b\.date\.localeCompare\(\a\.date\)\)', new_1, content, count=1)
# Replace second block
content = re.sub(r'// Add AMC Contract lines \(Actual Posting\)[\s\S]*?combined\.sort\(\(a, b\) => b\.date\.localeCompare\(\a\.date\)\)', new_2, content, count=1)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)
