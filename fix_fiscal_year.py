import re

with open('src/lib/fiscalYear.js', 'r') as f:
    content = f.read()

# getYearRange
content = re.sub(
    r'export function getYearRange\(year, today = new Date\(\)\) \{\n.*?return \{ from: ymd\(from\), to: ymd\(to\) \}\n\}',
    '''export function getYearRange(year) {
  const from = new Date(Date.UTC(year, 0, 1))
  const to = new Date(Date.UTC(year, 11, 31))
  return { from: ymd(from), to: ymd(to) }
}''', content, flags=re.DOTALL
)

# getMonthRange
content = re.sub(
    r'export function getMonthRange\(year, month, today = new Date\(\)\) \{\n.*?return \{ from: ymd\(from\), to: ymd\(to\) \}\n\}',
    '''export function getMonthRange(year, month) {
  const from = new Date(Date.UTC(year, month - 1, 1))
  const to = new Date(Date.UTC(year, month, 0))
  return { from: ymd(from), to: ymd(to) }
}''', content, flags=re.DOTALL
)

# getMTDRange (keep this as-is? Actually MTD is not directly used in resolvePeriodRange anymore except through getMonthRange)
# resolvePeriodRange uses getMonthRange for MTD

# getYTDRange
content = re.sub(
    r'export function getYTDRange\(fiscalYearStartMonth = 1, today = new Date\(\)\) \{\n  const y = today\.getUTCFullYear\(\)\n  const m = today\.getUTCMonth\(\) \+ 1 // 1-12\n  let startYear = y\n  if \(m < fiscalYearStartMonth\) startYear = y - 1\n  const from = new Date\(Date\.UTC\(startYear, fiscalYearStartMonth - 1, 1\)\)\n  return \{ from: ymd\(from\), to: ymd\(today\) \}\n\}',
    '''export function getYTDRange(fiscalYearStartMonth = 1, today = new Date()) {
  const y = today.getUTCFullYear()
  const m = today.getUTCMonth() + 1 // 1-12
  let startYear = y
  let endYear = y
  if (m < fiscalYearStartMonth) {
    startYear = y - 1
  } else {
    endYear = y + 1
  }
  const from = new Date(Date.UTC(startYear, fiscalYearStartMonth - 1, 1))
  const to = new Date(Date.UTC(endYear, fiscalYearStartMonth - 1, 0))
  return { from: ymd(from), to: ymd(to) }
}''', content, flags=re.DOTALL
)

# getLastNYearsRange
content = re.sub(
    r'export function getLastNYearsRange\(n, fiscalYearStartMonth = 1, today = new Date\(\)\) \{\n  const y = today\.getUTCFullYear\(\)\n  const m = today\.getUTCMonth\(\) \+ 1\n  let currentFYStartYear = m < fiscalYearStartMonth \? y - 1 : y\n  const fromYear = currentFYStartYear - \(n - 1\)\n  const from = new Date\(Date\.UTC\(fromYear, fiscalYearStartMonth - 1, 1\)\)\n  return \{ from: ymd\(from\), to: ymd\(today\) \}\n\}',
    '''export function getLastNYearsRange(n, fiscalYearStartMonth = 1, today = new Date()) {
  const y = today.getUTCFullYear()
  const m = today.getUTCMonth() + 1
  let currentFYStartYear = m < fiscalYearStartMonth ? y - 1 : y
  const fromYear = currentFYStartYear - (n - 1)
  const from = new Date(Date.UTC(fromYear, fiscalYearStartMonth - 1, 1))
  const to = new Date(Date.UTC(currentFYStartYear + 1, fiscalYearStartMonth - 1, 0))
  return { from: ymd(from), to: ymd(to) }
}''', content, flags=re.DOTALL
)

with open('src/lib/fiscalYear.js', 'w') as f:
    f.write(content)
