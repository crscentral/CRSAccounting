import re

def patch(filepath, table_type):
    with open(filepath, 'r') as f:
        content = f.read()

    if table_type == 'sales':
        # Invoices
        old_inv = """              { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },"""
        new_inv = """              { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
              { key: 'rate', label: 'Rate', render: r => r.currency === 'USD' ? '1.0000' : (r.fx_rate_locked || (r.amount / r.amount_usd).toFixed(4)) },
              { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },"""
        content = content.replace(old_inv, new_inv)

        # Receipts
        old_rec = """              { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },"""
        content = content.replace(old_rec, new_inv)

    elif table_type == 'purchase':
        old_pur = """              { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
              { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },"""
        new_pur = """              { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
              { key: 'rate', label: 'Rate', render: r => r.currency === 'USD' ? '1.0000' : (r.fx_rate_locked || (r.amount / r.amount_usd).toFixed(4)) },
              { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },"""
        content = content.replace(old_pur, new_pur)

    with open(filepath, 'w') as f:
        f.write(content)

patch('src/pages/SalesInvoices.jsx', 'sales')
patch('src/pages/PurchaseInvoices.jsx', 'purchase')
