import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. Update the useMemo for ancillaryMonthlySummary to also include local currency
new_useMemo = """
  const ancillaryMonthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    for (let m = 1; m <= 12; m++) {
      let mBudgetUsd = 0
      let mActualUsd = 0
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        if (ancillaryBudgets[k]) mBudgetUsd += Number(ancillaryBudgets[k].amount_usd) || 0
        if (ancillaryActuals[k]) mActualUsd += Number(ancillaryActuals[k]) || 0
      }
      totalBudget += mBudgetUsd
      totalActual += mActualUsd
      
      const r = displayCurrency === 'USD' ? 1 : (rates[displayCurrency] || rate)
      const mBudgetLocal = displayCurrency === 'USD' ? mBudgetUsd : mBudgetUsd * r
      const mActualLocal = displayCurrency === 'USD' ? mActualUsd : mActualUsd * r
      
      summary.push({ 
        month: m, name: MONTH_NAMES[m - 1], 
        budgetUsd: mBudgetUsd, actualUsd: mActualUsd, varianceUsd: mActualUsd - mBudgetUsd,
        budgetLocal: mBudgetLocal, actualLocal: mActualLocal, varianceLocal: mActualLocal - mBudgetLocal
      })
    }
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget }
  }, [ancillaryBudgets, ancillaryActuals, ancillaryAccounts, displayCurrency, rates, rate])
"""

content = re.sub(
    r'const ancillaryMonthlySummary = useMemo\(\(\) => \{.*?return \{ months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget \}\n  \}, \[ancillaryBudgets, ancillaryActuals, ancillaryAccounts\]\)',
    new_useMemo.strip(),
    content,
    flags=re.DOTALL
)

# 2. Update the table headers and cells in Table 2
table2_old = """<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} - Other Revenue vs Actuals</div>
            <table className="w-full text-sm">
              <thead className="bg-navy-800 text-white text-xs text-left">
                <tr>
                  <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                  <th className="py-2 px-3 font-semibold">Budget (USD)</th>
                  <th className="py-2 px-3 font-semibold">Actual (USD)</th>
                  <th className="py-2 px-3 font-semibold rounded-tr-lg">Variance (USD)</th>
                </tr>
              </thead>
              <tbody>
                {ancillaryMonthlySummary.months.map(m => (
                  <tr key={m.month} className="border-b border-slate-50 hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-medium text-slate-700 w-32">{m.name}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.budget)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.actual)}</td>
                    <td className={`py-2 px-3 font-medium ${m.variance < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{fmt(m.variance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>"""

table2_new = """<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} - Other Revenue vs Actuals</div>
            <table className="w-full text-sm">
              <thead className="bg-navy-800 text-white text-xs text-left">
                <tr>
                  <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                  <th className="py-2 px-3 font-semibold">Monthly Budget</th>
                  <th className="py-2 px-3 font-semibold">Monthly (USD)</th>
                  <th className="py-2 px-3 font-semibold">Actual</th>
                  <th className="py-2 px-3 font-semibold">Actual (USD)</th>
                  <th className="py-2 px-3 font-semibold">Variance</th>
                  <th className="py-2 px-3 font-semibold rounded-tr-lg">Variance (USD)</th>
                </tr>
              </thead>
              <tbody>
                {ancillaryMonthlySummary.months.map(m => (
                  <tr key={m.month} className="border-b border-slate-50 hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-medium text-slate-700 w-32">{m.name}</td>
                    <td className="py-2 px-3 text-slate-500 font-medium">{formatMoney(m.budgetLocal, displayCurrency)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.budgetUsd)}</td>
                    <td className="py-2 px-3 text-slate-500 font-medium">{formatMoney(m.actualLocal, displayCurrency)}</td>
                    <td className="py-2 px-3 text-slate-500">{fmt(m.actualUsd)}</td>
                    <td className={`py-2 px-3 font-medium ${m.varianceLocal < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{formatMoney(Math.abs(m.varianceLocal), displayCurrency)}</td>
                    <td className={`py-2 px-3 ${m.varianceUsd < 0 ? 'text-red-600' : 'text-emerald-600'}`}>{fmt(Math.abs(m.varianceUsd))}</td>
                  </tr>
                ))}
              </tbody>
            </table>"""

content = content.replace(table2_old, table2_new)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
