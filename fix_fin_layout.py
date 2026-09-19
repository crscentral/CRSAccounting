import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

# Fix Expenses table wrapping
code = code.replace('<th className="py-2 font-medium">Code</th>', '<th className="py-2 font-medium whitespace-nowrap">Code</th>')
code = code.replace('<th className="py-2 font-medium">Account</th>', '<th className="py-2 font-medium whitespace-nowrap">Account</th>')
code = code.replace('<th className="py-2 font-medium text-right">Amount</th>', '<th className="py-2 font-medium text-right whitespace-nowrap">Amount</th>')
code = code.replace('<th className="py-2 font-medium text-right">% of Total</th>', '<th className="py-2 font-medium text-right whitespace-nowrap">% of Total</th>')
code = code.replace('<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">', '<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 overflow-x-auto">')

# Fix Forecast layout
old_forecast = """        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-3">
            <h3 className="font-semibold text-slate-700">Monthly Forecast — {forecastYear}</h3>
            <div className="flex items-center gap-2">
              <select value={forecastYear} onChange={e => setForecastYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                {Array.from({ length: 6 }, (_, i) => new Date().getFullYear() + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <button onClick={() => setForecastReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-xs font-medium px-3 py-2 rounded-lg hover:border-navy-400">
                <Download size={13} /> Download
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 items-center pb-2 border-b border-slate-100 text-xs font-medium text-slate-400 uppercase tracking-wider">
            <span>Month</span>
            <span>Forecast Revenue</span>
            <span>Forecast Expenses</span>
            <span>Projected Profit</span>
            <span>Profit Margin %</span>
          </div>
          <div className="space-y-2">
            {MONTHS.map((m, i) => {"""

new_forecast = """        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-3">
            <h3 className="font-semibold text-slate-700">Monthly Forecast — {forecastYear}</h3>
            <div className="flex items-center gap-2">
              <select value={forecastYear} onChange={e => setForecastYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm">
                {Array.from({ length: 6 }, (_, i) => new Date().getFullYear() + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <button onClick={() => setForecastReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-xs font-medium px-3 py-2 rounded-lg hover:border-navy-400">
                <Download size={13} /> Download
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[650px]">
              <div className="grid grid-cols-5 gap-4 items-center pb-2 border-b border-slate-100 text-xs font-medium text-slate-400 uppercase tracking-wider">
                <span>Month</span>
                <span>Forecast Revenue</span>
                <span>Forecast Expenses</span>
                <span>Projected Profit</span>
                <span>Profit Margin %</span>
              </div>
              <div className="space-y-2">
                {MONTHS.map((m, i) => {"""

code = code.replace(old_forecast, new_forecast)

# And close the tags properly
old_close = """          </div>
        </div>
      )}

      {reportModalOpen && ("""

new_close = """              </div>
            </div>
          </div>
        </div>
      )}

      {reportModalOpen && ("""
code = code.replace(old_close, new_close)


old_row = """  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 items-center py-2 border-b border-slate-50 last:border-0">
      <span className="text-sm text-slate-600 font-medium">{label}</span>"""

new_row = """  return (
    <div className="grid grid-cols-5 gap-4 items-center py-2 border-b border-slate-50 last:border-0">
      <span className="text-sm text-slate-600 font-medium whitespace-nowrap">{label}</span>"""
code = code.replace(old_row, new_row)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(code)
