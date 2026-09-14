import re
with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

new_word = """    } else if (section.columns && section.rows) {
      const rgb = section.headColor || [27, 58, 107]
      const bgColor = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`
      const head = section.columns.map(c => `<th style="background:${bgColor};color:#fff;padding:5px 8px;text-align:left;">${esc(c)}</th>`).join('')
      const body = section.rows.map(r =>
        `<tr>${r.map(cell => `<td style="padding:5px 8px;border:1px solid #ddd;">${esc(cell)}</td>`).join('')}</tr>`
      ).join('')"""

code = re.sub(
    r"    \} else if \(section\.columns && section\.rows\) \{\n      const head = section\.columns\.map\(c => `<th style=\"background:#1B3A6B;color:#fff;padding:5px 8px;text-align:left;\">\$\{esc\(c\)\}</th>`\)\.join\(''\)\n      const body = section\.rows\.map\(r =>\n        `<tr>\$\{r\.map\(cell => `<td style=\"padding:5px 8px;border:1px solid #ddd;\">\$\{esc\(cell\)\}</td>`\)\.join\(''\)\}</tr>`\n      \)\.join\(''\)",
    new_word,
    code,
    flags=re.DOTALL
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
