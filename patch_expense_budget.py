import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

# 1. Update monthlySummary logic
old_summary = """  const monthlySummary = useMemo(() => {
    const summary = []
    let totalBudget = 0
    let totalActual = 0
    
    for (let m = 1; m <= 12; m++) {
      let mBudget = 0
      let mActual = 0
      for (const a of accounts) {
        const k = `${a.code}-${m}`
        if (budgets[k]) mBudget += Number(budgets[k].amount_usd) || 0
        if (actuals[k]) mActual += Number(actuals[k]) || 0
      }
      totalBudget += mBudget
      totalActual += mActual
      summary.push({ month: m, name: MONTH_NAMES[m - 1], budget: mBudget, actual: mActual, variance: mActual - mBudget })
    }
    return { months: summary, totalBudget, totalActual, totalVariance: totalActual - totalBudget }
  }, [budgets, actuals, accounts])"""

new_summary = """  const monthlySummary = useMemo(() => {
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
content = content.replace(old_summary, new_summary)

# 2. Update KPI cards and remove old Select Year div
old_kpi = """      <div className="flex items-center gap-3 mb-6 bg-slate-50 p-3 rounded-xl border border-slate-200">
        <span className="text-sm font-medium text-slate-600">Select Year:</span>
        <select value={selectedYear} onChange={e => setSelectedYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
          {Array.from({ length: 11 }, (_, i) => new Date().getFullYear() - 5 + i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${selectedYear} Total Actual`} value={fmt(monthlySummary.totalActual)} icon={TrendingUp} tone="green" />
        <KpiCard label={`${selectedYear} Total Variance`} value={fmt(monthlySummary.totalVariance)} icon={AlertTriangle} tone={monthlySummary.totalVariance > 0 ? "red" : "green"} />
      </div>"""

new_kpi = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedYear} Front Office Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" sublabel="Front Office Accounts" />
        <KpiCard label={`${selectedYear} F&B Expenses Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" sublabel="F&B Accounts" />
        <KpiCard label={`${selectedYear} Other Expenses Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" sublabel="Other Expenses" />
        <KpiCard label={`Total ${selectedYear} Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" sublabel="Combined Expenses" />
      </div>"""
content = content.replace(old_kpi, new_kpi)

# 3. Add Period dropdown to PageHeader actions
old_header = """        actions={
          <div className="flex items-center gap-3">
            <button onClick={() => setReportModalOpen(true)} className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors shadow-sm">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </div>
        }"""

new_header = """        actions={
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 bg-white border border-slate-300 rounded-lg px-2 py-1">
              <span className="text-sm text-slate-500 ml-1">Period:</span>
              <select value={selectedYear} onChange={e => setSelectedYear(Number(e.target.value))} className="bg-transparent text-sm font-medium focus:outline-none">
                {Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
            <button onClick={() => setReportModalOpen(true)} className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors shadow-sm">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </div>
        }"""
content = content.replace(old_header, new_header)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
