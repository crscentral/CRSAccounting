import re

# 1. Fix AppShell.jsx
with open('src/components/AppShell.jsx', 'r') as f:
    code = f.read()

code = code.replace("{const short = item.to === '/hotel-stats' ? 'Rev & Occ' : item.to === '/hotel-revenue' ? 'Daily Rev' : item.label.split(' ')[0]; return <span>{short}</span>}()",
                    "{(() => { const short = item.to === '/hotel-stats' ? 'Rev & Occ' : item.to === '/hotel-revenue' ? 'Daily Rev' : item.label.split(' ')[0]; return <span>{short}</span> })()}")
with open('src/components/AppShell.jsx', 'w') as f:
    f.write(code)

# 2. Fix FinancialPerformance.jsx
with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

# I had replaced `</div>` with `</div> </div> </div> </div>` incorrectly. Let's revert and fix properly.
code = code.replace("""              </div>
            </div>
          </div>
        </div>
      )}

      {reportModalOpen && (""", """              </div>
            </div>
          </div>
        </div>
      )}

      {reportModalOpen && (""") # wait, let me use git checkout to restore and redo carefully.
