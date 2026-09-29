with open('src/pages/HotelExpenses.jsx', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 166 <= i <= 174: # duplicated block
        pass
    else:
        new_lines.append(line)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.writelines(new_lines)
