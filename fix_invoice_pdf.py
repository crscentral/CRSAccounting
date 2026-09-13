import re

with open('src/lib/exportUtils.js', 'r') as f:
    content = f.read()

bad_block = """  const pageCount = doc.internal.getNumberOfPages()
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i)
    if (loadedLogo?.dataUrl) {
      const logoH = 12
      const logoW = logoH * loadedLogo.ratio
      doc.addImage(loadedLogo.dataUrl, 'PNG', pageWidth - 14 - logoW, 10, logoW, logoH)
    }
  }

  if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${invoice.invoice_number}.pdf`)
  }"""

good_block = """  if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${invoice.invoice_number}.pdf`)
  }"""

if bad_block in content:
    content = content.replace(bad_block, good_block)
    print("Fixed exportInvoicePDF")
else:
    print("Could not find the bad block!")

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(content)
