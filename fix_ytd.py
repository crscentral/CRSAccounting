import re

with open('src/lib/fiscalYear.js', 'r') as f:
    code = f.read()

old_ytd = r"""export function getYTDRange\(fiscalYearStartMonth = 1, today = new Date\(\)\) \{
  const y = today\.getUTCFullYear\(\)
  const m = today\.getUTCMonth\(\) \+ 1 // 1-12
  let startYear = y
  if \(m < fiscalYearStartMonth\) \{
    startYear = y - 1
  \}
  const from = new Date\(Date\.UTC\(startYear, fiscalYearStartMonth - 1, 1\)\)
  return \{ from: ymd\(from\), to: ymd\(today\) \}
\}"""

new_ytd = """export function getYTDRange(fiscalYearStartMonth = 1, today = new Date()) {
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
}"""

code = re.sub(old_ytd, new_ytd, code)

with open('src/lib/fiscalYear.js', 'w') as f:
    f.write(code)
