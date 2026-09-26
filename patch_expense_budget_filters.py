import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

# 1. Add startMonth state (wait, HotelExpenseBudget already has selectedYear and selectedMonth!)
# Let's check:
# const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
# const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
# Actually, wait, it has selectedMonth but the UI doesn't use it for the header! The UI had "Select Year". Let's change selectedMonth to allow 'all'.
content = content.replace("  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)",
                          "  const [selectedMonth, setSelectedMonth] = useState('all')")

# 2. Update monthlySummary to respect selectedMonth
old_summary = """  const monthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    let foBudget = 0
    let fbBudget = 0
    let otherBudget = 0
    
    for (let m = 1; m <= 12; m++) {
      let mBudget = 0
      let mActual = 0
      for (const a of accounts) {
        const k = `${a.code}-${m}`
        if (budgets[k]) {
          const b = Number(budgets[k].amount_usd) || 0
          mBudget += b
          if (a.code.startsWith('501')) foBudget += b
          else if (a.code.startsWith('502') || a.code.startsWith('503')) fbBudget += b
          else otherBudget += b
        }
        if (actuals[k]) mActual += Number(actuals[k]) || 0
      }
      totalBudget += mBudget
      totalActual += mActual
      summary.push({ month: m, name: MONTH_NAMES[m - 1], budget: mBudget, actual: mActual, variance: mActual - mBudget })
    }
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget, foBudget, fbBudget, otherBudget }
  }, [budgets, actuals, accounts])"""

new_summary = """  const monthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    let foBudget = 0
    let fbBudget = 0
    let otherBudget = 0
    
    const mStart = selectedMonth === 'all' ? 1 : Number(selectedMonth)
    const mEnd = selectedMonth === 'all' ? 12 : Number(selectedMonth)
    
    for (let m = mStart; m <= mEnd; m++) {
      let mBudget = 0
      let mActual = 0
      for (const a of accounts) {
        const k = `${a.code}-${m}`
        if (budgets[k]) {
          const b = Number(budgets[k].amount_usd) || 0
          mBudget += b
          if (a.code.startsWith('501')) foBudget += b
          else if (a.code.startsWith('502') || a.code.startsWith('503')) fbBudget += b
          else otherBudget += b
        }
        if (actuals[k]) mActual += Number(actuals[k]) || 0
      }
      totalBudget += mBudget
      totalActual += mActual
    }
    
    // Always build the full months array so the Annual table can use it if needed, or we can filter later.
    // Wait, the table maps over monthlySummary.months. So we should ONLY include the requested months in the array!
    for (let m = 1; m <= 12; m++) {
      if (selectedMonth !== 'all' && m !== Number(selectedMonth)) continue;
      
      let mBudget = 0
      let mActual = 0
      for (const a of accounts) {
        const k = `${a.code}-${m}`
        if (budgets[k]) mBudget += Number(budgets[k].amount_usd) || 0
        if (actuals[k]) mActual += Number(actuals[k]) || 0
      }
      summary.push({ month: m, name: MONTH_NAMES[m - 1], budget: mBudget, actual: mActual, variance: mActual - mBudget })
    }
    
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget, foBudget, fbBudget, otherBudget }
  }, [budgets, actuals, accounts, selectedMonth])"""
content = content.replace(old_summary, new_summary)

# 3. Update PageHeader dropdowns
old_header = """            <div className="flex items-center gap-1 bg-white border border-slate-300 rounded-lg px-2 py-1">
              <span className="text-sm text-slate-500 ml-1">Period:</span>
              <select value={selectedYear} onChange={e => setSelectedYear(Number(e.target.value))} className="bg-transparent text-sm font-medium focus:outline-none">
                {Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>"""

new_header = """            <div className="flex items-center gap-1 bg-white border border-slate-300 rounded-lg px-2 py-1">
              <span className="text-sm text-slate-500 ml-1">Period:</span>
              <select value={selectedYear} onChange={e => setSelectedYear(Number(e.target.value))} className="bg-transparent text-sm font-medium focus:outline-none pr-1">
                {Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <span className="text-slate-300">/</span>
              <select value={selectedMonth} onChange={e => setSelectedMonth(e.target.value)} className="bg-transparent text-sm font-medium focus:outline-none pl-1">
                <option value="all">Full Year</option>
                {MONTH_NAMES.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>"""
content = content.replace(old_header, new_header)

# 4. Update KPI cards labels
old_kpi = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedYear} Front Office Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" sublabel="Front Office Accounts" />
        <KpiCard label={`${selectedYear} F&B Expenses Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" sublabel="F&B Accounts" />
        <KpiCard label={`${selectedYear} Other Expenses Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" sublabel="Other Expenses" />
        <KpiCard label={`Total ${selectedYear} Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" sublabel="Combined Expenses" />
      </div>"""

new_kpi = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} FO Expenses Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" sublabel="FO Accounts" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} F&B Expenses Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" sublabel="F&B Accounts" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Other Expenses Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" sublabel="Other Expenses" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" sublabel="Combined Expenses" />
      </div>"""
content = content.replace(old_kpi, new_kpi)

# 5. Fix the bottom Detailed Budget view which relied on selectedMonth
# Before, selectedMonth was default (e.g. Sept), and it was used to render the bottom table.
# Wait, if selectedMonth is 'all', what happens to the bottom detailed budget table?
old_detailed_header = """<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{MONTH_NAMES[selectedMonth - 1]} {selectedYear} Detailed Budget</div>"""
new_detailed_header = """<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{selectedMonth === 'all' ? `All Months ${selectedYear}` : MONTH_NAMES[Number(selectedMonth) - 1]} Detailed Budget</div>"""
content = content.replace(old_detailed_header, new_detailed_header)

old_detailed_body = """                {accounts.map(a => {
                  const key = `${a.code}-${selectedMonth}`
                  const row = budgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
                  const monthlyUsd = Number(row.amount_usd) || 0
                  const actualUsd = actuals[key] || 0
                  
                  const cur = row.currency || displayCurrency
                  const rr = cur === 'USD' ? 1 : (rates[cur] || rate)
                  const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * rr)
                  
                  const varLocal = actualLocal - (Number(row.amount) || 0)
                  const varUsd = actualUsd - monthlyUsd"""
new_detailed_body = """                {accounts.map(a => {
                  let monthlyUsd = 0;
                  let actualUsd = 0;
                  let localAmt = 0;
                  let cur = displayCurrency;
                  
                  const mStart = selectedMonth === 'all' ? 1 : Number(selectedMonth)
                  const mEnd = selectedMonth === 'all' ? 12 : Number(selectedMonth)
                  
                  for(let i = mStart; i <= mEnd; i++) {
                     const key = `${a.code}-${i}`
                     const row = budgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
                     monthlyUsd += Number(row.amount_usd) || 0
                     actualUsd += actuals[key] || 0
                     localAmt += Number(row.amount) || 0
                     if (row.amount > 0) cur = row.currency || cur; // Best effort for 'all' mode
                  }
                  
                  // For 'all' mode editing is disabled, so best effort local currency is fine
                  const rr = cur === 'USD' ? 1 : (rates[cur] || rate)
                  const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * rr)
                  
                  const varLocal = actualLocal - localAmt
                  const varUsd = actualUsd - monthlyUsd
                  
                  // Fake row for the UI inputs (only functional when a specific month is selected)
                  const row = selectedMonth === 'all' ? { amount: localAmt, currency: cur, amount_usd: monthlyUsd } : (budgets[`${a.code}-${selectedMonth}`] || { amount: 0, currency: displayCurrency, amount_usd: 0 })
"""
content = content.replace(old_detailed_body, new_detailed_body)

old_detailed_inputs = """                        <select value={row.currency || displayCurrency} onChange={e => handleRowChange(a.code, 'currency', e.target.value)}
                          className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm bg-white" disabled={!can(['owner','admin','accountant'])}>
                          {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                        </select>
                        <input type="number" value={row.amount || ''} onChange={e => handleRowChange(a.code, 'amount', e.target.value)}
                          placeholder="Amount" className="w-24 border border-slate-300 rounded-lg px-2 py-1.5 text-sm" disabled={!can(['owner','admin','accountant'])} />"""
                          
new_detailed_inputs = """                        <select value={row.currency || displayCurrency} onChange={e => handleRowChange(a.code, 'currency', e.target.value)}
                          className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm bg-white" disabled={!can(['owner','admin','accountant']) || selectedMonth === 'all'}>
                          {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                        </select>
                        <input type="number" value={row.amount || ''} onChange={e => handleRowChange(a.code, 'amount', e.target.value)}
                          placeholder={selectedMonth === 'all' ? "Select Month to Edit" : "Amount"} className="w-24 border border-slate-300 rounded-lg px-2 py-1.5 text-sm" disabled={!can(['owner','admin','accountant']) || selectedMonth === 'all'} />"""
content = content.replace(old_detailed_inputs, new_detailed_inputs)


with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
