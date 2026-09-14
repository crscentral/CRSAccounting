import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# 1. Add handleCompanyDelete
func = """  async function handleCompanyDelete(companyId, companyName) {
    if (!window.prompt(`This will completely delete the company "${companyName}" and ALL of its data (invoices, accounts, ledgers). Type "DELETE" to confirm:`) === 'DELETE') return
    
    setActionInProgress(companyId)
    try {
      const { error } = await supabase.from('companies').delete().eq('id', companyId)
      if (error) throw error
      setAllCompanies(allCompanies.filter(c => c.id !== companyId))
      alert('Company deleted successfully.')
    } catch (err) {
      alert('Failed to delete company: ' + err.message)
    } finally {
      setActionInProgress(null)
    }
  }

  async function toggleCompanyProduct(c, product) {"""

code = code.replace("  async function toggleCompanyProduct(c, product) {", func)

# 2. Add Delete button in the UI
button_ui = """                      </div>
                    </div>
                    <div className="flex flex-col sm:flex-row items-end sm:items-center justify-between gap-3 w-full sm:w-auto">
                      <div className="flex flex-wrap gap-2">
                        {ALL_PRODUCTS.map(product => {
                          const isOn = enabled.includes(product)
                          const isSaving = productSaving === c.id + product
                          return (
                            <button
                              key={product}
                              disabled={isSaving}
                              onClick={() => toggleCompanyProduct(c, product)}
                              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50 ${isOn ? 'bg-navy-600 text-white border-navy-600' : 'bg-white text-slate-500 border-slate-200'}`}
                            >
                              {PRODUCT_LABELS[product]}
                            </button>
                          )
                        })}
                      </div>
                      <button
                        onClick={() => handleCompanyDelete(c.id, c.name)}
                        disabled={actionInProgress === c.id}
                        className="text-red-500 hover:text-red-700 bg-red-50 hover:bg-red-100 p-1.5 rounded-lg transition-colors ml-2"
                        title="Delete Company"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>"""

code = re.sub(
    r"                    </div>\n                    <div className=\"flex flex-wrap gap-2\">\n                      \{ALL_PRODUCTS\.map\(product => \{.*?\n                        \}\)\}\n                      </div>\n                  </div>",
    button_ui,
    code,
    flags=re.DOTALL
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
