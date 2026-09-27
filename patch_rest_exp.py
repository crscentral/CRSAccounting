import os
import re

with open('src/pages/RestaurantExpenses.jsx', 'r') as f:
    content = f.read()

# 1. Imports
import_lines = "import PurchaseInvoiceFormModal from '../components/PurchaseInvoiceFormModal'\nimport { FileText } from 'lucide-react'\n"
content = content.replace("import AccountFormModal from '../components/AccountFormModal'", "import AccountFormModal from '../components/AccountFormModal'\n" + import_lines)

# 2. State vars
state_vars = """  const [purchaseModalOpen, setPurchaseModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('daily') // 'daily' or 'purchase'
  const [purchaseInvoices, setPurchaseInvoices] = useState([])
  const [contacts, setContacts] = useState([])
"""
content = content.replace("const [expenseAccounts, setExpenseAccounts] = useState([])", "const [expenseAccounts, setExpenseAccounts] = useState([])\n" + state_vars)

# 3. loadAll query
old_promise = """    const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: budgetsData }] = await Promise.all(["""
new_promise = """    const [{ data: exp }, { data: amc }, { data: accs }, { data: settings }, { data: budgetsData }, { data: pi }, { data: cont }] = await Promise.all(["""
content = content.replace(old_promise, new_promise)

old_queries = """      supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    ])"""
new_queries = """      supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')
    ])"""
content = content.replace(old_queries, new_queries)

# 4. State updates
state_updates = """    setPurchaseInvoices(pi || [])
    setContacts(cont || [])"""
content = content.replace("setExpenseAccounts(accs || [])", "setExpenseAccounts(accs || [])\n" + state_updates)

# 5. KPI logic
# totalExpenses should include purchase invoices!
old_calc = """  const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalExpenses = entriesTotalUsd + amcTotalForView"""
new_calc = """  const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const piTotalUsd = purchaseInvoices.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd"""
content = content.replace(old_calc, new_calc)

# 6. Delete PI function
del_pi = """  async function handleDeletePI(row) {
    if (!confirm('Delete this purchase invoice?')) return
    await supabase.from('purchase_invoices').delete().eq('id', row.id)
    loadAll()
  }"""
content = content.replace("async function handleDeleteAmc", del_pi + "\n  async function handleDeleteAmc")

# 7. Buttons
buttons = """                <button onClick={() => { setEditingRow(null); setPurchaseModalOpen(true); }} className="flex items-center gap-1.5 bg-gold-600 hover:bg-gold-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <FileText size={15} /> New Purchase Invoice
                </button>
                <button onClick={() => { setEditingRow(null); setExpenseModalOpen(true); }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={15} /> New Expense
                </button>"""
content = content.replace("""                <button onClick={() => { setEditingRow(null); setExpenseModalOpen(true); }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                  <Plus size={15} /> New Expense
                </button>""", buttons)

# 8. Modals
modals = """      {purchaseModalOpen && (
        <PurchaseInvoiceFormModal companyId={activeCompany.id} product={activeProduct} company={activeCompany} contacts={contacts} accounts={expenseAccounts} invoice={editingRow} onClose={() => { setPurchaseModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />
      )}"""
content = content.replace("{expenseModalOpen &&", modals + "\n      {expenseModalOpen &&")

# 9. Tabs and Data Tables
# The original code has:
#       <div className="flex justify-between items-end mb-3 mt-8">
#         ... Expense Entries ...
#       <DataTable ... />
old_data_tables = """      <div className="flex justify-between items-end mb-3 mt-8">
        <div>
          <h3 className="font-semibold text-slate-700 flex items-center gap-3">
            <span>Expense Entries</span>"""
            
new_data_tables = """      <div className="flex gap-6 border-b border-slate-200 mb-6 mt-8">
        <button onClick={() => setActiveTab('daily')} className={`pb-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'daily' ? 'border-navy-600 text-navy-700' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>Daily Expenses</button>
        <button onClick={() => setActiveTab('purchase')} className={`pb-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'purchase' ? 'border-navy-600 text-navy-700' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>Purchase Invoices</button>
      </div>

      {activeTab === 'daily' && (
        <>
          <div className="flex justify-between items-end mb-3">
            <div>
              <h3 className="font-semibold text-slate-700 flex items-center gap-3">
                <span>Daily Expense Entries</span>"""
content = content.replace(old_data_tables, new_data_tables)

# 10. Close the activeTab wrapper and render PI table
old_amc_table_end = """        rows={amcContracts.map(r => [
          r.created_at.split('T')[0],
          r.contract_name,
          `${r.start_year}-${String(r.start_month).padStart(2, '0')}`,
          cp.fmt(r.annual_amount_usd),
          <button onClick={() => { setEditingRow(r); setAmcModalOpen(true); }} className="text-slate-400 hover:text-navy-600 p-1"><Pencil size={15} /></button>,
          <button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={15} /></button>
        ])}
      />"""

new_amc_table_end = old_amc_table_end + """
        </>
      )}

      {activeTab === 'purchase' && (
        <>
          <div className="flex justify-between items-end mb-3">
            <h3 className="font-semibold text-slate-700">Purchase Invoices</h3>
          </div>
          <DataTable
            columns={['Date', 'Invoice #', 'Supplier', 'Amount', 'Status', '', '']}
            rows={purchaseInvoices.map(r => [
              r.invoice_date,
              r.invoice_number,
              r.contact?.name || r.supplier_name_freeform || 'Unknown',
              cp.fmt(r.amount_usd),
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Draft' ? 'bg-slate-100 text-slate-600' : r.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{r.status}</span>,
              <button onClick={() => { setEditingRow(r); setPurchaseModalOpen(true); }} className="text-slate-400 hover:text-navy-600 p-1"><Pencil size={15} /></button>,
              <button onClick={() => handleDeletePI(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={15} /></button>
            ])}
          />
        </>
      )}"""
content = content.replace(old_amc_table_end, new_amc_table_end)

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)
