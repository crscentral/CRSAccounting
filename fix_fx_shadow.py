def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    old_block = """      let fxRate = 1
      if (currency !== 'USD') {
        if (fxRate && !isNaN(Number(fxRate))) {
          fxRate = Number(fxRate)
        } else {
          const rate = await getLatestRate(currency)
          fxRate = rate || 1
        }
      }"""
      
    new_block = """      let finalFxRate = 1
      if (currency !== 'USD') {
        // use state fxRate if provided
        if (fxRate && !isNaN(Number(fxRate))) {
          finalFxRate = Number(fxRate)
        } else {
          const rate = await getLatestRate(currency)
          finalFxRate = rate || 1
        }
      }"""

    # For Sales Invoice, it does grandTotal / fxRate
    # For Purchase Invoice, it does netPayable / fxRate
    
    # We must also replace fxRate with finalFxRate in the lines below
    content = content.replace(old_block, new_block)
    content = content.replace("grandTotal / fxRate", "grandTotal / finalFxRate")
    content = content.replace("netPayable / fxRate", "netPayable / finalFxRate")
    content = content.replace("fx_rate_locked: fxRate,", "fx_rate_locked: currency === 'USD' ? null : finalFxRate,")

    with open(filepath, 'w') as f:
        f.write(content)

fix_file('src/components/PurchaseInvoiceFormModal.jsx')
fix_file('src/components/SalesInvoiceFormModal.jsx')
