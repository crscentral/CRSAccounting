import re

with open('src/lib/fiscalYear.js', 'r') as f:
    content = f.read()

content = content.replace(
    "  { value: 'MTD', label: 'Month' },",
    "  { value: 'YESTERDAY', label: 'Yesterday' },\n  { value: 'MTD', label: 'Month' },"
)

yesterday_func = """/** Returns { from, to } for Yesterday. */
export function getYesterdayRange(today = new Date()) {
  const from = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate() - 1))
  return { from: ymd(from), to: ymd(from) }
}

/** Returns { from, to } for one full calendar year. If it's the current year, `to` is"""

content = content.replace(
    "/** Returns { from, to } for one full calendar year. If it's the current year, `to` is",
    yesterday_func
)

content = content.replace(
    "switch (periodType) {",
    "switch (periodType) {\n    case 'YESTERDAY': return getYesterdayRange(today)"
)

with open('src/lib/fiscalYear.js', 'w') as f:
    f.write(content)

with open('src/lib/useCurrencyAndPeriod.js', 'r') as f:
    content = f.read()

content = content.replace(
    "export function useCurrencyAndPeriod() {",
    "export function useCurrencyAndPeriod(defaultPeriod = 'YTD') {"
)
content = content.replace(
    "const [periodType, setPeriodType] = useState('YTD')",
    "const [periodType, setPeriodType] = useState(defaultPeriod)"
)

with open('src/lib/useCurrencyAndPeriod.js', 'w') as f:
    f.write(content)
