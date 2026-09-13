import re

def patch_file(filepath, table_type):
    with open(filepath, 'r') as f:
        content = f.read()

    if table_type == 'sales':
        # Invoices Tab
        old_cols1 = "columns={['Invoice #', 'Customer', 'Date', 'Due', 'Amount', `Amount (${selections.currency})`, 'Status', '']}"
        new_cols1 = "columns={['Invoice #', 'Customer', 'Date', 'Due', 'Amount', 'Rate', `Amount (${selections.currency})`, 'Status', '']}"
        content = content.replace(old_cols1, new_cols1)
        
        old_row1 = """              <div className="font-medium text-slate-800">{r.amount} {r.currency}</div>
            ),
            cp.fmt(r.amount_usd),"""
        new_row1 = """              <div className="font-medium text-slate-800">{r.amount} {r.currency}</div>
            ),
            r.currency === 'USD' ? '1.0000' : (r.fx_rate_locked || (r.amount / r.amount_usd).toFixed(4)),
            cp.fmt(r.amount_usd),"""
        content = content.replace(old_row1, new_row1)
        
        # Receipts Tab
        old_cols2 = "columns={['Receipt #', 'Invoice #', 'Date', 'Customer', 'Amount', `Amount (${selections.currency})`, 'Method', '']}"
        new_cols2 = "columns={['Receipt #', 'Invoice #', 'Date', 'Customer', 'Amount', 'Rate', `Amount (${selections.currency})`, 'Method', '']}"
        content = content.replace(old_cols2, new_cols2)

        old_row2 = """              <div className="font-medium text-slate-800">{r.amount} {r.currency}</div>
            ),
            cp.fmt(r.amount_usd),"""
        new_row2 = """              <div className="font-medium text-slate-800">{r.amount} {r.currency}</div>
            ),
            r.currency === 'USD' ? '1.0000' : (r.fx_rate_locked || (r.amount / r.amount_usd).toFixed(4)),
            cp.fmt(r.amount_usd),"""
        content = content.replace(old_row2, new_row2)

    elif table_type == 'purchase':
        old_cols = "columns={['Invoice #', 'Date', 'Supplier', 'Currency', 'Amount', `Amount (${selections.currency})`, 'Status', '']}"
        new_cols = "columns={['Invoice #', 'Date', 'Supplier', 'Currency', 'Amount', 'Rate', `Amount (${selections.currency})`, 'Status', '']}"
        content = content.replace(old_cols, new_cols)
        
        old_row = """              <div className="font-medium text-slate-800">{r.amount} {r.currency}</div>
            ),
            cp.fmt(r.amount_usd),"""
        new_row = """              <div className="font-medium text-slate-800">{r.amount} {r.currency}</div>
            ),
            r.currency === 'USD' ? '1.0000' : (r.fx_rate_locked || (r.amount / r.amount_usd).toFixed(4)),
            cp.fmt(r.amount_usd),"""
        content = content.replace(old_row, new_row)
        
    with open(filepath, 'w') as f:
        f.write(content)

patch_file('src/pages/SalesInvoices.jsx', 'sales')
patch_file('src/pages/PurchaseInvoices.jsx', 'purchase')
