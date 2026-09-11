import re

with open('src/lib/exportUtils.js', 'r') as f:
    content = f.read()

content = content.replace(
    "export function exportMultiSectionPDF({ title, subtitle, sections, filename }) {",
    "export function exportMultiSectionPDF({ title, subtitle, sections, filename, preview = false }) {"
)

content = content.replace(
    "doc.save(`${filename}.pdf`)",
    """if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${filename}.pdf`)
  }"""
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(content)
