const fs = require('fs')
let code = fs.readFileSync('src/lib/exportUtils.js', 'utf-8')

const target = `  if (invoice.payment_terms || invoice.notes) {
    const combined = [invoice.payment_terms, invoice.notes].filter(Boolean).join("\\n\\n")

')
    finalY = renderRichText(doc, combined, 14, finalY, pageWidth - 28)
  }`

const repl = `  if (invoice.payment_terms || invoice.notes) {
    const combined = [invoice.payment_terms, invoice.notes].filter(Boolean).join("\\n\\n")
    finalY = renderRichText(doc, combined, 14, finalY, pageWidth - 28)
  }`

code = code.replace(target, repl)

// While we are at it, replace any other stray "\\n\\n')\\n"
code = code.replace(/join\("\\n\\n"\)\s*'\)\s*/, 'join("\\n\\n")\n    ')

fs.writeFileSync('src/lib/exportUtils.js', code)
