import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

replacement = """{reportModalOpen && (
        <ReportOptionsModal
          onClose={() => setReportModalOpen(false)}
          onGenerate={generateReport}
          title="Expenses Budget"
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency }
          ]}
        />
      )}"""

content = re.sub(
    r'<ReportOptionsModal[\s\S]*?/>',
    replacement,
    content
)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
