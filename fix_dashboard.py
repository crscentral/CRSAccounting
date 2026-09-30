import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# 1. Add prodFilter to loadData
prod_filter_str = "    const prodFilter = activeProduct === 'hotel' ? ['hotel', 'restaurant'] : [activeProduct]\n"
content = content.replace("async function loadData() {\n", "async function loadData() {\n" + prod_filter_str)

# Replace .eq('product', activeProduct) with .in('product', prodFilter) in the top queries
content = re.sub(
    r"\.eq\('product', activeProduct\)",
    ".in('product', prodFilter)",
    content
)

# 2. Fix recent transactions length (from 10 to 3, and 5 to 3)
content = content.replace(".slice(0, 5)", ".slice(0, 3)")
content = content.replace(".slice(0, 10)", ".slice(0, 3)")

# Write back
with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
