with open('src/components/PaymentReceiptFormModal.jsx', 'r') as f:
    content = f.read()

old_select = """      if (inv) {
        if (!customerName) setCustomerName(inv.contact?.name || '')
        setCurrency(inv.currency)
        // Only set amount if empty, to allow partial payments
        if (!amount) setAmount(inv.amount)
      }"""

new_select = """      if (inv) {
        if (!customerName) setCustomerName(inv.contact?.name || '')
        setCurrency(inv.currency)
        // Auto-sync the exact conversion rate from the invoice
        const invRate = inv.fx_rate_locked || (inv.amount && inv.amount_usd && inv.currency !== 'USD' ? (inv.amount / inv.amount_usd).toFixed(4) : '')
        setFxRate(invRate)
        // Only set amount if empty, to allow partial payments
        if (!amount) setAmount(inv.amount)
      }"""

content = content.replace(old_select, new_select)

with open('src/components/PaymentReceiptFormModal.jsx', 'w') as f:
    f.write(content)
