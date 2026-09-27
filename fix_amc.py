import re

for filename in ['src/pages/RestaurantExpenses.jsx', 'src/pages/HotelExpenses.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # Find the AmcContractFormModal function block and remove invoiceNumber from it
    start_idx = content.find("function AmcContractFormModal")
    if start_idx != -1:
        amc_block = content[start_idx:]
        
        # Remove state
        amc_block = amc_block.replace("  const [invoiceNumber, setInvoiceNumber] = useState(editingRow?.invoice_number || '')\n", "")
        
        # Remove field
        field_str = """                <Field label="Invoice Number">
          <input value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} placeholder="Optional" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>\n"""
        amc_block = amc_block.replace(field_str, "")
        
        content = content[:start_idx] + amc_block
        
        with open(filename, 'w') as f:
            f.write(content)
