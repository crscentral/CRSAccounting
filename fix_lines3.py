with open('src/pages/HotelExpenses.jsx', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 442 <= i <= 447: # lines 443-448
        pass # skip them
    else:
        new_lines.append(line)
        
    if i == 447:
        new_lines.append("            </div>\n")
        new_lines.append("          )}\n")
        new_lines.append("        </>\n")
        new_lines.append("      )}\n")
        
with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.writelines(new_lines)
