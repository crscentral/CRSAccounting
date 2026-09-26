with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

old_modal = """function AmcContractFormModal({ companyId, product, onClose, onSaved }) {
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
    <Modal title="New AMC Contract" onClose={onClose}>"""

new_modal = """function AmcContractFormModal({ companyId, product, editingRow, onClose, onSaved }) {
  const [contractName, setContractName] = useState(editingRow?.contract_name || '')
  const [annualAmount, setAnnualAmount] = useState(editingRow?.annual_amount || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [startMonth, setStartMonth] = useState(editingRow?.start_month || new Date().getMonth() + 1)
  const [startYear, setStartYear] = useState(editingRow?.start_year || new Date().getFullYear())
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!contractName.trim() || Number(annualAmount) <= 0) { setError('Contract name and a positive annual amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, contract_name: contractName.trim(), annual_amount: Number(annualAmount),
        currency, fx_rate_locked: fxRate, annual_amount_usd: Math.round(Number(annualAmount) / fxRate * 100) / 100,
        start_year: startYear, start_month: startMonth, notes: notes || null,
      }
      
      let err
      if (editingRow) {
        const { error } = await supabase.from('hotel_amc_contracts').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_amc_contracts').insert(payload)
        err = error
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
    <Modal title={editingRow ? "Edit AMC Contract" : "New AMC Contract"} onClose={onClose}>"""

content = content.replace(old_modal, new_modal)

# Check for submit button label
old_button = """        <div className="flex justify-end gap-3 mt-6">
          <button type="button" onClick={onClose} className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-medium">Cancel</button>
          <button type="submit" disabled={saving} className="px-4 py-2 bg-navy-600 hover:bg-navy-700 text-white rounded-lg font-medium disabled:opacity-50">
            {saving ? 'Saving...' : 'Create Contract'}
          </button>
        </div>"""
new_button = """        <div className="flex justify-end gap-3 mt-6">
          <button type="button" onClick={onClose} className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-medium">Cancel</button>
          <button type="submit" disabled={saving} className="px-4 py-2 bg-navy-600 hover:bg-navy-700 text-white rounded-lg font-medium disabled:opacity-50">
            {saving ? 'Saving...' : (editingRow ? 'Save Changes' : 'Create Contract')}
          </button>
        </div>"""
content = content.replace(old_button, new_button)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
