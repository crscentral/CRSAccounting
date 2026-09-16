import re

with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

old_code = """  doc.text(fromNameWrapped, col1, y)
  doc.text(toNameWrapped, col2, y)
  doc.text(docNameWrapped, col3, y)
  
  y += Math.max(fromNameWrapped.length, toNameWrapped.length, docNameWrapped.length) * 4.5"""

new_code = """  doc.text(fromNameWrapped, col1, y)
  doc.text(toNameWrapped, col2, y)
  doc.text(docNameWrapped, col3, y)
  
  const y1 = y + fromNameWrapped.length * 4.5
  const y2 = y + toNameWrapped.length * 4.5
  const y3 = y + docNameWrapped.length * 4.5"""

code = code.replace(old_code, new_code)

old_code2 = """  const colStartY = y
  const endY1 = renderColumn(fromLines, col1, 60, colStartY)
  const endY2 = renderColumn(billLines, col2, 62, colStartY)
  const endY3 = renderColumn(docLines, col3, 46, colStartY)"""

new_code2 = """  const endY1 = renderColumn(fromLines, col1, 60, y1)
  const endY2 = renderColumn(billLines, col2, 62, y2)
  const endY3 = renderColumn(docLines, col3, 46, y3)"""

code = code.replace(old_code2, new_code2)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
