import re

with open('new_capital.jsx', 'r') as f:
    code = f.read()

# Patch LoanRepaymentFormModal
new_loan_rep = """function LoanRepaymentFormModal({ companyId, product, liabilityAccounts, cashAccounts, initialData, onClose, onSaved }) {
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || new Date().toISOString().slice(0, 10))
  const [loanAccountId, setLoanAccountId] = useState(initialData?.loan_account_id || liabilityAccounts[0]?.id || '')
  const [cashAccountId, setCashAccountId] = useState(initialData?.cash_account_id || cashAccounts[0]?.id || '')
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount || '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!loanAccountId || !cashAccountId || !amount || Number(amount) <= 0) { setError('Loan account, cash account, and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, payment_date: paymentDate,
        loan_account_id: loanAccountId, cash_account_id: cashAccountId,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err;
      if (initialData) {
        ({ error: err } = await supabase.from('loan_principal_payments').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('loan_principal_payments').insert(payload))
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Loan Principal Repayment" : "New Loan Principal Repayment"} onClose={onClose}>
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
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}
"""

new_div_rep = """function DividendFormModal({ companyId, product, initialData, onClose, onSaved }) {
  const [ownerName, setOwnerName] = useState(initialData?.owner_name || '')
  const [paymentDate, setPaymentDate] = useState(initialData?.payment_date || new Date().toISOString().slice(0, 10))
  const [currency, setCurrency] = useState(initialData?.currency || 'USD')
  const [amount, setAmount] = useState(initialData?.amount || '')
  const [notes, setNotes] = useState(initialData?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!ownerName.trim() || !amount || Number(amount) <= 0) { setError('Owner name and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, owner_name: ownerName.trim(), payment_date: paymentDate,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err;
      if (initialData) {
        ({ error: err } = await supabase.from('owner_dividends').update(payload).eq('id', initialData.id))
      } else {
        ({ error: err } = await supabase.from('owner_dividends').insert(payload))
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={initialData ? "Edit Owner Dividend" : "New Owner Dividend"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-xs text-slate-500 bg-slate-50 border border-slate-100 rounded-lg p-3">
          This records a dividend/withdrawal paid to an owner. It reduces Retained Earnings (Equity) and reduces Cash (Asset). It is NOT an expense.
        </p>
        <Field label="Date *">
          <input type="date" required value={paymentDate} onChange={e => setPaymentDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Owner Name *">
          <input type="text" required value={ownerName} onChange={e => setOwnerName(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
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
"""

code = re.sub(r"function LoanRepaymentFormModal\(.*?\).*?  \)\n\}", new_loan_rep, code, flags=re.DOTALL)
code = re.sub(r"function DividendFormModal\(.*?\).*?  \)\n\}", new_div_rep, code, flags=re.DOTALL)

with open('src/pages/CapitalTransactions.jsx', 'w') as f:
    f.write(code)
