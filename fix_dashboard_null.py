import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# I will replace all instances of .slice(0, 7) with safer optional chaining
content = content.replace("i.invoice_date.slice(0, 7)", "(i.invoice_date || '').slice(0, 7)")
content = content.replace("r.stat_date.slice(0, 7)", "(r.stat_date || '').slice(0, 7)")
content = content.replace("r.entry_date.slice(0, 7)", "(r.entry_date || '').slice(0, 7)")
content = content.replace("e.expense_date.slice(0, 7)", "(e.expense_date || '').slice(0, 7)")
content = content.replace("r.revenue_date.slice(0, 7)", "(r.revenue_date || '').slice(0, 7)")
content = content.replace("r.receipt_date.slice(0, 7)", "(r.receipt_date || '').slice(0, 7)")

# Also in the filter for YTD, check if m.month is truthy
old_ytd_rev = """    ytdRevenue = Object.values(monthlyMap).filter(m => {
      const [y, mo] = m.month.split('-')"""

new_ytd_rev = """    ytdRevenue = Object.values(monthlyMap).filter(m => {
      if (!m.month) return false
      const [y, mo] = m.month.split('-')"""

content = content.replace(old_ytd_rev, new_ytd_rev)

old_ytd_exp = """    ytdExpenses = Object.values(monthlyMap).filter(m => {
      const [y, mo] = m.month.split('-')"""

new_ytd_exp = """    ytdExpenses = Object.values(monthlyMap).filter(m => {
      if (!m.month) return false
      const [y, mo] = m.month.split('-')"""

content = content.replace(old_ytd_exp, new_ytd_exp)

# Also check that key is truthy before doing anything
# Since we replaced .slice with (|| '').slice(0, 7), if the date was null, key is empty string.
# monthlyMap[''] is safe (just creates an empty key in the object) but let's just make it bulletproof.
old_key = """      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }"""
new_key = """      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }"""
content = content.replace(old_key, new_key)


with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)

