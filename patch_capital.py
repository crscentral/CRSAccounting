import re

with open('src/pages/CapitalTransactions.jsx', 'r') as f:
    code = f.read()

# 1. Insert calculation logic before `return`
calc_logic = """  const currentList = tab === 'equity' ? ownerContributions :
                      tab === 'loans_taken' ? loansTaken :
                      tab === 'dividends' ? dividends :
                      loanPayments

  const byCurrency = {}
  let totalUsd = 0
  currentList.forEach(i => {
    byCurrency[i.currency] = byCurrency[i.currency] || { native: 0, usd: 0, count: 0 }
    byCurrency[i.currency].native += Number(i.amount)
    byCurrency[i.currency].usd += Number(i.amount_usd)
    byCurrency[i.currency].count++
    totalUsd += Number(i.amount_usd)
  })

  return ("""

code = code.replace("  return (", calc_logic)

# 2. Insert the widget below the tabs (before the `tab === 'equity'` block)
widget_ui = """      <div className="flex flex-wrap gap-2 mb-5">
        <button onClick={() => setTab('equity')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'equity' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Users size={15} /> Owner's Equity
        </button>
        <button onClick={() => setTab('loans_taken')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'loans_taken' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loans Taken
        </button>
        <button onClick={() => setTab('loans')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'loans' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loan Principal Repayments
        </button>
        <button onClick={() => setTab('dividends')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'dividends' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Users size={15} /> Owner Dividends
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-4">Currency Summary ({cp.displayCurrency} Consolidated)</h3>
        {Object.keys(byCurrency).length === 0 ? (
          <p className="text-sm text-slate-400">No transactions to summarize.</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(byCurrency).map(([code, v]) => (
              <div key={code} className="flex items-center justify-between text-sm flex-wrap gap-1">
                <div>
                  <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium mr-2">{code}</span>
                  <span className="text-slate-500">{v.native.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} • {v.count} entry(s)</span>
                </div>
                <span className="font-semibold text-slate-700">{cp.fmt(v.usd)}</span>
              </div>
            ))}
            <div className="flex items-center justify-between pt-3 border-t border-slate-100 font-bold text-emerald-700">
              <span>Grand Total ({cp.displayCurrency})</span>
              <span>{cp.fmt(totalUsd)}</span>
            </div>
          </div>
        )}
      </div>
"""

code = re.sub(
    r"      <div className=\"flex flex-wrap gap-2 mb-5\">.*?</div>\n",
    widget_ui,
    code,
    flags=re.DOTALL
)

with open('src/pages/CapitalTransactions.jsx', 'w') as f:
    f.write(code)
