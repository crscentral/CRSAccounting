import re
with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

new_code = """      const safeHead = section.columns.map((c, i) => {
        const text = sanitizeText(c)
        return (i > 0) ? { content: text, styles: { halign: 'right' } } : text
      })"""

code = re.sub(
    r"      const safeHead = section\.columns\.map\(sanitizeText\)",
    new_code,
    code
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
