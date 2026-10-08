with open("src/lib/exportUtils.js", "r") as f:
    content = f.read()

import re

old_block = """  doc.setDrawColor(220)
  doc.line(130, finalY - 2, rightX, finalY - 2)
  doc.setFont(undefined, 'bold')
  doc.setFontSize(11)
  doc.text(isSales ? 'Grand total' : 'Net Payable', 130, finalY + 3)
  doc.text(`${grandTotal.toFixed(2)} ${invoice.currency}`, rightX, finalY + 3, { align: 'right' })
  finalY += 9

  if (isSales) {
    doc.setFont(undefined, 'normal')
    doc.setFontSize(9)
    doc.setTextColor(90)
    doc.text('Paid', 130, finalY)
    doc.setTextColor(20)
    doc.text(`${paid.toFixed(2)} ${invoice.currency}`, rightX, finalY, { align: 'right' })
    finalY += 6
    doc.setFont(undefined, 'bold')
    doc.setTextColor(20)
    doc.text('Balance due', 130, finalY)
    doc.text(`${Math.max(0, grandTotal - paid).toFixed(2)} ${invoice.currency}`, rightX, finalY, { align: 'right' })
    finalY += 6
  }"""

new_block = """  const fxRate = Number(invoice.fx_rate_locked) || (invoice.amount ? (Number(invoice.amount) / Number(invoice.amount_usd)) : 1)
  const usdGrandTotal = Number(invoice.amount_usd) || grandTotal / (fxRate || 1)
  const usdPaid = paid / (fxRate || 1)
  const usdBalance = Math.max(0, grandTotal - paid) / (fxRate || 1)
  const printUsd = invoice.currency && invoice.currency !== 'USD'

  doc.setDrawColor(220)
  doc.line(130, finalY - 2, rightX, finalY - 2)
  doc.setFont(undefined, 'bold')
  doc.setFontSize(11)
  doc.text(isSales ? 'Grand total' : 'Net Payable', 130, finalY + 3)
  
  let grandTotalText = `${grandTotal.toFixed(2)} ${invoice.currency}`
  if (printUsd) grandTotalText += `  (USD ${usdGrandTotal.toFixed(2)})`
  doc.text(grandTotalText, rightX, finalY + 3, { align: 'right' })
  finalY += 9

  if (isSales) {
    doc.setFont(undefined, 'normal')
    doc.setFontSize(9)
    doc.setTextColor(90)
    doc.text('Paid', 130, finalY)
    doc.setTextColor(20)
    
    let paidText = `${paid.toFixed(2)} ${invoice.currency}`
    if (printUsd) paidText += `  (USD ${usdPaid.toFixed(2)})`
    doc.text(paidText, rightX, finalY, { align: 'right' })
    finalY += 6
    
    doc.setFont(undefined, 'bold')
    doc.setTextColor(20)
    doc.text('Balance due', 130, finalY)
    
    let balText = `${Math.max(0, grandTotal - paid).toFixed(2)} ${invoice.currency}`
    if (printUsd) balText += `  (USD ${usdBalance.toFixed(2)})`
    doc.text(balText, rightX, finalY, { align: 'right' })
    finalY += 6
  }"""

content = content.replace(old_block, new_block)

with open("src/lib/exportUtils.js", "w") as f:
    f.write(content)

