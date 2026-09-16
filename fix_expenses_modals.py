import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# Add editingRow state
code = code.replace(
    "const [expenseModalOpen, setExpenseModalOpen] = useState(false)",
    "const [expenseModalOpen, setExpenseModalOpen] = useState(false)\n  const [editingRow, setEditingRow] = useState(null)"
)

# Modify render actions to use edit modal
code = code.replace(
    """<button onClick={() => handleDeleteEntry(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>""",
    """<div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setExpenseModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteEntry(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div>"""
)

code = code.replace(
    """<button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>""",
    """<div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setAmcModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div>"""
)

# New Expenses button should clear editingRow
code = code.replace(
    """<button onClick={() => setExpenseModalOpen(true)} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">""",
    """<button onClick={() => { setEditingRow(null); setExpenseModalOpen(true); }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">"""
)
code = code.replace(
    """<button onClick={() => setAmcModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg">""",
    """<button onClick={() => { setEditingRow(null); setAmcModalOpen(true); }} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg">"""
)


# Modify ExpenseEntryFormModal
old_exp_modal = """function ExpenseEntryFormModal({ companyId, product, accounts, onClose, onSaved }) {
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')"""

new_exp_modal = """function ExpenseEntryFormModal({ companyId, product, accounts, editingRow, onClose, onSaved }) {
  const [expenseDate, setExpenseDate] = useState(editingRow?.expense_date || new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(editingRow?.account_id || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')"""
code = code.replace(old_exp_modal, new_exp_modal)

old_exp_insert = """      const { error: err } = await supabase.from('hotel_expense_entries').insert({
        company_id: companyId, product, expense_date: expenseDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      })"""

new_exp_insert = """      const payload = {
        company_id: companyId, product, expense_date: expenseDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_expense_entries').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_expense_entries').insert(payload)
        err = error
      }"""
code = code.replace(old_exp_insert, new_exp_insert)


# Modify AmcContractFormModal
old_amc_modal = """function AmcContractFormModal({ companyId, product, onClose, onSaved }) {
  const [contractName, setContractName] = useState('')
  const [annualAmount, setAnnualAmount] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10))"""

new_amc_modal = """function AmcContractFormModal({ companyId, product, editingRow, onClose, onSaved }) {
  const [contractName, setContractName] = useState(editingRow?.contract_name || '')
  const [annualAmount, setAnnualAmount] = useState(editingRow?.annual_amount ?? '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [startDate, setStartDate] = useState(editingRow?.start_date || new Date().toISOString().slice(0, 10))"""
code = code.replace(old_amc_modal, new_amc_modal)

old_amc_insert = """      const { error: err } = await supabase.from('hotel_amc_contracts').insert({
        company_id: companyId, product, contract_name: contractName,
        annual_amount: Number(annualAmount), currency, fx_rate_locked: fxRate, annual_amount_usd: Math.round(Number(annualAmount) / fxRate * 100) / 100,
        start_date: startDate,
      })"""

new_amc_insert = """      const payload = {
        company_id: companyId, product, contract_name: contractName,
        annual_amount: Number(annualAmount), currency, fx_rate_locked: fxRate, annual_amount_usd: Math.round(Number(annualAmount) / fxRate * 100) / 100,
        start_date: startDate,
      }
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_amc_contracts').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_amc_contracts').insert(payload)
        err = error
      }"""
code = code.replace(old_amc_insert, new_amc_insert)


# Update modal props
code = code.replace(
    """<ExpenseEntryFormModal companyId={activeCompany.id} product={activeProduct} accounts={expenseAccounts} onClose={() => setExpenseModalOpen(false)} onSaved={loadAll} />""",
    """<ExpenseEntryFormModal companyId={activeCompany.id} product={activeProduct} accounts={expenseAccounts} editingRow={editingRow} onClose={() => { setExpenseModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />"""
)
code = code.replace(
    """<AmcContractFormModal companyId={activeCompany.id} product={activeProduct} onClose={() => setAmcModalOpen(false)} onSaved={loadAll} />""",
    """<AmcContractFormModal companyId={activeCompany.id} product={activeProduct} editingRow={editingRow} onClose={() => { setAmcModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />"""
)

# And missing Pencil import
code = code.replace(
    "import { Plus, Trash2, Repeat } from 'lucide-react'",
    "import { Plus, Trash2, Repeat, Pencil } from 'lucide-react'"
)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
