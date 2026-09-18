import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

code = code.replace("function Dashboard() {", "export default function Dashboard() {")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
