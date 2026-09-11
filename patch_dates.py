import re
import os

def replace_in_file(filename, old, new):
    with open(filename, 'r') as f:
        content = f.read()
    if "export function formatDate(d)" not in content and 'fiscalYear.js' in filename:
        content += "\nexport function formatDate(d) {\n  if (!d) return '';\n  const [y, m, day] = d.split('-');\n  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];\n  return `${parseInt(day, 10)} ${months[parseInt(m, 10) - 1]}, ${y}`;\n}\n"
    elif 'fiscalYear.js' not in filename:
        if "import { resolveReportPeriod }" in content:
            content = content.replace("import { resolveReportPeriod }", "import { resolveReportPeriod, formatDate }")
        elif "import { resolveReportPeriod" in content:
             content = content.replace("import { resolveReportPeriod", "import { resolveReportPeriod, formatDate")
        elif "import { getYearRange" in content:
             pass
        else:
            # Need to add import formatDate from '../lib/fiscalYear'
            content = content.replace("import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'", "import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'\nimport { formatDate } from '../lib/fiscalYear'")
        
        # Replace date rendering in DataTable
        if filename == 'src/pages/PurchaseInvoices.jsx' or filename == 'src/pages/SalesInvoices.jsx':
            content = re.sub(
                r"\{ key: 'date', label: 'Date', render: r => r\.(invoice_date|receipt_date) \}",
                r"{ key: 'date', label: 'Date', render: r => <span className=\"whitespace-nowrap\">{formatDate(r.\1)}</span> }",
                content
            )
        elif filename == 'src/pages/Transactions.jsx':
            content = re.sub(
                r"\{ key: 'date', label: 'Date' \}",
                r"{ key: 'date', label: 'Date', render: r => <span className=\"whitespace-nowrap\">{formatDate(r.date)}</span> }",
                content
            )
            
    with open(filename, 'w') as f:
        f.write(content)

replace_in_file('src/lib/fiscalYear.js', '', '')
replace_in_file('src/pages/PurchaseInvoices.jsx', '', '')
replace_in_file('src/pages/SalesInvoices.jsx', '', '')
replace_in_file('src/pages/Transactions.jsx', '', '')
