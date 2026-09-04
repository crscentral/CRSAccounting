import { useEffect, useState } from 'react'
import { Plus, Trash2, Repeat } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod, MONTH_NAMES } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'
import KpiCard from '../components/KpiCard'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import AccountFormModal from '../components/AccountFormModal'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function HotelExpenses() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [expenseModalOpen, setExpenseModalOpen] = useState(false)
  const [amcModalOpen, setAmcModalOpen] = useState(false)
  const [newHeadModalOpen, setNewHeadModalOpen] = useState(false)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [entries, setEntries] = useState([])
  const [amcContracts, setAmcContracts] = useState([])
  const [expenseAccounts, setExpenseAccounts] = useState([])

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadAll() {
    const [{ data: exp }, { data: amc }, { data: accs }] = await Promise.all([
      supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to).order('expense_date', { ascending: false }),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('created_at', { ascending: false }),
      supabase.from('accounts').select('id, code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code'),
    ])
    setEntries(exp || [])
    setAmcContracts(amc || [])
    setExpenseAccounts(accs || [])
  }

  async function handleDeleteEntry(row) {
    if (!confirm('Delete this expense entry?')) return
    await supabase.from('hotel_expense_entries').delete().eq('id', row.id)
    loadAll()
  }
  async function handleDeleteAmc(row) {
    if (!confirm(`Delete AMC contract "${row.contract_name}"? This removes all 12 monthly postings.`)) return
    await supabase.from('hotel_amc_contracts').delete().eq('id', row.id)
    loadAll()
  }

  async function generateExpensesReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)
    const { data: exp } = await supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to).order('expense_date', { ascending: false })
    const sections = [{
      heading: 'Expenses',
      columns: ['Date', 'Expense Head', 'Amount', 'Notes'],
      rows: (exp || []).map(r => [r.expense_date, r.account ? `${r.account.code} - ${r.account.name}` : '—', f(r.amount_usd), r.notes || '—']),
    }]
    const title = 'Hotel Expenses'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'hotel_expenses' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_expenses' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_expenses' })
  }

  if (!activeCompany) return null

  const totalExpenses = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const byHead = {}
  entries.forEach(r => {
    const key = r.account?.name || 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })
  const topHeads = Object.entries(byHead).sort((a, b) => b[1] - a[1]).slice(0, 3)

  return (
    <div>
      <PageHeader
        title="Expenses"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button onClick={() => setAmcModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg">
                  <Repeat size={15} /> New AMC Contract
                </button>
                <button onClick={() => setExpenseModalOpen(true)} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={15} /> New Expense
                </button>
              </>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        {topHeads.map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}
      </div>

      <h3 className="font-semibold text-slate-700 mb-3 flex items-center justify-between">
        <span>Expense Entries</span>
        {can(['owner', 'admin', 'accountant']) && (
          <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
        )}
      </h3>
      <DataTable
        columns={[
          { key: 'expense_date', label: 'Date' },
          { key: 'account', label: 'Expense Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <button onClick={() => handleDeleteEntry(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button> }] : []),
        ]}
        rows={entries}
        emptyMessage="No expense entries in this range."
      />

      <h3 className="font-semibold text-slate-700 mb-3 mt-6">AMC Contracts (auto-split across 12 months)</h3>
      <DataTable
        columns={[
          { key: 'contract_name', label: 'Contract' },
          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => cp.fmt(r.annual_amount_usd) },
          { key: 'monthly', label: 'Monthly', render: r => cp.fmt(r.annual_amount_usd / 12) },
          { key: 'start', label: 'Starts', render: r => `${MONTH_NAMES[r.start_month - 1]} ${r.start_year}` },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button> }] : []),
        ]}
        rows={amcContracts}
        emptyMessage="No AMC contracts yet."
      />

      {expenseModalOpen && (
        <ExpenseEntryFormModal companyId={activeCompany.id} product={activeProduct} accounts={expenseAccounts} onClose={() => setExpenseModalOpen(false)} onSaved={loadAll} />
      )}
      {amcModalOpen && (
        <AmcContractFormModal companyId={activeCompany.id} product={activeProduct} onClose={() => setAmcModalOpen(false)} onSaved={loadAll} />
      )}
      {newHeadModalOpen && (
        <AccountFormModal companyId={activeCompany.id} product={activeProduct} account={{ type: 'Expenses', subtype: 'Hotel Operating Expenses' }} onClose={() => setNewHeadModalOpen(false)} onSaved={loadAll} />
      )}
      {reportModalOpen && (
        <ReportOptionsModal
          title="Expenses"
          fields={[{ type: 'currency', key: 'currency', default: cp.displayCurrency }, { type: 'period', key: 'period', default: 'ALL_TIME' }]}
          onGenerate={generateExpensesReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function ExpenseEntryFormModal({ companyId, product, accounts, onClose, onSaved }) {
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!accountId || Number(amount) <= 0) { setError('Expense head and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const { error: err } = await supabase.from('hotel_expense_entries').insert({
        company_id: companyId, product, expense_date: expenseDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      })
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const grouped = {}
  accounts.forEach(a => { grouped[a.subtype || 'Other'] = grouped[a.subtype || 'Other'] || []; grouped[a.subtype || 'Other'].push(a) })

  return (
    <Modal title="New Expense" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Date *">
          <input type="date" required value={expenseDate} onChange={e => setExpenseDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Expense Head *">
          <select required value={accountId} onChange={e => setAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select…</option>
            {Object.entries(grouped).map(([group, accs]) => (
              <optgroup key={group} label={group}>
                {accs.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
              </optgroup>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}

function AmcContractFormModal({ companyId, product, onClose, onSaved }) {
  const [contractName, setContractName] = useState('')
  const [annualAmount, setAnnualAmount] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [startMonth, setStartMonth] = useState(new Date().getMonth() + 1)
  const [startYear, setStartYear] = useState(new Date().getFullYear())
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!contractName.trim() || Number(annualAmount) <= 0) { setError('Contract name and a positive annual amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const { error: err } = await supabase.from('hotel_amc_contracts').insert({
        company_id: companyId, product, contract_name: contractName.trim(), annual_amount: Number(annualAmount),
        currency, fx_rate_locked: fxRate, annual_amount_usd: Math.round(Number(annualAmount) / fxRate * 100) / 100,
        start_year: startYear, start_month: startMonth, notes: notes || null,
      })
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title="New AMC Contract" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          Enter the annual contract value once — it automatically posts as 12 equal monthly expense entries starting from the month you choose.
        </p>
        <Field label="Contract Name / Type *">
          <input required value={contractName} onChange={e => setContractName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Elevator AMC, HVAC AMC" />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Annual Amount *">
            <input type="number" step="0.01" min="0" required value={annualAmount} onChange={e => setAnnualAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Start Month">
            <select value={startMonth} onChange={e => setStartMonth(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
            </select>
          </Field>
          <Field label="Start Year">
            <input type="number" value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Create Contract'}</button>
        </div>
      </form>
    </Modal>
  )
}
