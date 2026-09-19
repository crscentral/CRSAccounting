with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

# Fix Expenses wrapping
code = code.replace('<th className="py-2 font-medium">Code</th>', '<th className="py-2 font-medium whitespace-nowrap">Code</th>')
code = code.replace('<th className="py-2 font-medium">Account</th>', '<th className="py-2 font-medium whitespace-nowrap">Account</th>')
code = code.replace('<th className="py-2 font-medium text-right">Amount</th>', '<th className="py-2 font-medium text-right whitespace-nowrap">Amount</th>')
code = code.replace('<th className="py-2 font-medium text-right">% of Total</th>', '<th className="py-2 font-medium text-right whitespace-nowrap">% of Total</th>')
code = code.replace('<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">', '<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 overflow-x-auto">')

old_forecast = """          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 items-center pb-2 border-b border-slate-100 text-xs font-medium text-slate-400 uppercase tracking-wider">
            <span>Month</span>
            <span>Forecast Revenue</span>
            <span>Forecast Expenses</span>
            <span>Projected Profit</span>
            <span>Profit Margin %</span>
          </div>
          <div className="space-y-2">"""

new_forecast = """          <div className="overflow-x-auto">
            <div className="min-w-[650px]">
              <div className="grid grid-cols-5 gap-4 items-center pb-2 border-b border-slate-100 text-xs font-medium text-slate-400 uppercase tracking-wider">
                <span>Month</span>
                <span>Forecast Revenue</span>
                <span>Forecast Expenses</span>
                <span>Projected Profit</span>
                <span>Profit Margin %</span>
              </div>
              <div className="space-y-2">"""
code = code.replace(old_forecast, new_forecast)

old_close = """          </div>
        </div>
      )}"""

new_close = """              </div>
            </div>
          </div>
        </div>
      )}"""
# Only replace the last occurrence to avoid matching other tabs!
parts = code.rsplit(old_close, 1)
code = new_close.join(parts)


old_row = """  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 items-center py-2 border-b border-slate-50 last:border-0">"""

new_row = """  return (
    <div className="grid grid-cols-5 gap-4 items-center py-2 border-b border-slate-50 last:border-0">"""
code = code.replace(old_row, new_row)

old_label = """<span className="text-sm text-slate-600 font-medium">{label}</span>"""
new_label = """<span className="text-sm text-slate-600 font-medium whitespace-nowrap">{label}</span>"""
code = code.replace(old_label, new_label)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(code)
