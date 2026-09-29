with open('src/pages/HotelExpenses.jsx', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i == 420: # line 421 (0-indexed 420) is `        </>`
        if line.strip() == "</>":
            continue
    new_lines.append(line)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.writelines(new_lines)
