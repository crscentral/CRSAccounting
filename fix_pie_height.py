import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

code = code.replace('<ResponsiveContainer width="100%" height="80%">', '<ResponsiveContainer width="100%" height="100%">')

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
