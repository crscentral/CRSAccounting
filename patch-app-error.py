import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Replace the export
target = "export default function HotelExpenses() {"
replacement = """
export default function HotelExpenses() {
  return <ErrorBoundary><HotelExpensesInner /></ErrorBoundary>;
}

function HotelExpensesInner() {
"""
content = content.replace(target, replacement)

# Remove the internal ErrorBoundary
content = content.replace("<ErrorBoundary>\n    <div>", "<div>")
content = content.replace("    </ErrorBoundary>\n  )\n}", "  )\n}")

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
