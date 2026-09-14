import re
with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

button_ui = """                    </div>
                    <div className="flex flex-col sm:flex-row items-end sm:items-center justify-between gap-3 sm:gap-4 w-full sm:w-auto mt-3 sm:mt-0">
                      <div className="flex flex-wrap justify-end gap-2">
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
                        className="flex-shrink-0 text-red-500 hover:text-red-700 bg-red-50 hover:bg-red-100 p-2 rounded-lg transition-colors"
                        title="Delete Company"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>"""

code = re.sub(
    r"                    </div>\n                    <div className=\"flex flex-wrap gap-2\">\n                      \{ALL_PRODUCTS\.map\(product => \{.*?\n                      \}\)\}\n                    </div>\n                  </div>",
    button_ui,
    code,
    flags=re.DOTALL
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
