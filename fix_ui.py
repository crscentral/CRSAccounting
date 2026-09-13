import re
with open('src/pages/CapitalTransactions.jsx', 'r') as f:
    code = f.read()

new_tabs = """      <div className="flex flex-wrap gap-2 mb-5">
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
      </div>"""

code = re.sub(
    r"      <div className=\"flex gap-2 mb-5\">.*?</div>",
    new_tabs,
    code,
    flags=re.DOTALL
)

actions_header = """          <div className="flex gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <button onClick={() => { setEditItem(null); if (tab === 'equity') setContributionModalOpen(true); else if (tab === 'loans_taken') setLoanTakenModalOpen(true); else if (tab === 'dividends') setDividendModalOpen(true); else setLoanModalOpen(true); }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
              <Plus size={16} /> New Entry
            </button>
          </div>"""
          
code = re.sub(
    r"          <div className=\"flex items-center gap-2\">.*?</div>",
    actions_header,
    code,
    flags=re.DOTALL
)

with open('src/pages/CapitalTransactions.jsx', 'w') as f:
    f.write(code)
