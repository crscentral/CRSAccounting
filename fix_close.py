import sys

with open('src/pages/HotelBudget.jsx', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<Save size={14} /> {savingRooms ? \'Saving…\' : \'Save\'}' in line:
        lines[i+3] = "      </div>)}\n"
        break

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.writelines(lines)
