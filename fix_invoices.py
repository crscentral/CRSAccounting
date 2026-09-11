import re

for filename in ['src/pages/PurchaseInvoices.jsx', 'src/pages/SalesInvoices.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # Update dependencies for useEffect
    content = re.sub(
        r"useEffect\(\(\) => \{ if \(activeCompany\) loadData\(\) \}, \[activeCompany, activeProduct\]\)",
        "useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])",
        content
    )

    # Add .gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
    if 'PurchaseInvoices' in filename:
        content = re.sub(
            r"\.eq\('product', activeProduct\)\.order\('invoice_date', \{ ascending: false \}\),",
            ".eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),",
            content
        )
    else:
        content = re.sub(
            r"supabase\.from\('sales_invoices'\)\.select\('\*, contact:contacts\(name, email, phone, address\)'\)\.eq\('company_id', activeCompany\.id\)\.eq\('product', activeProduct\)\.order\('invoice_date', \{ ascending: false \}\)",
            "supabase.from('sales_invoices').select('*, contact:contacts(name, email, phone, address)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false })",
            content
        )
        content = re.sub(
            r"supabase\.from\('payment_receipts'\)\.select\('\*, invoice:sales_invoices\(invoice_number\)'\)\.eq\('company_id', activeCompany\.id\)\.eq\('product', activeProduct\)\.order\('receipt_date', \{ ascending: false \}\)",
            "supabase.from('payment_receipts').select('*, invoice:sales_invoices(invoice_number)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to).order('receipt_date', { ascending: false })",
            content
        )
        
    with open(filename, 'w') as f:
        f.write(content)
