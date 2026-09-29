import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

target = "formatter={(value, name, props) => [`${cp.fmt(value)} (${props.payload.percentStr})`, 'Amount']}"
replacement = "formatter={(value, name, props) => [`${cp.fmt(value)} (${props?.payload?.percentStr || ''})`, 'Amount']}"

content = content.replace(target, replacement)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
