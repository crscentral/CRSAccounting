import re

with open('src/lib/fiscalYear.js', 'r') as f:
    content = f.read()

content = content.replace(
    "{ value: 'YESTERDAY', label: 'Yesterday' },",
    "{ value: 'TODAY', label: 'Today' },\n  { value: 'YESTERDAY', label: 'Yesterday' },"
)

# Add getTodayRange
today_func = """
/** Returns { from, to } for Today. */
export function getTodayRange(today = new Date()) {
  const from = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()))
  return { from: ymd(from), to: ymd(from) }
}
"""

content = content.replace(
    "/** Returns { from, to } for Yesterday. */",
    today_func + "\n/** Returns { from, to } for Yesterday. */"
)

content = content.replace(
    "case 'YESTERDAY': return getYesterdayRange(today)",
    "case 'TODAY': return getTodayRange(today)\n    case 'YESTERDAY': return getYesterdayRange(today)"
)

with open('src/lib/fiscalYear.js', 'w') as f:
    f.write(content)
