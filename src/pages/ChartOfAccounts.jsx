import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import AccountFormModal from '../components/AccountFormModal'

const TYPE_COLORS = {
  Assets: 'bg-blue-100 text-blue-700',
  Liabilities: 'bg-rose-100 text-rose-700',
  Equity: 'bg-purple-100 text-purple-700',
  Revenue: 'bg-emerald-100 text-emerald-700',
  Expenses: 'bg-amber-100 text-amber-700',
}

export default function ChartOfAccounts() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [accounts, setAccounts] = useState([])
  const [filter, setFilter] = useState('All')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAccounts() }, [activeCompany, activeProduct])

  async function loadAccounts() {
    const { data } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('code')
    setAccounts(data || [])
  }

  async function handleDelete(account) {
    if (!confirm(`Delete account ${account.code} - ${account.name}? This cannot be undone.`)) return
    const { error } = await supabase.from('accounts').delete().eq('id', account.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAccounts()
  }


  async function generateAccountsReport(selections, format) {
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const scoped = selections.accountType === 'All' ? accounts : accounts.filter(a => a.type === selections.accountType)
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id)
    const balances = {}
    ;(entries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })

    const sections = [{
      heading: selections.accountType === 'All' ? 'All Accounts' : `${selections.accountType} Accounts`,
      columns: ['Code', 'Name', 'Type', 'Subtype', `Balance (${selections.currency})`],
      rows: scoped.map(a => [a.code, a.name, a.type, a.subtype || '—', fmt(balances[a.id] || 0)]),
    }]

    const title = 'Chart of Accounts'
    const subtitle = `${activeCompany.name} • ${selections.accountType} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'chart_of_accounts' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'chart_of_accounts' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'chart_of_accounts' })
  }

  if (!activeCompany) return null

  const filtered = filter === 'All' ? accounts : accounts.filter(a => a.type === filter)
  const counts = accounts.reduce((acc, a) => { acc[a.type] = (acc[a.type] || 0) + 1; return acc }, {})

  return (
    <div>
      <PageHeader
        title="Chart of Accounts"
        subtitle={`${activeCompany.name} • ${accounts.length} accounts`}
        currencyProps={cp.currencyProps}
        actions={
          <div className="flex gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingAccount(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                <Plus size={16} /> New Account
              </button>
            )}
          </div>
        }
      />

      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {['All', 'Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses'].map(t => (
          <button key={t} onClick={() => setFilter(t)}
            className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium border ${filter === t ? 'bg-navy-600 text-white border-navy-600' : 'bg-white text-slate-600 border-slate-200'}`}>
            {t}{t !== 'All' ? ` (${counts[t] || 0})` : ` (${accounts.length})`}
          </button>
        ))}
      </div>

      <DataTable
        columns={[
          { key: 'code', label: 'Code' },
          { key: 'name', label: 'Name' },
          { key: 'type', label: 'Type', render: r => <span className={`px-2 py-0.5 rounded text-xs font-medium ${TYPE_COLORS[r.type]}`}>{r.type}</span> },
          { key: 'subtype', label: 'Subtype', render: r => r.subtype || '—' },
          { key: 'currency', label: 'Currency' },
          ...(can(['owner', 'admin', 'accountant']) ? [{
            key: 'actions', label: '', render: r => (
              <div className="flex gap-2 justify-end md:justify-start">
                <button onClick={() => { setEditingAccount(r); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
                <button onClick={() => handleDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            )
          }] : []),
        ]}
        rows={filtered}
      />

      {modalOpen && (
        <AccountFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          account={editingAccount}
          onClose={() => setModalOpen(false)}
          onSaved={loadAccounts}
        />
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Chart of Accounts"
          fields={[
            { type: 'radio', key: 'accountType', label: 'Account Type', options: ['All', 'Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses'], default: 'All' },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
          ]}
          onGenerate={generateAccountsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
