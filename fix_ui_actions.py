import re
with open('src/pages/CapitalTransactions.jsx', 'r') as f:
    code = f.read()

actions_header = """          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin']) && (
              <button
                onClick={() => { setEditItem(null); if (tab === 'equity') setContributionModalOpen(true); else if (tab === 'loans_taken') setLoanTakenModalOpen(true); else if (tab === 'dividends') setDividendModalOpen(true); else setLoanModalOpen(true); }}
                className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
              >
                <Plus size={16} /> New Entry
              </button>
            )}
          </div>"""

code = re.sub(
    r"          <div className=\"flex flex-wrap gap-2\">.*?          </div>",
    actions_header,
    code,
    flags=re.DOTALL
)

with open('src/pages/CapitalTransactions.jsx', 'w') as f:
    f.write(code)
