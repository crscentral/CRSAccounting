import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

old_actions = r'actions=\{.*?</>\s*\)\}\s*</div>\s*\}'
new_actions = """actions={
          <div className="flex flex-wrap items-center gap-2">
            {can(['owner', 'admin']) && (
              <button onClick={() => {
                const newVal = !isLocked
                setIsLocked(newVal)
                localStorage.setItem(`daily_rev_lock_${activeCompany?.id}`, String(newVal))
              }} className={`flex items-center gap-1.5 border text-sm font-medium px-3 py-2 rounded-lg transition-colors ${isLocked ? 'border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}>
                {isLocked ? '🔒 Unlock Page' : '🔓 Lock Page'}
              </button>
            )}
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button disabled={isLocked} onClick={() => { setEditingRow(null); setRoomModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed">
                  <BedDouble size={15} /> Room Revenue
                </button>
                <button disabled={isLocked} onClick={() => { setEditingRow(null); setAncillaryModalOpen(true) }} className="flex items-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed">
                  <Plus size={15} /> Other Revenue
                </button>
              </>
            )}
          </div>
        }"""
code = re.sub(old_actions, new_actions, code, flags=re.DOTALL)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
