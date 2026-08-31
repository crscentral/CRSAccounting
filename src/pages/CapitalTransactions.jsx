import { useEffect, useState } from 'react'
import { Plus, Trash2, Landmark, Users } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { getLatestRate } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import Modal, { Field } from '../components/Modal'
import { CURRENCY_LIST } from '../lib/currencies'

export default function CapitalTransactions() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [tab, setTab] = useState('loans')
  const [accounts, setAccounts] = useState([])
  const [loanPayments, setLoanPayments] = useState([])
  const [dividends, setDividends] = useState([])
  const [loanModalOpen, setLoanModalOpen] = useState(false)
  const [dividendModalOpen, setDividendModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct])

  async function loadAll() {
    const [{ data: acc }, { data: loans }, { data: divs }] = await Promise.all([
      supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('code'),
      supabase.from('loan_principal_payments').select('*, loan_account:accounts!loan_principal_payments_loan_account_id_fkey(name, code)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('payment_date', { ascending: false }),
      supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('payment_date', { ascending: false }),
    ])
    setAccounts(acc || [])
    setLoanPayments(loans || [])
    setDividends(divs || [])
  }

  async function handleDeleteLoan(row) {
    if (!confirm('Delete this loan principal repayment? This cannot be undone.')) return
    const { error } = await supabase.from('loan_principal_payments').delete().eq('id', row.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAll()
  }

  async function handleDeleteDividend(row) {
    if (!confirm('Delete this dividend entry? This cannot be undone.')) return
    const { error } = await supabase.from('owner_dividends').delete().eq('id', row.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAll()
  }

  if (!activeCompany) return null

  const liabilityAccounts = accounts.filter(a => a.type === 'Liabilities')
  const cashAccounts = accounts.filter(a => a.type === 'Assets')

  // Per-owner running balance of cumulative dividends paid
  const byOwner = {}
  dividends.forEach(d => {
    byOwner[d.owner_name] = byOwner[d.owner_name] || { name: d.owner_name, total: 0 }
    byOwner[d.owner_name].total += Number(d.amount_usd)
  })
  const ownerBalances = Object.values(byOwner).sort((a, b) => b.total - a.total)

  return (
    <div>
      <PageHeader
        title="Capital & Loans"
        subtitle={`${activeCompany.name} • Loan principal repayments and owner dividends — balance sheet only, never part of P&L`}
        actions={
          can(['owner', 'admin']) && (
            <button
              onClick={() => tab === 'loans' ? setLoanModalOpen(true) : setDividendModalOpen(true)}
              className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
            >
              <Plus size={16} /> {tab === 'loans' ? 'New Repayment' : 'New Dividend'}
            </button>
          )
        }
      />

      <div className="flex gap-2 mb-5">
        <button onClick={() => setTab('loans')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'loans' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Landmark size={15} /> Loan Principal Repayments
        </button>
        <button onClick={() => setTab('dividends')} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${tab === 'dividends' ? 'bg-navy-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
          <Users size={15} /> Owner Dividends
        </button>
      </div>

      {tab === 'loans' ? (
        <DataTable
          columns={[
            { key: 'payment_date', label: 'Date' },
            { key: 'loan_account', label: 'Loan Account', render: r => r.loan_account ? `${r.loan_account.code} - ${r.loan_account.name}` : '—' },
            { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
            { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
            ...(can(['owner', 'admin', 'accountant']) ? [{
              key: 'actions', label: '', render: r => <button onClick={() => handleDeleteLoan(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
            }] : []),
          ]}
          rows={loanPayments}
          emptyMessage="No loan principal repayments recorded. This tracks only the principal portion — record Loan Interest as a normal expense via Purchase Invoices instead, since interest (not principal) belongs in the P&L."
        />
      ) : (
        <>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {ownerBalances.map(o => (
              <div key={o.name} className="bg-white rounded-xl border border-slate-200 p-4">
                <div className="text-sm font-medium text-slate-700">{o.name}</div>
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
                key: 'actions', label: '', render: r => <button onClick={() => handleDeleteDividend(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
              }] : []),
            ]}
            rows={dividends}
            emptyMessage="No owner dividend entries yet."
          />
        </>
      )}

      {loanModalOpen && (
        <LoanRepaymentFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          liabilityAccounts={liabilityAccounts}
          cashAccounts={cashAccounts}
          onClose={() => setLoanModalOpen(false)}
          onSaved={loadAll}
        />
      )}

      {dividendModalOpen && (
        <DividendFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          onClose={() => setDividendModalOpen(false)}
          onSaved={loadAll}
        />
      )}
    </div>
  )
}

function LoanRepaymentFormModal({ companyId, product, liabilityAccounts, cashAccounts, onClose, onSaved }) {
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().slice(0, 10))
  const [loanAccountId, setLoanAccountId] = useState(liabilityAccounts[0]?.id || '')
  const [cashAccountId, setCashAccountId] = useState(cashAccounts[0]?.id || '')
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!loanAccountId || !cashAccountId || !amount || Number(amount) <= 0) { setError('Loan account, cash account, and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const { error: err } = await supabase.from('loan_principal_payments').insert({
        company_id: companyId, product, payment_date: paymentDate,
        loan_account_id: loanAccountId, cash_account_id: cashAccountId,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
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

  return (
    <Modal title="New Loan Principal Repayment" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          This records only the principal portion of an EMI/loan payment — it reduces the loan balance and your cash, but is NOT an expense. If your payment also includes interest, record that separately as a normal expense (e.g. via a Purchase Invoice against a "Loan Interest" account).
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Loan Account (Liability) *">
          <select required value={loanAccountId} onChange={e => setLoanAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select loan account…</option>
            {liabilityAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <Field label="Paid From (Cash/Bank Account) *">
          <select required value={cashAccountId} onChange={e => setCashAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select cash account…</option>
            {cashAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Principal Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Add Repayment'}</button>
        </div>
      </form>
    </Modal>
  )
}

function DividendFormModal({ companyId, product, onClose, onSaved }) {
  const [ownerName, setOwnerName] = useState('')
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().slice(0, 10))
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!ownerName.trim() || !amount || Number(amount) <= 0) { setError('Owner name and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const { error: err } = await supabase.from('owner_dividends').insert({
        company_id: companyId, product, owner_name: ownerName.trim(), payment_date: paymentDate,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
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

  return (
    <Modal title="New Owner Dividend" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Owner Name *">
          <input required value={ownerName} onChange={e => setOwnerName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Sumant Singh" />
        </Field>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
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
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Add Dividend'}</button>
        </div>
      </form>
    </Modal>
  )
}
