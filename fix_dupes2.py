with open('src/pages/HotelExpenses.jsx', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 158 <= i <= 165: # lines 159 to 166
        continue
    new_lines.append(line)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.writelines(new_lines)
