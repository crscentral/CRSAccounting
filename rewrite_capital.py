import re

with open('old_capital.jsx', 'r') as f:
    code = f.read()

# Replace state and loadAll
new_state_and_load = """  const [tab, setTab] = useState('equity')
  const [accounts, setAccounts] = useState([])
  const [loanPayments, setLoanPayments] = useState([])
  const [dividends, setDividends] = useState([])
  const [ownerContributions, setOwnerContributions] = useState([])
  const [loansTaken, setLoansTaken] = useState([])
  
  const [loanModalOpen, setLoanModalOpen] = useState(false)
  const [dividendModalOpen, setDividendModalOpen] = useState(false)
  const [contributionModalOpen, setContributionModalOpen] = useState(false)
  const [loanTakenModalOpen, setLoanTakenModalOpen] = useState(false)
  
  const [editItem, setEditItem] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadAll() {
    const [{ data: acc }, { data: loans }, { data: divs }, { data: contribs }, { data: taken }] = await Promise.all([
      supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('code'),
      supabase.from('loan_principal_payments').select('*, loan_account:accounts!loan_principal_payments_loan_account_id_fkey(name, code)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
      supabase.from('loans_taken').select('*, loan_account:accounts!loans_taken_loan_account_id_fkey(name, code)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to).order('payment_date', { ascending: false }),
    ])
    setAccounts(acc || [])
    setLoanPayments(loans || [])
    setDividends(divs || [])
    setOwnerContributions(contribs || [])
    setLoansTaken(taken || [])
  }

  async function handleDelete(table, id) {
    if (!confirm('Delete this entry? This cannot be undone.')) return
    const { error } = await supabase.from(table).delete().eq('id', id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAll()
  }
"""
# Replace the state section
code = re.sub(
    r"  const \[tab, setTab\].*?  async function handleDeleteDividend\(row\) \{.*?\}", 
    new_state_and_load, 
    code, 
    flags=re.DOTALL
)

# Now fix generateCapitalReport
new_report_logic = """  async function generateCapitalReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const sections = []
    if (selections.sections.includes("Owner's Equity (Contributions)")) {
      const { data } = await supabase.from('owner_contributions').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: "Owner's Equity (Contributions)",
        columns: ['Date', 'Owner', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.owner_name, `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Loans Taken')) {
      const { data } = await supabase.from('loans_taken').select('*, loan_account:accounts!loans_taken_loan_account_id_fkey(name, code)')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Loans Taken',
        columns: ['Date', 'Loan Account', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—', `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Loan Principal Repayments')) {
      const { data } = await supabase.from('loan_principal_payments').select('*, loan_account:accounts!loan_principal_payments_loan_account_id_fkey(name, code)')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Loan Principal Repayments',
        columns: ['Date', 'Loan Account', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—', `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }
    if (selections.sections.includes('Owner Dividends')) {
      const { data } = await supabase.from('owner_dividends').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to).order('payment_date', { ascending: false })
      sections.push({
        heading: 'Owner Dividends',
        columns: ['Date', 'Owner', 'Amount', `Amount (${selections.currency})`, 'Notes'],
        rows: (data || []).map(r => [r.payment_date, r.owner_name, `${r.amount} ${r.currency}`, f(r.amount_usd), r.notes || '—']),
      })
    }

    const title = 'Capital & Loans'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'capital_loans_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'capital_loans_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'capital_loans_report' })
  }
"""
code = re.sub(
    r"  async function generateCapitalReport\(selections, format\) \{.*?  if \(!activeCompany\) return null",
    new_report_logic + "\n  if (!activeCompany) return null",
    code,
    flags=re.DOTALL
)

# Tabs
new_tabs = """        <div className="flex flex-wrap gap-2 mb-6">
          <button onClick={() => setTab('equity')} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${tab === 'equity' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
            <Users size={16} /> Owner's Equity
          </button>
          <button onClick={() => setTab('loans_taken')} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${tab === 'loans_taken' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
            <Landmark size={16} /> Loans Taken
          </button>
          <button onClick={() => setTab('dividends')} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${tab === 'dividends' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
            <Users size={16} /> Owner Dividends
          </button>
          <button onClick={() => setTab('loans')} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${tab === 'loans' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
            <Landmark size={16} /> Loan Principal Repayments
          </button>
        </div>"""
code = re.sub(
    r"        <div className=\"flex gap-2 mb-6\">.*?</div>",
    new_tabs,
    code,
    flags=re.DOTALL
)

# Right Actions Header
actions_header = """          <div className="flex gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-4 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <button onClick={() => { setEditItem(null); if (tab === 'equity') setContributionModalOpen(true); else if (tab === 'loans_taken') setLoanTakenModalOpen(true); else if (tab === 'dividends') setDividendModalOpen(true); else setLoanModalOpen(true); }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
              <Plus size={16} /> New Entry
            </button>
          </div>"""
code = re.sub(
    r"          <div className=\"flex gap-2\">.*?</div>",
    actions_header,
    code,
    flags=re.DOTALL
)

# Render Blocks
render_blocks = """
      {tab === 'equity' && (
        <>
          <p className="text-sm text-slate-500 mb-4 px-1">Record capital contributions made by owners into the business.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'owner_name', label: 'Owner' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setContributionModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('owner_contributions', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={ownerContributions}
            emptyMessage="No owner contributions recorded."
          />
        </>
      )}

      {tab === 'loans_taken' && (
        <>
          <p className="text-sm text-slate-500 mb-4 px-1">Record new loans received by the business.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'loan_account', label: 'Loan Account', render: r => r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setLoanTakenModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('loans_taken', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={loansTaken}
            emptyMessage="No loans taken recorded."
          />
        </>
      )}

      {tab === 'loans' && (
        <>
          <p className="text-sm text-slate-500 mb-4 px-1">No loan principal repayments recorded. This tracks only the principal portion — record Loan Interest as a normal expense via Purchase Invoices instead, since interest (not principal) belongs in the P&L.</p>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'loan_account', label: 'Loan Account', render: r => r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setLoanModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('loan_principal_payments', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={loanPayments}
            emptyMessage="No loan principal repayments recorded."
          />
        </>
      )}

      {tab === 'dividends' && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {ownerBalances.map(o => (
              <div key={o.name} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                <div className="text-sm font-semibold text-slate-600">{o.name}</div>
                <div className="text-xl font-bold text-slate-800 mt-1">{cp.fmt(o.total)}</div>
                <div className="text-xs text-slate-400 mt-1">Total dividends paid</div>
              </div>
            ))}
          </div>
          <DataTable
            columns={[
              { key: 'payment_date', label: 'Date' },
              { key: 'owner_name', label: 'Owner' },
              { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin']) ? [{
                key: 'actions', label: '', render: r => <div className="flex justify-end gap-2 text-slate-400">
                  <button onClick={() => { setEditItem(r); setDividendModalOpen(true) }} className="hover:text-emerald-600">Edit</button>
                  <button onClick={() => handleDelete('owner_dividends', r.id)} className="hover:text-red-600"><Trash2 size={15} /></button>
                </div>
              }] : []),
            ]}
            rows={dividends}
            emptyMessage="No owner dividend entries yet."
          />
        </>
      )}
"""
code = re.sub(
    r"      \{tab === 'loans'.*?      \)}",
    render_blocks,
    code,
    flags=re.DOTALL
)

# Modals
modals = """
      {contributionModalOpen && (
        <OwnerEquityFormModal companyId={activeCompany.id} product={activeProduct} initialData={editItem} cashAccounts={cashAccounts} onClose={() => setContributionModalOpen(false)} onSaved={loadAll} />
      )}
      {loanTakenModalOpen && (
        <LoanTakenFormModal companyId={activeCompany.id} product={activeProduct} initialData={editItem} liabilityAccounts={liabilityAccounts} cashAccounts={cashAccounts} onClose={() => setLoanTakenModalOpen(false)} onSaved={loadAll} />
      )}
      {loanModalOpen && (
        <LoanRepaymentFormModal companyId={activeCompany.id} product={activeProduct} initialData={editItem} liabilityAccounts={liabilityAccounts} cashAccounts={cashAccounts} onClose={() => setLoanModalOpen(false)} onSaved={loadAll} />
      )}
      {dividendModalOpen && (
        <DividendFormModal companyId={activeCompany.id} product={activeProduct} initialData={editItem} cashAccounts={cashAccounts} onClose={() => setDividendModalOpen(false)} onSaved={loadAll} />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Capital & Loans"
          fields={[
            { type: 'checkboxGroup', key: 'sections', label: 'Include Sections', options: ["Owner's Equity (Contributions)", 'Loans Taken', 'Loan Principal Repayments', 'Owner Dividends'], default: ["Owner's Equity (Contributions)", 'Loans Taken', 'Loan Principal Repayments', 'Owner Dividends'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateCapitalReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
"""
code = re.sub(
    r"      \{loanModalOpen.*?      \)}",
    modals,
    code,
    flags=re.DOTALL
)

with open('new_capital.jsx', 'w') as f:
    f.write(code)
