import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Replace the Draft Expenses block wrapper
old_draft_expenses = r'<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">\s*<h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">\s*<AlertCircle size=\{18\} className="text-slate-400" /> Draft Expenses \(\{draftExpenses\.length\}\)\s*</h2>\s*<div className="overflow-x-auto">\s*<table className="w-full min-w-\[600px\] text-left border-collapse">\s*<thead>.*?</table>\s*</div>\s*</div>'

new_draft_expenses = """{activeProduct !== 'hotel' && (
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <AlertCircle size={18} className="text-slate-400" /> Draft Expenses ({draftExpenses.length})
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px] text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/50">
                <th className="py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase">Expense #</th>
                <th className="py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase">Vendor</th>
                <th className="py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase">Due Date</th>
                <th className="py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase">Amount</th>
                <th className="py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase">Amount (USD)</th>
                <th className="py-2.5 px-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody>
              {draftExpenses.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-400 text-sm">
                    No draft expenses.
                  </td>
                </tr>
              ) : (
                draftExpenses.map(i => (
                  <tr key={i.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="py-2.5 px-3 text-sm text-slate-700 font-medium">{i.invoice_number}</td>
                    <td className="py-2.5 px-3 text-sm text-slate-600">{i.contact?.name || '—'}</td>
                    <td className="py-2.5 px-3 text-sm text-slate-600">{i.due_date}</td>
                    <td className="py-2.5 px-3 text-sm text-slate-600 font-medium">{cp.fmt(i.amount_usd)}</td>
                    <td className="py-2.5 px-3 text-sm text-slate-700 font-semibold">{cp.fmt(i.amount_usd)}</td>
                    <td className="py-2.5 px-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
                        Draft
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      )}"""

code = re.sub(old_draft_expenses, new_draft_expenses, code, flags=re.DOTALL)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
