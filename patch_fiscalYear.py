import re

with open('src/lib/fiscalYear.js', 'r') as f:
    content = f.read()

# Replace ymd
old_ymd = """function ymd(d) {
  return d.toISOString().slice(0, 10)
}"""

new_ymd = """function ymd(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}"""
content = content.replace(old_ymd, new_ymd)

# Replace all getUTC to local
content = content.replace("getUTCFullYear()", "getFullYear()")
content = content.replace("getUTCMonth()", "getMonth()")
content = content.replace("getUTCDate()", "getDate()")

# Replace all Date.UTC to just new Date(y, m, d)
content = re.sub(r'new Date\(Date\.UTC\((.*?)\)\)', r'new Date(\1)', content)

with open('src/lib/fiscalYear.js', 'w') as f:
    f.write(content)
