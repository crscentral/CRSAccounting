import re
with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

new_table_code = """    } else if (section.columns && section.rows) {
      autoTable(doc, {
        startY: y + 3,
        head: [section.columns],
        body: section.rows,
        headStyles: { fillColor: section.headColor || [27, 58, 107], fontSize: 8 },
        styles: { fontSize: 8, cellPadding: 2.5 },
        margin: { left: 14, right: 14 },
      })
      y = doc.lastAutoTable.finalY + 10
    }"""

code = re.sub(
    r"    \} else if \(section\.columns && section\.rows\) \{\n      autoTable\(doc, \{\n        startY: y \+ 3,\n        head: \[section\.columns\],\n        body: section\.rows,\n        headStyles: \{ fillColor: \[27, 58, 107\], fontSize: 8 \},\n        styles: \{ fontSize: 8, cellPadding: 2\.5 \},\n        margin: \{ left: 14, right: 14 \},\n      \}\)\n      y = doc\.lastAutoTable\.finalY \+ 10\n    \}",
    new_table_code,
    code,
    flags=re.DOTALL
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
