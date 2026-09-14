import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

# I need to add state for pending products selection.
# Or just a local state for each company?
# Since pendingCompanies is a mapped array, it's easier to add checkboxes right into the card.

new_card_jsx = """              {pendingCompanies.map(c => {
                const ownerMember = c.members?.find(m => m.role === 'owner')
                const ownerEmail = ownerMember?.profile?.email || c.email || 'N/A'
                const ownerName = ownerMember?.profile?.full_name || ''
                const isWorking = actionInProgress === c.id

                return (
                  <div key={c.id} className="flex flex-col sm:flex-row justify-between gap-4 border border-slate-200 rounded-xl p-4 bg-slate-50/50 hover:bg-white transition-colors">
                    <div className="flex-1">
                      <div className="font-semibold text-slate-800 text-sm">{c.name}</div>
                      <div className="text-xs text-slate-600 mt-1">
                        <strong>Applicant:</strong> {ownerName ? `${ownerName} (${ownerEmail})` : ownerEmail}
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5 mb-3">
                        Base Currency: <span className="font-medium text-slate-600">{c.base_currency}</span> • Created {new Date(c.created_at).toLocaleString()}
                      </div>
                      
                      <div className="text-xs font-semibold text-slate-700 mb-2">Select Products to Grant:</div>
                      <div className="flex flex-col gap-2">
                        <label className="flex items-center gap-2 text-sm text-slate-700">
                          <input type="checkbox" id={`prod-basic-${c.id}`} defaultChecked className="rounded border-slate-300 text-blue-600" />
                          CRS Basic Accounting
                        </label>
                        <label className="flex items-center gap-2 text-sm text-slate-700">
                          <input type="checkbox" id={`prod-hotel-${c.id}`} className="rounded border-slate-300 text-blue-600" />
                          CRS Hotel Accounting
                        </label>
                        <label className="flex items-center gap-2 text-sm text-slate-700">
                          <input type="checkbox" id={`prod-rest-${c.id}`} className="rounded border-slate-300 text-blue-600" />
                          CRS Restaurant Accounting
                        </label>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-end gap-2 justify-center">
                      <button
                        onClick={async () => {
                          const basic = document.getElementById(`prod-basic-${c.id}`).checked
                          const hotel = document.getElementById(`prod-hotel-${c.id}`).checked
                          const rest = document.getElementById(`prod-rest-${c.id}`).checked
                          
                          if (!basic && !hotel && !rest) {
                            alert('Please select at least one product before approving.')
                            return
                          }
                          
                          const products = []
                          if (basic) products.push('basic')
                          if (hotel) products.push('hotel')
                          if (rest) products.push('restaurant')
                          
                          // First set the products
                          const { error: err } = await supabase.rpc('set_company_products', {
                            p_company_id: c.id,
                            p_products: products
                          })
                          if (err) {
                            alert('Error setting products: ' + err.message)
                            return
                          }
                          
                          // Then approve
                          decideCompany(c, true)
                        }}
                        disabled={isWorking}
                        className="w-full sm:w-auto flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <Check size={16} />
                        {isWorking ? 'Processing…' : 'Approve Company'}
                      </button>
                      <button
                        onClick={() => decideCompany(c, false)}
                        disabled={isWorking}
                        className="w-full sm:w-auto flex items-center justify-center gap-1.5 border border-red-200 bg-white hover:bg-red-50 text-red-600 text-sm font-semibold px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <X size={16} />
                        Reject Request
                      </button>
                    </div>
                  </div>
                )
              })}"""

# Replace the old pending companies map
code = re.sub(
    r'              \{pendingCompanies\.map\(c => \{.*?                  </div>\n                \)\n              \}\)\}',
    new_card_jsx,
    code,
    flags=re.DOTALL
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
