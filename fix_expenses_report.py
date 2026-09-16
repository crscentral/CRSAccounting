import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# Add the checkboxGroup field for ReportOptionsModal
old_report = """        <ReportOptionsModal
          title="Expenses"
          fields={[{ type: 'currency', key: 'currency', default: cp.displayCurrency }, { type: 'period', key: 'period', default: 'ALL_TIME' }]}
          onGenerate={generateExpensesReport}
          onClose={() => setReportModalOpen(false)}
        />"""

new_report = """        <ReportOptionsModal
          title="Expenses"
          fields={[
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
            { type: 'checkboxGroup', key: 'sections', label: 'Select Specific Expense Heads (Optional, leave blank for all)', options: [...new Set(entries.map(e => e.account ? `${e.account.code} - ${e.account.name}` : 'Unknown'))] }
          ]}
          onGenerate={generateExpensesReport}
          onClose={() => setReportModalOpen(false)}
        />"""
code = code.replace(old_report, new_report)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
