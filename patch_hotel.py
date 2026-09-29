with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    content = f.read()

# Change the collected logic in the modal
old_logic = "        invoice_amount_usd: Math.round(invoiceAmount / fxRate * 100) / 100,\n        collected_amount_usd: Math.round((Number(collectedAmount) || 0) / fxRate * 100) / 100,"
new_logic = "        invoice_amount_usd: Math.round(invoiceAmount / fxRate * 100) / 100,\n        collected_amount_usd: Math.round((collectedAmount === '' ? invoiceAmount : (Number(collectedAmount) || 0)) / fxRate * 100) / 100,"
content = content.replace(old_logic, new_logic)

old_submit = "collected_amount: Number(collectedAmount) || 0,"
new_submit = "collected_amount: collectedAmount === '' ? invoiceAmount : (Number(collectedAmount) || 0),"
content = content.replace(old_submit, new_submit)

old_input = "<input type=\"number\" step=\"0.01\" min=\"0\" value={collectedAmount} onChange={e => setCollectedAmount(e.target.value)} className=\"w-full border border-slate-300 rounded-lg px-3 py-2 text-sm\" />"
new_input = "<input type=\"number\" step=\"0.01\" min=\"0\" placeholder={`Defaults to Full Total (${invoiceAmount.toFixed(2)})`} value={collectedAmount} onChange={e => setCollectedAmount(e.target.value)} className=\"w-full border border-slate-300 rounded-lg px-3 py-2 text-sm\" />"
content = content.replace(old_input, new_input)

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(content)

