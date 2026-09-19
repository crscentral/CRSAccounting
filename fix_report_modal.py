import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

replacement = """<ReportOptionsModal
        open={reportModalOpen}
        onClose={() => setReportModalOpen(false)}
        onGenerate={generateReport}
        title="Expenses Budget"
        fields={[
          { type: 'currency', key: 'currency', default: displayCurrency }
        ]}
      />"""

content = re.sub(
    r'<ReportOptionsModal\s*open=\{reportModalOpen\}\s*onClose=\{\(\) => setReportModalOpen\(false\)\}\s*onGenerate=\{generateReport\}\s*includeYearSelection=\{false\}\s*/>',
    replacement,
    content
)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
