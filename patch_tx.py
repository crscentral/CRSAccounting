import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

# Transactions AMC logic has two blocks (for main and export).
# First block:
old_amc_1 = """    // Add AMC amortization lines
    if (amc && amc.length > 0) {
      const amcMonthlyTotal = amc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
      if (amcMonthlyTotal > 0) {
        const start = new Date(cp.range.from)
        const end = new Date(Math.min(new Date(cp.range.to).getTime(), new Date().getTime()))
        let cur = new Date(start.getFullYear(), start.getMonth(), 1)
        while (cur <= end) {
          const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
          if (dStr >= cp.range.from && dStr <= cp.range.to) {
            combined.push({ id: `amc-${dStr}`, date: dStr, type: 'AMC Contract', desc: 'Amortized AMC (Monthly)', amount_usd: amcMonthlyTotal, amount: amcMonthlyTotal, currency: 'USD', direction: 'out' })
          }
          cur.setMonth(cur.getMonth() + 1)
        }
      }
    }"""

new_amc_1 = """    // Add AMC Contract lines (Actual Posting)
    if (amc && amc.length > 0) {
      amc.forEach(r => {
        const dStr = `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01`
        if (dStr >= cp.range.from && dStr <= cp.range.to) {
          combined.push({ id: `amc-${r.id}`, date: dStr, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount_usd: r.annual_amount_usd, amount: r.annual_amount || r.annual_amount_usd, currency: r.currency || 'USD', direction: 'out' })
        }
      })
    }"""

old_amc_2 = """    // Add AMC amortization lines
    if (amc && amc.length > 0) {
      const amcMonthlyTotal = amc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
      if (amcMonthlyTotal > 0) {
        const start = new Date(range.from)
        const end = new Date(range.to)
        let cur = new Date(start.getFullYear(), start.getMonth(), 1)
        while (cur <= end) {
          const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
          if (dStr >= range.from && dStr <= range.to) {
            combined.push({ date: dStr, type: 'AMC Contract', desc: 'Amortized AMC (Monthly)', amount: fmt(amcMonthlyTotal), direction: '-' })
          }
          cur.setMonth(cur.getMonth() + 1)
        }
      }
    }"""

new_amc_2 = """    // Add AMC Contract lines (Actual Posting)
    if (amc && amc.length > 0) {
      amc.forEach(r => {
        const dStr = `${r.start_year}-${String(r.start_month).padStart(2, '0')}-01`
        if (dStr >= range.from && dStr <= range.to) {
          combined.push({ date: dStr, type: 'AMC Contract', desc: r.contract_name || 'AMC Contract', amount: fmt(r.annual_amount_usd), direction: '-' })
        }
      })
    }"""

content = content.replace(old_amc_1, new_amc_1)
content = content.replace(old_amc_2, new_amc_2)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)
