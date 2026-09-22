import re

with open('src/lib/exportUtils.js', 'r') as f:
    content = f.read()

old_render = """  function renderColumn(lines, x, maxWidth, startY) {
    let cy = startY
    lines.forEach(line => {
      const wrapped = doc.splitTextToSize(line, maxWidth)
      doc.text(wrapped, x, cy)
      cy += wrapped.length * 4.5
    })
    return cy
  }"""

new_render = """  function renderColumn(lines, x, maxWidth, startY) {
    let cy = startY
    lines.forEach(line => {
      const explicitLines = line.split('\\n')
      explicitLines.forEach(el => {
        const wrapped = doc.splitTextToSize(el, maxWidth)
        wrapped.forEach(wl => {
          doc.text(wl, x, cy)
          cy += 4.5
        })
      })
    })
    return cy
  }"""

content = content.replace(old_render, new_render)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(content)
