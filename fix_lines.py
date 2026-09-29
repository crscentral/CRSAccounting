with open('src/pages/HotelExpenses.jsx', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # If line 393, 394 skip
    if 392 <= i <= 395:
        if line.strip() == "</>" or line.strip() == ")}":
            continue
    new_lines.append(line)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.writelines(new_lines)
