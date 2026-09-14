import re
with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

# 1. Add sanitizeText helper at the top
sanitize_func = """
function sanitizeText(str) {
  if (typeof str !== 'string') return str;
  return str
    .replace(/₹/g, 'INR ')
    .replace(/฿/g, 'THB ')
    .replace(/€/g, 'EUR ')
    .replace(/£/g, 'GBP ')
    .replace(/[^\x00-\x7F]/g, ''); // Strip remaining unsupported unicode for jsPDF
}
"""
code = re.sub(r"(import \* as XLSX from 'xlsx')", r"\1\n" + sanitize_func, code)

# 2. Update multi section PDF to use fixed column widths & sanitize
new_multi_pdf = """    } else if (section.columns && section.rows) {
      let columnStyles = {}
      if (section.columns.length === 3) {
        columnStyles = { 0: { cellWidth: 102 }, 1: { cellWidth: 40, halign: 'right' }, 2: { cellWidth: 40, halign: 'right' } }
      } else if (section.columns.length === 2) {
        columnStyles = { 0: { cellWidth: 142 }, 1: { cellWidth: 40, halign: 'right' } }
      }
      
      const safeHead = section.columns.map(sanitizeText)
      const safeBody = section.rows.map(row => row.map(sanitizeText))

      autoTable(doc, {
        startY: y + 3,
        head: [safeHead],
        body: safeBody,
        headStyles: { fillColor: section.headColor || [27, 58, 107], fontSize: 8 },
        styles: { fontSize: 8, cellPadding: 2.5 },
        columnStyles: columnStyles,
        margin: { left: 14, right: 14 },
      })
      y = doc.lastAutoTable.finalY + 10
    }"""

code = re.sub(
    r"    \} else if \(section\.columns && section\.rows\) \{\n      let columnStyles = \{\}\n      if \(section\.columns\.length === 3\) \{\n        columnStyles = \{ 1: \{ cellWidth: 40, halign: 'right' \}, 2: \{ cellWidth: 40, halign: 'right' \} \}\n      \} else if \(section\.columns\.length === 2\) \{\n        columnStyles = \{ 1: \{ cellWidth: 50, halign: 'right' \} \}\n      \}\n      \n      autoTable\(doc, \{\n        startY: y \+ 3,\n        head: \[section\.columns\],\n        body: section\.rows,\n        headStyles: \{ fillColor: section\.headColor \|\| \[27, 58, 107\], fontSize: 8 \},\n        styles: \{ fontSize: 8, cellPadding: 2\.5 \},\n        columnStyles: columnStyles,\n        margin: \{ left: 14, right: 14 \},\n      \}\)\n      y = doc\.lastAutoTable\.finalY \+ 10\n    \}",
    new_multi_pdf,
    code,
    flags=re.DOTALL
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
