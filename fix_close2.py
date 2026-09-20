import sys

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
"""          {can(['owner', 'admin', 'accountant']) && (
            <button onClick={saveRoomInventory} disabled={savingRooms} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg disabled:opacity-60">
              <Save size={14} /> {savingRooms ? 'Saving…' : 'Save'}
            </button>
          )}
      </div>)}
      </div>""",
"""          {can(['owner', 'admin', 'accountant']) && (
            <button onClick={saveRoomInventory} disabled={savingRooms} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg disabled:opacity-60">
              <Save size={14} /> {savingRooms ? 'Saving…' : 'Save'}
            </button>
          )}
        </div>
      </div>)}"""
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
